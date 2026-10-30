"""Подтверждённые варианты XOR-глифа, разделённые по сдвигу и правому краю.

Использование этих фактов при выпуске требует полной разметки из
GlyphRenderVerification.json. Этот модуль сам ничего не записывает.
"""

# shift, edge, восемь строк, префикс до границы знакоместа, байтов в одной развёрнутой строке.
KERNELS = (
    (0, False, 0xAF0C, 0xAF36, 5),
    (1, False, 0xAF67, 0xAFE0, 15), (1, True, 0xB057, 0xB089, 6),
    (2, False, 0xB0C1, 0xB152, 18), (2, True, 0xB1DE, 0xB220, 8),
    (3, False, 0xB266, 0xB30F, 21), (3, True, 0xB3B0, 0xB402, 10),
    (4, False, 0xB456, 0xB521, 24), (4, True, 0xB5D7, 0xB631, 11),
    (5, False, 0xB68C, 0xB735, 21), (5, True, 0xB7D6, 0xB828, 10),
    (6, False, 0xB87C, 0xB90D, 18), (6, True, 0xB999, 0xB9E3, 9),
    (7, False, 0xBA30, 0xBAA9, 15), (7, True, 0xBB20, 0xBB62, 8),
)

FUNCTIONS = {
    0xAE55: ("AdvanceTextRow", "Продвижение относительного текстового курсора на восемь пикселей с байтовым переполнением"),
    0xAE6B: ("GlyphHeightError", "Возврат кода 2 при достижении относительной высоты текстового окна"),
    0xAE71: ("GlyphWidthError", "Возврат кода 3 при переполнении или достижении относительной ширины окна"),
    0xAE77: ("GlyphOriginXError", "Обработка ненулевого старшего байта физического начала глифа по X"),
    0xAE7F: ("GlyphOriginYError", "Обработка ненулевого старшего байта физического начала глифа по Y"),
    0xAE88: ("GlyphBottomError", "Возврат кода 1 при верхней строке глифа не меньше 185"),
    0xAE8D: ("DrawGlyph", "Вывод восьмистрочного глифа через таблицу сдвигов и двухчастных переходов экранной раскладки"),
    0xB514: ("ReturnGlyph", "Общий успешный выход и восстановление сохранённого кадра регистров глифа"),
}
LABELS = {("Station", 0xB516): "Status"}
COMMENTS = {}
CONTRACTS = {}

for shift, edge, full, prefix, stride in KERNELS:
    variant = f"Edge{shift}" if edge else f"Shift{shift}"
    mode = f"сдвиг вправо на {shift} пикселей" + (", только крайний байт экрана" if edge else ", до двух соседних байтов")
    FUNCTIONS[full] = ("DrawGlyph" + variant, "XOR строк глифа, " + mode)
    FUNCTIONS[prefix] = ("SplitGlyph" + variant, "XOR префикса глифа до следующего знакоместа, " + mode)
    for row in range(1, 8):
        LABELS["Station", full + row*stride] = f"Rows{8-row}"
    for row in range(1, 7):
        LABELS["Station", prefix + row*stride] = f"Rows{7-row}"
    boundary = prefix + 7*stride
    LABELS["Station", boundary] = "WrapRow"
    LABELS["Station", boundary+10] = "NextPart"
    COMMENTS[full] = ([f"вывод восьми строк глифа, {mode}, дополнительные входы RowsN выводят последние N строк"], None)
    COMMENTS[prefix] = ([f"вывод семи строк до границы знакоместа, {mode}, RowsN сокращают префикс до N строк"], None)
    COMMENTS[boundary] = (["расчёт адреса следующей строки знакомест после завершения текущей восьмистрочной группы"], None)
    COMMENTS[boundary+4] = ([], "переход, если младший байт переполнился, старшая часть уже соответствует следующей трети экрана")
    COMMENTS[boundary+10] = (["возврат к табличному указателю второго слова и выбор оставшихся строк глифа"], None)
    for address, is_prefix in ((full, False), (prefix, True)):
        CONTRACTS["Station", address] = (
            ["HL - рабочий адрес экранной строки, DE - рабочий адрес строки глифа, Carry=0",
             "CPU-стек содержит FGlyphFrame, подготовленный DrawGlyph, обычный CALL с одним адресом возврата недопустим",
             "восемь строк либо RowsN должны соответствовать выбранному слову FGlyphRoute, правый край соответствует варианту процедуры"],
            ["выведенные пиксели объединены с bitmap через XOR, управление завершается общим ReturnGlyph",
             "AF=#0045, обычные и альтернативные регистры восстановлены из FGlyphFrame, SP увеличен на размер этого кадра"],
            ["HL, DE, BC, AF, HL', DE', BC', AF', относительно внутреннего входа заменяются сохранёнными значениями кадра"],
            [f"сдвиг по X равен {shift}, в каждой строке первый вклад равен байту глифа SHR {shift}",
             ("второй байт экрана не записывается, пиксели правее 255 отсекаются" if edge else
              "второй вклад равен младшим восьми битам байта глифа SHL (8-сдвиг), при нулевом сдвиге второй байт не требуется"),
             ("префикс завершает текущее знакоместо, корректирует HL и через второе слово FGlyphRoute передаёт управление остатку" if is_prefix else
              "Entry выводит восемь строк, вход RowsN начинает с нужного места развёрнутого блока и выводит N строк"),
             "индексные регистры, I и IFF сохраняются, атрибуты не записываются",
             "контракт относится к исходным XOR-инструкциям и кадру DrawGlyph, отдельного самостоятельного интерфейса здесь нет"])


