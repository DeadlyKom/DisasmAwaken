"""Договор восстановителя, именование исходных кодовых операндов и регистрация их писателей."""
from ClassifyActionRegionType import main
import ActionOffsetRestoreFacts as facts

if __name__=='__main__':
    variables='\n                ; Существующие операнды кода, отдельная память не выделяется\n                module ActionOffsetState\n'
    for name,value,note in facts.FIELDS:
        variables+=(name.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+note+'\n'
    variables+='                endmodule\n'
    constants='\n                module ActionOffsetConst\n'
    constants+=('HalvedClass'.ljust(16)+'equ #14').ljust(80)+'; полный код класса с временно делимыми вычитаемыми словами\n'
    constants+='                endmodule\n'
    main(facts,'ActionOffsetRestore','ActionOffsetRestore',(),include_blocks=(
        ('Includes/Variables/Include.inc','module ActionOffsetState',variables),
        ('Includes/Const/Include.inc','module ActionOffsetConst',constants)))
