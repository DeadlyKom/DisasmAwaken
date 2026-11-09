"""Физические суффиксы небейсиковых файлов, длина каталога не используется как доказательство неиспользуемости."""
import hashlib,json
from CheckIntro import ROOT


def main():
    reports=ROOT/'Tools/Disasm/Reports';manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes());entries={e['slot']:e for e in manifest['entries']}
    sm=json.loads((reports/'SourceMap.json').read_bytes());image=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes();rows=[];excluded=[]
    for fragment in sm:
        entry=entries[fragment['slot']];end=fragment['offset']+fragment['length'];length=entry['length']
        if fragment['kind']!='unclassified' or end<=length:continue
        if fragment['slot']==3:
            excluded.append(dict(path=fragment['path'],reason='BASIC имеет машинные модули после объявленной длины, общая классификация хвостом запрещена'));continue
        start=max(length,fragment['offset']);raw=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
        assert len(raw)==entry['allocated_length'] and entry['allocated_length']==entry['sector_count']*256
        assert raw==image[entry['offset']:entry['offset']+len(raw)]
        current=(ROOT/fragment['path']).read_bytes();assert current==raw[fragment['offset']:end]
        assert hashlib.sha256(current).hexdigest()==fragment['sha256']
        assert end<=entry['allocated_length'] and start>=length
        rows.append(dict(slot=fragment['slot'],name=entry['name'],old_path=fragment['path'],old_offset=fragment['offset'],old_length=fragment['length'],
            suffix_offset=start,suffix_length=end-start,declared_length=length,allocated_length=entry['allocated_length'],
            suffix_sha256=hashlib.sha256(raw[start:end]).hexdigest(),logical_prefix_kept_unknown=start-fragment['offset'],
            all_bytes_preserved=True,unused_proved=False,game_reader_or_writer_proved=False))
    assert len(rows)==16 and sum(r['suffix_length'] for r in rows)==2558
    assert sum(r['logical_prefix_kept_unknown']>0 for r in rows)==2
    result=dict(passed=True,method='original_disk_catalog_declared_length_and_allocated_sector_boundaries',
        source_map_sha256=hashlib.sha256((reports/'SourceMap.json').read_bytes()).hexdigest(),records=rows,
        selected_ranges=16,physical_suffix_bytes=2558,basic_ranges_excluded=excluded,
        classification_scope='physical_allocated_suffix_only_not_game_semantics',
        no_direct_or_indirect_reader_absence_assumed=True,source_map_changed=False,assembly_executed=False,native_execution=False)
    (reports/'AllocatedSectorSuffixInspection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','basic_ranges_excluded')},indent=2))


if __name__=='__main__':main()
