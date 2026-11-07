"""Ровно 26 исходных адресов, следующие байты кода частью таблицы не объявляются."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=(('Handler',2,'исходный адрес обработчика полного класса, алгоритм цели исследуется отдельно'),)
TABLE=('ActionClassHandlers','Source/Action/Data/ClassHandlers.asm',0x72D,0x761,
       'FClassHandler',FIELDS,tuple('Class'+format(i,'02X') for i in range(26)))
ORIGIN=0x5DC3
KNOWN_HANDLERS={26004:"Action.ConfigureClass1Link.Entry",25929:"Action.ConfigureClass2Link.Entry",26078:"Action.ConfigureClass3Link.Entry",26029:"Action.ConfigureClass4Link.Entry",25893:"Action.ConfigureClass5Link.Entry",25983:"Action.ConfigureClass6Link.Entry",25958:"Action.ConfigureClass7Link.Entry",25910:"Action.ConfigureClass8Link.Entry",0x6524:"Action.ReturnIgnoredRecordClass.Entry",0x65C6:"Action.ConfigureClass9Link.Entry",0x660E:"Action.ConfigureClass0Link.Entry"}


def render(source):
    text,labels=render_records(source,TABLE,ORIGIN)
    text=text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[диспетчер класса записи](../../../Docs/ActionClassDispatch.md)')
    for address,name in KNOWN_HANDLERS.items():
        lines=[]
        for line in text.splitlines():
            code,sep,note=line.partition(';');code=code.rstrip()
            if code.strip().startswith('#'):code=code.replace('#'+format(address,'04X'),'@'+name)
            if sep and code.strip():assert len(code)<80;line=code.ljust(80)+';'+note
            elif not sep:line=code
            lines.append(line)
        text='\n'.join(lines)+'\n'
    return text,labels


def parse(text):
    for address,name in KNOWN_HANDLERS.items():text=text.replace('@'+name,'#'+format(address,'04X'))
    clean=[line.partition(';')[0].strip() for line in text.splitlines()];clean=[line for line in clean if line]
    assert clean.pop(0)=='module ActionClassHandlers' and clean.pop(0)=='assert $ == #64F0'
    for label in TABLE[6]:
        assert clean.pop(0)==(label+':').ljust(16)+'FClassHandler {'
        assert re.fullmatch(r'#[0-9A-F]{4}',clean.pop(0))
        assert clean.pop(0)=='}'
    assert clean==['assert $ == #6524','endmodule']
    return parse_records(text,TABLE,ORIGIN)
