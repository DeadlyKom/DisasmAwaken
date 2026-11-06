"""E30F..E369, локальная проверка двух координатных допусков и записи альтернативного HL в 635C."""
from collections import Counter
import json,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags
from ReferenceControlsBufferPoints import sub16_flags
from ReferenceControlsPointRespawn import refresh
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter()
    def cost(a,b):return sum(2 if i.bytes[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in decoder(baseline).disassemble(a,b,'h'))
    y_prefix=cost(0xE30F,0xE322)+cost(0xE323,0xE329)+cost(0xE330,0xE339)
    x_prefix=cost(0xE339,0xE349)+cost(0xE34A,0xE350)+cost(0xE357,0xE360)
    commit_cost=cost(0xE360,0xE36A)
    def check(gate=0,size=40,x=0,y=0,aim_x=119,aim_y=43,record=0xA100):
        memory.recording=False;memory[0xE310]=gate;memory[0xE331:0xE333]=[size&255,size>>8]
        memory[0xE33A:0xE33C]=[x&255,x>>8];memory[0x9B19:0x9B1B]=[aim_x,aim_y]
        memory[0x635C:0x635E]=[0x78,0x56]
        initial=get_registers({'AF':0xA5FF,'HL':0x1357,'DE':y,'BC':0x369C,'^HL':record,
            '^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xE30F},None,False)
        initial[14],initial[15],initial[26],initial[27]=counts.total()&255,counts.total()&255,counts.total()&1,counts.total()%3
        wanted=list(initial);expected=list(memory);writes=[]
        def byte(a,v):expected[a]=v;writes.append((a,v))
        def axis(value,aim,center):
            offset=(center-aim)&255;signed_offset=offset if offset<128 else offset-256
            translated=(value+signed_offset)&65535;negative=bool(translated&32768)
            distance=(-translated)&65535 if negative else translated
            a=(~(translated>>8))&255 if negative else offset
            return distance,a,offset>=128,negative
        if gate:
            wanted[0:2]=[gate,and_flags(gate)];m1=3;path='gate_blocked'
        else:
            distance,a,extend,negative=axis(y,aim_y,43);m1=y_prefix+int(extend)+7*negative
            wanted[4:6]=[distance>>8,distance&255];value=(size-distance)&65535
            wanted[6:8]=[value>>8,value&255];wanted[0:2]=[a,sub16_flags(size,distance)]
            if size<distance:path='outside_y'
            else:
                distance,a,extend,negative=axis(x,aim_x,119);m1+=x_prefix+int(extend)+7*negative
                wanted[4:6]=[distance>>8,distance&255];value=(size-distance)&65535
                wanted[6:8]=[value>>8,value&255];wanted[0:2]=[a,sub16_flags(size,distance)]
                if size<distance:path='outside_x'
                else:
                    wanted[0]=1;byte(0xE310,1);byte(0x635C,record&255);byte(0x635D,record>>8)
                    m1+=commit_cost;path='captured'
        wanted[PC],wanted[15]=0xE36A,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(0xE30F,0xE36A);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(gate,size,x,y,aim_x,aim_y,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(path,memory.writes,writes)
        counts[path]+=1
    # Проверка всех байтов запрета, отсутствие записи при ненулевом значении.
    for gate in range(256):check(gate=gate)
    # Проверка всех слов каждой оси и всех слов допуска по отдельным сечениям, включая -32768 и переносы.
    for value in range(65536):
        check(y=value,aim_y=value&255)
        check(x=value,aim_x=value&255)
        check(size=value,x=value^0x8000,y=0)
    # Проверка всех сочетаний двух байтов точки отсчёта с попаданием в границы допуска и за ними.
    for aim_x in range(256):
        for aim_y in range(256):check(aim_x=aim_x,aim_y=aim_y,size=(aim_x^aim_y),record=0xA100+64*(aim_x%25))
    for record in range(0xA100,0xA740,64):
        for size in (0,1,40,32767,32768,65535):check(record=record,size=size)
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),
        method='independent_signed_offset_absolute_distance_and_capture_oracle',
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
        execution_boundary='E30F..E36A, no external continuation executed',maximum_additional_stack_bytes=0,
        pending_record_written_from_alternate_hl=True,gate_set_before_pointer_write=True,
        upstream_size_and_projection_proved=False,upstream_record_iteration_proved=False,
        game_event_meaning_proved=False,all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionProjectedCaptureVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
