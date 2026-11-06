"""Шесть переходников заполнителя, без пиксельного ядра и изменения его байтов."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP

SPECS=(('ActionPolygonSelectRight',0xD268,0xD3AD,256),
       ('ActionPolygonWrapLeft',0xD26B,0xD27E,65536),
       ('ActionPolygonWrapRight',0xD3A8,0xD3BC,256),
       ('ActionPolygonWrapLeftTop',0xD503,0xD547,65536),
       ('ActionPolygonWrapRightTop',0xD50A,0xD557,256),
       ('ActionPolygonReturn',0xD50F,0x3FFF,256))


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=base,out7ffd=16);sim=Simulator(memory);counts={}
    for name,entry,stop,number in SPECS:
        for serial in range(number):
            memory.recording=False;index=serial>>8;flags=serial&255
            memory[0xD3B7]=index
            memory[0xBFFC],memory[0xBFFD]=0x57,0x13
            memory[0xBFFE],memory[0xBFFF]=0xFF,0x3F
            initial=get_registers({'AF':0xA500|flags,'HL':0x903A,'DE':0x2789,'BC':0x80B3,
                'IX':0x2468,'IY':0x5C3A,'^AF':index*256+0x69,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,
                'SP':0xBFFC,'PC':entry},None,False)
            wanted=list(initial);wanted[PC]=stop
            # Проверка прямого переноса индекса либо снятия сохранённого контекста.
            if entry==0xD26B:wanted[0],wanted[7]=index,index
            elif entry in (0xD3A8,0xD50A):wanted[7]=1
            elif entry==0xD503:
                value=(index+1)&255;wanted[7]=value
                wanted[1]=(value&0xA8)|(64 if value==0 else 0)|(16 if index&15==15 else 0)|(4 if index==127 else 0)|(flags&1)
            elif entry==0xD50F:wanted[6:8]=[0x13,0x57];wanted[SP]=0xC000
            sim.registers[:]=initial;memory.writes=[];memory.recording=True
            sim.run(start=entry,stop=stop);memory.recording=False
            compared=(*range(13),14,*range(16,24),PC,26,27)
            assert all(wanted[i]==sim.registers[i] for i in compared),(name,serial,sim.registers[:8],wanted[:8])
            assert not memory.writes,(name,serial,memory.writes)
        counts[name]=number
        report=dict(passed=True,total_cases=number,entry=entry,stop=stop,exact_registers_flags_except_R=True,
            no_memory_writes=True,whole_polygon_fill_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
        (ROOT/('Tools/Disasm/Reports/'+name+'Verification.json')).write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(dict(passed=True,total_cases=sum(counts.values()),profiles=counts,assembly_executed=False),indent=2))


if __name__=='__main__':main()
