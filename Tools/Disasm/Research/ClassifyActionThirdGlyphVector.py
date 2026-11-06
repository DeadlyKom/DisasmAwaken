"""Именование проверенной обёртки векторного вычисления для третьего знака."""
from ClassifyActionRegionType import main
import ActionThirdGlyphVectorFacts as facts

if __name__=='__main__':main(facts,'ActionThirdGlyphVector','ActionThirdGlyphVector',(
    ('SourceWord0',0x9B79,'первое читаемое слово источника третьего знака, единицы ещё не установлены'),
    ('SourceWord1',0x9B7C,'второе читаемое слово источника, промежуточный байт не копируется'),
    ('SourceWord2',0x9B7F,'третье читаемое слово источника, полного типа соседних байтов пока нет')))
