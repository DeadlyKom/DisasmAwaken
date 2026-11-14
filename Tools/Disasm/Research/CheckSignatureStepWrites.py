"""Шаг рабочего ключа, шесть собственных записей и точный R без сборки.

Документация: ../../../Docs/WorldSignature.md#собственные-записи-шага-и-банковых-входов
"""
from hashlib import sha256
import json
from CheckWorldSignature import ROOT,Simulator,get_registers,step_key,logical_flags
from CheckGeometryReturnEntries import Memory


def main():
    m=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    e=next(e for e in m['entries'] if e['slot']==4)
    source=(ROOT/(e['path']+'.sectors.bin')).read_bytes()
    disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest()==m['sha256']
    assert source==disk[e['offset']:e['offset']+e['allocated_length']]
    assert sha256(source).hexdigest()==e['sectors_sha256']
    probe=Memory(65536);probe[0x4000:0x4003]=bytes.fromhex('320070')
    cpu=Simulator(probe);cpu.registers[24]=0x4000;probe.recording=True;cpu.run()
    assert probe.writes==[(0x7000,0)]
    memory=Memory(65536);memory[0x6000:]=source
    cpu=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,
        '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    count=0
    for profile in range(2):
        for first in range(65536):
            second=first^65535 if profile==0 else (((first<<7)|(first>>9))+0x1357)&65535
            memory[0x631C:0x6320]=first.to_bytes(2,'little')+second.to_bytes(2,'little')
            memory[0x7FFE:0x8000]=bytes([255,63])
            cpu.registers[:]=initial;r=cpu.registers;r[0],r[1],r[15]=second&255,first>>8,first&255
            expected=list(r);u,v,checksum=step_key(first,second)
            expected[6],expected[7],expected[4],expected[5]=u>>8,u&255,v>>8,v&255
            expected[0],expected[1],expected[12],expected[24]=checksum,logical_flags(checksum),0x8000,0x3FFF
            expected[15]=(r[15]&128)|((r[15]+32)&127)
            writes=[(0x7FFC,0xC9),(0x7FFD,0x36)]+[(0x631C+i,value) for i,value in enumerate(u.to_bytes(2,'little')+v.to_bytes(2,'little'))]
            memory.writes.clear();memory.recording=True;cpu.run(0xA9F3,0x3FFF);memory.recording=False
            assert memory.writes==writes,(first,second,memory.writes)
            assert all(r[i]==expected[i] for i in range(len(expected)) if i!=25),(first,second,list(r),expected)
            assert memory[0x7FFE:0x8000]==bytes([255,63])
            count+=1
    report=dict(passed=True,cases=count,method='original_signature_step_against_independent_formula_and_write_watch',
        exact_registers_except_T_checked=True,M1=32,exact_own_CPU_writes=6,
        physical_disk_and_sector_hashes_checked=True,CPU_write_watch_positive_control=True,
        original_return_word_preserved=True,second_word_profiles=['complement','rotate7_plus_1357'],
        full_first_second_AF_R_cartesian_product_checked=False,arbitrary_stack_addresses_checked=False,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/SignatureStepWritesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()

