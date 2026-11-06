"""Публикация проверенного обновления компонент с сохранением всех исходных инструкций и адресов."""
from ClassifyActionRegionType import main
import ActionRecordUpdateFacts as facts

if __name__=='__main__':
    constants='\n                module ActionRecordUpdateConst\n'
    for name,value,note in (('LimitBias',125,'из старшего байта масштабированного HL получается граница B'),
        ('NearLimit',8,'исключённый предел нормализованных старших байтов в близкой области'),
        ('WarningArmed',0x80,'бит 7 разрешает однократный запрос после входа в близкую область'),
        ('WarningSent',0x18,'после запроса бит 7 сброшен, отказ очереди не вооружает защёлку повторно'),
        ('DockingText',0xF3B9,'адрес сообщения о зоне стыковки в Controls банка 1')):
        constants+=(name.ljust(16)+'equ #'+format(value,'04X')).ljust(80)+'; '+note+'\n'
    constants+='                endmodule\n'
    fields=(('Base0',0xE5B0,'изменяемый операнд LoadBase0 перед вычитанием Active0'),
        ('Base1',0xE5CF,'изменяемый операнд LoadBase1 перед вычитанием Active1'),
        ('Base2',0xE5EA,'изменяемый операнд LoadBase2 перед вычитанием Active2'),
        ('WarningLatch',0xE644,'операнд LD A,n, бит 7 разрешает однократное сообщение о зоне стыковки'))
    main(facts,'ActionRecordUpdate','ActionRecordUpdate',fields,
        include_blocks=(('Includes/Const/Include.inc','module ActionRecordUpdateConst',constants),))
