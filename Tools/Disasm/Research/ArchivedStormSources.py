"""Строки, определения имён и полнострочные комментарии архивных исходников STORM.

Документация: ../../../Docs/AuthorSourceInventory.md#структура-строк-и-имён-storm
"""
from hashlib import sha256
import json
import re
from zipfile import ZipFile

from ArchivedSourceInventory import ARCHIVE, ARCHIVE_SHA256, load_sources
from ArchivedXasSources import QUERY_NAMES
from CheckIntro import ROOT
from InspectArchivePhysicalReferences import storm_reference_blocks


def split_records(content):
    end, records = len(content), []
    while end:
        footer = content[end - 1]
        length = footer & 0xBF
        start = end - 1 - length
        assert start >= 0, (end, footer)
        records.append(dict(file_offset=start, length=length, marked=bool(footer & 0x40),
                            footer=footer, data=content[start:end - 1]))
        end = start
    records.reverse()
    # Проверка обратимого разбиения, включая маркировку и пустые строки.
    assert b''.join(row['data'] + bytes((row['footer'],)) for row in records) == content
    return records


def decode_name(content):
    assert len(content) >= 2 and 0xC0 <= content[0] < 0xDC
    first = content[0]
    text = chr(first - 0x7F) if first < 0xDA else '.' if first == 0xDA else '='
    for offset, byte in enumerate(content[1:], 1):
        value = byte & 0x3F
        if value < 10:
            text += chr(value + 0x30)
        elif value == 10:
            pass
        elif value == 11:
            text += '_'
        elif value < 38:
            text += chr(value + 0x35)
        else:
            text += chr(value + 0x3B)
        if byte & 0x80:
            return text, offset + 1
    raise AssertionError(('Нет конца имени', content.hex()))


def decode_comment(content):
    assert content[:1] == b'/' and content[-1:] == b'\0'
    assert b'\0' not in content[1:-1]
    text = bytearray(b';')
    for byte in content[1:-1]:
        text.extend(b' ' * byte if byte < 0x20 else bytes((byte,)))
    return text.decode('cp866')


class SymbolWalker:
    """Обход границ операндов, без вычисления выражений и генерации машинного кода."""

    def __init__(self, content):
        self.content = content
        self.position = 0
        self.names = []
        self.comments = []
        self.literals = []

    def byte(self):
        assert self.position < len(self.content), ('За концом строки', self.content.hex())
        result = self.content[self.position]
        self.position += 1
        return result

    def symbol(self, first=None):
        start = self.position if first is None else self.position - 1
        if first is None:
            first = self.byte()
        if first < 0xC0:
            # Локальная числовая метка либо текущий адрес, дополнительных байтов имени нет.
            return
        assert first < 0xDC, ('Префикс имени', first, self.content.hex())
        name, length = decode_name(self.content[start:])
        self.position = start + length
        self.names.append(dict(name=name, byte_offset=start))

    def core(self, descriptor, depth=0):
        assert depth < 32
        while True:
            # Внутреннее описание выражения пропускается по тем же размерам, что AE55.
            if descriptor | 0x0F != 0xFF:
                kind = descriptor & 7
                if kind == 0:
                    self.core(self.byte(), depth + 1)
                elif kind < 3:
                    self.byte()
                elif kind == 3:
                    self.symbol()
                else:
                    self.byte()
                    self.byte()
            if descriptor & 8:
                return
            descriptor = self.byte()

    def operand(self, descriptor):
        # Индексный операнд имеет отдельные формы смещения по ADB5..ADF7.
        if descriptor & 0x30 == 0x30:
            kind = descriptor & 7
            if kind == 0:
                return
            if kind == 4:
                self.core(self.byte())
            else:
                self.core((kind & 3) | 8 | ((kind & 4) << 2))
        else:
            self.core(descriptor & 0x1F)

    def walk(self):
        if not self.content:
            return self.names
        if self.content[0] == 7:
            # Повтор строки содержит один готовый байт счётчика, AC7D..AC84.
            self.position = 2
            assert self.position <= len(self.content)
        while self.position < len(self.content):
            value = self.byte()
            if value == 0x2F:
                # После начала комментария имена операндов больше не читаются.
                self.comments.append(dict(byte_offset=self.position - 1,
                    text=decode_comment(self.content[self.position - 1:])))
                return self.names
            if value < 0x80:
                continue
            if value < 0xC0:
                self.operand(value)
            elif value < 0xDC:
                self.symbol(value)
            elif value == 0xDC:
                # Строковый литерал заканчивается нулём, его содержимое не является именами.
                start = self.position
                while self.byte():
                    pass
                text = decode_comment(b'/' + self.content[start:self.position])[1:]
                self.literals.append(dict(byte_offset=start - 1, text=text))
            else:
                # Однобайтовые константы и относительные значения текущего адреса.
                pass
        return self.names


