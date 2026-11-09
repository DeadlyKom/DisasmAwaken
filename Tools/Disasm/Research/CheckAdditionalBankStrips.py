"""Полные копии двух растров BANK3 в промежутках BANK4 и BANK5."""
import hashlib,json,os,tempfile
from CheckIntro import ROOT
import BankScreenStrips as facts


def main():
    sources={slot:(ROOT/('Tools/Disasm/Extracted/Active/'+str(slot)+'_BANK'+str(slot-33)+'.C.bin')).read_bytes() for slot in facts.SLOTS}
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    image=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    for entry in manifest['entries']:
        if entry['slot'] in sources:assert sources[entry['slot']]==image[entry['offset']:entry['offset']+16384]
    reference=next(t for t in facts.tables(sources) if t['slot']==36 and t['module'].endswith('Suffix'))
    start=reference['rows'][0]['start'];end=reference['rows'][1]['end'];original=sources[36][start:end]
    assert (start,end,len(original))==(8734,9820,1086)
    rows=[];published=0
    for table in facts.additional_tables(sources):
        slot=table['slot'];assert (table['start'],table['end'])==(start,end)
        data=sources[slot][start:end];assert data==original
        text,labels,bitmaps=facts.render(sources[slot],table)
        assert facts.parse(text,table,bitmaps)==(data,labels)
        if (ROOT/table['path']).exists():
            assert facts.parse((ROOT/table['path']).read_text('utf-8'),table)==(data,labels);published+=1
        rows.append(dict(slot=slot,start=start,end=end,records=2,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    assert len(rows)==2 and published in (0,2)
    result=dict(passed=True,additional_records=4,additional_graphic_bytes=2172,header_bytes=12,bitmap_bytes=2160,
        reference_slot=36,reference_start=start,reference_end=end,complete_header_and_bitmap_copies=True,
        publication_tables_checked=published,rows=rows,overlaps_main_prefix_or_suffix=False,
        runtime_reachability_proved=False,unused_or_garbage_asserted=False,
        hardware_bank_numbers_assigned=False,assembly_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/AdditionalBankStripsVerification.json'
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix='additional-bank-strips-',suffix='.tmp',delete=False) as out:
        temporary=out.name;out.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,path);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
