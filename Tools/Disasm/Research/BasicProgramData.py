"""Две строки исходного BASIC и доказанная ими адресная привязка машинного входа."""
import ast
import re

from CheckIntro import ROOT

ENTRY, PROGRAM_BASE = 23873, 23867
DETACHED_LINE_START, DETACHED_LINE_END = 0x007B, 0x0084
DETACHED_LINE_PATH = 'Source/Basic/Data/DetachedLineSuffix.asm'
DETACHED_NUMBER_START, DETACHED_NUMBER_END = 0x0084, 0x0090
DETACHED_NUMBER_PATH = 'Source/Basic/Data/DetachedSectorNumber.asm'
TYPES = {'FBasicLineHeader': (1, 1, 2), 'FBasicSmallInteger': (1, 1, 1, 1, 1)}
PARTS = (
    (0, 6, PROGRAM_BASE, 'Prefix', '''                module BasicProgramPrefix
                ; Документация [исходная BASIC-программа](../../../Docs/BasicProgram.md)
                assert $ == #5D3B
Line10:         FBasicLineHeader { #00, #0A, #0061 }
Remark:         db #20, #EA                                                     ; пробел и REM перед исходными 24 байтами Z80
                assert $ == #5D41
                endmodule
'''),
    (30, 101, PROGRAM_BASE + 30, 'Line10Tail', '''                module BasicProgramLine10Tail
                ; Документация [исходная BASIC-программа](../../../Docs/BasicProgram.md)
                assert $ == #5D59
Padding:        ds 70, #20                                                      ; семьдесят исходных пробелов внутри REM, байты не удаляются
EndLine:        db #0D                                                          ; завершение первой строки BASIC
                assert $ == #5DA0
                endmodule
'''),
    (101, 119, PROGRAM_BASE + 101, 'EntryLine', '''                module BasicProgramEntryLine
                ; Документация [исходная BASIC-программа](../../../Docs/BasicProgram.md)
                assert $ == #5DA0
Line20:         FBasicLineHeader { #00, #14, #000E }
Statement:      db #F9, #C0, "23873", #0E                                       ; RANDOMIZE USR, печатное число и маркер сохранённого числового значения
UsrNumber:      FBasicSmallInteger { #00, #00, #41, #5D, #00 }
EndLine:        db #0D                                                          ; завершение второй строки и логической программы
                assert $ == #5DB2
                endmodule
'''),
)


def parse(text, origin):
    raw, labels = bytearray(), {}
    code = '\n'.join(line.partition(';')[0] for line in text.splitlines())
    pattern = r'(\w+):\s+(?:(FBasic\w+)\s*\{([^}]+)\}|(db|ds)\s+([^\n]+))'
    for match in re.finditer(pattern, code):
        labels[match[1]] = origin + len(raw)
        if match[2]:
            values = [value.strip() for value in match[3].split(',')]
            sizes = TYPES[match[2]]
            assert len(values) == len(sizes)
            for value, size in zip(values, sizes):
                assert re.fullmatch(r'#[0-9A-Fa-f]+', value)
                raw.extend(int(value[1:], 16).to_bytes(size, 'little'))
        elif match[4] == 'db':
            for token in re.findall(r'"[^"\n]*"|#[0-9A-Fa-f]+', match[5]):
                raw.extend(ast.literal_eval(token).encode('ascii') if token.startswith('"') else bytes((int(token[1:], 16),)))
        else:
            count, value = (value.strip() for value in match[5].split(','))
            raw.extend(bytes((int(value[1:], 16),)) * int(count))
    return bytes(raw), labels


def original_program():
    data = (ROOT / 'Tools/Disasm/Extracted/Active/03_AWAKEN.B.bin').read_bytes()
    assert len(data) == 119
    position, lines = 0, []
    while position < len(data):
        number = int.from_bytes(data[position:position + 2], 'big')
        length = int.from_bytes(data[position + 2:position + 4], 'little')
        body = data[position + 4:position + 4 + length]
        assert len(body) == length and body[-1] == 13
        lines.append((number, position, length, body))
        position += 4 + length
    assert [(number, offset, length) for number, offset, length, _ in lines] == [(10, 0, 97), (20, 101, 14)]
    assert lines[0][3][:2] == b' \xEA' and lines[0][3][26:] == b' ' * 70 + b'\r'
    assert lines[1][3] == b'\xF9\xC023873\x0E\x00\x00\x41\x5D\x00\r'
    assert int(data[107:112]) == int.from_bytes(data[115:117], 'little') == ENTRY
    for start, end, origin, _, source in PARTS:
        assert parse(source, origin)[0] == data[start:end]
    return data, lines


def detached_sector_number(allocation):
    raw = allocation[DETACHED_NUMBER_START:DETACHED_NUMBER_END]
    assert raw == b'15616\x0E\x00\x00\x00\x3D\x00\r'
    assert int(raw[:5]) == int.from_bytes(raw[8:10], 'little') == 0x3D00
    return raw


def detached_line_suffix(allocation):
    raw = allocation[DETACHED_LINE_START:DETACHED_LINE_END]
    assert raw == b'uck"\xCA20\r\x80'
    return raw


def line_token_from_rom(basic):
    # Таблица ROM 1 кодирует последний символ каждого токена установленным битом 7.
    token_start = 0x96
    tokens = []
    for offset in range(token_start, 0x1E4):
        if basic[offset] & 128:
            tokens.append(basic[token_start:offset] + bytes((basic[offset] & 127,)))
            token_start = offset + 1
    assert tokens[0] == b'RND' and tokens[0xC0 - 0xA5] == b'USR'
    assert tokens[0xCA - 0xA5] == b'LINE'
    return 0xCA
