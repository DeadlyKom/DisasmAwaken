"""Именование проверенной обёртки векторного вычисления для третьего знака."""
from ClassifyActionRegionType import main
import ActionThirdGlyphVectorFacts as facts

if __name__=='__main__':main(facts,'ActionThirdGlyphVector','ActionThirdGlyphVector',(
    ('SourceWord0',0x9B79,'разряды 23..8 первой компоненты ActionWorkVector станции, младший байт не читается'),
    ('SourceWord1',0x9B7C,'разряды 23..8 второй компоненты ActionWorkVector станции, младший байт не читается'),
    ('SourceWord2',0x9B7F,'разряды 23..8 третьей компоненты ActionWorkVector станции, младший байт не читается')))
