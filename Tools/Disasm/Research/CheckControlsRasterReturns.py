"""Частичная проверка E2BB до первого RET, все пары изменяемого байта и C, не полный E291."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def main():
    original=base_memory()
    addresses=[original[0xE271+2*i]|(original[0xE272+2*i]<<8) for i in range(16)]
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    instructions=next(r for r in flow if r['name']=='Controls')['instructions']
    defined={i['address'] for i in instructions}
    assert len(set(addresses))==16 and all(address in defined for address in addresses)
    memory=Memory(original)
    simulator=Simulator(memory)
    counts=Counter()
    for operand in range(256):
        for coordinate in range(256):
            memory.recording=False
            memory[0xE2BC],memory[0xE471]=operand,original[0xE471]
            initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x3600|coordinate,
                '^AF':(operand<<8)|coordinate,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
                'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xE2BB},None,False)
            initial[14],initial[15],initial[26],initial[27]=coordinate,(operand+coordinate)&255,operand&1,coordinate%3
            index=(operand-coordinate)&15
            wanted=list(initial)
            index_flags=0x20|(0x40 if index==0 else 0)|(4 if index.bit_count()%2==0 else 0)
            wanted[0:8]=[operand,coordinate,0,0xBC,0x55,0x55,0x48,0xB2]
            wanted[16:24]=[5,index_flags,0x36,coordinate,0x24,0x68,0x13,0x57]
            wanted[SP],wanted[PC],wanted[15]=0xE273+2*index,addresses[index],refresh(initial[15],18)
            writes=[(0xE2BC,index),(0xE471,index)]
            expected=list(memory)
            for address,value in writes:
                expected[address]=value
            simulator.registers[:]=initial
            memory.writes=[]
            memory.recording=True
            # Проверка передачи через RET останавливается до исполнения выбранного рисующего хвоста.
            for _ in range(30):
                if simulator.registers[PC] in addresses:
                    break
                simulator.run()
            else:
                raise AssertionError(('передача',operand,coordinate))
            memory.recording=False
            compared=(*range(13),14,15,*range(16,24),PC,26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared), (operand,coordinate,
                [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert memory==expected and Counter(memory.writes)==Counter(writes)
            counts[index]+=1
    assert all(counts[index]==4096 for index in range(16))
    report=dict(passed=True,total_cases=sum(counts.values()),cases_by_index=dict(sorted(counts.items())),
        all_operand_c_pairs=True,all_alternative_af_words=True,exact_registers_flags_r_sp_and_target=True,
        every_ram_byte_and_write_checked=True,return_table_bytes_unchanged=True,
        dispatch_refresh_m1=18,stopped_before_selected_tail=True,
        full_rasterizer_proved=False,unknown_e291_status_preserved=True,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsRasterReturnsVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
