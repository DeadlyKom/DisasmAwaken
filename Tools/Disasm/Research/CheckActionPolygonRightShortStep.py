"""Общий короткий отрицательный хвост, все значения A и F независимо от допустимости наклона."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=base,out7ffd=16);sim=Simulator(memory)
    for af in range(65536):
        memory.recording=False;memory[0xFFDE],memory[0xFFDF]=0x27,0x8D
        initial=get_registers({'AF':af,'HL':0x903B,'DE':0x0489,'BC':0x80B3,'IX':0x2468,'IY':0x5C3A,
            '^AF':0x69CF,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'SP':0xFFDE,'PC':0xD4F5},None,False)
        expected=list(initial);expected[4],expected[6],expected[7]=0x27,0x8D,0x27
        expected[20:22]=[0x20,0];expected[SP],expected[PC]=0xFFE0,0xD4C1
        sim.registers[:]=initial;memory.writes=[];memory.recording=True
        sim.run(start=0xD4F5,stop=0xD4C1);memory.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(expected[i]==sim.registers[i] for i in compared),(af,sim.registers[:8],expected[:8])
        assert Counter(memory.writes)==Counter(((0,0x121F,af>>8),)) and memory[0xD21F]==af>>8
    report=dict(passed=True,total_cases=65536,all_AF_values=True,exact_registers_flags_except_R=True,
        all_ram_writes_accounted_for=True,write_multiplicity_proved=True,temporary_stack_word_consumed=True,
        whole_polygon_fill_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPolygonRightShortStepVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
