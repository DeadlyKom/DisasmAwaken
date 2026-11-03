"""Доказанный выбор значения и адреса изменяемого байта, игровой смысл пары остаётся открытым."""
FUNCTIONS={0x74FB:('SelectPreferredByte','Выбор ненулевого предпочтительного байта либо запасного значения с возвратом адреса выбранного поля')}
LOCAL={}
LABELS={}
RENAMES={'Action.Unknown74FB.Entry':'Action.SelectPreferredByte.Entry'}
CONTINUATIONS={}
LOCATION={0x74FB:'банк 5, перенесённое ядро ACTION #6000..#7F8E'}
CONTRACTS={('Action',0x74FB):(
    ['HL, DE, BC и AF исходных числовых аргументов не задают',
     'физическая ActionPreferredByteState.Value содержит Preferred и Fallback в текущем контексте ACTION',
     'внешний адрес возврата доступен на CPU-стеке, IRQ не вмешиваются'],
    ['HL указывает на Preferred при его ненулевом значении, иначе на Fallback',
     'DE и BC сохраняются, A содержит выбранный байт',
     'F соответствует AND Preferred, на запасном пути F=54 независимо от возвращённого Fallback',
     "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются",
     'SP=входной SP+2, R увеличивается на 4 M1 на предпочтительном пути или на 7 M1 на запасном'],
    ['HL, AF, R'],
    ['Carry всегда сброшен, Z показывает нулевой Preferred, а не обязательно нулевой выходной A',
     'код не изменяет RAM и CPU-стек, вызывающий может изменить выбранное поле через возвращённый HL',
     'полный перебор всех 65536 пар Preferred и Fallback проверен на исходных байтах перенесённого ядра',
     'игровое название двух значений не установлено, локальные имена описывают доказанный порядок выбора'])}
COMMENTS={
    0x74FB:(['Выбор физического предпочтительного поля в загруженном состоянии ACTION.'],None),
    0x74FF:(['Проверка нулевого предпочтительного значения, флаги этой проверки сохраняются и на запасном пути.'],None),
    0x7500:([],'выход, если Preferred ненулевой, A и HL уже задают выбранное поле'),
    0x7501:(['Выбор запасного поля вместе с его адресом, флаги AND Preferred остаются неизменными.'],None),
}


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0x74FB:
        operation=operation.replace('LD HL, #9C10','LD HL, @ActionPreferredByteState.Value.Preferred')
    return operation
