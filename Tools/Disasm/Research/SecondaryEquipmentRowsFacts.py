"""Смысл и исходные границы второго станционного списка по 735F..741D."""
import re


TAG = 'SecondaryEquipmentRows'
TITLE = 'второй список, общая печать, выбор и события LANG'
REGION = 'Station'
SLOT = 4
LOCATION = 'перенос STATIONF с 05CE в 6322'
CASES = 1292
KEYS = {}
MUTATION_TARGET_REGION = 'Station'
FUNCTIONS = {
    0x735F: ('ScrollSecondaryRows', 'Подготовка прокрутки второго списка и сохранение начального индекса'),
    0x7386: ('SelectSecondaryRow', 'Выбор описания либо отправка события 7 или 8 для второго списка'),
    0x73D7: ('TryDrawSecondaryList', 'Проверка текущего слова поиска рисователя второго списка'),
    0x73DE: ('DrawSecondaryList', 'Рамка, заголовки и счётчик строк второго списка оснащения'),
    0x7403: ('PrintSecondaryRows', 'Выбор пяти баз второго списка для общего печатателя'),
}
ENDS = dict(zip(FUNCTIONS, (*tuple(FUNCTIONS)[1:], 0x741E)))
CONTINUATIONS = {0x73D7: 0x73DE}
LOCAL = {
    0x737C: 'ReadTop',
    0x73B1: 'RepeatChoice',
    0x73BA: 'RunEvent',
    0x73FB: 'RenderRows',
    0x73FE: 'SaveRowCount',
}
MUTATIONS = (
    (0x736B, 0x73D8, 1, 0x73D7, 'Source/Station/TryDrawSecondaryList.asm'),
    (0x7371, 0xA265, 2, 0xA264, 'Source/Station/ScrollWindowRows.asm'),
    (0x7377, 0xA235, 2, 0xA234, 'Source/Station/ScrollWindowRows.asm'),
    (0x7382, 0x737D, 2, 0x737C, 'Source/Station/ScrollSecondaryRows.asm'),
    (0x739B, 0x6ACC, 1, 0x6ACB, 'Source/Station/UpdateEquipmentInfo.asm'),
    (0x73A1, 0x6AA4, 2, 0x6AA3, 'Source/Station/HandleEquipmentInfoAction.asm'),
    (0x73E9, 0x73D8, 1, 0x73D7, 'Source/Station/TryDrawSecondaryList.asm'),
    (0x73FF, 0x73D9, 1, 0x73D7, 'Source/Station/TryDrawSecondaryList.asm'),
)


def file_offset(address):
    return address - 0x5D54