class OperandReader(SymbolWalker):
    """Текст выражений по таблицам STORM, без вычисления и сборки команд."""

    def __init__(self, content, operators):
        super().__init__(content)
        self.operators = operators
        self.operands = []
        self.unresolved_local_tokens = []
        self.local_tokens = []

    def core_text(self, descriptor, first=True, depth=0):
        assert depth < 32
        result = ''
        while True:
            # Первая обычная компонента не требует плюса, последующие операции кодируются старшей тетрадой.
            if not first or descriptor & 0x10:
                operator = 15 + (descriptor & 7) if descriptor & 0xF0 == 0xF0 else descriptor >> 4
                result += self.operators[operator]
            if descriptor | 0x0F != 0xFF:
                kind = descriptor & 7
                if kind == 0:
                    result += '(' + self.core_text(self.byte(), depth=depth + 1) + ')'
                elif kind in (1, 2):
                    value = self.byte()
                    result += f'#{value:02X}' if kind == 1 else str(value)
                elif kind == 3:
                    start = self.position
                    token = self.byte()
                    if token >= 0xC0:
                        name, length = decode_name(self.content[start:])
                        self.position = start + length
                        result += name
                        self.names.append(dict(name=name, byte_offset=start))
                    else:
                        # B077..B089 выводит текущий адрес для нуля, иначе локальное имя =0..=7.
                        self.local_tokens.append(dict(byte_offset=start, token=token))
                        result += '$' if token == 0 else '=' + str((token - 1) & 7)
                else:
                    low, high = self.byte(), self.byte()
                    value = low | high << 8
                    if kind == 4:
                        result += '"' + bytes((high, low) if high else (low,)).decode('cp866') + '"'
                    elif kind == 5:
                        result += f'#{value:04X}'
                    elif kind == 6:
                        result += str(value)
                    else:
                        result += '%' + (f'{value:016b}' if high else f'{low:08b}')
            if descriptor & 8:
                return result
            descriptor = self.byte()
            first = False

    def operand(self, descriptor):
        start = self.position - 1
        if descriptor & 0x30 == 0x30:
            text = 'IY' if descriptor & 8 else 'IX'
            kind = descriptor & 7
            if kind:
                inner = self.byte() if kind == 4 else (kind & 3) | 8 | ((kind & 4) << 2)
                text += self.core_text(inner, first=False)
            text = '(' + text + ')'
        else:
            text = self.core_text(descriptor & 0x1F)
            if descriptor & 0x20:
                text = '(' + text + ')'
        self.operands.append(dict(byte_offset=start, end_exclusive=self.position, text=text))


def equ_expression(row, operators):
    """Текст определения EQU, включая короткие числа и отдельное имя без описателя."""
    _, length = decode_name(row['data'])
    assert row['data'][length] == 0x0A
    reader = OperandReader(row['data'], operators)
    reader.position = length + 1
    text = ''
    while reader.position < len(reader.content):
        token = reader.byte()
        if token == 0x2F:
            break
        if 0x80 <= token < 0xC0:
            reader.operand(token)
            text += reader.operands[-1]['text']
        elif 0xC0 <= token < 0xDC:
            name, size = decode_name(reader.content[reader.position - 1:])
            reader.position += size - 1
            text += name
        elif 0xDD <= token < 0xE7:
            text += str(token - 0xDD)
        elif token >= 0xE7:
            delta = token - 0xF3
            text += '$' + (f'{delta:+d}' if delta else '')
        else:
            raise AssertionError(('Неизвестный корневой токен EQU', token, row['data'].hex()))
    assert not reader.unresolved_local_tokens
    return text


