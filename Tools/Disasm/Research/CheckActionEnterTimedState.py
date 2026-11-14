"""62B5, все пары R/старое состояние и реальная рамка из трёх сохранённых слов."""
from collections import Counter
from itertools import product
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceActionLinkedMotionGate import MotionGateMachine


def check_timed_state_sequence(baseline):
    ix, stack = 0xA100, 0xBFFE
    total_ticks = 0
    profiles = 0
    for refresh_low, old_state in product(range(16), (0, 0x10, 0x11, 0xFF)):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=0x10)
        memory[ix + 8], memory[ix + 9] = 0xF8, 0xFC
        memory[ix + 0x0A], memory[ix + 0x0B] = old_state, 0xFF
        memory[0xA781] = 0x80
        memory[stack], memory[stack + 1] = 0xFF, 0x3F
        cpu = Simulator(memory)
        cpu.registers[:] = get_registers(
            {'PC': 0x62B5, 'SP': stack - 6, 'IX': ix, 'R': (refresh_low - 9) & 15}, None, False)
        cpu.run(0x62B5, 0x3FFF)
        duration = refresh_low + 5
        assert (memory[ix + 0x0A], memory[ix + 0x17], memory[ix + 0x19]) == (0x11, duration, old_state)
        assert cpu.registers[SP] == stack + 2
        # Исполняется табличная диспетчеризация, каждый тик останавливается у общего F0F8.
        for tick in range(1, duration + 71):
            cpu.registers[SP] = stack
            cpu.run(0xF843, 0xF0F8)
            if tick < duration:
                state, timer = 0x11, duration - tick
            elif tick < duration + 70:
                state, timer = 0x10, duration + 70 - tick
            else:
                state, timer = old_state, 0
            context = (refresh_low, old_state, tick)
            assert cpu.registers[PC] == 0xF0F8 and cpu.registers[SP] == stack - 4, context
            assert (memory[ix + 0x0A], memory[ix + 0x17], memory[ix + 0x19]) == (state, timer, old_state), context
            phase_ticks = min(tick, duration)
            assert memory[ix + 8] == (0xF8 + 4 * phase_ticks) & 0xFF, context
            assert memory[ix + 9] == (0xFC + 2 * phase_ticks) & 0xFF, context
            total_ticks += 1
        profiles += 1
    return dict(profiles=profiles, dispatched_ticks=total_ticks, states=[0x11, 0x10],
                phase_11_duration_range=[5, 20], phase_10_duration=70,
                previous_code_restored=True, unavailable_link_fixture=True,
                common_tail_executed=False)


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory);cases=0;timers=Counter()
    for r in range(256):
        for state in range(256):
            memory.recording=False
            for page in (0,2,5):memory.banks[page][:]=baseline[page]
            ix=0xA100;stack=0xBFF8;memory[ix+10]=state
            for k,word in enumerate((cases*73&65535,cases*109&65535,cases*137&65535,0x3FFF)):
                memory[stack+2*k],memory[stack+2*k+1]=word&255,word>>8
            initial=get_registers({'PC':0x62B5,'SP':stack,'AF':cases&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0xA140},None,False)
            initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
            model=MotionGateMachine(memory.banks,initial);model.enter_timed()
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(start=0x62B5,stop=0x3FFF);memory.recording=False
            compared=(*range(25),26,27)
            assert all(model.r[i]==simulator.registers[i] for i in compared),(cases,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
            assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM')
            timers[memory[ix+23]]+=1;cases+=1
    assert cases==65536 and set(timers)==set(range(5,21))
    result=dict(passed=True,total_cases=cases,all_initial_R_by_all_old_states=True,timers=dict(timers),
        timed_state_sequence=check_timed_state_sequence(baseline),
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        restores_three_words_before_outer_RET=True,additional_stack_writes=False,refresh_m1=17,
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionEnterTimedStateVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
