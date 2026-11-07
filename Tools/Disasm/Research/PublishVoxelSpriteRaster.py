"""Публикация развёрнутых групп VOXAL из проверенного физического диапазона."""
from collections import Counter
from pathlib import Path
import contextlib
import io
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from InspectZ80 import decoder
from VerifySources import main as verify

START, END, TAIL = 0xEE7A, 0xF931, 0xF8FA
ORIGIN = 0xEC00
PATH = 'Source/Voxel/RasterizeSprite.asm'
DESCRIPTION = 'Развёрнутый проход по парам кодов спрайта с маскированием прозрачных половин и шагом по строкам'


def label_map():
    labels = {START: 'Entry', TAIL: 'NextRow', 0xF904: 'SetRowHalf',
              0xF913: 'StepSource', 0xF92D: 'CarrySource',
              0xF8DA: 'RightOnly31', 0xF8D6: 'LeftOnly31', 0xF8CE: 'SkipPair31', 0xF8E1: 'MergePair31'}
    for group in range(1, 32):
        labels[START + 84 * group] = f'Pair{group:02}'
    for group in range(31):
        base = START + 84 * group
        for offset, role in ((39, 'SkipPair'), (47, 'LeftOnly'), (51, 'RightOnly'),
                             (57, 'MergePair'), (82, 'Advance')):
            labels[base + offset] = f'{role}{group:02}'
    return labels


def describe_branch(address):
    if address >= TAIL:
        return {
            0xF901: 'переход, если шаг назначения #80 не вызвал перенос в старший байт',
            0xF90D: 'переход, если дробный шаг Y не дал перенос в целую часть',
            0xF911: 'переход, если добавление шага строки ресурса перенеслось в старший байт',
            0xF91D: 'переход, если остались видимые строки спрайта',
        }[address]
    offset = (address - START) % 84
    return {
        12: 'переход, если старший код прозрачен, проверить младший отдельно',
        15: 'переход, если младший код прозрачен, сохранить младшую половину назначения',
        16: 'переход, если младший код прозрачен, сохранить младшую половину назначения',
        52: 'переход, если оба кода прозрачны, пропустить запись',
        54: 'переход, если оба кода прозрачны, пропустить запись',
    }[offset]