CONTRACTS["Station", 0xAE55] = (
    ["TextWindow.CursorY и Height - байтовые пиксельные значения, CursorX - текущая относительная колонка"],
    ["BC - B высота окна, C=(прежний CursorY+8) по модулю 256",
     "при C<Height CursorY=C, CursorX=0, AF=#0044, иначе курсор сохранён, A=C и Carry установлен",
     "при отказе F имеет S, Z и PV от CP(C,Height), биты 5 и 3 от C, Carry=1, H=N=0"],
    ["BC, AF"],
    ["переполнение Y+8 не проверяется, например 250 переходит в 2 до сравнения высоты",
     "HL, DE, альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается",
     "пиксели не записываются, равенство C и Height является отказом"])

CONTRACTS["Station", 0xAE8D] = (
    ["AF - A восьмибитный код глифа, TextWindow задаёт относительный курсор, размеры и знаковое начало",
     "подготовлены исходные таблицы адресации и FGlyphRoute, стек имеет место для FGlyphFrame",
     "код по GlyphState.KernelPrefix содержит исходные #68,#48,#26 либо временный JP ReturnGlyph.Entry"],
    ["HL, DE, BC, альтернативные и индексные регистры сохраняются, AF содержит статус выбранного выхода",
     "при успехе A=0,F=#45, принятая ширина прибавлена к CursorX, CursorY сохранён",
     "отказы по высоте и ширине возвращают A=2 и A=3 без изменения курсора, флаги от AND проверенного значения",
     "отказы координат и нижней границы, отрицательное невидимое начало и режим без рисования описаны в Font.md"],
    ["AF"],
    ["ширина сравнивается строго, равенство следующего CursorX и Width является отказом",
     "CursorX обновляется до проверки физического начала, отрицательный старший байт начала пропускает глиф с успешным статусом",
     "неотрицательный ненулевой старший X возвращает A=0,F=#44, старший Y возвращает A=1,F=#00",
     "физический верхний Y не меньше 185 возвращает A=1 с флагами CP(Y,185), курсор уже продвинут",
     "при исходном коде пиксели объединяются XOR, крайняя колонка не записывает соседний байт, атрибуты сохраняются",
     "JP в KernelPrefix обходит только пиксельную часть, проверки и продвижение остаются, изменяемый DispatchTarget в этом режиме не записывается",
     "I и IFF сохраняются, SP восстанавливается, изменяемые операнды делают вход не реентерабельным"])

CONTRACTS["Station", 0xB514] = (
    ["SP - FGlyphFrame с сохранёнными регистрами и исходным адресом возврата",
     "Entry формирует успех, дополнительный вход Status принимает готовый AF статуса"],
    ["Entry возвращает A=0,F=#45, Status возвращает переданный AF",
     "HL, DE, BC и альтернативные регистры восстановлены из кадра, SP увеличен на #10 после RET"],
    ["HL, DE, BC, AF, HL', DE', BC', AF', относительно внутреннего входа восстановлены из кадра"],
    ["сначала возвращается альтернативный AF, затем альтернативные HL,BC,DE и основной набор через EXX",
     "IX, IY, I и IFF сохраняются, прямой CALL без кадра DrawGlyph недопустим"])

