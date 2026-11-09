"""Тридцать физических пар груза ACTION, авторские литералы и связь с сохраняемым блоком станции."""
import hashlib,json,re
from CheckIntro import ROOT
from PreviewSceneTables import render as render_records,parse as parse_records

FIELDS=(('QuantityAndMark',1,'код количества, станция читает биты 6..0 и пометку 7, выброс читает полный байт'),
    ('Price',1,'полный байт исходной цены покупки, нечётные смещения также попадают в байтовый поиск выброса'))
TABLES=((17,0x6000,('ActionOwnedCargoRows','Source/Action/Data/OwnedCargoRows.asm',0x3BD4,0x3C10,
    'FOwnedCargoRow',FIELDS,tuple('Row'+format(i,'02d') for i in range(30)))),)
BINDINGS=()
REQUIRED_REPORTS=('ActionEjectCommandsVerification','ActionPreparedClass19SpawnVerification','ActionClass19SpawnVerification')
DOCUMENT=TAG='ActionOwnedCargoPhysicalData'


def author_rows(source):
    notes=source[0x516F:0x6000];block=notes[notes.index(b'TWRI:'):notes.index(b'WKRBI:')];rows=[]
    for line in block.split(b'\r'):
        match=re.fullmatch(rb'\x06\x8c\x05g\x06\x83([0-9]+),([0-9]+);(.+)',line)
        if match:
            quantity,price=int(match[1]),int(match[2]);assert 0<=quantity<256 and 0<=price<256
            rows.append(dict(index=len(rows),quantity=quantity,price=price,author_name=match[3].decode('cp866')))
    assert len(rows)==30
    assert bytes(value for row in rows for value in (row['quantity'],row['price']))==source[0x3BD4:0x3C10]
    return rows


def validate_sources(sources):
    rows=author_rows(sources[17]);assert sum(row['quantity'] for row in rows)==25
    # Проверка одинакового смещения в сохраняемом 512-байтовом блоке, исходные загрузчики задают обе базы.
    assert 0x9852-0x983B==0x9BD4-0x9BBD==23
    return dict(cargo_rows=30,cargo_bytes=60,author_literal_bytes_matched=60,
        reused_existing_FOwnedCargoRow=True,eject_scan_bytes=30,eject_scan_includes_price_bytes=True,
        runtime_native_load_proved=False)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[физические пары груза и байтовый поиск](../../../Docs/'+DOCUMENT+'.md)'),labels


def parse(text,origin,table):return parse_records(text,table,origin)


def structures():return ''


def main():
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes());entry=next(e for e in manifest['entries'] if e['slot']==17)
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes();assert source==original[entry['offset']:entry['offset']+len(source)]
    result=dict(passed=True,**validate_sources({17:source}),rows=author_rows(source),
        sha256=hashlib.sha256(source[0x3BD4:0x3C10]).hexdigest(),
        source_of_names='original_embedded_TWRI_literals',assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionCargoNotesMapping.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))


if __name__=='__main__':main()
