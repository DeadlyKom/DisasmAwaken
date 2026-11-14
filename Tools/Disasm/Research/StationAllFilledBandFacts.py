"""Вход в общий выбор режима с заполненной одиннадцатой строкой рамки."""

TAG = 'StationAllFilledBand'
TITLE = 'заполненная одиннадцатая строка полосовой рамки'
PROOF = 'BandModeVerification'
REGION = 'Station'
SLOT = 4
LOCATION = 'станционный банк 0'
CASES = 196608
KEYS = {}
FUNCTIONS = {0xCCAA: ('SetAllFilledBandMode', 'Настройка заполненной рамки с заполнением одиннадцатой строки')}
ENDS = {0xCCAA: 0xCCAF}
LOCAL = {}
MUTATIONS = ()

CONTRACTS = {('Station', 0xCCAA): (
    ['AF задаёт входной Carry, бит 0 StationRaster.FillMode выбирает обычный режим при единице',
     'выбран банк станции 0, шесть операндов установки узора доступны для записи, на стеке возврат'],
    ['HL сохранён, DE=#C1ED при обычном режиме либо #C1CF при заполненном, BC сохранён',
         'A равен FillMode SHR 1 с входным Carry в разряде 7, F соответствует RRA',
         "HL', DE', BC', AF', IX, IY, I, IM и IFF сохранены",
         'при заполнении все шесть операндов получают SetCutoutPattern, при единице восстанавливается обычный набор',
         'без IRQ R получает 20 M1 при обычном режиме либо 19 при заполненном с сохранением бита 7, SP увеличен на два, пиксели будут изменены последующим рисователем'],
    ['DE, AF, R и шесть операндов полосовой рамки'],
    ['общий вход ReadFillMode пропускает загрузку SetOutlinePattern в DE',
     'штатный вызов CCAA пока не установлен'],
)}

COMMENTS = {
    0xCCAA: (['Выбор заполненного узора для одиннадцатой строки рамки.'], None),
    0xCCAD: (['Передача выбранного узора общей проверке режима.'], None),
}


def file_offset(address):
    return address - 0x6000


def name_operands(region, address, operation):
    if (region, address) not in CONTRACTS:
        return operation
    return (operation.replace('#C1CF', '@Station.SetCutoutPattern.Entry')
            .replace('#CCB2', '@Station.SetBandFillMode.ReadFillMode'))


def prepare(pending, symbols, root):
    name = 'Station.SetBandFillMode.ReadFillMode'
    assert name not in symbols
    symbols[name] = 0xCCB2
    path = root / 'Source/Station/SetBandFillMode.asm'
    text = path.read_text('utf-8')
    source = '                LD A, (@StationRaster.FillMode)\n'
    assert text.count(source) == 1
    text = text.replace(source, 'ReadFillMode:   LD A, (@StationRaster.FillMode)\n')
    text = text.replace('сохранение обычной боковой линии 11', 'сохранение выбранного узора строки 11')
    pending[path] = text.encode('utf-8')