ERRORS = {
    0xAE6B: (["AF - A проверенная относительная строка"], "A=2, F от AND входного A"),
    0xAE71: (["AF - A проверенная байтовая сумма ширин"], "A=3, F от AND входного A"),
    0xAE77: (["AF - A ненулевой старший байт физического X"], "при отрицательном A успех #0045, иначе #0044"),
    0xAE7F: (["AF - A ненулевой старший байт физического Y"], "при отрицательном A успех #0045, иначе #0100"),
    0xAE88: (["AF - F от сравнения физического Y с 185"], "A=1, входной F сохраняется"),
}
for address, (inputs, result) in ERRORS.items():
    CONTRACTS["Station", address] = (
        [*inputs, "SP - FGlyphFrame, подготовленный DrawGlyph"],
        [result, "обычные и альтернативные регистры восстановлены общим выходом, SP увеличен на #10 после RET"],
        ["HL, DE, BC, AF, HL', DE', BC', AF', относительно внутреннего входа восстановлены из кадра"],
        ["общий выход использует ReturnGlyph.Status либо ReturnGlyph.Entry, дополнительный адрес возврата не создаётся",
         "IX, IY, I и IFF сохраняются, пиксели не записываются, самостоятельный CALL без кадра недопустим"])

DOCUMENTS = {("Station", address): "GlyphRendering.md" for address in FUNCTIONS}

LABELS.update({
    ("Station", 0xAEAA): "CheckHeight", ("Station", 0xAEB2): "CheckWidth",
    ("Station", 0xAEBA): "OriginX", ("Station", 0xAEBE): "OriginXHigh",
    ("Station", 0xAEC6): "OriginY", ("Station", 0xAECA): "OriginYHigh",
    ("Station", 0xAED1): "CheckBottom", ("Station", 0xAED5): "KernelPrefix",
    ("Station", 0xAEFF): "NextRoute", ("Station", 0xAF09): "Dispatch",
})
COMMENTS.update({
    0xAE55: (["чтение относительной вертикальной позиции текстового курсора"], None),
    0xAE58: (["расчёт следующей строки через восемь пикселей с исходным байтовым переполнением"], None),
    0xAE60: (["проверка строгой верхней границы относительного курсора"], None),
    0xAE62: ([], "выход, если новая относительная строка не меньше высоты окна, курсор сохраняется"),
    0xAE63: (["обновление принятой строки и возврат курсора к началу окна по X"], None),
    0xAE6B: (["подготовка флагов отказа по относительной высоте без изменения сохранённого кадра"], None),
    0xAE71: (["подготовка флагов отказа по байтовой сумме ширин"], None),
    0xAE77: (["проверка знака ненулевого старшего байта физического X"], None),
    0xAE78: ([], "переход, если физическое начало отрицательно по X, глиф пропускается с успешным статусом"),
    0xAE7B: (["выбор нулевого статуса без Carry для положительного выхода X за байтовую координату"], None),
    0xAE7F: (["проверка знака ненулевого старшего байта физического Y"], None),
    0xAE80: ([], "переход, если физическое начало отрицательно по Y, глиф пропускается с успешным статусом"),
    0xAE83: (["выбор кода 1 без Carry для положительного выхода Y за байтовую координату"], None),
    0xAE88: (["возврат кода нижней границы с сохранением флагов предшествующего CP"], None),
    0xAE8D: (["создание FGlyphFrame, сохраняются оба набора общих регистров и альтернативный AF"], None),
    0xAE98: (["подготовка адреса восьми строк глифа по восьмибитному коду символа"], None),
    0xAEA5: (["чтение относительных X и Y текстового курсора"], None),
    0xAEAA: (["проверка относительной строки до изменения курсора"], None),
    0xAEAC: ([], "переход, если относительный Y не меньше высоты окна, возвращается код 2"),
    0xAEAE: (["выбор ширины символа и расчёт следующей относительной позиции X"], None),
    0xAEB0: ([], "переход, если сумма ширины и CursorX переполнила байт, возвращается код 3"),
    0xAEB2: (["проверка строгой правой границы текстового окна"], None),
    0xAEB4: ([], "переход, если следующая позиция X не меньше ширины окна, возвращается код 3"),
    0xAEB7: (["обновление относительного курсора до проверки физического начала"], None),
    0xAEBA: (["расчёт физического X из исходного курсора и знакового начала окна"], None),
    0xAEC2: ([], "переход, если физический X не представим без ненулевого старшего байта"),
    0xAEC6: (["расчёт физического Y из относительной строки и знакового начала окна"], None),
    0xAECE: ([], "переход, если физический Y имеет ненулевой старший байт"),
    0xAED1: (["проверка, что все восемь строк глифа помещаются в видимые 192 строки"], None),
    0xAED3: ([], "переход, если верхняя физическая строка не меньше 185, возвращается код 1"),
    0xAED5: (["начало пиксельной части, временный JP ReturnGlyph.Entry позволяет только продвижение курсора"], None),
    0xAEFF: (["выбор очередного слова FGlyphRoute и запись цели общего изменяемого JP"], None),
    0xAF09: (["передача управления выбранному числу строк ядра сдвига"], None),
    0xB514: (["формирование успешного статуса после вывода либо допустимого пропуска глифа"], None),
    0xB516: (["восстановление обоих наборов общих регистров и альтернативного AF из FGlyphFrame"], None),
    0xB517: (["восстановление FGlyphFrame.SavedAFAlt перед возвратом статуса в основной AF"], None),
    0xB519: (["восстановление FGlyphFrame.SavedHLAlt, SavedBCAlt и SavedDEAlt"], None),
    0xB51D: (["восстановление FGlyphFrame.SavedHL, SavedBC и SavedDE после обмена наборов"], None),
    0xB520: (["возврат по FGlyphFrame.ReturnAddress, весь шестнадцатибайтовый кадр снят со стека"], None),
})


