"""Физические 26 отдельных указателей и 27 читаемых пар IN, перекрывающееся слово не дублируется."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records
POINTER_FIELDS=(('Target',2,'адрес обработчика в общей RAM, назначение описывается отдельно для каждой цели'),)
INPUT_FIELDS=(('RowSelect',1,'старший байт порта IN A,(C), младший байт FE'),
              ('InputMask',1,'маска входного байта, нулевой результат AND допускает обработчик'))
TABLES=(
    ('ActionKeyHandlerPointers','Source/Action/Data/KeyHandlerPointers.asm',0x1254,0x1288,
     'FKeyHandlerPointer',POINTER_FIELDS,tuple('Index'+format(i,'02X') for i in range(26))),
    ('ActionKeyScanInputs','Source/Action/Data/KeyScanInputs.asm',0x3D4C,0x3D82,
     'FKeyScanInput',INPUT_FIELDS,tuple('Index'+format(i,'02X') for i in range(27))))


def origin(table):return 0x5DC3 if table[0]=='ActionKeyHandlerPointers' else 0x6000


def render(source,table):
    text,labels=render_records(source,table,origin(table))
    if table[0]=='ActionKeyHandlerPointers':
        lines=text.splitlines();count=0
        for index,line in enumerate(lines):
            if line.partition(';')[0].strip()=='#704B':
                lines[index]=(' '*20+'@Action.IgnoreKey.Entry').ljust(80)+';'+line.partition(';')[2]
                count+=1
        assert count==1
        text='\n'.join(lines)+'\n'
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[частичный диспетчер клавиш](../../../Docs/ActionKeyDispatchPrefix.md)'),labels


def parse(text,table):
    module,path,start,end,structure,fields,names=table
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module '+module and clean.pop(0)=='assert $ == #'+format(origin(table)+start,'04X')
    for name in names:
        assert clean.pop(0)==(name+':').ljust(16)+structure+' {'
        for index,(_,width,_) in enumerate(fields):
            value=clean.pop(0)
            if value=='@Action.IgnoreKey.Entry':
                assert module=='ActionKeyHandlerPointers' and name=='Index18'
            else:
                assert re.fullmatch(r'#[0-9A-F]{'+str(2*width)+'}'+(',' if index+1<len(fields) else ''),value)
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #'+format(origin(table)+end,'04X'),'endmodule']
    return parse_records(text.replace('@Action.IgnoreKey.Entry','#704B'),table,origin(table))


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0x6F1D:
        operation=operation.replace('LD IX, #9D4C','LD IX, @ActionKeyScanInputs.Index00.RowSelect')
        operation=operation.replace('LD DE, #7015','LD DE, @ActionKeyHandlerPointers.Index00 - 2')
    return operation
