"""DD87, подтверждённый сброс векторов и списков с продолжением DE0A."""
TAG = 'ControlsResetFlightContext'
TITLE = 'сброс полётного контекста и активация параметров'
SLOT, REGION = 23, 'Controls'
CASES = 2048
FUNCTIONS = {0xDD87: ('ResetFlightContext', 'Сброс рабочих векторов, списков объектов и эффектов и перенос ключа перед активацией параметров')}
ENDS = {0xDD87: 0xDE0A}
KEYS = {}
LOCAL = {0xDD92: 'StoreVector', 0xDDA7: 'CopyVectors', 0xDDB6: 'NextObject',
         0xDDC4: 'ClearObject', 0xDDD2: 'BeginEffects', 0xDDD9: 'NextEffect',
         0xDDE8: 'CopyContext', 0xDE06: 'StoreOpcode'}
MUTATIONS = ((0xDE07, 0x7B60, 1, 0x7B60, 'Source/Action/ScheduleSpawn.asm'),)
LOCATION = 'исходное окно CONTROL банка 1'


def file_offset(address):
    return address - 0xDADE


CONTRACTS = {('Controls', 0xDD87): (
    ['HL, DE, BC и AF числовых аргументов не задают, доступен HyperDiablo.Value, две таблицы широких векторов и OtherContext',
     'список объектов с шагом FActionRecord имеет маркер 8080, список эффектов с шагом FVisualEffect имеет отрицательный State',
     'верхнее окно показывает банк 1, общее ядро ACTION доступно на запись, на CPU-стеке действительный внешний адрес возврата',
     'для последовательного продолжения действуют договоры BuildAndActivateParameters и незаблокированный paging, IRQ не вмешиваются'],
    ['старшие слова первых двух компонент ActionTransformWorkVector обнулены, третье получает 0200 при HyperDiablo.Value=FF и 1100 иначе',
     'в ActionWideVectors скопирован один из двух исходных шаблонов, FF выбирает DF91, прочие значения DFD9',
     'до маркера объектов каждая запись получает Component0=8000 и ReuseByte=FF, до отрицательного маркера эффектов обнуляются State',
     'OtherContext и SelectedIndex скопированы в ParameterSeeds, по ScheduleSpawn.OpcodeGate записан XOR четырёх байтов ключа AND 7 либо C9 при нуле',
     'на границе DE0A HL=OtherSecond, DE=OtherFirst, BC=значение опкода, A равен этому же байту, F от AND 07, даже при подстановке C9',
     'HL\', DE\', BC\', AF\' сохранены до DE0A, IX указывает маркер эффектов, IY указывает маркер объектов, SP и банк 1 на этой границе сохранены',
     'полный выход через BuildAndActivateParameters выбирает банк 0 и снимает первоначальный внешний адрес возврата'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, IY, R, указанные векторы, записи до маркеров, ParameterSeeds, опкод и состояние дочерней активации'],
    ['исходный контроль окончания списка объектов проверяет полный маркер 8080, текущая запись с любым иным заголовком сбрасывается',
     'запись в планировщик меняет байт инструкции, его прежний непосредственный операнд не перезаписывается',
     '2048 сценариев проверили все байты оборудования, восемь результатов свёртки, выбор шаблона и обе границы списков',
     'регистры префикса сверены кроме R и тактов, все банки и последовательность записей сверены до полного возврата через настоящий дочерний код',
     'остаточный загрузчик содержит прямой CALL DD87, его перенос в настоящей игре, исполнение подставленного опкода и нативный запуск не доказаны'])}


COMMENTS = {
    0xDD87: (['-----------------------------------------', 'Подготовка полётных векторов',
              'Проверка кода оборудования, только FF выбирает исходный набор без гиперсистемы.'], None),
    0xDD8E: ([], 'переход, если HyperDiablo.Value равен FF, сохранить старшее слово 0200'),
    0xDD92: (['Обновление старших слов трёх компонент, младшие байты остаются прежними.'], None),
    0xDD9F: (['Выбор одного из двух исходных шаблонов широких векторов по сохранённому Z.'], None),
    0xDDA2: ([], 'переход, если HyperDiablo.Value равен FF, копировать шаблон DF91'),
    0xDDA7: (['Копирование шести широких векторов в рабочий список.'], None),
    0xDDAF: (['-----------------------------------------', 'Освобождение записей объектов',
              'Подготовка позиции перед первой физической записью и размера шага.'], None),
    0xDDB8: (['Проверка обоих байтов маркера 8080 перед сбросом текущей записи.'], None),
    0xDDBD: ([], 'переход, если младший байт компоненты отличается от 80, освободить запись'),
    0xDDC2: ([], 'переход, если оба байта равны 80, закончить обход объектов'),
    0xDDC4: (['Установка заголовка доступной записи и признака однократного пропуска.'], None),
    0xDDD2: (['-----------------------------------------', 'Освобождение записей эффектов',
              'Выбор позиции до первого эффекта.'], None),
    0xDDDB: (['Проверка знака полного байта State до очистки текущего эффекта.'], None),
    0xDDDF: ([], 'переход, если State отрицателен, закончить обход эффектов'),
    0xDDE2: (['Освобождение записи эффекта без изменения остальных полей.'], None),
    0xDDE8: (['-----------------------------------------', 'Перенос ключа и запись опкода',
              'Копирование двух слов ключа и связанного байта в активный контекст.'], None),
    0xDDFB: (['Расчёт трёхбитной свёртки четырёх байтов двух слов.'], None),
    0xDE02: ([], 'переход, если свёртка ненулевая, сохранить её как байт опкода'),
    0xDE07: (['Обновление опкода планировщика в общей RAM, байт непосредственного операнда остаётся прежним.'], None),
}


def name_operands(region, address, operation):
    if (region, address) != ('Controls', 0xDD87):
        return operation
    replacements = {
        '(#9C30)': '(@ActionShipEquipment.HyperDiablo.Value)',
        'LD BC, #0200': 'LD BC, @ControlsResetFlightConst.NoDiabloWord',
        'LD B, #11': 'LD B, @ControlsResetFlightConst.DiabloHigh',
        '(#9B70)': '(@ActionTransformWorkVector.Value.Component0.LowWord + 1)',
        '(#9B73)': '(@ActionTransformWorkVector.Value.Component1.LowWord + 1)',
        '(#9B76)': '(@ActionTransformWorkVector.Value.Component2.LowWord + 1)',
        '#DF91': '@ControlsVectorsNoDiablo.Vector00',
        '#DFD9': '@ControlsVectorsWithDiablo.Vector00',
        '#9B27': '@ActionWideVectors.Vector00',
        'LD BC, #0048': 'LD BC, @ControlsResetFlightConst.VectorBytes',
        '#A0C0': '@ActionObjectRecords.Record00 - @FActionRecord',
        'LD DE, #0040': 'LD DE, @FActionRecord',
        '(IY+#00)': '(IY + @FActionRecord.Components.Component0.Low)',
        '(IY+#01)': '(IY + @FActionRecord.Components.Component0.High)',
        '(IY+#18)': '(IY + @FActionRecord.ReuseByte)',
        'CP #80': 'CP @ActionReuseConst.ReusableHigh',
        ', #FF': ', @ActionReuseConst.SkipOnce',
        '#A783': '@ActionBankedCallbackState.ContextBase',
        'LD DE, #0012': 'LD DE, @FVisualEffect',
        '(IX+#07)': '(IX + @FVisualEffect.State)',
        '(#9BC6)': '(@ActionOtherContext.Value.OtherFirst)',
        '(#9BC8)': '(@ActionOtherContext.Value.OtherSecond)',
        '(#9BCA)': '(@ActionContextIndex.Value.SelectedIndex)',
        '(#9BC1)': '(@ActionParameterSeeds.Value.SeedFirst)',
        '(#9BC3)': '(@ActionParameterSeeds.Value.SeedSecond)',
        '(#9BC5)': '(@ActionParameterSeeds.Value.StepControl)',
        'AND #07': 'AND @ControlsResetFlightConst.FoldMask',
        'LD C, #C9': 'LD C, @ControlsResetFlightConst.ZeroFoldOpcode',
        '(#7B60)': '(@Action.ScheduleSpawn.OpcodeGate)',
    }
    replacements.update({'#' + format(target, '04X'): '@Controls.ResetFlightContext.' + name
                         for target, name in LOCAL.items()})
    for before, after in replacements.items():
        operation = operation.replace(before, after)
    return operation


def prepare(pending, symbols, root):
    import json
    from SourcePresentation import format_function

    const = root / 'Includes/Const/Include.inc'
    text = const.read_text('utf-8')
    assert text.count('                endif') == 1
    lines = ['                module ControlsResetFlightConst']
    for name, value, note in (
        ('NoDiabloWord', 0x0200, 'старшее слово третьей компоненты при коде оборудования FF'),
        ('DiabloHigh', 0x11, 'старший байт третьей компоненты при остальных кодах оборудования'),
        ('VectorBytes', 0x48, 'размер шести копируемых широких векторов'),
        ('FoldMask', 7, 'маска трёхбитной свёртки четырёх байтов ключа'),
        ('ZeroFoldOpcode', 0xC9, 'опкод RET при нулевой свёртке'),
    ):
        lines.append((name.ljust(16) + f'equ #{value:04X}').ljust(80) + '; ' + note)
        symbols['ControlsResetFlightConst.' + name] = value
    lines.extend(('                assert VectorBytes == 6 * FActionWideVector', '                endmodule', ''))
    pending[const] = text.replace('                endif', '\n'.join(lines) + '\n                endif').encode('utf-8')

    target = root / 'Source/Action/ScheduleSpawn.asm'
    text = target.read_text('utf-8')
    original = '                NOP\n                LD A, #00\n                DEC A'
    assert text.count(original) == 1
    patched = ('                NOP\n'
               '                ; Загрузка исходного счётчика, ResetFlightContext может заменить опкод по этому адресу.\n'
               'OpcodeGate:     LD A, #00\n                DEC A')
    pending[target] = text.replace(original, patched).encode('utf-8')
    symbols['Action.ScheduleSpawn.OpcodeGate'] = 0x7B60
    names = root / 'Tools/Disasm/Research/SemanticNames.py'
    pending[names] += b"\nLABELS['Action',0x7B60]='OpcodeGate'\n"

    path = root / 'Tools/Disasm/Research/Analyze.py'
    text = path.read_text('utf-8')
    original = 'block(23, 0, 6474, 0xDADE, "Controls", (0xDADE,))'
    assert text.count(original) == 1
    pending[path] = text.replace(original, original.replace('(0xDADE,)', '(0xDADE, 0xDD87)')).encode('utf-8')
    path = root / 'Tools/Disasm/Reports/ControlFlow.json'
    flow = json.loads(pending[path])
    group = next(row for row in flow if row['name'] == 'Controls')
    block = next(row for row in group['blocks'] if row['slot'] == 23 and row['origin'] == 0xDADE)
    block['roots'].append(0xDD87)
    pending[path] = (json.dumps(flow, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    path = root / 'Source/Controls/ResetFlightContext.asm'
    text = pending[path].decode('utf-8')
    pending[path] = format_function(text, {'region': 'Controls', 'name': 'BuildAndActivateParameters',
                                          'path': 'Source/Controls/BuildAndActivateParameters.asm'}).encode('utf-8')
    path = root / 'Source/Files/23_CONTROL.inc'
    text = pending[path].decode('utf-8')
    for index, file in enumerate(('ResetFlightContext', 'BuildAndActivateParameters')):
        old = f'include "../Controls/{file}.asm"'
        assert text.count(old) == 1
        text = text.replace(old, old.ljust(64) + f'; ({index}) жёсткий порядок, последовательное исполнение')
    pending[path] = text.encode('utf-8')