def paired_expression_contexts(text_sources, sources, operators):
    """Наличие выражений в соответствующих строках обычных редакций, не равенство полных команд."""
    entries = []
    for source in sources:
        ordinary = next((row for row in text_sources
            if row['member'] == 'awk4.trd' and row['name'] == source['name']), None)
        if ordinary is None:
            continue
        lines = ordinary['content'].decode('cp866').split('\r')
        offset = {'CNVVOXTBC': 2, 'INVTAB3DC': 1}.get(source['name'], 0)
        assert all(line.startswith(';') for line in lines[:offset])
        records = source['records'][:len(lines) - offset]
        matched = []
        for row in records:
            reader = OperandReader(row['data'], operators)
            reader.walk()
            line = lines[row['line'] - 1 + offset]
            # Отсечение только настоящего комментария, точка с запятой внутри литерала сохраняется.
            code = re.split(r';(?=(?:[^"]*"[^"]*")*[^"]*$)', line, maxsplit=1)[0]
            for operand in reader.operands:
                text = operand['text']
                tokens = re.findall(r'"[^"]*"|#[0-9A-F]+|%[01]+|[A-Za-z_][A-Za-z_0-9]*|[0-9]+|.', text)
                pattern = r'\s*'.join(re.escape(token) for token in tokens)
                # Проверка границ имени и числа исключает совпадение короткого значения внутри длинного.
                if text[0].isalnum() or text[0] in '_#':
                    pattern = r'(?<![A-Za-z0-9_#])' + pattern
                if text[-1].isalnum() or text[-1] == '_':
                    pattern += r'(?![A-Za-z0-9_])'
                assert re.search(pattern, code), (source['name'], row['line'], text, line)
                matched.append(dict(structured_line=row['line'], ordinary_line=row['line'] + offset,
                    byte_offset=operand['byte_offset'], operand=text, original_ordinary_line=line))
        entries.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
            source_sha256=source['sha256'], ordinary_member=ordinary['member'], ordinary_slot=ordinary['slot'],
            ordinary_sha256=ordinary['sha256'], ordinary_initial_comment_lines=offset,
            records_compared=len(records), structured_records_not_compared=len(source['records']) - len(records),
            operand_contexts_matched=len(matched),
            matched_contexts_sha256=sha256(json.dumps(matched, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()))
    assert len(entries) == 16 and sum(row['operand_contexts_matched'] for row in entries) == 2382
    return dict(source_pairs=len(entries), operand_contexts_matched=2382, entries=entries,
        complete_instructions_compared=False, all_source_versions_equivalent=False,
        matching_is_case_sensitive=True, quoted_literals_preserved=True)


