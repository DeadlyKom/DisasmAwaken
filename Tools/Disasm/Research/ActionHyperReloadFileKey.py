"""Физический ключ ACTION в девятибайтовом хвосте копируемой стадии гиперперехода."""
import re
FIELDS=(('Name',8,'восемь символов имени с исходными пробелами'),('Extension',1,'тип C'))
TABLES=((17,0x2DF8,('ActionHyperReloadFileKey','Source/Action/Data/HyperReloadFileKey.asm',0x1462,0x146B,
    'FTrDosFileKey',FIELDS,('Action',))),)
BINDINGS=()
REQUIRED_REPORTS=('ActionHyperReloadVerification','ActionHyperJumpPreparationVerification')
DOCUMENT='ActionHyperReload'
TAG='ActionHyperReloadFileKey'


def validate_sources(sources):
    assert sources[17][0x1462:0x146B]==b'ACTION  C'
    return dict(file_key_bytes=9,source_runtime_address=0x7225,copied_runtime_address=0x425A,terminator_present=False)


def render(source,origin,table):
    module,path,start,end,structure,fields,names=table;assert source[start:end]==b'ACTION  C'
    lines=['                module '+module,
      '                ; Документация [ключ копируемого загрузчика](../../../Docs/ActionHyperReload.md)',
      '                assert $ == #425A',
      ('Action:         FTrDosFileKey { { "ACTION  " }, #43 }').ljust(80)+'; Name и Extension, исходные два пробела, тип C, терминатора нет',
      '                assert $ == #4263','                endmodule']
    text='\n'.join(lines)+'\n';raw,labels=parse(text,origin,table);assert raw==source[start:end]
    return text,labels


def parse(text,origin,table):
    clean='\n'.join(line.split(';',1)[0] for line in text.splitlines())
    match=re.search(r'Action:\s+FTrDosFileKey\s*\{\s*\{\s*"([^"]{8})"\s*\},\s*#([0-9A-Fa-f]{2})\s*\}',clean)
    assert match and len(re.findall('FTrDosFileKey',clean))==1
    raw=match[1].encode('ascii')+bytes([int(match[2],16)]);assert raw==b'ACTION  C'
    return raw,{'ActionHyperReloadFileKey.Action':0x425A,'ActionHyperReloadFileKey.Action.Name':0x425A,'ActionHyperReloadFileKey.Action.Extension':0x4262}


def structures():return ''
