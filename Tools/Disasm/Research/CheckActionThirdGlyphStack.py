"""Одна исходная LD SP,nn по 6CB1, все значения сохранённого CPU SP, остановка до RET PE."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def main(entry=0x6CB1,report_tag='ActionThirdGlyphStack'):
    assert entry in (0x6CB1,0x6C40,0x6AAD)
    target=entry+3
    flat=flat_action();assert flat[entry:target]==[0x31,0,0]
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    for value in range(65536):
        memory.recording=False;memory[entry+1],memory[entry+2]=value&255,value>>8
        initial=get_registers({'AF':value,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':entry,
            'SP':(value*73+17)&65535,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=value&255,value&255,value&1,value%3
        expected=[bytes(b) for b in memory.banks];wanted=list(initial)
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],1),value,target
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=target);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),value
        assert all(a==b for a,b in zip(expected,memory.banks)) and not memory.writes,value
    report=dict(passed=True,total_cases=65536,entry=entry,all_saved_SP_words=True,stop_before_first_stack_read=True,
        exact_registers_including_R=True,refresh_m1=1,all_physical_ram_bytes_proved=True,
        no_RAM_writes=True,fallthrough_target=target,independent_numeric_oracle=True,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/('Tools/Disasm/Reports/'+report_tag+'Verification.json')).write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
