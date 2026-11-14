"""State11, сохранённые через AF' флаги таймера, две фазы и переход 10."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from CheckActionMissileConsume import dec_flags
from CheckActionRecordIndex import add_flags
from ReferenceControlsPointRespawn import refresh


def profiles():
    for timer in range(256):
        for first in range(256):
            for carry in (0,1):yield timer,first,(timer+73*first)&255,carry,'all_timers_phase1_and_carry'
    for first in range(256):
        for second in range(256):yield 1,first,second,(first+second)&1,'all_phase_pairs_on_transition'


def reference(initial, record, ix):
    # Префикс сохраняет флаги таймера вокруг двух ADD через альтернативный AF.
    wanted = list(initial)
    timer, first, second = record[23], record[8], record[9]
    new_timer, next_first, next_second = (timer - 1) & 255, (first + 4) & 255, (second + 2) & 255
    wanted[0:2] = [new_timer, dec_flags(timer, initial[1] & 1)]
    wanted[16:18] = [next_second, add_flags(second, 2)]
    operations = [(ix + 23, new_timer), (ix + 8, next_first), (ix + 9, next_second)]
    if new_timer == 0:
        operations.extend(((ix + 23, 70), (ix + 10, 16)))
        m1, path = 23, 'state_10'
    else:
        m1, path = 18, 'continue'
    wanted[15], wanted[24] = refresh(initial[15], m1), 0xF0F8
    return wanted, operations, path


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;counts=Counter();paths=Counter();witnesses={}
    witness_cases={(2,28,254,0):'continue_even_when_phase_Z',(1,14,255,0):'transition_even_when_phase_NZ'}
    for timer,first,second,carry,profile in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        ix=0xA100+64*(cases%26);stack=0xBFFE
        memory[ix+23],memory[ix+8],memory[ix+9]=timer,first,second
        memory[ix+10]=17;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0xF3A1,'SP':stack,'AF':0xA5FE|carry,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':(cases*109)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        wanted,operations,path=reference(initial,{23:timer,8:first,9:second},ix)
        expected=[bytearray(bank) for bank in memory.banks];writes=[]
        for address,value in operations:expected[2][address&0x3FFF]=value;writes.append((2,address&0x3FFF,value))
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(40):
            if simulator.registers[24]==0xF0F8:break
            simulator.run()
        else:raise AssertionError('не достигнут общий хвост')
        memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,timer,first,second,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert memory.banks==expected and Counter(memory.writes)==Counter(writes)
        # Проверка противоположных Z таймера и фазы, ветвление должно следовать основной паре AF.
        witness=witness_cases.get((timer,first,second,carry))
        if witness:
            regs=simulator.registers
            assert bool(regs[1]&64)!=bool(regs[17]&64)
            assert not regs[1]&1 and regs[17]&1
            assert memory[ix+10]==(16 if timer==1 else 17)
            witnesses[witness]=dict(timer_in=timer,phase1_in=first,phase2_in=second,
                final_AF=regs[0]*256+regs[1],final_AF_prime=regs[16]*256+regs[17],
                timer_out=memory[ix+23],state_out=memory[ix+10],outcome=path)
        cases+=1;counts[profile]+=1;paths[path]+=1
    assert cases==196608 and set(witnesses)==set(witness_cases.values())
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),all_timer_phase1_carry_products=True,
        all_phase_pairs_on_state_transition=True,AF_prime_contains_second_phase_add_result=True,
        opposite_timer_and_phase_Z_witnesses=witnesses,all_joint_input_products_exhausted=False,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        cpu_stack_written=False,common_tail_executed=False,boundary=0xF0F8,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionTimedPhaseStateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
