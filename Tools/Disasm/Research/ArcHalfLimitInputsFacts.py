"""Подготовка C' и E' из полуширины окна карты и начальной строки."""

TAG = 'ArcHalfLimitInputs'
TITLE = 'подготовка альтернативных счётчиков дуги от полуширины окна'
REGION = 'Map'
SLOT = 7
LOCATION = 'образ KARTA по C000'
CASES = 65536
KEYS = {}
FUNCTIONS = {0xE289: ('LoadHalfLimitArcInputs', 'Загрузка смещений и разности полуширины окна для счётчиков дуги')}
ENDS = {0xE289: 0xE299}
LOCAL = {}
MUTATIONS = ()

CONTRACTS = {('Map', 0xE289): (
    ['MapArcState.OffsetX, OffsetY, HalfXLimit и StartY читаемы, на стеке внешний возврат'],
    ['HL, DE сохранены, BC содержит B=OffsetX и C=OffsetY',
     'AF содержит A=StartY и F от вычитания HalfXLimit минус OffsetX',
     "E' содержит StartY, C' содержит разность по модулю 256",
     'SP увеличен на два, R получает десять M1, записей в RAM нет'],
    ["BC, AF, E', C', R"],
    ['остальные альтернативные и индексные регистры, I, IM и IFF сохранены',
     'арифметика байтовая, Carry от вычитания сохраняется при чтении StartY',
     'проверены все 65536 пары аргументов, вызывающая цепочка пока не установлена'],
)}

COMMENTS = {
    0xE289: (['Загрузка смещений без изменения HL и DE.'], None),
    0xE28D: (['Расчёт разности полуширины окна и горизонтального смещения.'], None),
    0xE291: (['Подготовка начального горизонтального счётчика в альтернативном C.'], None),
    0xE293: (['Загрузка начальной строки в альтернативный E с сохранением флагов вычитания.'], None),
}


def file_offset(address):
    return address - 0xC000


def name_operands(region, address, operation):
    if (region, address) not in CONTRACTS:
        return operation
    return (operation.replace('#DFAF', '@MapArcState.OffsetY')
            .replace('#DFC1', '@MapArcState.HalfXLimit')
            .replace('#DFB3', '@MapArcState.StartY'))