def format_evidence():
    blocks = storm_reference_blocks()
    # В загрузчике источник и назначение основного распаковываемого блока получают 6F19.
    assert blocks[0]['data'][5:13] == bytes.fromhex('11196F626BC3005B')
    base, body = 0x6F19, blocks[1]['data']
    snippets = ((0xA474, '2B5ECBB3AF57ED52C9'),
                (0xAC91, 'FEC03823FEDC301F5F0ACB77281A7BCD39B0'),
                (0xB039, 'FEC0383AFEDA380828043E3D18043EADD67F'),
                (0xB04E, '11353F0AA2FE0C3812FE263802C60683772CC80A031730EBAF3CC9'),
                (0xB069, 'FE0A380628F23E5F18EB C63018E7'),
                (0xAFE9, '0A03B72812FE20300936202CC83D20F918EE772C20EAC9'),
                (0xAC79, 'FE09303CFE072009362E2CCD6CAE201B'),
                (0xACC3, 'B7F2DBAC166CFEDC2835164EFEC0302FE620282B164A1827'),
                (0xACDB, 'FE2FCA2BB03822164AFE40381AFE6F3818FE753812164DFE77380C165E2808164EFE7C38021650'),
                (0xAD04, 'EBFE4920040A03C680D609C56F2600292901CDB509EB012004'),
                (0x7188, 'EBC30000EBC389AFEBC36CAEEBC337B0EBC3D3AFEBC3A6AFEBC3BFAEEBC3B6AF'),
                (0xADFB, '573004CB672825E6F0FEF020087AE607C60F8718030F0F0FD511A871'),
                (0xAE5F, 'FE0228098787C688EB26716FE9'),
                (0xB077, 'B7280C3DE607C630363D2CC8772CC936242CC9'),
                (0xADB5, '5FCB6B282D36282CC8CB63282536492CC83658CB5B2801342CC87BE6072823E60320050A03B7180DF608CB532807F6101803E61F37D51E0ACDFBADD1C8CB6BCA2FAD'),
                (0xAE27, '7AF60F3C28217AE607201636282CC81DC80A03D537CDFBADD1C836292CC81C1806D5CD5FAED1C8CB5AC00A0318A6'),
                (0xAE55, 'FE033804CA37B00303C9'))
    proofs = []
    for address, raw in snippets:
        expected = bytes.fromhex(raw)
        actual = body[address - base:address - base + len(expected)]
        assert actual == expected, (hex(address), actual.hex(), raw)
        proofs.append(dict(address=address, bytes_hex=expected.hex()))
    return dict(reference_member='awk2.trd', reference_slot=0, reference_name='STORM   B',
        restored_main_base=base, restored_main_sha256=blocks[1]['restored_sha256'],
        loader_literal_proof_hex=blocks[0]['data'][5:13].hex(), snippets=proofs,
        footer_length_mask=0xBF, footer_mark_mask=0x40,
        name_character_mask=0x3F, name_terminator_mask=0x80,
        name_definition_mask_in_second_byte=0x40,
        restored_program_executed=False, assembly_executed=False)


def load_storm_sources(archive_path=ARCHIVE):
    assert sha256(archive_path.read_bytes()).hexdigest() == ARCHIVE_SHA256
    sources = []
    with ZipFile(archive_path) as archive:
        for member in sorted(name for name in archive.namelist() if name.endswith('.trd')):
            disk = archive.read(member)
            for slot in range(128):
                header = disk[slot * 16:(slot + 1) * 16]
                if header[0] == 0:
                    break
                if header[8] != ord('C') or int.from_bytes(header[9:11], 'little') != 0xC00B:
                    continue
                start = (header[15] * 16 + header[14]) * 256
                size = int.from_bytes(header[11:13], 'little')
                assert size <= header[13] * 256
                content = disk[start:start + size]
                records = split_records(content)
                for number, row in enumerate(records, 1):
                    raw = row['data']
                    row['line'] = number
                    if raw[:1] == b'/':
                        row['comment'] = decode_comment(raw)
                    if len(raw) >= 2 and 0xC0 <= raw[0] < 0xDC and raw[1] & 0x40:
                        row['definition'], row['definition_bytes'] = decode_name(raw)
                sources.append(dict(member=member, slot=slot, name=header[:9].decode('cp866'),
                    disk_offset=start, bytes=size, sha256=sha256(content).hexdigest(),
                    records=records))
    assert len(sources) == 31
    return sources