CONTRACTS = {
    ('Station', 0x735F): (
        ['HL и BC контекст, IX выбранный элемент, окно и ввод по договорам XorRowIfSelected и ScrollWindowRows',
         'SecondaryEquipmentState.Row и RowCount задают исходное слово полосы, TopRow содержит полный индекс'],
        ['HL, DE, BC, AF и альтернативные пары по результату ScrollWindowRows',
         'Row=FF, RenderCall указывает на DrawSecondaryList.RenderRows, EndLimit=13, TopOffset=24',
         'TopRow обновлён полным возвращённым HL, обычный возврат увеличивает SP на два'],
        ['HL, DE, BC, AF, BC\', AF\', экран, прокрутка, указатель и контекст детей'],
        ['E исходной инверсии берётся из Row, а D из RowCount, подмена E значением 24 меняет оригинал',
         'входы с недостаточной высотой проверены до полного возврата, штатный вызов не установлен'],
    ),
    ('Station', 0x7386): (
        ['Row и TopRow читаются из существующих операндов, EquipmentInfoState.TextIndex доступен',
         'договоры BeginScreenUpdate, DrawItem00, обоих рисователей и EndScreenUpdate соблюдены',
         'для повторного выбора LANG загружен в банк 6, выбран станционный банк 0'],
        ['при Row=FF A=0 и F=50 OR входной Carry, прочие регистры и состояние сохранены',
         'индекс описания равен (Row+TopRow.low+30) AND FF',
         'при новом индексе TextIndex обновлён, TopRow описания обнулён, выполнена условная перерисовка',
         'при том же индексе EventCode=7 при нулевом режиме либо 8 иначе, LANG исполнен, банк 0 возвращён',
         'на обоих путях перерисовки конечные регистры по последнему EndScreenUpdate, обычный SP+2'],
        ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX по LANG, рисунок и рабочие операнды детей'],
        ['первые 30 индексов относятся к основной таблице описаний, дополнительный набор начинается с 30',
         'при смене индекса вызывается TryDrawSecondaryList, при повторении прямой DrawSecondaryList',
         '256 режимов проверены до входа LANG, три профиля исполнили LANG и настоящий полный хвост'],
    ),
    ('Station', 0x73D7): (
        ['HL, BC контекст, DrawListState.HeadOperand задаёт читаемый список',
         'DrawPointer читается как слово из операнда LD DE, его байты совпадают с Row и RowCount'],
        ['HL и BC сохранены, DE содержит прочитанный DrawPointer, AF по результату TestDrawPointer',
         'при Z=0 выполнен RET NZ, при Z=1 исполнение продолжается в DrawSecondaryList'],
        ['DE, AF на отказе, на продолжении действуют договоры рисователя'],
        ['начальное слово 73DE совпадает с DrawSecondaryList.Entry, после изменения строки и счётчика это может быть другой адрес',
         'проверяется точное слово, обратной нормализации после перерисовки нет'],
    ),
    ('Station', 0x73DE): (
        ['банк станции 0 выбран, начальный индекс элемента в операнде LD HL равен нулю',
         'текст, рамка, ключ и таблицы подготовлены согласно DrawCaptionItem, SetupEquipmentColumns и PrintSecondaryRows',
         'RenderRows принимает HL полный индекс, рамка и колонки уже подготовлены'],
        ['на прямом входе отрисована рамка, колонки настроены, Row=FF и напечатаны общие заголовки',
         'при Carry заголовков тело пропущено, RowCount=0, AF=0044, AF\' содержит статус заголовков',
         'иначе регистры по PrintSecondaryRows, AF содержит счётчик попыток, AF\' последний статус, RowCount=A',
         'RenderRows меняет счётчик и тело, но сам не обновляет Row, SP обычного возврата увеличен на два'],
        ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', экран, курсор, ключ и рабочие операнды детей'],
        ['оба входа приходят в общий SaveRowCount, попытка маркера 80 включена в счётчик',
         'модель прямого входа использует действительный IM2 при HALT рамки, вызывающий путь не установлен'],
    ),
    ('Station', 0x7403): (
        ['HL полный начальный индекс, CurrentModels.SkimmerIndex доступен',
         'договоры общей PrintEquipmentRows, окно, отступы и таблицы подготовлены'],
        ['результаты HL, DE, BC, AF и альтернативных пар по PrintEquipmentRows, но адреса относятся ко второму набору',
         'тело использует 98F6, 95D4, 9632, 9484 и F066, сохранён исходный общий кадр',
         'IX, IY, I, IM и IFF сохранены, SP обычного возврата увеличен на два, страница не меняется'],
        ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', курсор, bitmap и операнды печати'],
        ['первый CR по F066 выбирает строку топлива, следующий CR выбирает подписи доставки',
         'у строковых баз нет встроенной проверки индекса, модели больших индексов используют конечный подготовленный текст',
         'общий вход AtNameStream принимает DE индекс, HL текст и пять уже уложенных слов вместе с внешним возвратом'],
    ),
}


COMMENTS = {
    0x735F: (['чтение слова полосы из изменяемого операнда проверки рисователя'], None),
    0x7366: (['снятие прежней XOR-полосы при существующей строке'], None),
    0x7369: (['обновление выбора на FF перед прокруткой'], None),
    0x736E: (['настройка внутреннего рисователя принятого индекса'], None),
    0x7374: (['выбор верхнего индекса 13 для дополнительного набора'], None),
    0x737A: (['выбор отступа 24 и исходного полного индекса'], None),
    0x7382: (['обновление начальной строки полным результатом прокрутки'], None),
    0x7386: (['проверка FF отсутствующей выбранной строки'], None),
    0x738A: ([], 'выход, если строка отсутствует, сохранить контекст списка'),
    0x738B: (['расчёт общего индекса описания из строки, базы и смещения 30'], None),
    0x7394: (['проверка повторения прежнего индекса описания'], None),
    0x7398: ([], 'переход, если индекс уже выбран, вызвать событие LANG'),
    0x739A: (['обновление индекса описания и обнуление его прокрутки'], None),
    0x73A4: (['скрытое обновление описания и второго списка по наличию рисователей'], None),
    0x73AD: (['показ подготовленного экрана и возврат указателя'], None),
    0x73B1: (['проверка общего режима перед выбором события 7 или 8'], None),
    0x73B7: ([], 'переход, если режим нулевой, оставить событие 7'),
    0x73BA: (['обновление номера события и выбор банка LANG'], None),
    0x73C5: (['возврат банка станции после сценария'], None),
    0x73CA: (['скрытое обновление статуса и второго списка после сценария'], None),
    0x73D7: (['проверка точного текущего слова рисователя, операнд также хранит строку и счётчик'], None),
    0x73DD: ([], 'выход, если текущий указатель отсутствует в списке'),
    0x73DE: (['рисование рамки элемента и настройка числовых колонок'], None),
    0x73E7: (['обновление выбранной строки после рисования рамки'], None),
    0x73EC: (['вывод общих заголовков и проверка результата печати'], None),
    0x73F5: ([], 'переход, если печать заголовков вернула Carry, сохранить нулевой счётчик'),
    0x73F8: (['чтение начального индекса второго списка'], None),
    0x73FB: (['рисование строк с подготовленными параметрами окна'], None),
    0x73FE: (['обновление числа строк из альтернативного счётчика печатателя'], None),
    0x7403: (['сохранение полного индекса и выбор базы слов цен'], None),
    0x7408: (['чтение типа скимера для отметки отсутствующего типа'], None),
    0x740C: (['сохранение четырёхбайтовых наборов допустимых типов'], None),
    0x7410: (['сохранение базы пар порога и веса'], None),
    0x7414: (['сохранение базы количеств и выбор исходного текста'], None),
}


