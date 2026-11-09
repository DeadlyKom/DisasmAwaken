"""Физические ячейки результата проекции исходных моделей, не готовые координаты объекта."""
from PreviewSceneTables import render as render_records,parse as parse_records

TABLE=('ActionProjectedPoints','Source/Action/Data/ProjectedPoints.asm',0x2E00,0x2EC8,'FRenderProjectedPoint',
    (('Second',2,'исходное содержимое второго экранного слова, заменяется перспективой'),
     ('First',2,'исходное содержимое первого экранного слова, заменяется перспективой'),
     ('ClipCode',1,'исходный байт сохранён перспективой, код границ заполняется отдельным проходом')),
    tuple('Point'+format(i,'02X') for i in range(40)))


def render(source):
    text,labels=render_records(source,TABLE,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические ячейки проекции ACTION](../../../Docs/ActionProjectedPointsData.md)'),labels


def parse(text):return parse_records(text,TABLE,0x6000)
