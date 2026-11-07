"""Восстановление двух проверенных входов в конце файла VOXAL."""
from collections import Counter
from pathlib import Path
import contextlib
import hashlib
import io
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from InspectZ80 import decoder
from VerifySources import main as verify

ORIGIN = 0xEC00
FUNCTIONS = (
    (0xF9E9, 0xFA3A, 'ProjectEffectPoint', 'Проекция точки эффекта с двумя знаковыми поправками'),
    (0xFA3A, 0xFAC8, 'DrawProjectedEffect', 'Проекция двух углов эффекта и передача прямоугольника на отсечение'),
)
ENTRIES = {0xF9E9: 'Voxel.ProjectEffectPoint.Entry', 0xFA3A: 'Voxel.DrawProjectedEffect.Entry',
           0xAE73: 'Action.DivideScaledLogarithmic.Entry', 0xEC7F: 'Voxel.ClipSprite.Entry'}
LOCAL = {0xF9F9: 'ShiftVertical', 0xFA1C: 'ShiftHorizontal', 0xFA35: 'Reject',
         0xFA80: 'DiscardCorner', 0xFA82: 'CheckWidth'}
BEFORE = {
    0xF9E9: 'Проверка знака глубины до логарифмического деления.',
    0xF9EF: 'Расчёт вертикального числителя со знаковой поправкой из Hprime.',
    0xFA0C: 'Смещение первой проекции на 48 и сохранение для второй половины.',
    0xFA12: 'Расчёт горизонтального числителя со знаковой поправкой из Lprime.',
    0xFA2D: 'Смещение второй проекции на 128, флаг переполнения сохраняется.',
    0xFA3A: 'Настройка числа удвоений в обеих половинах проектора.',
    0xFA4A: 'Сохранение исходных компонент в операндах второго вызова.',
    0xFA55: 'Подготовка знаковых поправок для первого угла.',
    0xFA6F: 'Подготовка противоположных поправок для второго угла.',
    0xFA82: 'Расчёт горизонтальной разности и проверка диапазона.',
    0xFA99: 'Расчёт вертикальной разности и проверка диапазона.',
    0xFAA9: 'Подготовка координат, размеров и шагов ресурса для отсечения.',
}
RIGHT = {
    0xF9EC: 'переход, если глубина отрицательна, восстановить входной HL',
    0xFA0A: 'переход, если первая проекция выставила Carry',
    0xFA2B: 'переход, если вторая проекция выставила Carry',
    0xFA63: 'выход, если первая проекция выставила P/V',
    0xFA7D: 'переход, если вторая проекция сбросила P/V, проверить размеры',
    0xFA85: 'переход, если горизонтальная разность равна нулю',
    0xFA8D: 'переход, если горизонтальная разность не меньше 1024',
    0xFA9C: 'выход, если вертикальная разность равна нулю',
    0xFAA3: 'выход, если вертикальная разность не меньше 1024',
    0xFAA8: 'выход, если старший байт уменьшенной вертикальной разности ненулевой',
}
CONTRACTS = (
    ("HL, DE, BC задают горизонталь, глубину и вертикаль, HL' задаёт поправки в L' и H'",
     'Успех возвращает горизонталь в HL и вертикаль в DE, отказ выставляет A=3 и P/V',
     'HL, DE, BC, AF, рабочие операнды делителя, R и временный стек'),
    ("HL, DE, BC задают компоненты центра, A задаёт режим 0..6, HL' задаёт полуразмеры, DE' указывает ресурс",
     'Отказ возвращает управление, видимый прямоугольник передаётся ClipSprite хвостовым JP',
     "HL, DE, BC, AF, HL', AF', R, операнды проекции и стек, после перехода действует договор ClipSprite"),
)


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    root = ROOT / 'Tools/Disasm/Reports'
    pending = {}

    def read(stem):
        return json.loads((root / (stem + '.json')).read_text(encoding='utf-8'))

    def save(stem, value):
        pending[root / (stem + '.json')] = json.dumps(value, ensure_ascii=False, indent=2) + '\n'

    for proof in ('VoxelEffectProjectionVerification', 'VoxelEffectDrawEntryVerification'):
        assert read(proof)['passed']
    resource = 'Source/Resources/21_VOXAL/'
    raw_path = ROOT / (resource + 'Unclassified001.bin')
    image = (ROOT / 'Tools/Disasm/Extracted/Active/21_VOXAL.C.sectors.bin').read_bytes()
    assert raw_path.read_bytes() == image[0xDE9:] and len(image) == 0xF00
    memory = [0] * 65536
    memory[ORIGIN:ORIGIN + len(image)] = image
    disassembler = decoder(memory)
    flow = read('ControlFlow')
    voxel = next(region for region in flow if region['name'] == 'Voxel')
    functions = read('Functions')
    symbols = read('Symbols')
    ranges = read('SourceMap')
    old_range = next(item for item in ranges if ROOT / item['path'] == raw_path)
    assert old_range['offset'] == 0xDE9 and old_range['length'] == 279
    sections, indexes, details, inserted = [], [], [], []
    instruction_count = 0
    for index, (start, end, name, description) in enumerate(FUNCTIONS):
        path = 'Source/Voxel/' + name + '.asm'
        decoded = disassembler.disassemble(start, end, 'h')
        raw = image[start - ORIGIN:end - ORIGIN]
        assert bytes(byte for item in decoded for byte in item.bytes) == raw
        assert not {i.address for i in decoded}.intersection(i['address'] for i in voxel['instructions'])
        assert not any(item.operation.startswith('DEFB') for item in decoded)
        lines = ['                module Voxel', '                module ' + name,
                 '                ; Документация [две проекции эффекта](../../Docs/ActionVisualEffectWalk.md)',
                 '                ; -----------------------------------------', '                ; ' + description,
                 '                ;   банк 3, исходная запись 21',
                 '                ; In:', '                ;   ' + CONTRACTS[index][0],
                 '                ;   доступны код банка 3, таблицы делителя и стек, IRQ не вмешиваются',
                 '                ; Out:', '                ;   ' + CONTRACTS[index][1],
                 '                ; Corrupt:', '                ;   ' + CONTRACTS[index][2],
                 '                ; Note:',
                 '                ;   точные ветви, масштабирование и границы проверки приведены в документации',
                 '                ; -----------------------------------------']
        for item in decoded:
            pc = item.address
            operation = item.operation.replace(',', ', ')
            voxel['instructions'].append(dict(address=pc, operation=item.operation, hex=item.bytes.hex(),
                                              slot=21, offset=pc - ORIGIN))
            if pc in BEFORE:
                lines.append('                ; ' + BEFORE[pc])
            label = 'Entry' if pc == start else LOCAL.get(pc)
            if label:
                qualified = f'Voxel.{name}.{label}'
                assert qualified not in symbols
                symbols[qualified] = pc
            if operation.startswith(('JR ', 'JP ', 'CALL ')):
                target = int(operation.rsplit('#', 1)[1], 16)
                bank_symbol = ENTRIES.get(target)
                if target in LOCAL and target != pc:
                    bank_symbol = f'Voxel.{name}.{LOCAL[target]}'
                if bank_symbol:
                    operation = operation.rsplit('#', 1)[0] + '@' + bank_symbol
                voxel['calls' if operation.startswith('CALL ') else 'branches'].append(target)
            line = (f'{label}:'.ljust(16) if label else ' ' * 16) + operation
            if pc in RIGHT:
                line = line.ljust(80) + '; ' + RIGHT[pc]
            if pc in (0xF9F9, 0xFA1C):
                line = line.ljust(80) + '; исходный переход на себя, смещение задаёт DrawProjectedEffect'
            lines.append(line)
            if operation.startswith(('JR ', 'JP ', 'RET')):
                lines.append('')
        pending[ROOT / path] = '\n'.join(lines + ['                endmodule', '                endmodule', ''])
        functions.append(dict(region='Voxel', name=name, address=start, slot=21, offset=start - ORIGIN,
                              end_offset=end - ORIGIN, path=path, description=description, semantic_status='described'))
        inserted.append(dict(slot=21, offset=start - ORIGIN, length=len(raw), path=path, kind='code',
                             origin=start, sha256=hashlib.sha256(raw).hexdigest()))
        sections.extend((f'                disp #{start:04X}', f'                include "../Voxel/{name}.asm"',
                         '                ent', f'                assert $ == #{end - ORIGIN:04X}'))
        indexes.append(f'| #{start:04X} | [Voxel.{name}](../{path}) | {description} |')
        details.append(f'## {name}\n\n[Voxel.{name}](../../{path})\n\n{description}.\n')
        instruction_count += len(decoded)

    tail_path = resource + 'SectorTail.bin'
    tail = image[0xEC8:]
    inserted.append(dict(slot=21, offset=0xEC8, length=len(tail), path=tail_path, kind='unclassified',
                         origin=None, sha256=hashlib.sha256(tail).hexdigest()))
    sections.extend(('                ; Хвост последнего физического сектора после логического конца файла.',
                     '                incbin "../Resources/21_VOXAL/SectorTail.bin"'))
    ranges[ranges.index(old_range):ranges.index(old_range) + 1] = inserted
    voxel['instructions'].sort(key=lambda i: (i['address'], i['slot'], i['offset']))
    voxel['instruction_count'] += instruction_count
    voxel['code_bytes'] += 0xEC8 - 0xDE9
    voxel['classified_fraction'] = voxel['code_bytes'] / voxel['total_bytes']
    for key in ('calls', 'branches'):
        voxel[key] = sorted(set(voxel[key]))
    inventory = read('Inventory')
    inventory['instructions'] += instruction_count
    inventory['described'] += len(FUNCTIONS)
    inventory['fragments'] += len(FUNCTIONS)
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in ranges))
    sizes = Counter()
    for item in ranges:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for stem, value in (('ControlFlow', flow), ('Functions', functions), ('SourceMap', ranges),
                        ('Symbols', symbols), ('Inventory', inventory)):
        save(stem, value)

    def replace(relative, old, new):
        path = ROOT / relative
        text = pending.get(path, path.read_text(encoding='utf-8'))
        assert text.count(old) == 1, (relative, old)
        pending[path] = text.replace(old, new)

    replace('Source/Files/21_VOXAL.inc', '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
            '                incbin "../Resources/21_VOXAL/Unclassified001.bin"', '\n'.join(sections))
    replace('Source/Action/ResumeVisualEffect.asm', 'CALL #FA3A', 'CALL @Voxel.DrawProjectedEffect.Entry')
    replace('Tools/Disasm/Research/Analyze.py', '"Voxel": ((0xEE7A, 0xF931),),',
            '"Voxel": ((0xEE7A, 0xF931), (0xF9E9, 0xFAC8)),')
    path = ROOT / 'Docs/Functions.md'
    text = path.read_text(encoding='utf-8')
    line = next(line for line in text.splitlines() if line.startswith('| #F957 | [Voxel.Divide7BitFixed]'))
    replace('Docs/Functions.md', line, line + '\n' + '\n'.join(indexes))
    match = re.search(r'\| Voxel \| (\d+) \| (\d+) \|', pending[path])
    assert match
    replace('Docs/Functions.md', match[0], f'| Voxel | {int(match[1]) + 2} | {int(match[2]) + 2} |')
    path = ROOT / 'Docs/FunctionDetails/Voxel.md'
    pending[path] = path.read_text(encoding='utf-8').rstrip() + '\n\n' + '\n'.join(details)
    replace('Docs/ActionVisualEffectWalk.md', 'В `#F9E9` при отрицательном',
            'В [ProjectEffectPoint](../Source/Voxel/ProjectEffectPoint.asm) по `#F9E9` при отрицательном')
    replace('Docs/ActionVisualEffectWalk.md', 'После двух проекций со сброшенным',
            'В [DrawProjectedEffect](../Source/Voxel/DrawProjectedEffect.asm) после двух проекций со сброшенным')
    path = ROOT / 'Tools/Disasm/Research/Knowledge.py'
    line = next(line for line in path.read_text(encoding='utf-8').splitlines() if '0xF957: ("Divide7BitFixed"' in line)
    definitions = [f'        0x{start:04X}: ("{name}", "{description}"),' for start, _, name, description in FUNCTIONS]
    replace('Tools/Disasm/Research/Knowledge.py', line, line + '\n' + '\n'.join(definitions))

    candidate = ROOT / 'Tools/Disasm/Research/Candidates/VoxelEffectTail'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeVoxelEffectTail'
    assert not candidate.exists() and not history.exists()
    files = {path: text.encode('utf-8') for path, text in pending.items()}
    files[ROOT / tail_path] = tail
    originals = {path: path.read_bytes() if path.exists() else None for path in (*files, raw_path)}
    for path, data in files.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for path, data in originals.items():
        assert path.read_bytes() == data if data is not None else not path.exists()
        if data is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for path, data in files.items():
        path.write_bytes(data)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert raw_path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
    assert raw_path.read_bytes() == image[0xDE9:]
    raw_path.unlink()
    print(f'{instruction_count} инструкций, {0xEC8 - 0xDE9} байта кода, {len(tail)} байтов секторного хвоста')


if __name__ == '__main__':
    main()
