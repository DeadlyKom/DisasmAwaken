"""Согласованная адресная база остаточного дискового фрагмента, это не доказательство его переноса игрой."""
import hashlib,json,sys
from CheckIntro import ROOT
from CheckControlsTextQueue import payload
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    source=payload(23);start,end=0x7F,0x13B;raw=source[start:end]
    witnesses=((0x5E4D,0xAD),(0x5ED2,0x132),(0x5ED6,0x136),(0x5E61,0xC1),(0x5E33,0x93))
    bases=[address-offset for address,offset in witnesses];assert set(bases)=={0x5DA0};base=bases[0]
    memory=[0]*65536;memory[base:base+len(source)]=source;instructions=decoder(memory).disassemble(base+start,base+end,'h')
    assert b''.join(i.bytes for i in instructions)==raw
    table={i.address:i for i in instructions}
    assert table[0x5E4D].operation=='LD A,D'
    assert table[0x5ED2].operation=='LD IX,#2A53'
    assert table[0x5ED6].operation=='PUSH IX' and table[0x5ED8].operation=='JP #3D2F'
    assert table[0x5E61].operation=='LD A,(#5D16)'
    assert table[0x5E32].operation=='LD SP,#0000' and source[0x93:0x95]==bytes(2)
    assert source[2:6]==bytes.fromhex('ed73335e')
    branches=[]
    for item in instructions:
        for target,offset in witnesses[:4]:
            if item.operation.endswith('#'+format(target,'04X')) and item.operation.startswith(('CALL ','JP ')):
                branches.append(dict(source_address=item.address,source_offset=item.address-base,operation=item.operation,target_offset=offset))
    assert len(branches)==12,len(branches)
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes());entry=next(e for e in manifest['entries'] if e['slot']==23)
    original=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes();assert raw==original[entry['offset']+start:entry['offset']+end]
    evidence=ROOT/'Tools/Disasm/Research/Evidence/ControlsLegacyDiskFragment.asm.txt'
    lines=['; Исследовательский вид исходных байтов 007F..013A CONTROL. Не включается в сборку.',
      '; База 5DA0 получена из пяти внутренних адресных совпадений. Реальный перенос игрой не доказан.']
    lines += ['; '+format(i.address,'04X')+' '+i.bytes.hex(' ').ljust(14)+' '+i.operation for i in instructions]
    evidence.write_text('\n'.join(lines)+'\n','utf-8')
    result=dict(passed=True,method='five_independent_internal_absolute_address_equalities_and_original_byte_decode',
        slot=23,file_offset=start,code_candidate_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),consistent_legacy_base=base,
        witnesses=[dict(target_address=a,target_file_offset=o,derived_base=a-o) for a,o in witnesses],
        matching_direct_control_references=branches,saved_SP_writer_points_to_legacy_LD_SP_operand=True,
        legacy_fragment_end_after_JP_3D2F=True,remaining_gap_bytes_not_classified=318-len(raw),
        source_map_changed=False,actual_game_relocation_proved=False,actual_game_entry_proved=False,
        TRDOS_ROM_routine_semantics_proved=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsLegacyDiskFragmentInspection.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in result.items() if k not in ('witnesses','matching_direct_control_references')},indent=2))


if __name__=='__main__':main()
