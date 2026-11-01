"""Именованные физические записи Antichrist, читатель источников не запускает ассемблер."""
from pathlib import PurePosixPath
import re
from MusicCompositionLayout import ORIGIN, EXTRA_STRUCTURES, layout, word

STRUCTURES = dict(EXTRA_STRUCTURES)
STRUCTURES.update({
    'FMusicLoopHeader': (('LoopPosition', 1, 'db', 'позиция возврата после достижения длины'), ('Length', 1, 'db', 'число физических шагов')),
    'FMusicSampleStep': (('ShiftControl', 1, 'db', 'управление уровнем и шумовым либо огибающим вкладом'),
                         ('LevelModes', 1, 'db', 'базовый уровень, накопление и вклад в микшер'),
                         ('ToneDelta', 2, 'dw', 'слово тональной поправки'))})


def descriptions(data):
    result = layout(data)
    names = dict(header=('Header', 'AntichristHeader'), sample_offsets=('SampleOffsets', 'AntichristSampleRefs'),
                 ornament_offsets=('OrnamentOffsets', 'AntichristOrnamentRefs'), positions=('Positions', 'AntichristPositions'),
                 pattern_offsets=('PatternOffsets', 'AntichristPatternRefs'))
    for item in result:
        kind = item['kind']
        if kind in names:
            filename, module = names[kind]
        elif kind == 'pattern':
            filename = 'Patterns/' + item['name']
            module = 'Antichrist' + item['name']
        else:
            filename = ('Samples/Sample' if kind == 'sample' else 'Ornaments/Ornament') + format(item['index'], '02X')
            module = 'Antichrist' + PurePosixPath(filename).name
        item.update(path='Source/Music/Composition/' + filename + '.asm', module=module)
    return result


def records(data, item):
    """Физические записи в исходном порядке, без раскрытия нулевых относительных адресов."""
    start, kind = item['offset'], item['kind']
    result = []
    def record(label, structure, address):
        result.append((label, structure, address))
    if kind == 'header':
        record('Entry', 'FMusicModuleHeader', 0)
    elif kind in ('sample_offsets', 'ornament_offsets'):
        count = 32 if kind == 'sample_offsets' else 16
        prefix = 'Sample' if kind == 'sample_offsets' else 'Ornament'
        for index in range(count):
            record(prefix + format(index, '02X'), 'FMusicRelativePointer', start + 2 * index)
    elif kind == 'positions':
        for index in range(item['length']):
            record('End' if index + 1 == item['length'] else 'Position' + format(index, '02X'), 'FMusicPositionByte', start + index)
    elif kind == 'pattern_offsets':
        for index in range(19):
            record('Pattern' + format(index, '02X'), 'FMusicPatternPointers', start + 6 * index)
    elif kind in ('sample', 'ornament'):
        record('Header', 'FMusicLoopHeader', start)
        structure = 'FMusicSampleStep' if kind == 'sample' else 'FMusicOrnamentStep'
        for index in range(item['step_count']):
            record('Step' + format(index, '02X'), structure, start + 2 + item['step_size'] * index)
    return result


