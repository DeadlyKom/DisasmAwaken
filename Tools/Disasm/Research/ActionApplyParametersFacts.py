"""Прямое применение пятнадцатибайтового набора, игровые имена полей не выдумываются."""
FUNCTIONS = {0xAC5D: ('ApplyParameterSet','Применение пятнадцати полей набора к исходным адресам ACTION, поле 1 читается без записи, поле 6 используется дважды')}
LOCATION = {0xAC5D:'общий код фиксированного банка 2, верхнее окно банка 0'}
LOCAL = {}
LABELS = {}
CONTINUATIONS = {}
RENAMES = {'Action.UnknownAC5D.Entry':'Action.ApplyParameterSet.Entry'}
TARGETS = (
    ('CImmediate00',0xF79C,'поле 00, операнд LD C, n в верхнем банке 0'),
    ('CImmediate02',0xF798,'поле 02, соседний операнд LD C, n в верхнем банке 0'),
    ('AddImmediate03',0xA968,'поле 03, операнд ADD A, n в фиксированном банке 2'),
    ('Unknown04',0x63B9,'поле 04, целевой потребитель ещё не установлен'),
    ('AddImmediate05',0xA8B5,'поле 05, операнд ADD A, n в фиксированном банке 2'),
    ('Compare06A',0x7B6B,'поле 06, операнд CP n в фиксированном банке 5'),
    ('AddImmediate06B',0x6874,'поле 06, вторая цель, операнд ADD A, n в фиксированном банке 5'),
    ('Unknown07',0x6615,'поле 07, целевой потребитель ещё не установлен'),
    ('Unknown08',0xE6E7,'поле 08, целевой потребитель верхнего банка 0 ещё не установлен'),
    ('Unknown09',0xE823,'поле 09, целевой потребитель верхнего банка 0 ещё не установлен'),
    ('Unknown0A',0x65E5,'поле 0A, целевой потребитель ещё не установлен'),
    ('Compare0B',0x79A4,'поле 0B, операнд CP n в фиксированном банке 5'),
    ('OrImmediate0C',0x7E07,'поле 0C, операнд OR n в фиксированном банке 5'),
    ('HImmediate0D',0x7E09,'поле 0D, операнд LD H, n в фиксированном банке 5'),
    ('OrImmediate0E',0x7DE4,'поле 0E, операнд OR n в фиксированном банке 5'),
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
     'пять целей Unknown04, Unknown07, Unknown08, Unknown09 и Unknown0A пока не отнесены к доказанным инструкциям или полям данных',
     'десять остальных целей являются доказанными непосредственными операндами исходных инструкций ACTION',
     'игровые имена полей и поведение всех изменяемых процедур ещё не установлены, гарантируется точная маршрутизация байтов'])}
COMMENTS = {
    0xAC5D: (['выбор пятнадцатибайтового набора, подготовленного BuildParameterTables'],None),
    0xAC60: (['применение поля 00 к операнду CImmediate00 в верхнем банке 0'],None),
    0xAC65: (['чтение поля 01 сохранено, следующий LD A, (HL) заменяет его без использования'],None),
    0xAC67: (['применение поля 02 к соседнему операнду CImmediate02'],None),
    0xAC6C: (['применение поля 03 к аддитивному операнду общего кода'],None),
    0xAC71: (['обновление Unknown04, игровой потребитель этого байта ещё не установлен'],None),
    0xAC76: (['применение поля 05 ко второму аддитивному операнду общего кода'],None),
    0xAC7B: (['применение одного поля 06 к порогу Compare06A и аддитивному операнду AddImmediate06B'],None),
    0xAC83: (['обновление Unknown07, назначение целевого потребителя не объявляется доказанным'],None),
    0xAC88: (['обновление Unknown08 в выбранном верхнем банке 0'],None),
    0xAC8D: (['обновление Unknown09 в выбранном верхнем банке 0'],None),
    0xAC92: (['обновление Unknown0A, назначение целевого потребителя не объявляется доказанным'],None),
    0xAC97: (['применение поля 0B к порогу Compare0B'],None),
    0xAC9C: (['применение поля 0C к маске OrImmediate0C'],None),
    0xACA1: (['применение поля 0D к операнду HImmediate0D'],None),
    0xACA6: (['применение поля 0E к маске OrImmediate0E, это же значение остаётся в A'],None),
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
