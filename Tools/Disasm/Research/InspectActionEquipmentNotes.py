"""Побайтовая связь встроенного авторского описания оборудования и исходного блока ACTION."""
from pathlib import Path
import hashlib,json,re
from CheckIntro import ROOT


def decode_rows(blob,initial_group):
    rows=[];group=initial_group;group_index=0
    for line in blob.split(b'\r'):
        label=re.fullmatch(rb'([A-Z][A-Z0-9]*):',line)
        if label:group=label[1].decode('ascii');group_index=0;continue
        # Чтение только числовых литералов выделенной последовательности, текст не исполняется.
        match=re.fullmatch(rb'\x06\x8c\x05g\x06\x83(#[0-9A-Fa-f]+|[0-9]+)(?:;(.+))?',line)
        if match:
            literal=match[1].decode('ascii');value=int(literal[1:],16) if literal.startswith('#') else int(literal)
            assert 0<=value<256
            rows.append(dict(author_group=group,group_index=group_index,value=value,
                author_comment=(match[2] or b'').decode('cp866')))
            group_index+=1
    return rows


def main():
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();notes=source[0x516F:0x6000]
    ship=decode_rows(notes[notes.index(b'FUEL:'):notes.index(b'WSKMI:')],'FUEL')
    skimmer=decode_rows(notes[notes.index(b'WSKMI:'):notes.index('СОСТОЯНИЕ НОВОСТЕЙ'.encode('cp866'))],'WSKMI')
    assert len(ship)==34 and len(skimmer)==15
    assert ship[-1]['value']==skimmer[-1]['value']==128
    rows=ship+skimmer;raw=bytes(row['value'] for row in rows)
    assert raw==source[0x3C10:0x3C41] and len(raw)==49
    # Проверка исходного диска независимо от текущего ресурса и текстового представления заметок.
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==17)
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert raw==original[entry['offset']+0x3C10:entry['offset']+0x3C41]
    for index,row in enumerate(rows):row.update(address=0x9C10+index,file_offset=0x3C10+index)
    result=dict(passed=True,method='numeric_literals_from_embedded_original_notes_match_entire_initial_byte_sequence',
        matched_bytes=49,ship_bytes=34,skimmer_bytes=15,start_address=0x9C10,end_exclusive=0x9C41,
        notes_file_offset=0x516F,notes_sha256=hashlib.sha256(notes).hexdigest(),
        initial_codes_sha256=hashlib.sha256(raw).hexdigest(),rows=rows,
        direct_consumers_already_established={
            '9C10..9C11':'SelectFuelStock, пополнение разрешается кодом по 9C29',
            '9C12..9C13':'SelectMissileStock и ConsumeMissileStock, вывод остатка ракет',
            '9C1A..9C1B':'CheckRecordEffectThreshold, допуски 1E и 3C при LinkIndex=1A и бите 3',
            '9C1C..9C1E':'UpdateFrame, стоимость события 3, 2 или 1 по первому байту не FF',
            '9C29':'UpdateBodyMotion, FF запрещает путь пополнения счётчика'},
        all_game_consumers_of_each_named_item_proved=False,skimmer_gameplay_proved=False,
        original_bytes_modified=False,source_map_changed=False,assembly_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionEquipmentNotesMapping.json'
    assert not path.exists();path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','direct_consumers_already_established')},indent=2))


if __name__=='__main__':main()
