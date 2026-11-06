"""Вызов E500 в странице 3 и возврат в страницу ACTION."""
FUNCTIONS = {0xADB7: ('RotateBankedBasis', 'Поворот базисных векторов через VOXAL в странице 3')}
RENAMES = {'Action.UnknownADB7.Entry': 'Action.RotateBankedBasis.Entry'}
LOCAL = {}
CONTRACTS = {('Action', 0xADB7): (
    ['HL, DE, BC и AF передаются в поворот с A = #13, F сохраняется до дочернего входа',
     'IY задаёт начальное состояние SignedSeededProduct, доступны векторы #9B00..#9B11 и углы #9B12..#9B14',
     'выбор страниц разрешён, SP и рамки вызовов находятся в общей RAM, IRQ не вмешиваются'],
    ['результат RotateBasisVectors, A = #10, регистр страницы возвращён к #10',
     'SP = входной SP + 2, внешняя рамка снята, IX, I, IM и IFF сохраняются',
     'R получает стоимость дочернего поворота и ещё 18 M1, бит 7 сохраняется'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IY, R, состояние поворота, регистр 7FFD и временные байты стека'],
    ['записи в 7FFD идут в порядке #13, #10',
     'модель сверяет обёртку с прямым исполнением исходного поворота, математические свойства поворота отдельно не доказываются'],
)}
COMMENTS = {
    0xADB7: (['Выбор страницы VOXAL с поворотом базисных векторов.'], None),
    0xADBC: (['Поворот базиса по подготовленной тройке углов.'], None),
    0xADBF: (['Возврат страницы ACTION с сохранением флагов поворота.'], None),
}


def name_operands(region, address, operation):
    if region == 'Action' and address == 0xADB7:
        return operation.replace('CALL #E500', 'CALL @Voxel.RotateBasisVectors.Entry')
    return operation
