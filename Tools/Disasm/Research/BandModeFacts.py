"""Два исходных режима шести изменяемых операндов полосовой рамки."""

FUNCTIONS = {
    0xCCAF: ("SetBandFillMode", "Настройка заполненного либо обычного режима полосовой рамки по биту 0 FillMode"),
    0xCCD4: ("ResetBandMode", "Восстановление шести исходных операндов обычной полосовой рамки"),
}
DOCUMENTS = {("Station", address): ("StationSpans", "самомодификация режима полосовой рамки") for address in FUNCTIONS}
CONTRACTS = {
    ("Station", 0xCCAF): (
        ["AF - входной Carry участвует в старшем бите результата A, S, Z, PV сохраняются",
         "StationRaster.FillMode - бит 0 выбирает обычный режим при единице, заполненный при нуле",
         "код станционной страницы и шесть изменяемых операндов доступны для записи"],
        ["HL и BC сохранены, DE=#C1ED при обычном режиме, иначе DE=#C1CF",
         "AF - A=(FillMode SHR 1) OR (входной Carry SHL 7), Carry=исходный бит 0 FillMode",
         "F имеет S, Z, PV входного F, биты 5 и 3 от выходного A, H=N=0",
         "шесть операндов переведены в выбранный режим, сам FillMode и текущий BandPattern не меняются"],
        ["DE, AF"],
        ["альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается",
         "SetBandFillMode при бите 0 FillMode переходит в ResetBandMode, дополнительного CALL не создаёт",
         "восстановление всегда задаёт исходный режим, не сохраняет произвольные прежние цели",
         "эффект относится к последующим DrawBandFrame, рамка и пиксели здесь не рисуются"]),
    ("Station", 0xCCD4): (
        ["шесть слов StationRaster для обычной полосовой рамки доступны для записи"],
        ["HL и BC сохранены, DE=#C1ED, AF сохранён побитно",
         "шесть операндов восстановлены, StationRaster.FillMode и BandPattern не меняются"],
        ["DE"],
        ["альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается",
         "восстанавливается фиксированный обычный набор, прежние значения не читаются",
         "режим нужен последующим рисователям, текущие пиксели не меняются"]),
}
MODE_NOTES = [
    "шесть изменяемых операндов имеют обычный набор ResetBandMode либо заполненный набор SetBandFillMode",
    "в заполненном режиме строки 3..10 всегда SetCutoutPattern, строки 12 и 13..15 и середина также заполнены",
    "нижнее знакоместо заполненного режима содержит пять строк SetCutoutPattern, одну фиксированную SetOutlinePattern, SetSixBitPattern и ClearSpanPattern",
    "строки 2,11 и третья снизу сохраняют обычный боковой узор, их фиксированные вызовы не подменяются",
]
COMMENTS = {
    0xCCAF: (["выбор обычного установщика для строки 11 перед чтением режима заливки"], None),
    0xCCB2: (["проверка бита 0 FillMode с сохранением остальных разрядов в результате RRA"], None),
    0xCCB6: ([], "переход, если бит 0 FillMode установлен, восстановить обычный режим рамки"),
    0xCCB8: (["сохранение обычной боковой линии 11 и выбор заполненного узора для остальных изменяемых участков"], None),
    0xCCD4: (["восстановление обычных боковых узоров в шести исходных операндах"], None),
    0xCCE7: (["восстановление нулевых разделителей строки 12 и начала нижнего знакоместа"], None),
    0xC094: (["выбор установщика верхней полосы из изменяемого слова StationRaster.BandDefault"], None),
    0xC0F1: (["выбор текущего установщика строки 11 через изменяемый операнд BandLine11"], None),
    0xC0F7: (["выбор разделителя строки 12 через BandLine12, обычный режим очищает его, заполненный рисует SetCutoutPattern"], None),
    0xC0FE: (["выбор бокового узора после разделителя через изменяемый операнд BandSides"], None),
    0xC13D: (["выбор первой строки нижнего знакоместа через BandBottom0"], None),
    0xC143: (["выбор узора следующих четырёх строк нижнего знакоместа через BandBottom1"], None),
    0xC152: (["возврат к фиксированному обычному контуру перед нижней фаской, даже в заполненном режиме"], None),
}
FIELDS = {0xC095: "BandDefault", 0xC0F2: "BandLine11", 0xC0F8: "BandLine12",
          0xC0FF: "BandSides", 0xC13E: "BandBottom0", 0xC144: "BandBottom1"}


def name_operands(region, address, operation):
    if region != "Station":
        return operation
    for value, name in FIELDS.items():
        operation = operation.replace(f"(#{value:04X})", "(@StationRaster."+name+")")
    if address in FUNCTIONS:
        operation = operation.replace("(#99B4)", "(@StationRaster.FillMode)")
        for value, name in ((0xC1C0, "SetOutlinePattern"), (0xC1CF, "SetCutoutPattern"), (0xC1ED, "ClearSpanPattern")):
            operation = operation.replace(f"LD DE, #{value:04X}", "LD DE, @Station."+name+".Entry")
    return operation
