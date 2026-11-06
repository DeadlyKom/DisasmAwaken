"""Повторное использование защищённого публикатора двух загрузочных таблиц, без сборки."""
from ClassifyActionLogarithmTable import main
import ActionExponentialTableFacts as facts


if __name__=='__main__':
    main(facts,'ActionExponentialTable',0x4355,'BuildProjectionTable',
        (('Values',0x9300,'256 физических байтов приближённой экспоненты'),))
