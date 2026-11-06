"""Разбор трёх записей с доказанным протоколом поиска без исправления исходного порядка."""
from ClassifyActionRegionType import main
import ActionRecordReuseFacts as facts

if __name__=='__main__':
    block='\n                module ActionReuseConst\n'
    for name,value,note in (('ReusableHigh',0x80,'полный старший байт Component0 доступной записи'),
        ('ReusableLow',0,'младший байт кода 8000, отличается от маркера конца 80'),
        ('SkipOnce',0xFF,'первое достижение записи поиском обнуляет код и пропускает её')):
        block+=(name.ljust(16)+'equ #'+format(value,'02X')).ljust(80)+'; '+note+'\n'
    block+='                endmodule\n'
    main(facts,'ActionRecordReuse','ActionRecordReuse',(),include_blocks=(('Includes/Const/Include.inc','module ActionReuseConst',block),))
