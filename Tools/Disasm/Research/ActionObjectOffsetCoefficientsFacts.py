"""Три коэффициента из фазовых пар и разностей табличных квадратов."""
FUNCTIONS = {0xB044: ('BuildObjectOffsetCoefficients', 'Подготовка коэффициентов смещения по трём фазовым парам')}
LOCAL = {0xB0AD: 'StoreSecond', 0xB0E5: 'StoreThird'}
MODIFIED_WRITERS = ((0xB075, 0x6D0E, 0x6D0D, 1), (0xB0AD, 0x6D1C, 0x6D1B, 1), (0xB0E5, 0x6D2A, 0x6D29, 1))
CONTRACTS = {('Action', 0xB044): (
    [
        'HL, DE, BC и AF числовых аргументов не задают',
        'Offset0..2 содержат байтовые индексы x, y, z, страницы фаз 9900 и табличных квадратов 9800 читаемы',
        'три операнда Coefficient0..2 доступны для записи, код ACTION банка 0 не перекрыт ими или рамкой возврата',
        'CPU-стек содержит внешний возврат, IRQ и повторный вход не вмешиваются в общие операнды',
    ],
    [
        'HL - H=98, L=(s(P(u,b))-s(d)+d) AND FF',
        'DE - D=d, E=T[(s(P(u,b))-s(d)) AND FF], BC=256*b+c',
        'AF - A равен третьему коэффициенту, F от заключительного ADD, NEG либо DEC по условиям знаковой коррекции',
        "HL', DE', BC', AF' сохраняются",
        'IX - IXH=P(v,c), IXL=u, IYH сохраняется, IYL=v',
        'Coefficient0..2 содержат три байта по формулам ActionObjectOffsetCoefficients.md, иные байты RAM не записываются',
        'SP=входной SP+2, I, IM, IFF и paging сохраняются, порты не используются',
        'R учитывает 135 M1 плюс две условные коррекции, его старший бит сохраняется',
    ],
    [
        'HL, DE, BC, AF, IX, IYL, R, три байта Coefficient0..2',
    ],
    [
        'b=W[x], c=W[(x+64) AND FF], u=W[y], v=W[(y+64) AND FF], d=W[z], e=W[(z+64) AND FF]',
        'W обозначает страницу 9900, T страницу 9800, s(a)=floor(s8(a)/2), P(a,b)=(T[(s(a)-s(b)+b) AND FF]-T[(s(a)-s(b)) AND FF]) AND FF',
        'переполнение второй и третьей разности исправляется исходным NEG, его переполнение для 80 исправляется DEC до 7F',
        'каждая выполненная коррекция NEG добавляет три M1, её дополнительный DEC добавляет ещё одну M1',
        'собственных записей CPU-стека нет, RET снимает внешний адрес, CALL вызывающего относится к его рамке',
        '8192 самостоятельных сценария и 73728 проходов обёртки проверяют точные регистры, R и исходные записи, это не полный перебор всех таблиц',
        'IRQ, точные T и нативный запуск этой проверкой не подтверждены',
    ],
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
