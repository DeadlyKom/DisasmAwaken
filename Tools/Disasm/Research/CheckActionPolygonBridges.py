"""Шесть переходников заполнителя, без пиксельного ядра и изменения его байтов."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh

SPECS=(('ActionPolygonSelectRight',0xD268,0xD3AD,256),
       ('ActionPolygonWrapLeft',0xD26B,0xD27E,65536),
       ('ActionPolygonWrapRight',0xD3A8,0xD3BC,256),
       ('ActionPolygonWrapLeftTop',0xD503,0xD547,65536),
       ('ActionPolygonWrapRightTop',0xD50A,0xD557,256),
       ('ActionPolygonReturn',0xD50F,0x3FFF,256))


def main():
    costs={0xD268:1,0xD26B:3,0xD3A8:2,0xD503:5,0xD50A:2,0xD50F:2}
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=base,out7ffd=16);sim=Simulator(memory);counts={}
    for name,entry,stop,number in SPECS:
        refresh_values=set()
        for serial in range(number):
            memory.recording=False;index=serial>>8;flags=serial&255
            memory[0xD3B7]=index
            memory[0xBFFC],memory[0xBFFD]=0x57,0x13
            memory[0xBFFE],memory[0xBFFF]=0xFF,0x3F
            initial=get_registers({'AF':0xA500|flags,'HL':0x903A,'DE':0x2789,'BC':0x80B3,
                'IX':0x2468,'IY':0x5C3A,'^AF':index*256+0x69,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,
                'SP':0xBFFC,'PC':entry},None,False)
            initial[14],initial[15],initial[26],initial[27]=serial&255,(serial*73)&255,serial&1,serial%3
            refresh_values.add(initial[15])
            wanted=list(initial);wanted[PC]=stop;wanted[15]=refresh(initial[15],costs[entry])
            # Проверка прямого переноса индекса либо снятия сохранённого контекста.
            if entry==0xD26B:wanted[0],wanted[7]=index,index
            elif entry in (0xD3A8,0xD50A):wanted[7]=1
            elif entry==0xD503:
                value=(index+1)&255;wanted[7]=value
                wanted[1]=(value&0xA8)|(64 if value==0 else 0)|(16 if index&15==15 else 0)|(4 if index==127 else 0)|(flags&1)
            elif entry==0xD50F:wanted[6:8]=[0x13,0x57];wanted[SP]=0xC000
            sim.registers[:]=initial;memory.writes=[];memory.recording=True
            measured_m1=0
            for _ in range(7):
                if sim.registers[PC]==stop:break
                before_r=sim.registers[15];sim.run()
                increment=(sim.registers[15]-before_r)&127
                assert increment==1
                measured_m1+=increment
            else:raise AssertionError(('нет границы',name,serial))
            assert measured_m1==costs[entry]
            memory.recording=False
            compared=(*range(13),14,15,*range(16,24),PC,26,27)
            assert all(wanted[i]==sim.registers[i] for i in compared),(name,serial,sim.registers[:8],wanted[:8])
            assert not memory.writes,(name,serial,memory.writes)
        assert refresh_values==set(range(256))
        counts[name]=number
        report=dict(passed=True,total_cases=number,entry=entry,stop=stop,exact_registers_flags_except_R=False,exact_registers_including_R=True,
            all_256_initial_R_values=True,constant_refresh_M1=costs[entry],
            full_M1_count_compared_not_only_R_modulo_128=True,
            no_memory_writes=True,whole_polygon_fill_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
        (ROOT/('Tools/Disasm/Reports/'+name+'Verification.json')).write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(dict(passed=True,total_cases=sum(counts.values()),profiles=counts,assembly_executed=False),indent=2))


if __name__=='__main__':main()
