"""Исходные дисковые байты рабочих областей ACTION, не подмена сгенерированными таблицами."""
RESOURCES=(
    (0x21CC,0x2C00,'Source/Action/Resources/InitialLinearBufferTail.bin','INITIAL_LINEAR_BUFFER_TAIL',
     'начальное содержимое 81CC..8BFF, хвост строки 14 с байта 12 и строки 15..95 линейного буфера'),
    (0x3100,0x3200,'Source/Action/Resources/InitialLogarithmLow.bin','INITIAL_LOGARITHM_LOW_STORAGE',
     'исходные байты страницы 9100, BuildLogarithmTable заменяет их младшими байтами результатов'),
    (0x3200,0x3300,'Source/Action/Resources/InitialLogarithmHigh.bin','INITIAL_LOGARITHM_HIGH_STORAGE',
     'исходные байты страницы 9200, BuildLogarithmTable заменяет их старшими байтами результатов'),
    (0x3300,0x3400,'Source/Action/Resources/InitialExponential.bin','INITIAL_EXPONENTIAL_STORAGE',
     'исходные байты страницы 9300, BuildExponentialTable создаёт значения во время загрузки'),
    (0x3400,0x3500,'Source/Action/Resources/InitialRowHigh.bin','INITIAL_ROW_HIGH_STORAGE',
     'исходные байты страницы 9400, затем HIGH(8000+32*Y) для Y от 0 до 255'),
    (0x3500,0x3600,'Source/Action/Resources/InitialRowLow.bin','INITIAL_ROW_LOW_STORAGE',
     'исходные байты страницы 9500, затем LOW(32*Y) для Y от 0 до 255'),
    (0x3600,0x3700,'Source/Action/Resources/InitialColumnByte.bin','INITIAL_COLUMN_BYTE_STORAGE',
     'исходные байты страницы 9600, затем X DIV 8 для X от 0 до 255'),
    (0x3700,0x3800,'Source/Action/Resources/InitialColumnMask.bin','INITIAL_COLUMN_MASK_STORAGE',
     'исходные байты страницы 9700, затем 80 >> (X AND 7) для X от 0 до 255'))
