"""Физические границы BANK0..5 и отрицательные наблюдения без объявления формата или неиспользуемости."""
from collections import Counter
import hashlib,json,math
from CheckIntro import ROOT


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    source_map=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'))
    entries={e['slot']:e for e in manifest['entries']};results=[]
    payloads={slot:(ROOT/(e['path']+'.bin')).read_bytes() for slot,e in entries.items()}
    # Проверка каждой физической копии и геометрии без предположений о номере рабочего банка.
    for slot in range(33,39):
        entry=entries[slot];data=payloads[slot]
        assert entry['name']=='BANK'+str(slot-33) and entry['length']==entry['allocated_length']==16384
        assert entry['parameter']==0xC000 and entry['sector_count']==64 and entry['first_sector']==6
        assert data==original[entry['offset']:entry['offset']+16384]
        mapped=[r for r in source_map if r['slot']==slot]
        assert len(mapped)==1 and mapped[0]['kind']=='unclassified' and data==(ROOT/mapped[0]['path']).read_bytes()
        # Поиск только буквальных имён в извлечённых полезных данных, динамический поиск этим не исключается.
        needle=entry['name'].encode('ascii');occurrences=[]
        for other,payload in payloads.items():
            start=0
            while (found:=payload.find(needle,start))>=0:
                occurrences.append(dict(slot=other,offset=found));start=found+1
        counts=Counter(data);entropy=-sum(n/len(data)*math.log2(n/len(data)) for n in counts.values())
        results.append(dict(slot=slot,name=entry['name'],image_offset=entry['offset'],
            first_lba=entry['offset']//256,sectors=64,catalog_parameter=0xC000,
            catalog_parameter_is_not_runtime_load_proof=True,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
            source_resource=mapped[0]['path'],literal_name_payload_occurrences=occurrences,
            byte_entropy=round(entropy,6),most_common_bytes=counts.most_common(8),
            hr_prefix_matches=False,first_twelve_bytes=data[:12].hex(),
            hr_header_candidate_unpacked_size=int.from_bytes(data[2:4],'little'),
            hr_header_candidate_packed_size=int.from_bytes(data[4:6],'little')))
        assert data[:2]!=b'HR'
    result=dict(passed=True,method='original_disk_catalog_payload_and_source_resource_comparison',
        physical_bytes_checked=98304,records=results,
        preview_hypotheses=['raw_bit_rows_256x512','first_6912_bytes_as_ULA','raw_gray_bytes_128x128'],
        previews_establish_format=False,compression_excluded=False,unreferenced_status_proved=False,
        runtime_bank_numbers_proved=False,game_loader_proved=False,source_map_changed=False,
        original_bytes_modified=False,assembly_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/AuxiliaryBankPayloadInspection.json'
    assert not target.exists();target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(dict(passed=True,physical_bytes_checked=98304,
        name_occurrences_by_slot={r['slot']:len(r['literal_name_payload_occurrences']) for r in results},
        format_proved=False,unclassified_status_preserved=True,assembly_executed=False),indent=2))


if __name__=='__main__':main()
