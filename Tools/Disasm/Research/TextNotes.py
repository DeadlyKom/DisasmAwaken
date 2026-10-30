"""Смысловые пояснения подтверждённых внутренних обработчиков языка."""

NOTES = {}

COMMENTS = {
    0xC900: (["чтение выбранной строки и компоненты смещения списка оснащения"], None),
    0xC907: (["расчёт байтового индекса оснащения, переполнение не расширяет результат до слова"], None),
    0xC918: (["чтение выбранной строки и компоненты смещения списка товаров"], None),
    0xC91F: (["расчёт байтового индекса товара, переполнение не расширяет результат до слова"], None),
    0xC79C: (["чтение символа операции с продвижением входного курсора"], None),
    0xC7A1: (["поиск обработчика в таблице одиннадцати бинарных операторов"], None),
    0xC7AD: (["запись указателя обработчика в буфер выражения через альтернативный HL"], None),
    0xC7DA: (["поиск записи символа перед хвостовой передачей управления её обработчику"], None),
    0xC7E3: (["установка шага физической записи FScriptToken"], None),
    0xC7E6: (["поиск следующей записи, начальный HL указывает за три байта до первой"], None),
    0xC7E7: (["проверка совпадения искомого символа с полем Symbol текущей записи"], None),
    0xC7E8: ([], "выход, если символ текущей записи совпадает с искомым"),
    0xC1B9: (["перенос слова результата в альтернативный набор без изменения основного DE"], None),
    0xC6EA: (["переход за уже проверенную первую цифру перед поиском конца числа"], None),
    0xC726: (["преобразование последней прочитанной цифры в единицы результата"], None),
    0xC731: (["расчёт вклада десятков, цифра умножается на 10 и добавляется к единицам"], None),
    0xC746: (["расчёт вклада сотен, цифра умножается на 100 и добавляется к младшим разрядам"], None),
    0xC75F: (["расчёт вклада тысяч, промежуточные суммы дают множитель 1000"], None),
    0xC77E: (["расчёт вклада десятков тысяч, переполнение 16-битной суммы сохраняется как в оригинале"], None),
    0xC825: (["создание адреса возврата, который поместит результат DE обратно в стек выражений"], None),
    0xC829: (["поиск начала шестибайтовой записи относительно вершины стека в альтернативном HL"], None),
    0xC82D: (["расчёт начала записи, из указателя вершины вычитается размер FExpressionCall"], None),
    0xC832: (["передача левого операнда из записи в основной DE"], None),
    0xC83A: (["передача адреса обработчика из записи в основной HL"], None),
    0xC845: (["расчёт новой вершины, указатель возвращается к началу использованной записи"], None),
    0xC847: (["передача правого операнда в BC и хвостовой вход в обработчик"], None),
    0xC3D6: (["сброс входного переноса перед проверкой равенства двух слов"], None),
    0xC3D7: (["расчёт разности левого и правого операндов, ноль означает равенство"], None),
    0xC3DC: ([], "выход, если операнды равны, DE содержит истину"),
    0xC489: (["расчёт суммы операндов с проверкой выхода за пределы 16 бит"], None),
    0xC48A: ([], "переход, если сумма не превышает 65535, ограничение не требуется"),
    0xC48C: (["ограничение переполненной суммы максимальным беззнаковым словом"], None),
    0xC492: (["сброс входного переноса перед вычитанием правого операнда"], None),
    0xC493: (["расчёт разности с проверкой ухода ниже нуля"], None),
    0xC495: ([], "переход, если левый операнд не меньше правого, ограничение не требуется"),
    0xC497: (["ограничение отрицательной беззнаковой разности нулём"], None),
    0xC49D: (["сброс входного переноса перед беззнаковым сравнением операндов"], None),
    0xC49E: (["расчёт разности, заём означает, что левый операнд меньше правого"], None),
    0xC4A3: ([], "выход, если левый операнд меньше правого, DE содержит истину"),
    0xC4A7: (["сброс входного переноса перед проверкой строгого превышения"], None),
    0xC4A8: (["расчёт разности для исключения равенства и меньшего левого операнда"], None),
    0xC4AD: ([], "выход, если операнды равны, строгое превышение ложно"),
    0xC4AE: ([], "выход, если левый операнд меньше правого, строгое превышение ложно"),
    0xC4B2: (["сброс входного переноса перед проверкой отношения не больше"], None),
    0xC4B3: (["расчёт разности для проверки меньшего либо равного левого операнда"], None),
    0xC4B8: ([], "выход, если левый операнд меньше правого, DE содержит истину"),
    0xC4B9: ([], "выход, если операнды равны, отношение не больше истинно"),
    0xC4BD: (["сброс входного переноса перед проверкой отношения не меньше"], None),
    0xC4BE: (["расчёт разности, заём исключает отношение не меньше"], None),
    0xC4C3: ([], "выход, если левый операнд меньше правого, отношение не меньше ложно"),
    0xC4C7: (["пересечение установленных битов старших байтов двух слов"], None),
    0xC4CA: (["пересечение установленных битов младших байтов двух слов"], None),
    0xC4CE: (["объединение установленных битов старших байтов двух слов"], None),
    0xC4D1: (["объединение установленных битов младших байтов двух слов"], None),
}

