"""Независимая формула хвоста 6380, без предположений об игровом смысле 9BCD."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh


def cp_flags(left,right):
    return (sub8_flags(left,right)&~0x28)|(right&0x28)


def signed(value):return value if value<128 else value-256


def main():
    original=flat_action();table=original[0x634B:0x635B]
    assert table==list(bytes.fromhex('fa 0a 0f 12 09 fa fa fa 06 00 00 00 00 00 00 00'))
    memory=Memory(original);simulator=Simulator(memory);counts=Counter();paths=Counter()

    def check(index,mode,old,kind):
        serial=counts.total();memory.recording=False
        memory[0x9B83],memory[0x9BCD]=mode,old;memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':index*256+0xA7,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0x6380},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);writes=[]
        if index>=16:
            wanted[0:2]=[index,cp_flags(index,16)];m1=3;paths['index_rejected']+=1
        else:
            delta=signed(table[index]);boost=bool(mode and delta>=0)
            delta+=10 if boost else 0
            total=signed(old)+delta
            clamped=max(0,min(127,total));result=clamped|(32 if old<32 else 0)
            wanted[0:2]=[result,cp_flags(old,32)]
            wanted[2:4]=[old,result];wanted[6:8]=[0x63,0x4B+index]
            writes=[(0x9BCD,result)];expected[0x9BCD]=result
            # Расчёт M1 по независимым решениям формулы, переполнение учитывает SUB перед проверкой знака.
            overflow=not -128<=total<=127
            negative=(old>=128) if overflow else total<0
            m1=23+(5 if boost else 3 if mode else 0)+2*overflow+negative+2*(old<32)
            paths['clamp_high' if total>127 else 'clamp_low' if total<0 else 'in_range']+=1
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(40):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',index,mode,old))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(index,mode,old,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==writes,(index,mode,old,memory.writes,writes)
        counts[kind]+=1
    # Проверка каждого допустимого индекса и исходного байта в двух классах режима.
    for index in range(16):
        for mode in (0,1):
            for old in range(256):check(index,mode,old,'all_valid_indices_and_bytes')
    # Проверка всех значений режима на краях знакового диапазона и границе установки бита 5.
    for index in range(16):
        for mode in range(256):
            for old in (0,31,32,127,128):check(index,mode,old,'all_mode_bytes')
    # Проверка каждого недопустимого индекса в 256 сценариях с различными входными AF.
    for index in range(16,256):
        for old in range(256):check(index,old,old,'rejected_indices')
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        method='independent_signed_clamp_and_bit5_formula_against_original_cpu_instructions',
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,no_cpu_stack_writes=True,
        all_type_indices=True,all_state_bytes=True,all_mode_bytes=True,all_joint_inputs_exhausted=False,
        table_signed_deltas=[signed(i) for i in table],game_meaning_of_state_and_mode_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionTypeDeltaVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
