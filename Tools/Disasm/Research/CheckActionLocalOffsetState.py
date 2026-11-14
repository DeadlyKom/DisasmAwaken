"""F6CD и State04, отдельные байты 0D..0F как фазы, все умножители до внешнего RET."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import put
from CheckActionRecordIndex import add_flags
from ReferenceActionObjectOffsetVector import evaluate
from ReferenceControlsPointRespawn import refresh


def check_inherited_local_phases(baseline):
    parent, child, stack = 0xA100, 0xA140, 0xBFFE
    for value in range(256):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=0x10)
        phases = (value, value ^ 0xA5, (value * 73) & 0xFF)
        put(memory, parent + 7, phases)
        memory[child + 0x10] = value
        sim = Simulator(memory, {'PC': 0x6482, 'SP': stack, 'IX': parent, 'IY': child})
        memory.writes = []
        memory.recording = True
        sim.run(0x6482, 0x6494)
        assert memory.writes == [(2, (child + offset) & 0x3FFF, phase)
                                 for offset, phase in zip((0x0D, 0x0E, 0x0F), phases)]
        assert sim.registers[SP] == stack
        sim.registers[:] = get_registers({'PC': 0xF6CD, 'SP': stack, 'IX': child}, None, False)
        memory.writes.clear()
        original_phase0 = memory[child + 7]
        sim.run(0xF6CD, 0x6D06)
        assert sim.registers[PC] == 0x6D06 and sim.registers[SP] == stack
        assert tuple(sim.registers[4:6]) == (0, value)
        assert memory.writes == [(2, (child + 7) & 0x3FFF, (original_phase0 + 1) & 0xFF),
                                 (2, 0x3045, phases[0]), (2, 0x304F, phases[1] ^ 0x80),
                                 (2, 0x305C, phases[2])]
        assert tuple(memory[child + 0x0D:child + 0x10]) == phases
    return dict(profiles=256, original_phase_writer_and_reader=True,
                reader_stop_before_multiply=0x6D06, field_byte_offsets=[0x0D, 0x0E, 0x0F])


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;counts=Counter();overflows=Counter()
    for entry in (0xF6CD,0xF6AB):
        for first in range(256):
            for second in range(256):
                memory.recording=False
                for page in (0,2,5):memory.banks[page][:]=baseline[page]
                ix=0xA100+64*(cases%26);stack=0xBFFE
                phases=[first^second,first,second];raw=(second,first,(73*first+second)&255);rate=(first+second)&255
                for offset,value in zip((7,8,9,13,14,15,16),(*phases,*raw,rate)):memory[ix+offset]=value
                memory[stack],memory[stack+1]=255,63
                initial=get_registers({'PC':entry,'SP':stack,'AF':(first<<8)|second,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
                initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
                operations=[]
                if entry==0xF6AB:
                    # Расчёт всех промежуточных записей, два INC фазы 1 и три INC фазы 2 не сворачиваются в одну запись.
                    for axis,steps in ((1,2),(2,3)):
                        for _ in range(steps):phases[axis]=(phases[axis]+1)&255;operations.append((ix+7+axis,phases[axis]))
                phases[0]=(phases[0]+1)&255;operations.append((ix+7,phases[0]))
                offsets=(raw[0],(raw[1]+128)&255,raw[2])
                operations.extend(zip((0xB045,0xB04F,0xB05C),offsets))
                child=list(initial);child[4:6]=[0,rate];child[0:2]=[raw[2],add_flags(raw[1],128)]
                child[15]=refresh(initial[15],16+(11 if entry==0xF6AB else 0))
                calculated=evaluate(memory,child,offsets,0x3FFF);wanted=calculated['registers'];operations.extend(calculated['writes'])
                expected=[bytearray(bank) for bank in memory.banks];writes=[]
                for address,value in operations:
                    bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                    expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                for _ in range(1000):
                    if simulator.registers[24]==0x3FFF:break
                    simulator.run()
                else:raise AssertionError(('нет возврата',entry,first,second))
                memory.recording=False
                assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,hex(entry),[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
                assert memory.banks==expected and Counter(memory.writes)==Counter(writes),(cases,'RAM')
                counts[hex(entry)]+=1;overflows[str(calculated['overflow'])]+=1;cases+=1
                if cases%32768==0:print(str(cases)+' local offset cases passed',flush=True)
    assert cases==131072
    result=dict(passed=True,total_cases=cases,cases_by_entry=dict(counts),coefficient_overflow_paths=dict(overflows),
        inherited_local_phases=check_inherited_local_phases(baseline),
        all_first_two_offset_bytes_for_core=True,all_phase1_phase2_bytes_for_state04=True,
        all_rate_and_third_offset_bytes_covered=True,real_coefficient_and_three_multiply_children_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        maximum_additional_stack_bytes=6,complete_external_return=True,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLocalOffsetStateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
