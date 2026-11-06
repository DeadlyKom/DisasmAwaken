"""Публикация обоих доказанных входов с явным сохранением отличающихся исходных табличных значений."""
from ClassifyActionRegionType import main
import ActionCachedRootFacts as facts

if __name__=='__main__':
    constants='\n                module ActionRootCacheConst\n'
    for name,value,note in (('InitialPage',0xC0,'страница начальной оценки в Controls банка 1, следующие две страницы дают базовое слово'),
        ('NegativeHigh',0xFF,'старший байт подготовки отрицательной нечётной разности'),
        ('FirstOddStep',0xFFFF,'первая разность -1 для малого слова')):
        constants+=(name.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+note+'\n'
    constants+='                endmodule\n'
    main(facts,'ActionCachedRoot','ActionCachedRoot',(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionRootCacheConst',constants),))
