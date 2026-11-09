"""Физические границы BANK0..5, текущие графические цепочки и пределы отрицательных наблюдений."""
from collections import Counter
import hashlib,json,math,os,tempfile
from BankArchiveRouteCopies import TABLES as route_tables, parse as parse_route, validate_sources as validate_routes
from CheckIntro import ROOT


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    source_map=json.loads((ROOT/'Tools/Disasm/Reports/SourceMap.json').read_text('utf-8'))
    entries={e['slot']:e for e in manifest['entries']};results=[]
    payloads={slot:(ROOT/(e['path']+'.bin')).read_bytes() for slot,e in entries.items()}
    published={r['path']:r for r in source_map}
    route_bytes=0
    for slot,origin,route in route_tables:
        path=route[1]
        if path in published:
            raw,_=parse_route((ROOT/path).read_text('utf-8'),origin,route)
            assert raw==payloads[slot][route[2]:route[3]] and len(raw)==published[path]['length']
            route_bytes+=len(raw)
    if route_bytes:
        validate_routes(payloads)
    graphic_bytes=sum(r['length'] for r in source_map if r['slot'] in range(33,39) and r['kind']=='typed_data')-route_bytes
    unknown_gap_bytes=98304-graphic_bytes-route_bytes
    if graphic_bytes:
        from BankScreenStrips import verify_published
        verify_published(payloads,source_map)
    # Проверка каждой физической копии и геометрии без предположений о номере рабочего банка.
    for slot in range(33,39):
        entry=entries[slot];data=payloads[slot]
        assert entry['name']=='BANK'+str(slot-33) and entry['length']==entry['allocated_length']==16384
        assert entry['parameter']==0xC000 and entry['sector_count']==64 and entry['first_sector']==6
        assert data==original[entry['offset']:entry['offset']+16384]
        mapped=[r for r in source_map if r['slot']==slot]
        if not graphic_bytes:
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
            source_resources=[row['path'] for row in mapped],literal_name_payload_occurrences=occurrences,
            byte_entropy=round(entropy,6),most_common_bytes=counts.most_common(8),
            hr_prefix_matches=False,first_twelve_bytes=data[:12].hex(),
            hr_header_candidate_unpacked_size=int.from_bytes(data[2:4],'little'),
            hr_header_candidate_packed_size=int.from_bytes(data[4:6],'little')))
        assert data[:2]!=b'HR'
    result=dict(passed=True,method='original_disk_catalog_payload_and_source_resource_comparison',
        physical_bytes_checked=98304,records=results,graphic_source_bytes_verified=graphic_bytes,
        route_copy_bytes_verified=route_bytes,unknown_gap_bytes=unknown_gap_bytes,
        preview_hypotheses=['raw_bit_rows_256x512','first_6912_bytes_as_ULA','raw_gray_bytes_128x128'],
        previews_establish_format=False,compression_excluded=False,unreferenced_status_proved=False,
        runtime_bank_numbers_proved=False,game_loader_proved=False,source_map_changed=False,
        original_bytes_modified=False,assembly_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/AuxiliaryBankPayloadInspection.json'
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='bank-boundaries-',suffix='.tmp',delete=False) as out:
        temporary=out.name;out.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,target)
    print(json.dumps(dict(passed=True,physical_bytes_checked=98304,
        name_occurrences_by_slot={r['slot']:len(r['literal_name_payload_occurrences']) for r in results},
        graphic_source_bytes_verified=graphic_bytes,route_copy_bytes_verified=route_bytes,
        unknown_gap_bytes=unknown_gap_bytes,
        game_loader_proved=False,assembly_executed=False),indent=2))


if __name__=='__main__':main()