OPERANDS = {
    0x73D8: 'SecondaryEquipmentState.Row', 0x73D9: 'SecondaryEquipmentState.RowCount',
    0x737D: 'SecondaryEquipmentState.TopRow', 0xA265: 'ScrollState.RenderCall',
    0xA235: 'ScrollState.EndLimit', 0x6ACC: 'EquipmentInfoState.TextIndex',
    0x6AA4: 'EquipmentInfoState.TopRow', 0x71EC: 'EquipmentTradeState.OwnedMode',
    0x983A: 'ScriptCallState.EventCode', 0xEE19: 'EquipmentListText.Headings',
    0x984A: 'CurrentModels.SkimmerIndex', 0x95D4: 'SecondEquipmentPrices.Row00.Price',
    0x9484: 'EquipmentSkimmerTypeSets.Row00.Type0', 0x9632: 'SecondWeightFactors.Row00.Threshold',
    0x98F6: 'SecondaryEquipmentData.Quantities', 0xF066: 'SecondaryEquipmentData.Names',
    0x7264: 'Station.PrintEquipmentRows.AtNameStream', 0xA26F: 'Station.XorRowIfSelected.Entry',
    0xA1D6: 'Station.ScrollWindowRows.Entry', 0xA49F: 'Station.BeginScreenUpdate.Entry',
    0x6AAF: 'Station.TryDrawEquipmentInfo.Entry', 0xA496: 'Station.EndScreenUpdate.Entry',
    0x6396: 'Station.SelectRamBank.Entry', 0xC000: 'Text.RunMarketScript.Entry',
    0x7F35: 'Station.DrawItem00.Entry', 0xCB64: 'Station.TestDrawPointer.Entry',
    0xC287: 'Station.DrawCaptionItem.Entry', 0x733F: 'Station.SetupEquipmentColumns.Entry',
    0xBD08: 'Station.PrintText.Entry',
}
OPERANDS.update({address: f'Station.{name}.Entry' for address, (name, _) in FUNCTIONS.items()})
OPERANDS.update({0x73B1: 'Station.SelectSecondaryRow.RepeatChoice',
                 0x73BA: 'Station.SelectSecondaryRow.RunEvent',
                 0x73FB: 'Station.DrawSecondaryList.RenderRows',
                 0x73FE: 'Station.DrawSecondaryList.SaveRowCount'})


def name_operands(region, address, operation):
    if region != REGION or address not in FUNCTIONS:
        return operation
    return re.sub(r'#([0-9A-F]{4})\b',
                  lambda match: '@' + OPERANDS[int(match[1], 16)] if int(match[1], 16) in OPERANDS else match[0],
                  operation)


def prepare(pending, symbols, root):
    path = root / 'Source/Station/PrintEquipmentRows.asm'
    text = path.read_text('utf-8')
    needle = '                LD BC, @EquipmentListConst.FirstCursor'
    assert text.count(needle) == 1
    pending[path] = text.replace(needle, 'AtNameStream:   LD BC, @EquipmentListConst.FirstCursor').encode('utf-8')
    symbols['Station.PrintEquipmentRows.AtNameStream'] = 0x7264
    path = root / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    needle = '                module EquipmentListText'
    assert text.count(needle) == 1
    lines = ('                module SecondaryEquipmentState\n'
             'TopRow          equ #737D                                                       ; слово начального индекса в LD HL прокрутки\n'
             'Row             equ #73D8                                                       ; младший байт LD DE и номер подсвеченной строки\n'
             'RowCount        equ #73D9                                                       ; старший байт LD DE и число попыток печати\n'
             '                assert TopRow == @Station.ScrollSecondaryRows.ReadTop + 1\n'
             '                assert Row == @Station.TryDrawSecondaryList.Entry + 1\n'
             '                assert RowCount == Row + 1\n'
             '                endmodule\n\n'
             '                module SecondaryEquipmentData\n'
             'Quantities      equ #98F6                                                       ; байтовые количества второго набора\n'
             'Names           equ #F066                                                       ; исходный CR-поток топлива и подписей доставки\n'
             '                endmodule\n\n')
    pending[path] = text.replace(needle, lines + needle).encode('utf-8')
    symbols.update({'SecondaryEquipmentState.TopRow': 0x737D, 'SecondaryEquipmentState.Row': 0x73D8,
                    'SecondaryEquipmentState.RowCount': 0x73D9, 'SecondaryEquipmentData.Quantities': 0x98F6,
                    'SecondaryEquipmentData.Names': 0xF066})
