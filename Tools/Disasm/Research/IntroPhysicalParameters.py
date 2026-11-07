"""Физические параметры вступления, разметка по установленным потребителям."""
import re
from CheckIntro import ROOT

# Проверка охвата выполняется отдельно, байт 66A2 не входит в 63 чтения построителя.
BLOCKS = (
    (0x315, 9, 'StationFileKey', 'StationFileKey.asm'),
    (0x32C, 12, 'FinalTexturePhases', 'FinalTexturePhases.asm'),
    (0x363, 63, 'AlternatingLookup', 'AlternatingLookup.asm'),
    (0x693, 16, 'AttributeNibbleSeeds', 'AttributeNibbleSeeds.asm'),
    (0x873, 32, 'ColumnTailSamples', 'ColumnTailSamples.asm'),
    (0x962, 40, 'ScaleCycle', 'ScaleCycle.asm'),
)
TYPES = (
    ('FIntroLookupParameter', 'InitialIYL', 'исходный IYL для одной из 63 последовательностей построителя'),
    ('FIntroAttributeSeed', 'Nibbles', 'старший полубайт столбца и младший полубайт строки матрицы атрибутов'),
    ('FIntroColumnTailSample', 'LookupCode', 'код выборки хвоста, затем прибавляются фазы косвенной адресации'),
    ('FIntroScaleSample', 'Offset', 'добавка 0..15 к базовому индексу строки масштаба 56'),
)
REPLACEMENTS = {
    'LoadStation': {'LD HL, #6615': 'LD HL, @IntroStationFileKey.Entry'},
    'DrawFinalTextureFrame': {'LD HL, #662C': 'LD HL, @IntroFinalTexturePhases.First',
                             'LD BC, #6632': 'LD BC, @IntroFinalTexturePhases.Second'},
    'BuildAlternatingTexture': {'LD HL, #6663': 'LD HL, @IntroAlternatingLookup.P00'},
    'BuildAttributeWriter': {'LD HL, #6993': 'LD HL, @IntroAttributeNibbleSeeds.A0'},
    'InitializeColumnEffect': {'LD HL, #6B73': 'LD HL, @IntroColumnTailSamples.P00',
                               'LD (#6993), A': 'LD (@IntroAttributeNibbleSeeds.A0), A'},
    'InitializeLookupEffect': {'LD (#6993), A': 'LD (@IntroAttributeNibbleSeeds.A0), A'},
    'AdvanceTextureScale': {'LD HL, #6C62': 'LD HL, @IntroScaleCycle.P00'},
}


def source_path(filename):
    return 'Source/Intro/Data/' + filename


def render(block, raw):
    offset, length, module, _ = block
    assert len(raw) == length
    origin = 0x6300 + offset
    lines = ['                module Intro' + module,
             '                ; Документация [параметры вступления](../../../Docs/IntroPhysicalParameters.md)',
             f'                assert $ == #{origin:04X}']
    labels = {}

    def add(name, instruction, note, index):
        lines.append((f'{name}:'.ljust(16) + instruction).ljust(80) + '; ' + note)
        labels['Intro' + module + '.' + name] = origin + index

    if module == 'StationFileKey':
        assert raw == b'STATIONFC'
        add('Entry', 'FTrDosFileKey { { "STATIONF" }, #43 }',
            'имя STATIONF и тип C, девять байтов без завершающего нуля', 0)
    elif module == 'FinalTexturePhases':
        for index, name in ((0, 'First'), (6, 'Second')):
            values = [int.from_bytes(raw[index+j:index+j+2], 'little') for j in (0, 2, 4)]
            add(name, 'FTexturePhase { ' + ', '.join(f'#{v:04X}' for v in values) + ' }',
                'Phase, Step, StepDelta, начальная фаза 8000 и нулевое движение', index)
    else:
        struct, note = {
            'AlternatingLookup': ('FIntroLookupParameter', 'начальный IYL очередной последовательности'),
            'AttributeNibbleSeeds': ('FIntroAttributeSeed', 'упакованные старший и младший полубайты атрибута'),
            'ColumnTailSamples': ('FIntroColumnTailSample', 'код выборки для хвоста каждой из 32 страниц'),
            'ScaleCycle': ('FIntroScaleSample', 'добавка к индексу масштаба 56, байт не является набором флагов'),
        }[module]
        for index, value in enumerate(raw):
            name = (('A' if index < 8 else 'B') + str(index % 8)
                    if module == 'AttributeNibbleSeeds' else f'P{index:02X}')
            add(name, f'{struct} {{ #{value:02X} }}', note, index)
    lines += [f'                assert $ == #{origin+length:04X}', '                endmodule', '']
    return '\n'.join(lines), labels


def parse(block, text):
    module = block[2]
    code = '\n'.join(line.partition(';')[0] for line in text.splitlines())
    if module == 'StationFileKey':
        found = re.findall(r'FTrDosFileKey\s*\{\s*\{\s*"([^"]*)"\s*\}\s*,\s*#([0-9A-F]+)\s*\}', code)
        assert len(found) == 1 and len(found[0][0]) == 8
        return found[0][0].encode('ascii') + bytes([int(found[0][1], 16)])
    if module == 'FinalTexturePhases':
        found = re.findall(r'FTexturePhase\s*\{([^}]+)\}', code)
        assert len(found) == 2
        result = b''
        for row in found:
            values = re.findall(r'#([0-9A-F]{4})', row)
            assert len(values) == 3
            result += b''.join(int(value, 16).to_bytes(2, 'little') for value in values)
        return result
    struct = {'AlternatingLookup': 'FIntroLookupParameter', 'AttributeNibbleSeeds': 'FIntroAttributeSeed',
              'ColumnTailSamples': 'FIntroColumnTailSample', 'ScaleCycle': 'FIntroScaleSample'}[module]
    values = re.findall(struct + r'\s*\{\s*#([0-9A-F]{2})\s*\}', code)
    assert len(values) == block[1]
    return bytes(int(value, 16) for value in values)


def name_operands(region, function_address, operation):
    if region != 'Intro':
        return operation
    functions = {0x65B7: 'LoadStation', 0x661E: 'DrawFinalTextureFrame', 0x6638: 'BuildAlternatingTexture',
                 0x692D: 'BuildAttributeWriter', 0x6AC1: 'InitializeColumnEffect',
                 0x6C9C: 'InitializeLookupEffect', 0x6C21: 'AdvanceTextureScale'}
    return REPLACEMENTS.get(functions.get(function_address), {}).get(operation, operation)