def instruction_head(content, table):
    """Имя команды по выбору таблицы в AC91..AD28, без перевода её операндов."""
    position = 0
    if content[:1] == b'\x07':
        position = 2
    # Пропуск только помеченного определения, обычное имя может быть сокращённым переходом.
    if len(content) > position + 1 and 0xC0 <= content[position] < 0xDC and content[position + 1] & 0x40:
        _, length = decode_name(content[position:])
        position += length
    if position >= len(content) or content[position] == 0x2F:
        return None
    token = content[position]
    if token < 9 or token == 0x49:
        # Директивы повтора и особая расширенная форма требуют отдельного разбора.
        return None
    if token >= 0x80:
        index_token = 0x6C if token == 0xDC else 0x4E if token >= 0xC0 or not token & 0x20 else 0x4A
    elif token < 0x2F or 0x40 <= token < 0x6F:
        index_token = token
    elif token < 0x75:
        index_token = 0x4A
    elif token < 0x77:
        index_token = 0x4D
    elif token == 0x77:
        index_token = 0x5E
    elif token < 0x7C:
        index_token = 0x4E
    else:
        index_token = 0x50
    index = index_token - 9
    return dict(token_offset=position, original_token=token, table_index=index, mnemonic=table[index])


def temporary_module_references(text_sources, sources, table):
    """Контексты архивного переходника, без вывода о достижимости текущей игры."""
    names = ('ADHDP', 'M18', 'M20', 'JL1', 'JL2', 'EFF', 'HIPER', 'SETHJRET', 'TS_CON', 'SL_CON')
    hits = []
    # Поиск буквальных имён в текстах не подменяет разбор их команд.
    for source in text_sources:
        for number, raw in enumerate(source['content'].split(b'\r'), 1):
            text = raw.decode('cp866')
            for name in names:
                for match in re.finditer(r'(?<![A-Z0-9_])' + re.escape(name) + r'(?![A-Z0-9_])', text, re.I):
                    hits.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
                        line=number, identifier=name, kind='raw_text_occurrence', decoded_text=text,
                        text_column=match.start(), original_line_hex=raw.hex()))
    # Поиск в STORM отделяет операнды от комментариев и строковых литералов.
    for source in sources:
        for row in source['records']:
            walker = SymbolWalker(row['data'])
            symbols = walker.walk()
            mentions = [dict(identifier=item['name'].upper(), byte_offset=item['byte_offset'],
                kind='leading_definition' if item['byte_offset'] == 0 and 'definition' in row else 'operand_symbol')
                for item in symbols if item['name'].upper() in names]
            for kind, parts in (('comment', walker.comments), ('string_literal', walker.literals)):
                for part in parts:
                    for name in names:
                        for match in re.finditer(r'(?<![A-Z0-9_])' + re.escape(name) + r'(?![A-Z0-9_])', part['text'], re.I):
                            mentions.append(dict(identifier=name, kind=kind, byte_offset=part['byte_offset'],
                                decoded_text=part['text'], text_column=match.start()))
            for mention in mentions:
                hits.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
                    line=row['line'], file_offset=row['file_offset'], original_record_hex=row['data'].hex(),
                    instruction_head=instruction_head(row['data'], table), **mention))
    return dict(queried_names=list(names), ordinary_text_source_count=len(text_sources),
        structured_source_count=len(sources), source_count=len(text_sources) + len(sources), occurrences=hits,
        raw_text_contexts_classified_as_instructions=False,
        numeric_indirect_local_or_alias_references_excluded=False,
        current_game_caller_or_relocation_proved=False)


