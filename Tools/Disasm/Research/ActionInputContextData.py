"""Доказанные физические входы коррекции точек и генератора параметров."""
from PreviewSceneTables import render as render_records,parse as parse_records

TABLES=(
    ('ActionFlightControls','Source/Action/Data/FlightControls.asm',0x3B95,0x3B98,'FFlightControls',
     (('YControl',1,'знаковое байтовое управление проходом Y'),
      ('XControl',1,'знаковое байтовое управление проходом X'),
      ('TurnControl',1,'индекс синусоиды получается отрицанием по модулю 256')),('Value',)),
    ('ActionParameterSeeds','Source/Action/Data/ParameterSeeds.asm',0x3BC1,0x3BC6,'FParameterSeeds',
     (('SeedFirst',2,'первое слово исходного зерна'),
      ('SeedSecond',2,'второе слово исходного зерна'),
      ('StepControl',1,'полный управляющий байт повторов генератора')),('Value',)),
)


def render(source,table):
    text,labels=render_records(source,table,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические входные состояния](../../../Docs/ActionInputContextData.md)'),labels


def parse(text,table):return parse_records(text,table,0x6000)


def structures():
    return '''
                ; Физические знаковые управления, это числовые байты, не наборы флагов
                struct FFlightControls
YControl        db #00                                                          ; управление проходом Y
XControl        db #00                                                          ; управление проходом X
TurnControl     db #00                                                          ; отрицание по модулю 256 задаёт индекс синусоиды
                ends
                assert FFlightControls == 3
                assert FFlightControls.YControl == 0
                assert FFlightControls.XControl == 1
                assert FFlightControls.TurnControl == 2

                ; Физическое зерно BuildParameterTables, размещено в общем ядре ACTION
                struct FParameterSeeds
SeedFirst       dw #0000                                                        ; первое слово зерна
SeedSecond      dw #0000                                                        ; второе слово зерна
StepControl     db #00                                                          ; управляющий байт количества повторов
                ends
                assert FParameterSeeds == 5
                assert FParameterSeeds.SeedFirst == 0
                assert FParameterSeeds.SeedSecond == 2
                assert FParameterSeeds.StepControl == 4
'''
