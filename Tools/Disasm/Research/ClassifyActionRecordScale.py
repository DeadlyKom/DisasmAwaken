"""Точечная классификация E55C, исходная граница и изменяемый JR сохранены."""
from ClassifyActionRegionType import main
import ActionRecordScaleFacts as facts

if __name__=='__main__':
    constants='\n                module ActionRecordScaleConst\n'
    for name,value,note in (('SkipBase',6,'из старшего байта заголовка получается смещение JR 6-e'),
        ('InitialValue',200,'исходное слово перед цепью удвоений')):
        constants+=(name.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+note+'\n'
    constants+='                endmodule\n'
    main(facts,'ActionRecordScale','ActionRecordScale',(('ShiftSkip',0xE59E,'изменяемое смещение JR по E59D, 6-e'),),
        include_blocks=(('Includes/Const/Include.inc','module ActionRecordScaleConst',constants),))
