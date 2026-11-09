"""Извлечение исследовательского представления исходных заметок без изменения сборочных ресурсов."""
from pathlib import Path
import hashlib,json,re
from CheckIntro import ROOT


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==17)
    start,end=0x516F,0x6000
    source=(ROOT/(entry['path']+'.bin')).read_bytes();raw=source[start:end]
    # Проверка совпадения физического образа, извлечённого файла и ресурса текущих исходников.
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert raw==original[entry['offset']+start:entry['offset']+end]
    source_map=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_bytes())
    resource=next(row['path'] for row in source_map if row['slot']==17 and row['offset']==start and row['length']==end-start)
    assert raw==(ROOT/resource).read_bytes() and len(raw)==3729
    decoded=raw.decode('cp866');assert decoded.encode('cp866')==raw
    assert b'\n' not in raw and '\u0421\u0420\u0415\u0414\u041d\u0418\u0419' in decoded
    # Создание представления с явными управляющими байтами, имена не переносятся автоматически в код.
    rendered=''.join('\n' if byte==13 else f'\\x{byte:02X}' if byte<32 or byte==127 else bytes([byte]).decode('cp866') for byte in raw)
    path=ROOT/'Tools/Disasm/Research/Evidence/ActionEmbeddedNotes.txt'
    if path.exists():assert path.read_text('utf-8').replace('\r\n','\n')==rendered
    else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(rendered,'utf-8')
    labels=re.findall(r'(?m)^([A-Z][A-Z0-9]*):',rendered)
    result=dict(passed=True,method='physical_original_bytes_with_lossless_cp866_interpretation',
        slot=17,file_offset=start,length=len(raw),runtime_range=[0xB16F,0xBFFF],
        image_offset=entry['offset']+start,sha256=hashlib.sha256(raw).hexdigest(),
        source_resource=resource,decoded_evidence='Tools/Disasm/Research/Evidence/ActionEmbeddedNotes.txt',
        visible_labels=labels,control_bytes_rendered_as_hex=True,original_resource_modified=False,
        source_map_classification_changed=False,live_game_consumer_proved=False,
        labels_and_layout_of_current_binary_automatically_assumed=False,
        complete_document_present=False,assembly_executed=False,native_execution=False)
    report=ROOT/'Tools/Disasm/Reports/ActionEmbeddedNotesInspection.json'
    if report.exists():
        previous=json.loads(report.read_bytes());assert (previous['slot'],previous['file_offset'],previous['length'],previous['sha256'])==(17,start,len(raw),result['sha256'])
        report=ROOT/'Tools/Disasm/Reports/ActionEmbeddedNotesVerification.json'
        result['historical_inspection_preserved']=True
        result['current_source_kind']=next(row['kind'] for row in source_map if row['path']==resource)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