for lower, upper in ((0xC6F1, 0xC6F5), (0xC6FF, 0xC703),
                     (0xC70D, 0xC711), (0xC71B, 0xC71F)):
    COMMENTS[lower] = (["проверка нижней границы десятичной цифры в следующем символе"], None)
    COMMENTS[upper] = (["проверка верхней границы десятичной цифры в следующем символе"], None)
    COMMENTS[lower + 2] = ([], "переход, если следующий символ меньше кода цифры ноль, чтение числа завершено")
    COMMENTS[upper + 2] = ([], "переход, если следующий символ больше кода цифры девять, чтение числа завершено")

from MarketAccessFacts import COMMENTS as MARKET_ACCESS_COMMENTS
COMMENTS.update(MARKET_ACCESS_COMMENTS)

from FieldSuffixFacts import COMMENTS as FIELD_SUFFIX_COMMENTS
COMMENTS.update(FIELD_SUFFIX_COMMENTS)

from WeightedLoadFacts import COMMENTS as WEIGHTED_LOAD_COMMENTS
COMMENTS.update(WEIGHTED_LOAD_COMMENTS)

from MarketFieldFacts import COMMENTS as MARKET_FIELD_COMMENTS
COMMENTS.update(MARKET_FIELD_COMMENTS)

from DelimitedRecordFacts import COMMENTS as DELIMITED_RECORD_COMMENTS
COMMENTS.update(DELIMITED_RECORD_COMMENTS)

from KeyChoiceFacts import COMMENTS as KEY_CHOICE_COMMENTS
COMMENTS.update(KEY_CHOICE_COMMENTS)

from StrideFiveFacts import COMMENTS as STRIDE_FIVE_COMMENTS
COMMENTS.update(STRIDE_FIVE_COMMENTS)

from MembershipFlagsFacts import COMMENTS as MEMBERSHIP_FLAGS_COMMENTS
COMMENTS.update(MEMBERSHIP_FLAGS_COMMENTS)

from ThresholdSetFacts import COMMENTS as THRESHOLD_SET_COMMENTS
COMMENTS.update(THRESHOLD_SET_COMMENTS)

from ActiveNeighborFacts import COMMENTS as ACTIVE_NEIGHBOR_COMMENTS
COMMENTS.update(ACTIVE_NEIGHBOR_COMMENTS)

from CargoFieldFacts import COMMENTS as CARGO_FIELD_COMMENTS
COMMENTS.update(CARGO_FIELD_COMMENTS)

from WeightFieldFacts import COMMENTS as WEIGHT_FIELD_COMMENTS
COMMENTS.update(WEIGHT_FIELD_COMMENTS)

from EntryThresholdFacts import COMMENTS as ENTRY_THRESHOLD_COMMENTS
COMMENTS.update(ENTRY_THRESHOLD_COMMENTS)

from KeyFieldSelectorFacts import COMMENTS as KEY_FIELD_SELECTOR_COMMENTS
COMMENTS.update(KEY_FIELD_SELECTOR_COMMENTS)

from RecordFieldSelectorFacts import COMMENTS as RECORD_FIELD_SELECTOR_COMMENTS
COMMENTS.update(RECORD_FIELD_SELECTOR_COMMENTS)

from ExpressionPushFacts import COMMENTS as EXPRESSION_PUSH_COMMENTS
COMMENTS.update(EXPRESSION_PUSH_COMMENTS)

from MultiplyFacts import COMMENTS as MULTIPLY_COMMENTS
COMMENTS.update(MULTIPLY_COMMENTS)

from NumericFieldFacts import COMMENTS as NUMERIC_FIELD_COMMENTS
COMMENTS.update(NUMERIC_FIELD_COMMENTS)

from ScalarWriterFacts import COMMENTS as SCALAR_WRITER_COMMENTS
COMMENTS.update(SCALAR_WRITER_COMMENTS)

from IndexedWriterFacts import COMMENTS as INDEXED_WRITER_COMMENTS
COMMENTS.update(INDEXED_WRITER_COMMENTS)

from AssignmentPipelineFacts import COMMENTS as ASSIGNMENT_PIPELINE_COMMENTS
COMMENTS.update(ASSIGNMENT_PIPELINE_COMMENTS)

from UnaryModeFacts import COMMENTS as UNARY_MODE_COMMENTS
COMMENTS.update(UNARY_MODE_COMMENTS)

from QueuedTextFacts import TEXT_COMMENTS as QUEUED_TEXT_COMMENTS
COMMENTS.update(QUEUED_TEXT_COMMENTS)

from ScriptControlFacts import COMMENTS as SCRIPT_CONTROL_COMMENTS
COMMENTS.update(SCRIPT_CONTROL_COMMENTS)

from ExpressionControlFacts import COMMENTS as EXPRESSION_CONTROL_COMMENTS
COMMENTS.update(EXPRESSION_CONTROL_COMMENTS)

from TonnageCommandFacts import COMMENTS as TONNAGE_COMMAND_COMMENTS
COMMENTS.update(TONNAGE_COMMAND_COMMENTS)

from StationTransitionFacts import TEXT_COMMENTS as TRANSITION_TEXT_COMMENTS
COMMENTS.update(TRANSITION_TEXT_COMMENTS)