def main():
    proof = format_evidence()
    sources = load_storm_sources()
    # Чтение четырёхбайтовых названий команд из самого архивного STORM.
    program = storm_reference_blocks()[1]['data']
    table_bytes = program[0xB5CD - 0x6F19:0xB7B9 - 0x6F19]
    mnemonic_table = [table_bytes[offset:offset + 4].decode('ascii').strip()
                      for offset in range(0, len(table_bytes), 4)]
    assert len(mnemonic_table) == 123 and mnemonic_table[0x41] == 'LD'
    operator_bytes = program[0x71A8 - 0x6F19:0x71D6 - 0x6F19]
    operators = [operator_bytes[offset:offset + 2].decode('ascii').rstrip()
                 for offset in range(0, len(operator_bytes), 2)]
    # Проверка всех имён определений EQUS по отдельной обычной текстовой редакции.
    text_sources = load_sources()[0]
    plain = next(row for row in text_sources
                 if row['member'] == 'awk4.trd' and row['name'] == 'EQUS    C')
    expected = [match[1].decode('ascii') for line in plain['content'].split(b'\r')
                if (match := re.match(rb'^([A-Za-z_][A-Za-z_0-9]*)\s+EQU\b', line))]
    equs = next(row for row in sources if row['member'] == 'awk2.trd' and row['name'] == 'EQUS    C')
    actual = [row['definition'] for row in equs['records'] if 'definition' in row]
    assert actual == expected, (actual, expected)
    assert all(instruction_head(row['data'], mnemonic_table)['mnemonic'] == 'EQU'
               for row in equs['records'] if 'definition' in row)
    # Проверка текста всех выражений по отдельному обычному EQUS, без вычисления их значений.
    expected_expressions = {match[1]: match[2].split(';', 1)[0].strip()
        for line in plain['content'].decode('cp866').split('\r')
        if (match := re.match(r'^(\w+)\s+EQU\s+(.+)', line))}
    actual_expressions = {row['definition']: equ_expression(row, operators)
                          for row in equs['records'] if 'definition' in row}
    assert actual_expressions == expected_expressions and len(actual_expressions) == 82
    # Сверка текущего адреса внутри перехода, определения, адреса записи и операции выравнивания.
    current_address_cases = (('XR1     C', 24, '$+23'), ('LAND    C', 134, '$-HSCR'),
        ('VSPRITE C', 530, '($-2)'), ('S3D     C', 32, '$['),
        ('XR2     C', 42, '$`+#C0'), ('BLOK1   C', 140, '($-3)'))
    for filename, number, expected_operand in current_address_cases:
        packed = next(row for row in sources if row['name'] == filename)
        ordinary = next(row for row in text_sources if row['member'] == 'awk4.trd' and row['name'] == filename)
        reader = OperandReader(packed['records'][number - 1]['data'], operators)
        reader.walk()
        assert expected_operand in [row['text'] for row in reader.operands]
        assert expected_operand in ordinary['content'].decode('cp866').split('\r')[number - 1]
        assert reader.local_tokens and all(row['token'] == 0 for row in reader.local_tokens)
    # Независимая обычная редакция LAND подтверждает две сокращённые команды записи PLAYER.
    land = next(row for row in sources if row['member'] == 'awk2.trd' and row['name'] == 'LAND    C')
    plain_land = next(row for row in text_sources if row['member'] == 'awk4.trd' and row['name'] == 'LAND    C')
    land_lines = plain_land['content'].decode('cp866').split('\r')
    for number, expected_line in ((179, 'LD (PLAYER+Type),A'), (180, 'LD (PLAYER+Mode),A')):
        assert land_lines[number - 1].strip() == expected_line
        assert instruction_head(land['records'][number - 1]['data'], mnemonic_table)['mnemonic'] == 'LD'
    # Независимая проверка полного порядка символов EQUS по обычному тексту, а не только определений.
    plain_symbols = []
    for line in plain['content'].decode('cp866').split('\r'):
        code = re.sub(r'#[0-9a-fA-F]+', '', line.split(';', 1)[0])
        plain_symbols.extend(name for name in re.findall(r'[A-Za-z_][A-Za-z_0-9]*', code)
                             if name.upper() != 'EQU')
    decoded_symbols = [name['name'] for row in equs['records'] for name in SymbolWalker(row['data']).walk()]
    assert decoded_symbols == plain_symbols and len(decoded_symbols) == 122
    # Проверка ложных имён в числах, строках, комментариях и повторе, настоящий M1 закодирован CC81.
    boundary_cases = (('CC81', ['M1']), ('8DCC81', []), ('DCCC8100', []),
        ('2FCC8100', []), ('B1CC', []), ('B3CC81', ['M1']),
        ('8889CC', []), ('8D2FDCCC81', ['M1']), ('07CC16', []))
    for encoded, names in boundary_cases:
        assert [row['name'] for row in SymbolWalker(bytes.fromhex(encoded)).walk()] == names, encoded
    hits, operand_hits, literal_hits, entries = [], [], [], []
    walked_records, walked_symbols, walked_literals, decoded_operands, local_operand_tokens = 0, 0, 0, 0, 0
    current_address_tokens = 0
    for source in sources:
        for row in source['records']:
            walker = SymbolWalker(row['data'])
            names = walker.walk()
            # Независимое чтение текста должно сохранить прежние границы имён, строк и комментариев.
            operand_reader = OperandReader(row['data'], operators)
            assert operand_reader.walk() == names
            assert operand_reader.comments == walker.comments and operand_reader.literals == walker.literals
            decoded_operands += len(operand_reader.operands)
            local_operand_tokens += len(operand_reader.unresolved_local_tokens)
            current_address_tokens += sum(row['token'] == 0 for row in operand_reader.local_tokens)
            walked_records += 1
            walked_symbols += len(names)
            walked_literals += len(walker.literals)
            for mention in names:
                if mention['name'].upper() in QUERY_NAMES:
                    operand_hits.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
                        line=row['line'], file_offset=row['file_offset'], byte_offset=mention['byte_offset'],
                        identifier=mention['name'].upper(), actual_name=mention['name'],
                        kind='leading_definition' if mention['byte_offset'] == 0 and 'definition' in row else 'operand_symbol',
                        instruction_head=instruction_head(row['data'], mnemonic_table),
                        decoded_expression_operands=operand_reader.operands,
                        original_record_hex=row['data'].hex()))
            for comment in walker.comments:
                for name in QUERY_NAMES:
                    if re.search(r'(?<![A-Z0-9_])' + name + r'(?![A-Z0-9_])', comment['text'], re.I):
                        operand_hits.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
                            line=row['line'], file_offset=row['file_offset'], byte_offset=comment['byte_offset'],
                            identifier=name, kind='comment', decoded_text=comment['text'],
                            original_record_hex=row['data'].hex()))
            # Поиск имён в строках отдельно от исполняемых символических операндов.
            for literal in walker.literals:
                for name in QUERY_NAMES:
                    for match in re.finditer(r'(?<![A-Z0-9_])' + re.escape(name) + r'(?![A-Z0-9_])', literal['text'], re.I):
                        literal_hits.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
                            line=row['line'], file_offset=row['file_offset'], byte_offset=literal['byte_offset'],
                            identifier=name, kind='string_literal', decoded_text=literal['text'],
                            text_column=match.start(), original_record_hex=row['data'].hex()))
            for name in QUERY_NAMES:
                kind = None
                if row.get('definition', '').upper() == name:
                    kind = 'leading_definition'
                elif re.search(r'(?<![A-Z0-9_])' + name + r'(?![A-Z0-9_])', row.get('comment', ''), re.I):
                    kind = 'whole_line_comment'
                if kind:
                    hits.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
                        line=row['line'], file_offset=row['file_offset'], identifier=name, kind=kind,
                        original_record_hex=row['data'].hex(),
                        decoded_text=row.get('comment', row.get('definition'))))
        entries.append(dict(member=source['member'], slot=source['slot'], name=source['name'],
            disk_offset=source['disk_offset'], bytes=source['bytes'], sha256=source['sha256'],
            records=len(source['records']), marked_records=sum(row['marked'] for row in source['records']),
            leading_definitions=sum('definition' in row for row in source['records']),
            whole_line_comments=sum('comment' in row for row in source['records']),
            byte_exact_record_roundtrip=True))
    # Поиск в обычных текстах сохраняет контекст, но не объявляет каждое совпадение обращением к памяти.
    text_hits = []
    for source in text_sources:
        for number, raw in enumerate(source['content'].split(b'\r'), 1):
            line = raw.decode('cp866')
            for name in QUERY_NAMES:
                for match in re.finditer(r'(?<![A-Z0-9_])' + re.escape(name) + r'(?![A-Z0-9_])', line, re.I):
                    text_hits.append(dict(member=source['member'], slot=source['slot'], source=source['name'],
                        line=number, identifier=name, kind='raw_text_occurrence', text_column=match.start(),
                        decoded_text=line, original_line_hex=raw.hex()))
    # Проверка непересекающихся физических каталогов двух способов чтения.
    text_keys = {(row['member'], row['slot']) for row in text_sources}
    structured_keys = {(row['member'], row['slot']) for row in sources}
    assert len(text_keys) == 129 and len(structured_keys) == 31 and not text_keys & structured_keys
    combined_hits = text_hits + operand_hits + literal_hits
    combined = dict(source_count=len(text_keys | structured_keys), ordinary_text_source_count=len(text_keys),
        structured_source_count=len(structured_keys), occurrences=combined_hits,
        text_source_hashes=[dict(member=row['member'], slot=row['slot'], name=row['name'], sha256=row['sha256'])
                            for row in text_sources],
        counts_by_identifier={name: {kind: sum(row['identifier'] == name and row['kind'] == kind
            for row in combined_hits) for kind in ('raw_text_occurrence', 'leading_definition',
                'operand_symbol', 'comment', 'string_literal')} for name in QUERY_NAMES},
        raw_text_contexts_classified_as_instructions=False,
        numeric_indirect_or_alias_references_excluded=False,
        archived_names_prove_current_game_semantics=False)
    report = dict(passed=True, archive_sha256=ARCHIVE_SHA256, structured_sources=len(sources),
        source_bytes=sum(row['bytes'] for row in sources), records=sum(row['records'] for row in entries),
        format_evidence=proof, entries=entries, paired_EQUS_definition_names=actual,
        instruction_name_table=dict(address=0xB5CD, bytes=len(table_bytes), sha256=sha256(table_bytes).hexdigest(),
            names=mnemonic_table, all_operand_text_rendered=False, paired_EQUS_EQU_heads_checked=len(actual),
            paired_LAND_LD_heads_checked=2, repeat_and_extended_heads_fully_decoded=False),
        expression_operand_decoding=dict(operator_table_address=0x71A8, operator_table_hex=operator_bytes.hex(),
            operator_texts=operators, decoded_operands=decoded_operands, records_checked=walked_records,
            unresolved_local_token_occurrences=local_operand_tokens,
            current_address_token_occurrences=current_address_tokens,
            paired_current_address_contexts=[dict(source=name, line=number, operand=operand)
                                             for name, number, operand in current_address_cases],
            paired_EQUS_expression_count=len(actual_expressions), paired_EQUS_expressions=actual_expressions,
            all_expression_texts_proved=False, expression_values_evaluated=False,
            full_instructions_rendered=False),
        paired_expression_contexts=paired_expression_contexts(text_sources, sources, operators),
        paired_EQUS_name_count=len(actual), queried_names=list(QUERY_NAMES),
        definition_and_whole_comment_hits=hits,
        decoded_symbol_and_comment_occurrences=operand_hits,
        decoded_string_literal_occurrences=literal_hits,
        combined_named_reference_search=combined,
        temporary_module_named_reference_search=temporary_module_references(text_sources, sources, mnemonic_table),
        operand_boundary_records_checked=walked_records, symbol_occurrences_decoded=walked_symbols,
        string_literals_decoded=walked_literals,
        paired_EQUS_full_symbol_sequence=decoded_symbols, paired_EQUS_full_symbol_count=len(decoded_symbols),
        symbol_boundary_positive_and_negative_cases=len(boundary_cases),
        operand_symbol_boundary_walk_complete=True,
        instruction_and_inline_expression_decoding_complete=False,
        full_arithmetic_expression_text_not_rendered=True,
        numeric_or_differently_named_references_excluded=False,
        current_game_field_semantics_proved=False, native_execution=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ArchivedStormSourceStructure.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f"31 sources, {report['source_bytes']} bytes, {report['records']} records, "
          f"{len(actual)} EQUS definition names matched")


if __name__ == '__main__':
    main()