def name_operands(region, address, operation):
    if region != "Station":
        return operation
    if address == 0xAD35:
        operation = operation.replace("(#AED5)", "(@GlyphState.KernelPrefix)")
        operation = operation.replace("(#AED6)", "(@GlyphState.KernelPrefix + 1)")
        operation = operation.replace("LD DE, #B514", "LD DE, @Station.ReturnGlyph.Entry")
        operation = operation.replace("LD A, #C3", "LD A, @GlyphOpcode.SkipJump")
        operation = operation.replace("LD A, #68", "LD A, @GlyphOpcode.ResumeFirst")
        operation = operation.replace("LD DE, #2648", "LD DE, @GlyphOpcode.ResumePair")
    if address == 0xAE2A:
        operation = operation.replace("CP #03", "CP @GlyphStatus.Width")
    if address not in FUNCTIONS:
        return operation
    if address == 0xAE6B:
        operation = operation.replace("LD A, #02", "LD A, @GlyphStatus.Height")
    if address == 0xAE71:
        operation = operation.replace("LD A, #03", "LD A, @GlyphStatus.Width")
    if address == 0xAE88:
        operation = operation.replace("LD A, #01", "LD A, @GlyphStatus.Vertical")
    fields = {0x6320: "TextWindow.CursorX", 0x6321: "TextWindow.CursorY",
              0xAEAB: "TextWindow.Height", 0xAEB3: "TextWindow.Width",
              0xAF0A: "GlyphState.DispatchTarget"}
    for pointer, name in fields.items():
        operation = operation.replace(f"(#{pointer:04X})", "(@"+name+")")
    operation = operation.replace("LD H, #49", "LD H, @FontConst.RouteHalfPage")
    operation = operation.replace("LD H, #82", "LD H, @StationTables.RowHighPage")
    operation = operation.replace("CP #B9", "CP @FontConst.GlyphTopLimit")
    operation = operation.replace("AND #07", "AND @ScreenConst.PixelOffsetMask")
    operation = operation.replace("AND #1F", "AND @ScreenConst.ColumnMask")
    operation = operation.replace("ADD A, #20", "ADD A, @ScreenConst.ByteColumns")
    operation = operation.replace("SUB #08", "SUB @ScreenConst.PixelsPerChar")
    operation = operation.replace("ADD A, #08", "ADD A, @ScreenConst.PixelsPerChar")
    return operation


def verify_table(data):
    """Проверка всех исходных слов таблицы по размерам развёрнутых строк, не по похожести имён."""
    for shift, edge, y in product_routes():
        kernel = next(k for k in KERNELS if k[0] == shift and k[1] == (edge if shift else False))
        _, _, full, prefix, stride = kernel
        expected = (full, 0) if y == 0 else (prefix+(y-1)*stride, full+(8-y)*stride)
        index = (2*shift + int(edge))*8 + y
        actual = tuple(int.from_bytes(data[0x3200+4*index+offset:0x3202+4*index+offset], "little") for offset in (0, 2))
        if actual != expected:
            raise ValueError("Изменена таблица или не подтверждены размеры строк ядра глифа")


def product_routes():
    for shift in range(8):
        for edge in (False, True):
            for y in range(8):
                yield shift, edge, y
