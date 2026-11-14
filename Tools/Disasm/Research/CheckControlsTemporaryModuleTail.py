"""Условный хвост DB29 после нормального возврата временного кода, штатный вход не доказан."""
import json
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC,SP,Simulator,get_registers
from CheckScreenUpdate import PortTrace,put
from skoolkit.simutils import I, IFF, IM


def check_tail_DI(baseline):
    cases = []
    for initial_iff in (0, 1):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=17)
        assert memory[0xDB29] == 0xF3
        cpu = Simulator(memory)
        cpu.registers[:] = get_registers({'PC': 0xDB29, 'SP': 0xBFFE, 'I': 0x80}, None, False)
        cpu.registers[IFF], cpu.registers[IM] = initial_iff, 2
        cpu.run()
        assert cpu.registers[PC] == 0xDB2A and cpu.registers[IFF] == 0
        assert cpu.registers[IM] == 2 and cpu.registers[I] == 0x80
        cases.append(dict(initial_iff=initial_iff, final_iff=0,
            original_DI_address=0xDB29, next_pc=cpu.registers[PC],
            I_and_IM_preserved_by_DI=True))
    return cases


def evaluate_tail():
    flat=flat_action();baseline=[bytearray(0x4000) for _ in range(8)]
    for bank,start in ((5,0x4000),(2,0x8000),(0,0xC000)):baseline[bank][:]=bytes(flat[start:start+0x4000])
    baseline[1][:]=bytes(base_memory()[0xC000:])
    template=bytes(baseline[1][0x1ADE:0x1B5D]);assert len(template)==127
    # Используется прежний гипотетический адрес проверки, нового размещения в игре нет.
    fixture=0x5000;start=fixture+0xDB29-0xDADE;cases=[]
    for pattern in (0,0x55,0xA5):
        for saved_stack in (0x3FFE,0x4FFE,0x5FA0):
            memory=RecordedBanks(banks=[bank.copy() for bank in baseline],out7ffd=17)
            original_core=bytes(memory.banks[5][0x2000:])
            original_work=bytes(memory.banks[2][0x0C00:])
            memory.banks[1][0x2000:]=original_core
            memory.banks[6][:0x3400]=original_work
            memory.banks[2][:0xC00]=bytes([pattern])*0xC00
            put(memory,fixture,template);put(memory,0x5E33,saved_stack.to_bytes(2,'little'))
            sim=Simulator(memory);sim.registers[:]=get_registers({'PC':start,'SP':0x6000,
                'HL':0x1357,'DE':0x2468,'BC':0x3579,'AF':0x5A5D,'IX':0x1234,'IY':0x5678,
                '^HL':0x6789,'^DE':0x789A,'^BC':0x89AB,'^AF':0x9ABC},None,False)
            trace=PortTrace(sim);sim.set_tracer(trace)
            for steps in range(100000):
                if sim.registers[PC]==0x6000:break
                sim.run()
            else:raise AssertionError(('instruction_limit',hex(sim.registers[PC])))
            assert trace.writes==[(0x7FFD,22),(0x7FFD,16),(0x7FFD,17)]
            assert bytes(memory.banks[2][0x0C00:])==original_work
            assert bytes(memory.banks[5][0x2000:])==original_core
            assert bytes(memory.banks[2][:0xC00])==bytes([255])*0xC00
            # Проверка настоящего вывода, каждая из 96 растровых строк получает 32 байта FF.
            for y in range(96):
                offset=((y&0xC0)<<5)|((y&7)<<8)|((y&0x38)<<2)
                assert bytes(memory.banks[5][offset:offset+32])==bytes([255])*32
            assert sim.registers[SP]==0x5FFE and bytes(memory[0x5FFE:0x6000])==bytes([0xFD,0x7F])
            assert bytes(memory[0x5E33:0x5E35])==saved_stack.to_bytes(2,'little')
            assert bytes(memory[0x6000:0x6010])==bytes.fromhex('083E11CD1BAB08CD56EC3E10CD1BABC9')
            # Настоящий копировщик читает индексные пары из уже заполненного FF растра.
            assert sim.registers[8:12] == [255, 255, 255, 255]
            cases.append(dict(initial_linear_pattern=pattern,saved_stack_word=saved_stack,
                pc=sim.registers[PC],sp=sim.registers[SP],stack_top_word=0x7FFD,steps=steps,
                final_ix=sim.registers[8]*256+sim.registers[9],
                final_iy=sim.registers[10]*256+sim.registers[11]))
    result=dict(passed=True,cases=cases,first_DI_cases=check_tail_DI(baseline),hypothetical_fixed_copy_fixture=fixture,
        original_tail_and_real_clear_and_copy_executed=True,
        original_core_and_work_restored=True,linear_buffer_and_upper_screen_cleared_to_ff=True,
        restored_entry='Source/Action/QueueNumberBank1.asm',restored_entry_not_executed=True,
        saved_stack_word_not_restored_to_sp=True,remaining_stack_top_word=0x7FFD,
        starts_after_assumed_normal_temporary_call_return=True,
        legitimate_relocation_and_temporary_payload_proved=False,
        irq_executed=False,r_and_timing_proved=False,assembly_executed=False,native_execution=False)
    return result


def main():
    result = evaluate_tail()
    target=ROOT/'Tools/Disasm/Reports/ControlsTemporaryModuleTailVerification.json';assert not target.exists()
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
