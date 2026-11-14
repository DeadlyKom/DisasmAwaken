"""Временная подмена вызова регистрации в центрируемом рисователе."""

TAG = 'DrawCenteredWithoutOwner'
TITLE = 'центрируемый элемент без записи в карту владельцев'
REGION = 'Station'
SLOT = 4
LOCATION = 'станционный банк 0'
CASES = 5172
KEYS = {}
FUNCTIONS = {0xC2CB: ('DrawCenteredWithoutOwner', 'Рисование центрируемого элемента без регистрации в карте владельцев')}
ENDS = {0xC2CB: 0xC2DF}
LOCAL = {0xC2DE: 'Return'}
MUTATION_TARGET_REGION = 'Station'
MUTATIONS = (
    (0xC2CF, 0xC2F9, 2, 0xC2F8, 'Source/Station/DrawCenteredItem.asm'),
    (0xC2DA, 0xC2F9, 2, 0xC2F8, 'Source/Station/DrawCenteredItem.asm'),
)

CONTRACTS = {('Station', 0xC2CB): (
    ['HL индекс элемента, остальные требования к рамке, тексту и стеку по DrawCenteredItem',
     'банк 0 выбран, операнд CenteredItemDrawState.RegisterTarget доступен для записи, IRQ не вмешивается'],
    ['HL, DE, BC сохранены, AF содержит A=C3 и F последнего текстового прохода',
     'рамка и текст записаны в bitmap, таблица индексов и карта владельцев сохранены',
     'RegisterTarget восстановлен на RegisterItemCells.Entry, SP увеличен на два'],
    ["AF, HL' в части L', AF', R, CenteredItemDrawState.RegisterTarget, TextWindow, bitmap, текстовые и растровые операнды, временные слова CPU-стека"],
    ['временная цель RegisterTarget указывает на собственный RET, реальный CALL сохраняет слово C2FB',
     'после возврата записывается постоянная цель BEAE, прежнее произвольное слово теряется',
     'при рисовании доступен весь текстовый договор DrawCenteredItem, регистрация и освобождение старой записи пропущены',
     'штатный вызов C2CB не установлен'],
)}

COMMENTS = {
    0xC2CB: (['Сохранение индекса элемента перед отключением регистрации.'], None),
    0xC2CC: (['Подмена цели регистрации адресом собственного RET.'], None),
    0xC2D2: (['Восстановление индекса и рисование рамки с текстом.'], None),
    0xC2D6: (['Сохранение возвращённого HL и восстановление постоянной цели регистрации.'], None),
    0xC2DD: (['Восстановление HL и общий выход, этот RET служит также пустой целью регистрации.'], None),
}


def file_offset(address):
    return address - 0x6000


def name_operands(region, address, operation):
    if (region, address) not in CONTRACTS:
        return operation
    return (operation.replace('#C2DE', '@Station.DrawCenteredWithoutOwner.Return')
            .replace('#C2F9', '@CenteredItemDrawState.RegisterTarget')
            .replace('#C2DF', '@Station.DrawCenteredItem.Entry')
            .replace('#BEAE', '@Station.RegisterItemCells.Entry'))


def prepare(pending, symbols, root):
    assert 'Station.DrawCenteredItem.RegisterCall' not in symbols
    assert 'CenteredItemDrawState.RegisterTarget' not in symbols
    symbols.update({'Station.DrawCenteredItem.RegisterCall': 0xC2F8,
                    'CenteredItemDrawState.RegisterTarget': 0xC2F9})

    path = root / 'Source/Station/DrawCenteredItem.asm'
    source = path.read_text('utf-8')
    instruction = '                CALL @Station.RegisterItemCells.Entry\n'
    assert source.count(instruction) == 1
    pending[path] = source.replace(instruction, 'RegisterCall:   CALL @Station.RegisterItemCells.Entry\n').encode('utf-8')

    path = root / 'Includes/Variables/Include.inc'
    source = path.read_text('utf-8')
    before = '                module EquipmentListText\n'
    block = ('                module CenteredItemDrawState\n'
             + 'RegisterTarget  equ #C2F9'.ljust(80)
             + '; операнд вызова регистрации, временно указывает на пустой RET\n'
             + '                assert RegisterTarget == @Station.DrawCenteredItem.RegisterCall + 1\n'
             + '                endmodule\n\n')
    assert source.count(before) == 1
    pending[path] = source.replace(before, block + before).encode('utf-8')
