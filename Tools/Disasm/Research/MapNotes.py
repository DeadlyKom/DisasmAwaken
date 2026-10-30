"""Подтверждённые внутренние алгоритмы карты, привязанные к исходным инструкциям."""

NOTES = {}
COMMENTS = {
    0xE57E: (["сравнение текущей строки с включённой верхней границей, колонка не участвует"], None),
    0xE589: (["проверка равенства байтового адреса строки верхней границе"], None),
    0xE58D: ([], "переход, если текущая строка уже является верхней границей, растровый вызов завершается"),
    0xE58F: (["расчёт предыдущей пиксельной строки с учётом чересстрочной раскладки Spectrum"], None),
    0xE593: ([], "переход, если предыдущая строка остаётся внутри восьмистрочной группы"),
    0xE596: (["переход к предыдущей группе строк, обе колонки переносятся вместе"], None),
    0xE59E: ([], "переход, если вычитание шага группы вышло за младший байт адреса"),
    0xE5A0: (["коррекция старшего байта при переходе между восьмистрочными группами"], None),
    0xE5A5: (["отмена внутреннего возврата и восстановление стека внешнего растрового вызова"], None),
    0xE5AC: (["расчёт следующей пиксельной строки с учётом чересстрочной раскладки Spectrum"], None),
    0xE5B0: ([], "переход, если следующая строка остаётся внутри восьмистрочной группы"),
    0xE5B3: (["переход к следующей группе строк, обе колонки переносятся вместе"], None),
    0xE5BB: ([], "переход, если сложение шага группы перенеслось в старшую часть адреса"),
    0xE5BD: (["коррекция старшего байта при переходе между восьмистрочными группами"], None),
    0xE5C1: (["сравнение следующей строки с исключённой нижней границей без учёта колонки"], None),
    0xE5CC: (["проверка равенства нового адреса строки нижней границе"], None),
    0xE5D0: ([], "выход, если новая строка ещё не достигла исключённой нижней границы"),
    0xE5D1: (["отмена внутреннего возврата и восстановление стека внешнего растрового вызова"], None),
    0xE666: (["сброс альтернативных накопителей растрового прохода и выбор направления вниз"], None),
    0xE674: (["сброс альтернативных накопителей растрового прохода и выбор направления вверх"], None),
    0xE65D: (["сохранение указателя вызывающего кода перед выборкой квадрата"], None),
    0xE660: (["поиск младшего байта квадрата по входному A"], None),
    0xE662: (["выбор следующей страницы со старшими байтами, входной Carry сохраняется"], None),
    0xE554: (["сохранение регистров и входного AF, его Carry участвует в разности квадратов"], None),
    0xE558: (["получение квадрата первого аргумента D"], None),
    0xE55E: (["восстановление второго аргумента A и входного Carry перед его возведением в квадрат"], None),
    0xE562: (["расчёт разности квадратов с входным заёмом по модулю 65536"], None),
    0xE567: (["сохранение постоянной разности для всех восьми пробных разрядов корня"], None),
    0xE56D: (["расчёт кандидата корня с очередным установленным битом"], None),
    0xE571: (["проверка, помещается ли квадрат кандидата в сохранённую разность"], None),
    0xE573: ([], "переход, если квадрат кандидата не превышает разность, пробный бит сохраняется"),
    0xE575: (["отмена пробного бита, квадрат кандидата оказался слишком большим"], None),
    0xE576: (["выбор следующего младшего разряда результата"], None),
    0xE578: ([], "переход, если младший разряд результата ещё не проверен"),
}

from SelectionBandFacts import COMMENTS as SELECTION_BAND_COMMENTS
COMMENTS.update(SELECTION_BAND_COMMENTS)

from WorldSignatureFacts import MAP_COMMENTS as SIGNATURE_MAP_COMMENTS
COMMENTS.update(SIGNATURE_MAP_COMMENTS)

from SignedMultiplyFacts import COMMENTS as SIGNED_MULTIPLY_COMMENTS
COMMENTS.update(SIGNED_MULTIPLY_COMMENTS)

from SeededRootFacts import COMMENTS as SEEDED_ROOT_COMMENTS
COMMENTS.update(SEEDED_ROOT_COMMENTS)

from SignedDivisionFacts import COMMENTS as SIGNED_DIVISION_COMMENTS
COMMENTS.update(SIGNED_DIVISION_COMMENTS)

from CoordinateDistanceFacts import COMMENTS as COORDINATE_DISTANCE_COMMENTS
COMMENTS.update(COORDINATE_DISTANCE_COMMENTS)

from SystemNameFacts import COMMENTS as SYSTEM_NAME_COMMENTS
COMMENTS.update(SYSTEM_NAME_COMMENTS)

from StoredMapPointFacts import COMMENTS as STORED_MAP_POINT_COMMENTS
COMMENTS.update(STORED_MAP_POINT_COMMENTS)

