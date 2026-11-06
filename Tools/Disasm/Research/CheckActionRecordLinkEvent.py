"""635B, преобразование полей записи и продолжение в реальный ApplyIndexedDelta."""
from collections import Counter
import json,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckActionTypeDelta import cp_flags,signed
from ReferenceControlsPointRespawn import refresh
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter();touched=set()
    prefix=sum(2 if i.bytes[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in decoder(baseline).disassemble(0x635B,0x6380,'h'))
    table=baseline[0x634B:0x635B]
    def check(pointer=0xA100,link=0,class_code=0,link_flags=0,old=40,mode=0,flags=255):
        nonlocal touched
        memory.recording=False
        for address in touched:memory[address]=baseline[address]
        memory[0x635C:0x635E]=[pointer&255,pointer>>8]
        if pointer:memory[pointer+11],memory[pointer+12],memory[pointer+18]=link,link_flags,class_code
        memory[0x9BCD],memory[0x9B83]=old,mode;memory[0xECA9:0xECAB]=[0x34,0x12];memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':0xA500|flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0x635B},None,False)
        initial[14],initial[15],initial[26],initial[27]=counts.total()&255,counts.total()&255,counts.total()&1,counts.total()%3
        wanted=list(initial);expected=list(memory);writes=[]
        def byte(address,value):expected[address]=value;writes.append((address,value))
        if not pointer:
            wanted[6:8]=[0,0];wanted[0:2]=[0,0x44];m1=4;path='no_pointer'
        else:
            byte(pointer+12,link_flags|1);byte(pointer+11,26)
            byte(0x635C,0);byte(0x635D,0);byte(0xECA9,0x3B);byte(0xECAA,0xEF)
            wanted[6:8]=[0xEF,0x3B];wanted[2:4]=[class_code,link];wanted[0:2]=[link,cp_flags(link,26)]
            m1=prefix
            if link==26:path='already_1a'
            elif class_code>=16:
                wanted[0:2]=[class_code,cp_flags(class_code,16)];m1+=3;path='class_outside_table'
            else:
                delta=signed(table[class_code]);boost=bool(mode and delta>=0);delta+=10 if boost else 0
                total=signed(old)+delta;result=max(0,min(127,total))|(32 if old<32 else 0)
                byte(0x9BCD,result);wanted[6:8]=[0x63,0x4B+class_code];wanted[2:4]=[old,result]
                wanted[0:2]=[result,cp_flags(old,32)]
                overflow=not -128<=total<=127;negative=(old>=128) if overflow else total<0
                m1+=23+(5 if boost else 3 if mode else 0)+2*overflow+negative+2*(old<32);path='delta_applied'
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(0x635B,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(pointer,link,class_code,old,mode,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(memory.writes,writes)
        touched={a for a,_ in writes};counts[path]+=1
    # Проверка нулевого указателя при всех входных флагах.
    for flags in range(256):check(pointer=0,flags=flags)
    # Проверка всех прежних кодов связи и классов, включая код 1A и классы вне таблицы.
    for link in range(256):
        for class_code in range(256):check(link=link,class_code=class_code,link_flags=link^class_code)
    # Проверка каждого исходного байта состояния, обоих режимов и каждой табличной поправки.
    for old in range(256):
        for mode in (0,255):
            for class_code in range(16):check(old=old,mode=mode,class_code=class_code)
    # Проверка всех исходных разрядов LinkFlags у каждого из 25 начальных слотов без изменения размещения.
    for index in range(25):
        for flags in range(256):check(pointer=0xA100+64*index,link_flags=flags,class_code=index)
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),
        method='parent_field_transition_and_checked_delta_formula_against_real_instructions',
        independent_complete_child_oracle=False,exact_registers_flags_refresh_sp=True,
        every_ram_byte_and_write_multiplicity_checked=True,maximum_additional_stack_bytes=0,
        pending_pointer_cleared_before_optional_delta=True,link_1a_skips_only_delta=True,
        pending_pointer_producer_proved=False,game_event_meaning_proved=False,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordLinkEventVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
