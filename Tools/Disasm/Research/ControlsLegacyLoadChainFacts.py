"""Разметка старого загрузчика в согласованных адресах по исходным внутренним ссылкам."""
TAG = 'ControlsLegacyLoadChain'
TITLE = 'старое чтение секторов, распаковка и восстановление полётного контекста'
SLOT, REGION = 23, 'Controls'
CASES = 4
FUNCTIONS = {
    0x5E1F: ('LoadLegacyPackedBlock', 'Старый вход чтения и распаковки блока с возвратом через восстановленный полётный контекст'),
    0x5E4D: ('ReadLegacySectors', 'Чтение последовательных секторов через внутренние входы ROM с повтором при ошибке'),
    0x5ED2: ('WriteLegacyDiskPort', 'Подготовка ROM-входа вывода байта в порт'),
    0x5ED6: ('CallLegacyDosRom', 'Передача внутреннему ROM-входу TR-DOS через подготовленный стек'),
}
ENDS = {0x5E1F: 0x5E4D, 0x5E4D: 0x5ED2, 0x5ED2: 0x5ED6, 0x5ED6: 0x5EDB}
KEYS = {}
LOCAL = {0x5E22: 'SectorCount', 0x5E32: 'RestoreStack', 0x5E61: 'NextSector', 0x5E6E: 'SelectSide',
         0x5E83: 'ReadAttempt', 0x5ECD: 'CountDown'}
MUTATIONS = ()
LOCATION = 'согласованные адреса старой копии, фактический перенос игрой неизвестен'


def file_offset(address):
    return address - 0x5DA0


CONTRACTS = {
    ('Controls', 0x5E1F): (
        ['HL, DE, BC и AF входных числовых аргументов не задают, исходные DE и B загружаются из изменяемых операндов',
         'в этих операндах должны быть допустимые координаты сектора и ненулевое число секторов, исходные нули сохранены',
         'выбран подходящий банк назначения по C000, загружаемый поток удовлетворяет договору UnpackResource',
         'на входном CPU-стеке слово 7FFD, операнд RestoreStack задаёт адрес сохранённых IX и внешнего возврата',
         'доступны ROM и порты диска, банк 1 содержит ResetFlightContext, IRQ не вмешиваются'],
        ['в выбранный банк по C000 прочитан блок, затем выполняется исходная распаковка на месте',
         'из рамки извлечён порт 7FFD, установлен сохранённый SP, выбран банк 1 и выполнен ResetFlightContext',
         'после активации остаётся банк 0, выбраны регистр AY 7 и значение DB, A=DB, BC=BFFD',
         'IX извлечён из сохранённой рамки, IFF сброшен, PC и SP определяются её внешним возвратом'],
        ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, IY, SP, IFF, R, память чтения и распаковки, данные активации и порты'],
        ['загрузчик ACTION пишет координаты CONTROL0 по этим адресам, наличие старых команд в рабочей RAM не подтверждено',
         'четыре профиля с подготовленными координатами PANEL исполнили дисковые ROM, распаковку, сброс контекста и внешний возврат',
         'PANEL использован как совместимый исходный ресурс проверки, игровой файл этого входа не установлен']),
    ('Controls', 0x5E4D): (
        ['HL, начало доступного назначения, DE, D логический трек, E сектор 1..16, BC, B ненулевое число секторов',
         'дисковые сигналы и внутренние ROM-входы доступны, 5CC2 содержит системный RET, конфигурация 5D16 подготовлена',
         'CPU-стек допускает рамки внутренних ROM, области чтения не задевают выполняемые команды и живой стек'],
        ['записаны B входных секторов по 256 байтов, после ошибки по 5CCD AND 7F повторяется тот же сектор и тот же адрес',
         'на проверенном возврате DE указывает логический трек и сектор следующего блока, B=0, HL\' равен концу назначения',
         'SP увеличен на два после обычного RET, R и регистры зависят от достигнутых ROM'],
        ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, CPU-стек, дисковое состояние ROM, назначение, порты и R'],
        ['после 16 сектора увеличивается D, при новом чётном D выполняется команда 58',
         'при успехе увеличивается H, младший L сохраняется, при повторе не продвигаются ни адрес, ни сектор',
         'нулевой B в исходном коде не проверяется, такой вход не входит в доказанный рабочий договор',
         '16 сценариев сверены на четырёх ROM с моделью портов и выборки ROM, в том числе повтор и переход трека']),
    ('Controls', 0x5ED2): (
        ['BC, адрес порта, AF, байт A, на CPU-стеке внешний адрес возврата, доступно переключение ROM'],
        ['IX получает адрес 2A53, последовательное продолжение выполняет OUT (C), A и возвращается через внешнее слово'],
        ['IX, SP по возврату, R, состояние порта'],
        ['в четырёх проверенных ROM по 2A53 находятся ED 79 C9, общего сервиса 3D13 нет']),
    ('Controls', 0x5ED6): (
        ['IX, адрес внутренней процедуры ROM, прочие регистры по её договору, под стеком есть место для адреса IX'],
        ['PUSH IX и JP 3D2F передают управление в ROM, его NOP и RET снимают IX как адрес исполнения',
         'возврат самой процедуры ROM использует прежнюю рамку вызывающего, регистры определяются её кодом'],
        ['SP временно уменьшен на два, дальнейшие изменения по достигнутой процедуре ROM'],
        ['вход 3D2F требует выбора TR-DOS при выборке команды, CALL на него вместо исходного JP не добавляется']),
}


