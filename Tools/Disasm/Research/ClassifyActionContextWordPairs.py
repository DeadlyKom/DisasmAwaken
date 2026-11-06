"""Публикация точного сравнения существующих слов контекста."""
import ActionContextWordPairsFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionContextWordPairs','ActionContextWordPairs',state_fields=(
        ('OtherFirst',0x9BC6,'первое сравниваемое слово другого контекста, полный игровой смысл ещё не доказан'),
        ('OtherSecond',0x9BC8,'второе сравниваемое слово другого контекста')))