def render(decoded, labels):
    lines = [
        '                module Voxel', '                module RasterizeSprite',
        '                ; Документация [развёрнутый проход](../../Docs/VoxelSpriteClipBounds.md)',
        '                ; -----------------------------------------',
        '                ; ' + DESCRIPTION,
        '                ; In:',
        '                ;   контекст формируется ClipSprite, в SP временно находится шаг ресурса по X',
        '                ;   IXH хранит число видимых строк, IXL младший байт целого шага по Y, IYL младший адрес назначения',
        '                ;   доступны таблицы преобразования #C0..#C3 банка 3, поток ресурса и буфер #8000..#8BFF',
        '                ;   изменяемые операнды должны быть установлены для текущего спрайта, IRQ не вмешиваются',
        '                ; Out:',
        '                ;   для каждой непустой пары записаны четыре байта буфера, прозрачные пары не пишутся',
        '                ;   по завершении всех строк маска первого столбца возвращена к #F0, SP восстановлен до RET',
        '                ;   значения регистров после вызова ClipSprite приведены в документации',
        '                ; Corrupt:',
        "                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, изменяемая маска и буфер",
        '                ; Note:',
        '                ;   каждая группа занимает 84 байта, у последней отдельная проверка маски правого края',
        '                ;   при нечётной левой границе вход смещается на 3, а непосредственная маска временно обнуляется',
        '                ; -----------------------------------------',
    ]
    for item in decoded:
        address, operation = item.address, item.operation.replace(',', ', ')
        label = labels.get(address)
        if address < TAIL and (address - START) % 84 == 0:
            group = (address - START) // 84
            lines.extend(['                ; -----------------------------------------',
                          f'                ; Пара {group:02}, считывание двух кодов и выбор способа записи четырёх подстрок.'])
        if address == TAIL:
            lines.append('                ; Продвижение адреса назначения и источника после конца строки.')
        if address == 0xF920:
            lines.append('                ; Восстановление маски первого столбца и настоящего CPU-стека.')
        if label and label.startswith('MergePair'):
            lines.append('                ; Сохранение прозрачной половины назначения по маске E.')
        if label and label.startswith('SkipPair'):
            lines.append('                ; Обе половины прозрачны, обновить только позицию внутри строки.')
        if label and label.startswith('RightOnly'):
            lines.append('                ; Подготовка правого кода при прозрачной левой половине.')
        if label and label.startswith('LeftOnly'):
            lines.append('                ; Подготовка маски при прозрачной правой половине.')
        if operation.startswith(('JP ', 'JR ')):
            target = int(operation.rsplit('#', 1)[1], 16)
            if target in labels:
                operation = operation.rsplit('#', 1)[0] + '@Voxel.RasterizeSprite.' + labels[target]
            elif target == 0xEE73:
                operation = operation.rsplit('#', 1)[0] + '@Voxel.ClipSprite.NextRow'
            else:
                raise AssertionError((address, target))
        line = (f'{label}:'.ljust(16) if label else ' ' * 16) + operation
        if operation.startswith(('JP NZ,', 'JR Z,', 'JR C,', 'JR NC,')):
            line = line.ljust(80) + '; ' + describe_branch(address)
        lines.append(line)
        if operation.startswith(('JP ', 'JR ', 'RET')):
            lines.append('')
        if address < TAIL and (address - START + len(item.bytes)) % 84 == 0:
            lines.append('                ; -----------------------------------------')
    lines.extend(['                endmodule', '                endmodule', ''])
    return '\n'.join(lines)


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    pending = {}

    def read(stem):
        return json.loads((reports / (stem + '.json')).read_text(encoding='utf-8'))

    def save(stem, value):
        pending[reports / (stem + '.json')] = json.dumps(value, ensure_ascii=False, indent=2) + '\n'

    proof = read('VoxelSpriteSampleRasterVerification')
    assert proof['passed'] and proof['all_32_raster_entries'] and proof['exact_code_write_order']
    raw_path = ROOT / 'Source/Resources/21_VOXAL/Unclassified000.bin'
    image = (ROOT / 'Tools/Disasm/Extracted/Active/21_VOXAL.C.bin').read_bytes()
    raw = image[START - ORIGIN:END - ORIGIN]
    assert raw_path.read_bytes() == raw and len(raw) == 2743
    memory = [0] * 65536
    memory[ORIGIN:ORIGIN + len(image)] = image
    decoded = decoder(memory).disassemble(START, END, 'h')
    assert bytes(byte for item in decoded for byte in item.bytes) == raw
    assert all(not item.operation.startswith('DEFB') for item in decoded)
    labels = label_map()
    addresses = {item.address for item in decoded}
    assert labels.keys() <= addresses
    pending[ROOT / PATH] = render(decoded, labels)

    flow = read('ControlFlow')
    voxel = next(region for region in flow if region['name'] == 'Voxel')
    assert not addresses.intersection(item['address'] for item in voxel['instructions'])
    voxel['instructions'].extend(dict(address=i.address, operation=i.operation, hex=i.bytes.hex(),
                                      slot=21, offset=i.address - ORIGIN) for i in decoded)
    voxel['instructions'].sort(key=lambda i: (i['address'], i['slot'], i['offset']))
    voxel['instruction_count'] += len(decoded)
    voxel['code_bytes'] += len(raw)
    voxel['classified_fraction'] = voxel['code_bytes'] / voxel['total_bytes']
    voxel['branches'] = sorted(set(voxel['branches']) | {
        int(i.operation.rsplit('#', 1)[1], 16) for i in decoded if i.operation.startswith(('JP ', 'JR '))
    })
    save('ControlFlow', flow)
    functions = read('Functions')
    clip = next(item for item in functions if item['region'] == 'Voxel' and item['address'] == 0xEC7F)
    functions.insert(functions.index(clip) + 1, dict(region='Voxel', name='RasterizeSprite', address=START,
        slot=21, offset=START - ORIGIN, end_offset=END - ORIGIN, path=PATH,
        description=DESCRIPTION, semantic_status='described'))
    save('Functions', functions)
    ranges = read('SourceMap')
    item = next(item for item in ranges if ROOT / item['path'] == raw_path)
    assert (item['slot'], item['offset'], item['length'], item['kind']) == (21, START - ORIGIN, len(raw), 'unclassified')
    item.update(kind='code', path=PATH, origin=START)
    save('SourceMap', ranges)
    inventory = read('Inventory')
    inventory['instructions'] += len(decoded)
    inventory['fragments'] += 1
    inventory['described'] += 1
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in ranges))
    sizes = Counter()
    for item in ranges:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    save('Inventory', inventory)
    symbols = read('Symbols')
    added = {'Voxel.RasterizeSprite.' + label: address for address, label in labels.items()}
    added['Voxel.ClipSprite.NextRow'] = 0xEE73
    assert not added.keys() & symbols.keys()
    symbols.update(added)
    save('Symbols', symbols)

    def replace(relative, old, new):
        path = ROOT / relative
        text = pending.get(path, path.read_text(encoding='utf-8'))
        assert text.count(old) == 1, (relative, old)
        pending[path] = text.replace(old, new)

    replace('Source/Voxel/ClipSprite.asm', "                EX AF, AF'\n                LD H, B\n                LD L, #00\n                JP #0000",
            "NextRow:        EX AF, AF'\n                LD H, B\n                LD L, #00\n                JP #0000")
    replace('Source/Files/21_VOXAL.inc',
            '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
            '                incbin "../Resources/21_VOXAL/Unclassified000.bin"',
            '                disp #EE7A\n                include "../Voxel/RasterizeSprite.asm"\n                ent')
    replace('Docs/Functions.md', '| #F931 | [Voxel.Multiply7BitWord]',
            '| #EE7A | [Voxel.RasterizeSprite](../' + PATH + ') | ' + DESCRIPTION + ' |\n| #F931 | [Voxel.Multiply7BitWord]')
    path = ROOT / 'Docs/Functions.md'
    table = pending[path]
    match = re.search(r'\| Voxel \| (\d+) \| (\d+) \|', table)
    assert match
    pending[path] = table.replace(match[0], f'| Voxel | {int(match[1]) + 1} | {int(match[2]) + 1} |', 1)
    replace('Docs/FunctionDetails/Voxel.md', '## Multiply7BitWord',
            '## RasterizeSprite\n\n[Voxel.RasterizeSprite](../../' + PATH + ')\n\n' + DESCRIPTION
            + '.\n\n[Схема групп и проверки](../VoxelSpriteClipBounds.md).\n\n## Multiply7BitWord')
    replace('Tools/Disasm/Research/Analyze.py', '"ThreeD": THREED_OVERLAY_CODE_RANGES,',
            '"ThreeD": THREED_OVERLAY_CODE_RANGES,\n              "Voxel": ((0xEE7A, 0xF931),),')

    tag = 'VoxelSpriteRaster'
    candidate = ROOT / ('Tools/Disasm/Research/Candidates/' + tag)
    history = ROOT / ('Tools/Disasm/Research/History/Before' + tag)
    assert not candidate.exists() and not history.exists()
    originals = {path: path.read_bytes() if path.exists() else None for path in (*pending, raw_path)}
    for path, text in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    for path, old in originals.items():
        assert path.read_bytes() == old if old is not None else not path.exists()
        if old is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(old)
    for path, text in pending.items():
        path.write_text(text, encoding='utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert raw_path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
    assert raw_path.read_bytes() == (history / raw_path.relative_to(ROOT)).read_bytes() == raw
    raw_path.unlink()
    print(f'EE7A..F930: {len(raw)} байт и {len(decoded)} инструкций, 32 входа')


if __name__ == '__main__':
    main()