from MapViewCenterFacts import COMMENTS as MAP_VIEW_CENTER_COMMENTS
COMMENTS.update(MAP_VIEW_CENTER_COMMENTS)

from VariantLabelFacts import COMMENTS as VARIANT_LABEL_COMMENTS
COMMENTS.update(VARIANT_LABEL_COMMENTS)

from MapSectorTableFacts import COMMENTS as MAP_SECTOR_TABLE_COMMENTS
COMMENTS.update(MAP_SECTOR_TABLE_COMMENTS)

from MapScreenTableFacts import COMMENTS as MAP_SCREEN_TABLE_COMMENTS
COMMENTS.update(MAP_SCREEN_TABLE_COMMENTS)

from MapPointMarkerFacts import COMMENTS as MAP_POINT_MARKER_COMMENTS
COMMENTS.update(MAP_POINT_MARKER_COMMENTS)

from VariantResourceFacts import COMMENTS as VARIANT_RESOURCE_COMMENTS
COMMENTS.update(VARIANT_RESOURCE_COMMENTS)

from SecondaryPointOrderFacts import COMMENTS as SECONDARY_POINT_ORDER_COMMENTS
COMMENTS.update(SECONDARY_POINT_ORDER_COMMENTS)

from RasterPreparationFacts import COMMENTS as RASTER_PREPARATION_COMMENTS
COMMENTS.update(RASTER_PREPARATION_COMMENTS)

from MapPointOutcodeFacts import COMMENTS as MAP_POINT_OUTCODE_COMMENTS
COMMENTS.update(MAP_POINT_OUTCODE_COMMENTS)

from ClipProductFacts import COMMENTS as CLIP_PRODUCT_COMMENTS
COMMENTS.update(CLIP_PRODUCT_COMMENTS)

from ClipIntersectionFacts import COMMENTS as CLIP_INTERSECTION_COMMENTS
COMMENTS.update(CLIP_INTERSECTION_COMMENTS)

from ClipTailFacts import COMMENTS as CLIP_TAIL_COMMENTS
COMMENTS.update(CLIP_TAIL_COMMENTS)

from ClipCaseFacts import COMMENTS as CLIP_CASE_COMMENTS
COMMENTS.update(CLIP_CASE_COMMENTS)

from ArcPreparationFacts import COMMENTS as ARC_PREPARATION_COMMENTS
COMMENTS.update(ARC_PREPARATION_COMMENTS)

from ArcClosingFacts import COMMENTS as ARC_CLOSING_COMMENTS
COMMENTS.update(ARC_CLOSING_COMMENTS)

from MapLineFacts import COMMENTS as MAP_LINE_COMMENTS
COMMENTS.update(MAP_LINE_COMMENTS)

from MapPointChainFacts import COMMENTS as MAP_POINT_CHAIN_COMMENTS
COMMENTS.update(MAP_POINT_CHAIN_COMMENTS)

from SumSquares8Facts import COMMENTS as SUM_SQUARES8_COMMENTS
COMMENTS.update(SUM_SQUARES8_COMMENTS)

from MapRasterSetupFacts import COMMENTS as MAP_RASTER_SETUP_COMMENTS
COMMENTS.update(MAP_RASTER_SETUP_COMMENTS)

from MapDistanceMinimumFacts import COMMENTS as MAP_DISTANCE_MINIMUM_COMMENTS
COMMENTS.update(MAP_DISTANCE_MINIMUM_COMMENTS)

from NearestMapVariantFacts import COMMENTS as NEAREST_MAP_VARIANT_COMMENTS
COMMENTS.update(NEAREST_MAP_VARIANT_COMMENTS)

from VisibleMapPointsFacts import COMMENTS as VISIBLE_MAP_POINTS_COMMENTS
COMMENTS.update(VISIBLE_MAP_POINTS_COMMENTS)

from NearestVisiblePointFacts import COMMENTS as NEAREST_VISIBLE_POINT_COMMENTS
COMMENTS.update(NEAREST_VISIBLE_POINT_COMMENTS)

from ArcRecurrenceFacts import COMMENTS as ARC_RECURRENCE_COMMENTS
COMMENTS.update(ARC_RECURRENCE_COMMENTS)

from ArcKernelFacts import COMMENTS as ARC_KERNEL_COMMENTS
COMMENTS.update(ARC_KERNEL_COMMENTS)

from ArcGeometryFacts import COMMENTS as ARC_GEOMETRY_COMMENTS
COMMENTS.update(ARC_GEOMETRY_COMMENTS)

from ArcDispatcherFacts import COMMENTS as ARC_DISPATCHER_COMMENTS
COMMENTS.update(ARC_DISPATCHER_COMMENTS)

from MapSceneFacts import COMMENTS as MAP_SCENE_COMMENTS
COMMENTS.update(MAP_SCENE_COMMENTS)

from AnimatedVariantFacts import COMMENTS as ANIMATED_VARIANT_COMMENTS
COMMENTS.update(ANIMATED_VARIANT_COMMENTS)