COMMENTS = {
    0x5E1F: (['Подготовка координат дискового блока и его длины из исходных операндов.'], None),
    0x5E24: (['Чтение блока в текущий банк с сохранением адреса для распаковки.'], None),
    0x5E2C: (['Распаковка на месте, DE повторяет HL.'], None),
    0x5E31: (['Восстановление порта и CPU-стека из рамки до выбора банка 1.'], None),
    0x5E39: (['Сброс полётного состояния и активация параметров, дочерний код выбирает банк 0.'], None),
    0x5E3C: (['Восстановление исходного значения микшера AY перед выходом.'], None),
    0x5E49: (['Снятие сохранённого IX, запрет IRQ и возврат вызывающему.'], None),
    0x5E4D: (['Расчёт физического трека как D SHR 1 и начальная команда позиционирования.'], None),
    0x5E5C: (['Перенос координат и счётчика в другой набор регистров перед последовательным чтением.'], None),
    0x5E61: (['Обновление управляющего порта с выбором стороны по чётности логического трека.'], None),
    0x5E68: (['Проверка бита стороны, чётный логический трек устанавливает бит 4 порта.'], None),
    0x5E6A: ([], 'переход, если логический трек нечётный, оставить бит стороны сброшенным'),
    0x5E74: (['Запись физического трека и текущего номера сектора.'], None),
    0x5E83: (['Чтение одной попытки, адрес HL сохраняется для повтора.'], None),
    0x5E95: (['Передача текущего физического трека ROM и получение статуса по 5CCD.'], None),
    0x5EA6: (['Проверка всех младших семи битов статуса перед продвижением.'], None),
    0x5EAC: ([], 'переход, если статус после маски ненулевой, повторить чтение в прежний адрес'),
    0x5EAE: (['Продвижение адреса на 256 и номера сектора на один после успеха.'], None),
    0x5EB2: (['Проверка границы логического трека после увеличения сектора.'], None),
    0x5EB4: ([], 'переход, если следующий сектор меньше 17, продолжить отсчёт'),
    0x5EB6: (['Переход к следующему логическому треку и сектору 1.'], None),
    0x5EB9: (['Проверка чётности следующего трека для команды шага головки.'], None),
    0x5EBB: ([], 'переход, если следующий логический трек нечётный, не двигать головку'),
    0x5EBD: (['Выдача команды 58 и ожидание завершения перед новым треком.'], None),
    0x5ECD: (['Проверка числа оставшихся секторов после обновления адреса и координат.'], None),
    0x5ECE: ([], 'переход, если осталось прочитать хотя бы один сектор'),
    0x5ED2: (['Выбор ROM-процедуры, выполняющей OUT (C), A.'], None),
    0x5ED6: (['Передача адреса ROM через вершину стека без дополнительной рамки CALL.'], None),
}


def name_operands(region, address, operation):
    if (region, address) == ('ActionBoot', 0x4200):
        return operation.replace('(#5E20)', '(@Controls.LoadLegacyPackedBlock.Entry + 1)').replace(
            '(#5E23)', '(@Controls.LoadLegacyPackedBlock.SectorCount + 1)')
    if (region, address) == ('Controls', 0xDADE):
        return operation.replace('(#5E33)', '(@Controls.LoadLegacyPackedBlock.RestoreStack + 1)')
    if region != 'Controls' or address not in FUNCTIONS:
        return operation
    replacements = {
        '#AB23': '@Action.UnpackResource.Entry', '#DD87': '@Controls.ResetFlightContext.Entry',
        '#FFFD': '@Hardware.AySelect', '#3D2F': '@TrDosLegacy.RomReturn',
        '#2A53': '@TrDosLegacy.PortOutput', '#2F55': '@TrDosLegacy.SeekInitial',
        '#2F59': '@TrDosLegacy.WaitReady', '#3FE5': '@TrDosLegacy.ReceiveSector',
        '#2740': '@TrDosLegacy.ReadStatus', '#5D16': '@TrDosLegacy.DriveConfig',
        '#5CD8': '@TrDosLegacy.ReadContext', '#5CCD': '@TrDosLegacy.SavedStatus',
        'LD C, #7F': 'LD C, @TrDosLegacy.DataPort', 'LD C, #FF': 'LD C, @TrDosLegacy.DrivePort',
        'LD C, #3F': 'LD C, @TrDosLegacy.TrackPort', 'LD C, #5F': 'LD C, @TrDosLegacy.SectorPort',
        'LD C, #1F': 'LD C, @TrDosLegacy.CommandPort',
    }
    replacements.update({'#' + format(target, '04X'): '@Controls.' + name + '.Entry'
                         for target, (name, _) in FUNCTIONS.items()})
    replacements.update({'#' + format(target, '04X'): '@Controls.' + FUNCTIONS[address][0] + '.' + name
                         for target, name in LOCAL.items()})
    for before, after in replacements.items():
        operation = operation.replace(before, after)
    return operation


