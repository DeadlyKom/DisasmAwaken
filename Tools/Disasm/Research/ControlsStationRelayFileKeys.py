"""Две реальные девятибайтовые записи STATIONF, разные копии и разные рабочие адреса."""
import re
FIELDS=(('Name',8,'восемь символов STATIONF'),('Extension',1,'тип C без терминатора'))
TABLES=(
 (23,0x3E35,('ControlsDirectStationKey','Source/Controls/Data/DirectStationKey.asm',0x1FC,0x205,'FTrDosFileKey',FIELDS,('Value',))),
 (23,0x3FBB,('ControlsStateStationKey','Source/Controls/Data/StateStationKey.asm',0x276,0x27F,'FTrDosFileKey',FIELDS,('Value',))))
BINDINGS=()
REQUIRED_REPORTS=('ControlsDirectStationRelayVerification','ControlsStateStationRelayVerification')
DOCUMENT='ControlsDirectStationRelay'
TAG='ControlsStationRelayFileKeys'


def validate_sources(sources):
    assert sources[23][0x1FC:0x205]==sources[23][0x276:0x27F]==b'STATIONFC'
    return dict(physical_file_keys=2,total_key_bytes=18,runtime_addresses=[0x4031,0x4231],terminators_present=False)


def render(source,origin,table):
    module,path,start,end,structure,fields,names=table;assert source[start:end]==b'STATIONFC'
    doc='ControlsDirectStationRelay' if start==0x1FC else 'ControlsStateStationRelay'
    lines=['                module '+module,'                ; Документация [ключ перенесённой загрузки станции](../../../Docs/'+doc+'.md)',
      '                assert $ == #'+format(origin+start,'04X'),
      'Value:          FTrDosFileKey { { "STATIONF" }, #43 }'.ljust(80)+'; Name и Extension, восемь символов и тип C, терминатора нет',
      '                assert $ == #'+format(origin+end,'04X'),'                endmodule']
    text='\n'.join(lines)+'\n';raw,labels=parse(text,origin,table);assert raw==source[start:end]
    return text,labels


def parse(text,origin,table):
    module,path,start,end,structure,fields,names=table;clean='\n'.join(line.split(';',1)[0] for line in text.splitlines())
    match=re.search(r'Value:\s+FTrDosFileKey\s*\{\s*\{\s*"([^"]{8})"\s*\},\s*#([0-9A-Fa-f]{2})\s*\}',clean)
    assert match and len(re.findall('FTrDosFileKey',clean))==1
    raw=match[1].encode('ascii')+bytes([int(match[2],16)]);assert raw==b'STATIONFC'
    address=origin+start;return raw,{module+'.Value':address,module+'.Value.Name':address,module+'.Value.Extension':address+8}


def structures():return ''
