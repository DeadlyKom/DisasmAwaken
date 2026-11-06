"""Три коэффициента из фазовых пар и разностей табличных квадратов."""
FUNCTIONS = {0xB044: ('BuildObjectOffsetCoefficients', 'Подготовка коэффициентов смещения по трём фазовым парам')}
LOCAL = {0xB0AD: 'StoreSecond', 0xB0E5: 'StoreThird'}
MODIFIED_WRITERS = ((0xB075, 0x6D0E, 0x6D0D, 1), (0xB0AD, 0x6D1C, 0x6D1B, 1), (0xB0E5, 0x6D2A, 0x6D29, 1))
CONTRACTS = {('Action', 0xB044): (
    ['Offset0..2 задают три байтовых индекса, фазовая страница 9900 и таблица квадратов 9800 доступны'],
    ['Coefficient0..2 получают три числовых коэффициента, BC содержит первую фазовую пару, IX и IYL содержат рабочие значения',
     'HL и DE содержат адрес и данные последней разности, AF возвращает третий коэффициент и его флаги',
     'SP=входной SP+2, записи выполняются только в три операнда'],
    ['HL, DE, BC, AF, IX, IYL, R и три операнда'],
    ['арифметические деления байтов на два и разности таблицы сохраняют оборачивание',
     'переполнение второй и третьей разности исправляется исходным NEG, результат 80 после NEG уменьшается до 7F',
     '8192 самостоятельных сценария и композиционная проверка обёртки подтверждают точные регистры и записи'],
)}
COMMENTS = {
    0xB044: (['Чтение трёх фазовых пар, второй элемент каждой находится на 64 позиции дальше по модулю байта.'], None),
    0xB065: (['Расчёт первого коэффициента через разность табличных квадратов.'], None),
    0xB078: (['Расчёт двух вкладов второго коэффициента с сохранением промежуточного байта в IXH.'], None),
    0xB0A4: ([], 'переход, если вычитание вкладов не переполнилось, записать второй коэффициент'),
    0xB0A9: ([], 'переход, если отрицание не переполнилось, записать второй коэффициент'),
    0xB0B0: (['Расчёт двух вкладов третьего коэффициента.'], None),
    0xB0DC: ([], 'переход, если сложение вкладов не переполнилось, записать третий коэффициент'),
    0xB0E1: ([], 'переход, если отрицание не переполнилось, записать третий коэффициент'),
}
CONST_BLOCK = '\n                ; Страницы и шаг фазовых пар вычислителя смещения\n                module ActionObjectOffsetConst\n'
for name, value, note in (('PhasePage', 0x99, 'страница фазовых пар'), ('SquarePage', 0x98, 'страница табличных квадратов'),
                          ('PhaseStep', 0x40, 'смещение второго элемента пары')):
    CONST_BLOCK += name.ljust(16) + ('equ #'+format(value,'02X')).ljust(64) + '; '+note+'\n'
CONST_BLOCK += '                endmodule\n\n'
INCLUDE_BLOCKS = (('Includes/Const/Include.inc', 'module ActionObjectOffsetConst', CONST_BLOCK),)


def qualify_mutations(modified, flow, functions, pieces):
    for item in modified:
        if item['region'] == 'Action' and item['writer'] in (0xB075, 0xB0AD, 0xB0E5):
            item.update(target_bank=5, target_source_classified=True, target_path='Source/Action/ApplyObjectOffsetVector.asm')


def name_operands(region, address, operation):
    if region != 'Action' or address != 0xB044:
        return operation
    for index, literal in enumerate(('6D0E', '6D1C', '6D2A')):
        operation = operation.replace('(#'+literal+')', '(@ActionObjectOffsetVectorState.Coefficient'+str(index)+')')
    return (operation.replace('LD H, #99', 'LD H, @ActionObjectOffsetConst.PhasePage')
            .replace('LD H, #98', 'LD H, @ActionObjectOffsetConst.SquarePage')
            .replace('ADD A, #40', 'ADD A, @ActionObjectOffsetConst.PhaseStep'))
