"""Прямое применение пятнадцатибайтового набора, игровые имена полей не выдумываются."""
FUNCTIONS = {0xAC5D: ('ApplyParameterSet','Применение пятнадцати полей набора к исходным адресам ACTION, поле 1 читается без записи, поле 6 используется дважды')}
LOCATION = {0xAC5D:'общий код фиксированного банка 2, верхнее окно банка 0'}
LOCAL = {}
LABELS = {}
CONTINUATIONS = {}
RENAMES = {'Action.UnknownAC5D.Entry':'Action.ApplyParameterSet.Entry'}
TARGETS = (
    ('Link1ABaseLimit',0xF79C,'поле 00, базовый порог связи 1A при сброшенном бите 3 LinkFlags'),
    ('OtherLinkLimit',0xF798,'поле 02, порог для LinkedIndex, отличного от 1A'),
    ('RegenPhaseStep',0xA968,'поле 03, шаг фазы восстановления первой шкалы'),
    ('PairedLineStep',0x63B9,'поле 04, шаг фазового допуска RequestPairedAimLines'),
    ('ThirdGaugeStep',0xA8B5,'поле 05, шаг фазы повышения третьей шкалы'),
    ('SpawnLowLimit',0x7B6B,'поле 06, начальный порог младшего байта потока 0 в ScheduleSpawn'),
    ('SpawnBiasBase',0x6874,'поле 06, база последующего пересчёта SpawnLowLimit в UpdateBodyMotion'),
    ('Class0RLimit',0x6615,'поле 07, изменяемый операнд CP аппаратного R в ConfigureClass0Link'),
    ('RandomLowLimit',0xE6E7,'поле 08, изменяемый операнд CP младшего байта Stream10 в FindFilteredRecordOr26'),
    ('LinkedRLimit',0xE823,'поле 09, порог R обратной связи в CheckAndToggleLinkedOverlay'),
    ('Class3RLimit',0x65E5,'поле 0A, изменяемый операнд CP аппаратного R в ConfigureClass3Link'),
    ('SavedLowLimit',0x79A4,'поле 0B, нижний предел младшего байта сохранённого слова с верхним байтом 23'),
    ('SpawnValueMask',0x7E07,'поле 0C, маска OR кандидата Unknown13 в обоих создателях'),
    ('SpawnValueCap',0x7E09,'поле 0D, исключённый верхний предел Unknown13, ноль даёт FF'),
    ('SpawnField11',0x7DE4,'поле 0E, значение Unknown11 после непересекающихся случайных масок'),
)
CONTRACTS = {('Action',0xAC5D):(
    ['HL, DE, BC и AF входных аргументов не задают, последовательные поля 00..0E читаются из Parameters по 9BA4',
     'перед входом выбран верхний банк 0, общий код ACTION перенесён в 6000, все перечисленные целевые адреса доступны для записи',
     'на CPU-стеке внешний возврат, дополнительная рамка не требуется, IRQ не вмешиваются'],
    ['HL=9BB2, DE и BC сохраняются, A=поле 0E, F сохраняется буквально',
     'выполнены 15 записей по таблице маршрутов, поле 01 только прочитано, поле 06 записано в две разные цели',
     "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2, R получает 46 M1"],
    ['HL, AF в части A, пятнадцать целевых байтов, R'],
    ['исходный набор читается в фиксированном порядке, указатель HL продвигается только четырнадцать раз',
     'поля 04 и 09 задают PairedLineStep фазового допуска и LinkedRLimit обратной связи, их потребители установлены',
     'все пятнадцать целей являются доказанными непосредственными операндами исходных инструкций ACTION',
     'игровые имена полей и поведение всех изменяемых процедур ещё не установлены, гарантируется точная маршрутизация байтов'])}
COMMENTS = {
    0xAC5D: (['выбор пятнадцатибайтового набора, подготовленного BuildParameterTables'],None),
    0xAC60: (['обновление базового порога Link1ABaseLimit для связи 1A при сброшенном бите 3'],None),
    0xAC65: (['чтение поля 01 сохранено, следующий LD A, (HL) заменяет его без использования'],None),
    0xAC67: (['обновление порога OtherLinkLimit для индекса связи, отличного от 1A'],None),
    0xAC6C: (['применение поля 03 к аддитивному операнду общего кода'],None),
    0xAC71: (['обновление PairedLineStep фазового допуска двух линий прицела'],None),
    0xAC76: (['применение поля 05 ко второму аддитивному операнду общего кода'],None),
    0xAC7B: (['применение одного поля 06 к порогу SpawnLowLimit и аддитивному операнду SpawnBiasBase'],None),
    0xAC83: (['обновление операнда Class0RLimit, порога аппаратного R для класса 0'],None),
    0xAC88: (['обновление операнда RandomLowLimit, порога младшего байта Stream10 в банке 0'],None),
    0xAC8D: (['обновление порога R обратной связи CheckAndToggleLinkedOverlay в банке 0'],None),
    0xAC92: (['обновление операнда Class3RLimit, порога аппаратного R для класса 3'],None),
    0xAC97: (['применение поля 0B к порогу SavedLowLimit'],None),
    0xAC9C: (['применение поля 0C к маске SpawnValueMask'],None),
    0xACA1: (['применение поля 0D к операнду SpawnValueCap'],None),
    0xACA6: (['применение поля 0E к маске SpawnField11, это же значение остаётся в A'],None),
}


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0xAC5D:
        operation = operation.replace('#9BA4','@ControlsParameterTablesState.Parameters')
        for name,address,_ in TARGETS:
            operation = operation.replace('(#'+format(address,'04X')+')','(@ActionApplyParametersState.'+name+')')
    return operation


def qualify_mutations(mutations,regions,functions):
    """Уточнение только десяти доказанных операндов, неизвестные цели не превращаются в код."""
    action = next(region for region in regions if region['name']=='Action')
    known = {address for name,address,_ in TARGETS if not name.startswith('Unknown')}
    matched = set()
    for item in mutations:
        if item['region']!='Action' or not 0xAC5D<=item['writer']<0xACAB:
            continue
        assert item['target'] in known
        target = next(i for i in action['instructions'] if i['address']==item['target_instruction'])
        assert item['target_operation']==target['operation'] and item['target']==target['address']+1
        owner = next(f for f in functions if f['region']=='Action'
            and f['address']<=target['address']<f['address']+f['end_offset']-f['offset'])
        item.update(writer_bank=2,target_bank=5 if item['target']<0x8000 else 2 if item['target']<0xC000 else 0,
            target_region='Action',target_slot=17,target_offset=target['offset']+1,target_path=owner['path'])
        matched.add(item['target'])
    assert matched==known
