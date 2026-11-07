"""Физические шаблоны и выборки параметров планировщика ACTION."""
import re
from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT

TABLES = ((0x7799, 0x7859, 'ActionSpawnTemplates', 'Source/Action/Data/SpawnTemplates.asm'),
          (0x7AC6, 0x7B48, 'ActionSpawnModels', 'Source/Action/Data/SpawnModelChoices.asm'))
TYPES = {'FSpawnDataPointer': (('Address', 2),),
         'FSpawnTemplateRow': (('Delta0', 2), ('Delta1', 2), ('Delta2', 2), ('ModelOffset', 1), ('OffsetPhase1', 1)),
         'FSpawnTemplateEnd': (('Unknown00', 1), ('EndCode', 1)),
         'FSpawnModelPair': (('ModelOffset', 1), ('RecordByte0F', 1))}


def render(table):
    start, end, module, path = table
    memory = flat_action()
    lines = ['                module ' + module,
             '                ; Документация [физические таблицы создания](../../../Docs/ActionSpawnPhysicalRows.md)',
             f'                assert $ == #{start:04X}']
    position = start
    labels = {}
    def row(label, kind, note):
        nonlocal position
        labels[label] = position
        lines.append('                ; ' + note)
        lines.append((label + ':').ljust(16) + kind + ' {')
        fields = TYPES[kind]
        for index, (field, size) in enumerate(fields):
            value = int.from_bytes(bytes(memory[position:position + size]), 'little')
            text = f'                    #{value:0{size * 2}X}' + (',' if index + 1 < len(fields) else '')
            lines.append(text.ljust(80) + '; ' + kind + '.' + field + ', исходное значение')
            position += size
        lines.append('                }')
    if start == 0x7799:
        pointers = [memory[start + 2 * i] + 256 * memory[start + 2 * i + 1] for i in range(16)]
        assert len(set(pointers)) == 16
        for index, address in enumerate(pointers):
            row(f'Seed{index:02}', 'FSpawnDataPointer', f'Шаблон Template{index:02}, адрес #{address:04X}.')
        for address in sorted(pointers):
            assert address == position
            index = pointers.index(address)
            row(f'Template{index:02}', 'FSpawnTemplateRow', 'Три знаковые поправки и два байта объектной записи.')
            assert memory[position:position + 2] == [255, 128]
            row(f'End{index:02}', 'FSpawnTemplateEnd', 'EndCode=80 завершает обход, смысл младшего FF не установлен.')
    else:
        pointers = [memory[start + 2 * i] + 256 * memory[start + 2 * i + 1] for i in range(9)]
        assert pointers[0] == pointers[5] and pointers[6] == pointers[7]
        for index, address in enumerate(pointers):
            row(f'Class{index:02}', 'FSpawnDataPointer', f'Класс {index}, восемь пар от C{address:04X}_0.')
        for address in sorted(set(pointers)):
            assert address == position
            for index in range(8):
                row(f'C{address:04X}_{index}', 'FSpawnModelPair', f'Вариант {index}, выбирается младшими тремя битами R.')
    assert position == end
    lines.extend((f'                assert $ == #{end:04X}', '                endmodule', ''))
    return '\n'.join(lines), labels


def parse(text):
    code = '\n'.join(line.partition(';')[0] for line in text.splitlines())
    raw, labels = bytearray(), {}
    for match in re.finditer(r'(\w+):\s+(FSpawn\w+)\s*\{([^}]+)\}', code):
        assert match[1] not in labels
        labels[match[1]] = len(raw)
        fields = TYPES[match[2]]
        values = [value.strip() for value in match[3].split(',')]
        assert len(values) == len(fields)
        for value, (_, size) in zip(values, fields):
            assert re.fullmatch(r'#[0-9A-Fa-f]+', value)
            raw.extend(int(value[1:], 16).to_bytes(size, 'little'))
    return bytes(raw), labels
