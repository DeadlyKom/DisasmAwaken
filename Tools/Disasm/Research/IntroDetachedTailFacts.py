"""Три замкнутых последовательности в перенесённом хвосте AWAKEN.B."""

TAG = 'IntroDetachedTail'
TITLE = 'условные входы за концом экранного потока'
REGION = 'IntroUnpack'
SLOT = 3
LOCATION = 'перенос хвоста из 8F6B в 746B'
CASES = 287
KEYS = {}
FUNCTIONS = {
    0x74CD: ('WaitNonzeroKeyByte', 'Очистка и ожидание ненулевого байта по 5C08'),
    0x74D8: ('CopyScreenToBankWindow', 'Копирование экрана из 4000 в выбранное окно C000'),
    0x74E4: ('CopyScreenFromBankWindow', 'Копирование экрана из выбранного окна C000 в 4000'),
}
ENDS = {0x74CD: 0x74D8, 0x74D8: 0x74E4, 0x74E4: 0x74EC}
LOCAL = {0x74D1: 'PollKey', 0x74DE: 'CopyBlock'}
MUTATIONS = ()

CONTRACTS = {('IntroUnpack', 0x74CD): (
    ['KeyByte по 5C08 доступен, ROM при IM 1 может обновить LAST_K, на стеке возврат'],
    ['AF содержит ненулевой байт и флаги OR A, остальные рабочие регистры сохранены',
     'KeyByte очищен перед циклом, при прочитанном ненулевом значении SP увеличен на два'],
    ['AF, R, KeyByte'],
    ['нулевой LAST_K оставляет ожидание в PollKey, проверены писатели ROM 48K и 128K ROM 1 по 0308',
     'условный договор, обычный вызов из установленного кода вступления не найден'],
)}
for address, source, target in ((0x74D8, '4000', 'C000'), (0x74E4, 'C000', '4000')):
    CONTRACTS['IntroUnpack', address] = (
        [f'{source} читается, {target} доступен для записи, 7FFD выбирает окно C000, на стеке возврат'],
        ['HL и DE указывают за исходным и целевым экраном, BC обнулён, A сохранён',
         'F сохраняет S, Z и Carry, X/Y от A и последнего байта, H, N и P/V сброшены',
         'перенесены 6912 байтов, 7FFD сохранён, SP увеличен на два'],
        ['HL, DE, BC, F, R и 6912 байтов экрана назначения'],
        ['при выборе банка 5 обе области совпадают, исходный LDIR сохранён',
         'условный договор, обычный вызов из установленного кода вступления не найден'],
    )

COMMENTS = {
    0x74CD: (['Очистка старого байта до начала ожидания.'], None),
    0x74D1: (['Проверка появления нового ненулевого байта после очистки.'], None),
    0x74D5: ([], 'переход, если байт всё ещё нулевой, повторить чтение'),
    0x74D8: (['Выбор базового экрана как источника и верхнего окна как назначения.'], None),
    0x74DE: (['Копирование пикселей и атрибутов одного экрана в прямом порядке.'], None),
    0x74E4: (['Выбор верхнего окна как источника и базового экрана как назначения.'], None),
    0x74EA: (['Передача выбранных указателей общему копировщику с сохранением внешнего возврата.'], None),
}


def file_offset(address):
    return address - 0x4800


def name_operands(region, address, operation):
    if (region, address) not in CONTRACTS:
        return operation
    for value, name in ((0x5C08, 'IntroTailState.KeyByte'), (0x74D1, 'IntroUnpack.WaitNonzeroKeyByte.PollKey'),
                        (0x4000, 'ScreenUpdateConst.BaseScreen'), (0xC000, 'ScreenUpdateConst.BankWindow'),
                        (0x1B00, 'ScreenUpdateConst.ScreenBytes'), (0x74DE, 'IntroUnpack.CopyScreenToBankWindow.CopyBlock')):
        operation = operation.replace(f'#{value:04X}', '@' + name)
    return operation


def prepare(pending, symbols, root):
    alias = 'IntroTailState.KeyByte'
    assert alias not in symbols
    symbols[alias] = 0x5C08
    path = root / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    anchor = '                module EquipmentListText\n'
    block = ('                module IntroTailState\n'
             + 'KeyByte         equ #5C08'.ljust(80) + '; исходный байт ожидания после очистки\n'
             + '                endmodule\n\n')
    assert text.count(anchor) == 1
    pending[path] = text.replace(anchor, block + anchor).encode('utf-8')
