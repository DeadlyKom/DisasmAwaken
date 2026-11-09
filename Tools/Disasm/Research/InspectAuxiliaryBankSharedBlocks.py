"""Поиск точных общих блоков BANK0..BANK5 с остальными файлами оригинального диска."""
from collections import defaultdict,Counter
import hashlib,json,os,tempfile
from CheckIntro import ROOT


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    payloads={e['slot']:(ROOT/(e['path']+'.bin')).read_bytes() for e in manifest['entries']}
    image=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    for e in manifest['entries']:
        assert payloads[e['slot']]==image[e['offset']:e['offset']+len(payloads[e['slot']])]
    seeds=defaultdict(list);eligible=Counter();matches=[];covered=defaultdict(list)
    # Индексация только точных 64-байтовых окон с восемью различными значениями или более.
    for bank in range(33,39):
        data=payloads[bank]
        for offset in range(len(data)-63):
            block=data[offset:offset+64]
            if len(set(block))>=8:
                seeds[block].append((bank,offset));eligible[bank]+=1
    # Поиск во всех остальных логических файлах, включая удалённые записи.
    for slot,data in payloads.items():
        if slot in range(33,39):continue
        for other_offset in range(len(data)-63):
            block=data[other_offset:other_offset+64]
            for bank,bank_offset in seeds.get(block,()):
                diagonal=(bank,slot,other_offset-bank_offset)
                if any(first<=bank_offset<end for first,end in covered[diagonal]):continue
                source=payloads[bank];first,other=bank_offset,other_offset
                while first and other and source[first-1]==data[other-1]:first-=1;other-=1
                end,other_end=bank_offset+64,other_offset+64
                while end<len(source) and other_end<len(data) and source[end]==data[other_end]:end+=1;other_end+=1
                covered[diagonal].append((first,end))
                assert source[first:end]==data[other:other_end]
                matches.append(dict(bank_slot=bank,bank_offset=first,other_slot=slot,other_offset=other,
                    length=end-first,sha256=hashlib.sha256(source[first:end]).hexdigest()))
    result=dict(passed=True,method='exact_common_64_byte_seeds_with_at_least_eight_distinct_values_and_maximal_extension',
        seed_windows_by_slot=dict(eligible),minimum_seed_length=64,minimum_distinct_seed_values=8,
        includes_deleted_logical_files=True,compares_allocated_sector_tails=False,
        matches=sorted(matches,key=lambda row:(-row['length'],row['bank_slot'],row['bank_offset'])),
        matching_bytes_do_not_prove_runtime_loader=True,formats_or_compression_not_excluded=True,
        semantic_classification_performed=False,assembly_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/AuxiliaryBankSharedBlockInspection.json'
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='shared-bank-blocks-',suffix='.tmp',delete=False) as output:
        temporary=output.name;output.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,target)
    print(json.dumps(dict(passed=True,eligible_seed_windows=sum(eligible.values()),matches=len(matches),
        longest_matches=result['matches'][:8],semantic_classification_performed=False),indent=2))


if __name__=='__main__':main()