def prepare(pending, symbols, root):
    import json
    from SourcePresentation import format_function

    reports = root / 'Tools/Disasm/Reports'
    sectors = json.loads((reports / 'ControlsLegacySectorReadVerification.json').read_bytes())
    assert sectors['passed'] and sectors['total_cases'] == 16
    const = root / 'Includes/Const/Include.inc'
    text = const.read_text('utf-8')
    assert text.count('                endif') == 1
    lines = ['                module TrDosLegacy']
    for name, value, note in (
        ('RomReturn', 0x3D2F, 'вход NOP и RET после выбора дисковой ROM'),
        ('PortOutput', 0x2A53, 'внутренний OUT (C), A с обычным RET'),
        ('SeekInitial', 0x2F55, 'выдача начальной команды позиционирования и ожидание'),
        ('WaitReady', 0x2F59, 'ожидание готовности и программная задержка'),
        ('ReceiveSector', 0x3FE5, 'внутренний приём данных через INI'),
        ('ReadStatus', 0x2740, 'получение статуса и исходная подготовка после чтения'),
        ('DriveConfig', 0x5D16, 'системный байт, из которого берутся разряды команды порта FF'),
        ('ReadContext', 0x5CD8, 'ненулевой код для раннего выхода из проверки трека по 207D'),
        ('SavedStatus', 0x5CCD, 'прочитанный статус, сохраняемый внутренним входом ROM'),
        ('DataPort', 0x7F, 'младший байт порта данных'),
        ('DrivePort', 0xFF, 'младший байт порта выбора стороны и диска'),
        ('TrackPort', 0x3F, 'младший байт порта физического трека'),
        ('SectorPort', 0x5F, 'младший байт порта сектора'),
        ('CommandPort', 0x1F, 'младший байт порта команды и статуса'),
    ):
        lines.append((name.ljust(16) + f'equ #{value:04X}').ljust(80) + '; ' + note)
        symbols['TrDosLegacy.' + name] = value
    lines.extend(('                endmodule', ''))
    pending[const] = text.replace('                endif', '\n'.join(lines) + '\n                endif').encode('utf-8')

    path = root / 'Source/Controls/RunTemporaryModule.asm'
    text = path.read_text('utf-8')
    before = '                LD (#5E33), SP'
    assert text.count(before) == 1
    pending[path] = text.replace(before, '                LD (@Controls.LoadLegacyPackedBlock.RestoreStack + 1), SP').encode('utf-8')
    path = reports / 'ModifiedCode.json'
    rows = json.loads(pending[path])
    assert not any(row['region'] == 'Controls' and row['writer'] == 0xDAE0 for row in rows)
    rows.append(dict(region='Controls', writer=0xDAE0, target=0x5E33, size=2, target_instruction=0x5E32,
                     target_operation='LD SP,#0000', path='Source/Controls/RunTemporaryModule.asm',
                     target_path='Source/Controls/LoadLegacyPackedBlock.asm', target_region='Controls',
                     target_slot=23, target_offset=0x93))
    rows.sort(key=lambda row: (row['region'], row['writer'], row['target']))
    pending[path] = (json.dumps(rows, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    path = root / 'Tools/Disasm/Research/Analyze.py'
    text = path.read_text('utf-8')
    before = 'BLOCKS = [\n'
    assert text.count(before) == 1
    pending[path] = text.replace(before, before + (
        '    # Согласованные адреса старого блока, реальная игровая релокация не доказана.\n'
        '    block(23, 0x7F, 0xBC, 0x5E1F, "Controls", (0x5E1F, 0x5E4D, 0x5ED2, 0x5ED6)),\n'
    )).encode('utf-8')
    path = reports / 'ControlFlow.json'
    flow = json.loads(pending[path])
    group = next(row for row in flow if row['name'] == 'Controls')
    group['blocks'].append(dict(slot=23, offset=0x7F, length=0xBC, origin=0x5E1F,
                                name='Controls', roots=list(FUNCTIONS)))
    pending[path] = (json.dumps(flow, ensure_ascii=False, indent=2) + '\n').encode('utf-8')

    path = root / 'Source/Controls/WriteLegacyDiskPort.asm'
    pending[path] = format_function(pending[path].decode('utf-8'), {
        'region': 'Controls', 'name': 'CallLegacyDosRom', 'path': 'Source/Controls/CallLegacyDosRom.asm',
    }).encode('utf-8')
    path = root / 'Source/Files/23_CONTROL.inc'
    text = pending[path].decode('utf-8')
    for index, name in enumerate(('WriteLegacyDiskPort', 'CallLegacyDosRom')):
        before = f'include "../Controls/{name}.asm"'
        assert text.count(before) == 1
        text = text.replace(before, before.ljust(64) + f'; ({index}) жёсткий порядок, последовательное исполнение')
    pending[path] = text.encode('utf-8')