def render(data, item):
    module, path, start, length = (item[key] for key in ('module', 'path', 'offset', 'length'))
    link = '../' * (len(PurePosixPath(path).parts) - 1) + 'Docs/MusicComposition.md'
    lines = ['                module ' + module, '                ; Документация [исходная композиция](' + link + ')',
             '                assert $ == #' + format(ORIGIN + start, '04X')]
    symbols = {}
    if item['kind'] == 'pattern':
        lines += ['                ; Общий физический поток, ссылки ' + ', '.join(str(ref['pattern']) + ref['channel'] for ref in item['references'])]
        for entry in item['records']:
            address, count, label = entry['offset'], entry['length'], entry['label']
            line = ((label + ':').ljust(16) if label else ' ' * 16) + 'DB ' + ', '.join('#' + format(value, '02X') for value in data[address:address + count])
            if label:
                symbols[module + '.' + label] = ORIGIN + address
            if len(line) < 80:
                lines.append(line.ljust(80) + '; ' + entry['note'])
            else:
                lines += ['                ; ' + entry['note'], line]
    else:
        for label, structure, address in records(data, item):
            lines += ['                ; -----------------------------------------',
                      '                ; исходная физическая запись ' + label,
                      (label + ':').ljust(16) + structure + ' {']
            symbols[module + '.' + label] = ORIGIN + address
            offset = address
            fields = STRUCTURES[structure]
            for index, (field, width, directive, note) in enumerate(fields):
                symbols[module + '.' + label + '.' + field] = ORIGIN + offset
                blob = data[offset:offset + width]
                offset += width
                argument = ('{ "' + blob.decode('ascii') + '" }' if directive == 'text'
                            else '#' + format(int.from_bytes(blob, 'little'), '02X' if width == 1 else '04X'))
                line = ' ' * 20 + argument + (',' if index + 1 < len(fields) else '')
                if len(line) < 80:
                    lines.append(line.ljust(80) + '; ' + field + ', ' + note)
                else:
                    lines += ['                ; ' + field + ', ' + note, line]
            lines.append('                }')
    lines += ['                assert $ == #' + format(ORIGIN + start + length, '04X'), '                endmodule']
    return '\n'.join(lines) + '\n', symbols


def parse(text, data, item):
    """Строгое чтение фактических директив, лишние байты и перестановка записей отвергаются."""
    module, start, length = item['module'], item['offset'], item['length']
    lines = [line.partition(';')[0].strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    assert lines.pop(0) == 'module ' + module
    assert lines.pop(0) == 'assert $ == #' + format(ORIGIN + start, '04X')
    raw, symbols = bytearray(), {}
    if item['kind'] == 'pattern':
        for entry in item['records']:
            code = lines.pop(0)
            label = entry['label']
            if label:
                prefix = (label + ':').ljust(16)
                assert code.startswith(prefix)
                code = code[len(prefix):]
                symbols[module + '.' + label] = ORIGIN + start + len(raw)
            assert code.startswith('DB ')
            values = code[3:].split(', ')
            assert len(values) == entry['length'] and all(re.fullmatch(r'#[0-9A-F]{2}', value) for value in values)
            raw.extend(int(value[1:], 16) for value in values)
    else:
        for label, structure, address in records(data, item):
            assert lines.pop(0) == (label + ':').ljust(16) + structure + ' {'
            assert start + len(raw) == address
            symbols[module + '.' + label] = ORIGIN + address
            fields = STRUCTURES[structure]
            for index, (field, width, directive, _) in enumerate(fields):
                value = lines.pop(0)
                comma = ',' if index + 1 < len(fields) else ''
                symbols[module + '.' + label + '.' + field] = ORIGIN + start + len(raw)
                if directive == 'text':
                    match = re.fullmatch(r'\{ "([^"\r\n]*)" \}' + comma, value)
                    assert match is not None
                    blob = match[1].encode('ascii')
                    assert len(blob) == width
                else:
                    assert re.fullmatch(r'#[0-9A-F]{' + str(2 * width) + '}' + comma, value)
                    blob = int(value[1:-1] if comma else value[1:], 16).to_bytes(width, 'little')
                raw.extend(blob)
            assert lines.pop(0) == '}'
    assert len(raw) == length
    assert lines == ['assert $ == #' + format(ORIGIN + start + length, '04X'), 'endmodule']
    return bytes(raw), symbols


def update_end_comments(root, data):
    """Только уточнение пояснений границ B/C, директивы и значения не переписываются."""
    count = 0
    for item in descriptions(data):
        if item['kind'] != 'pattern':
            continue
        p = root/item['path']
        before = p.read_text('utf-8')
        old = 'исходный нулевой байт границы потока, проверяется вызывающим путём A'
        assert before.count(old) == 1
        after = before.replace(old, item['records'][-1]['note'])
        assert parse(before, data, item) == parse(after, data, item)
        p.write_text(after, encoding='utf-8')
        count += 1
    assert count == 41
