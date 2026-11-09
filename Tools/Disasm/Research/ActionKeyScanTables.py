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
NAMED_TARGETS={
    '@Action.RequestHyperJump.Entry':('Index17',0x70F6),
    '@Action.RequestBoost.Entry':('Index0F',0x74A3),
    '@Action.ActivateAntimissileSystem.Entry':('Index14',0x722E),
    '@Action.RequestAimOrCollectTarget.Entry':('Index06',0x7317),
    '@Action.ToggleViewDirection.Entry':('Index19',0x762A),
    '@Action.EjectCargo.Entry':('Index15',0x7594),
    '@Action.EjectMine.Entry':('Index16',0x75CF),
    '@Action.RequestStationReturn.Entry':('Index12',0x7606),
    '@Action.ToggleFreeFlightMode.Entry':('Index10',0x754C),
    '@Action.ToggleTractorMode.Entry':('Index13',0x7439),
    '@Action.CycleTargetOverlayMode.Entry':('Index11',0x7480),
    '@Action.RequestYNegative.Entry':('Index00',0x7753),
    '@Action.RequestYPositive.Entry':('Index01',0x7776),
    '@Action.RequestXNegative.Entry':('Index02',0x770D),
    '@Action.RequestXPositive.Entry':('Index03',0x7730),
    '@Action.RequestTurnNegative.Entry':('Index04',0x76C7),
    '@Action.RequestTurnPositive.Entry':('Index05',0x76EA),
    '@Action.IncreaseGaugeWord.Entry':('Index07',0x7680),
    '@Action.DecreaseGaugeWord.Entry':('Index08',0x76A3),
    '@Action.IgnoreKey.Entry':('Index18',0x704B),
    '@Action.RequestMissile0.Entry':('Index0C',0x704C),
    '@Action.RequestMissile1.Entry':('Index0D',0x7075),
    '@Action.RequestMissile2.Entry':('Index0E',0x7088),
    '@Action.ClearMissileTargets.Entry':('Index0B',0x72BE),
    '@Action.ToggleTargetRequest.Entry':('Index0A',0x72E2)}


def origin(table):return 0x5DC3 if table[0]=='ActionKeyHandlerPointers' else 0x6000


def render(source,table):
    text,labels=render_records(source,table,origin(table))
    if table[0]=='ActionKeyHandlerPointers':
        lines=text.splitlines();count=0
        for index,line in enumerate(lines):
            for target,(_,address) in NAMED_TARGETS.items():
                if line.partition(';')[0].strip()=='#'+format(address,'04X'):
                    lines[index]=(' '*20+target).ljust(80)+';'+line.partition(';')[2]
                    count+=1
        assert count==len(NAMED_TARGETS)
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
            if value in NAMED_TARGETS:
                assert module=='ActionKeyHandlerPointers' and name==NAMED_TARGETS[value][0]
            else:
                assert re.fullmatch(r'#[0-9A-F]{'+str(2*width)+'}'+(',' if index+1<len(fields) else ''),value)
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #'+format(origin(table)+end,'04X'),'endmodule']
    for target,(_,address) in NAMED_TARGETS.items():text=text.replace(target,'#'+format(address,'04X'))
    return parse_records(text,table,origin(table))


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0x6F1D:
        operation=operation.replace('LD IX, #9D4C','LD IX, @ActionKeyScanInputs.Index00.RowSelect')
        operation=operation.replace('LD DE, #7015','LD DE, @ActionKeyHandlerPointers.Index00 - 2')
    return operation
