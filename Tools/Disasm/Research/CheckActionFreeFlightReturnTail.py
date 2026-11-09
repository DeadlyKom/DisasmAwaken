"""Реальный RET по 6E72 после команды свободного полёта, только граница хвоста."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def main():
    baseline=flat_action();assert baseline[0x6E72]==0x3A
    command=json.loads((ROOT/'Tools/Disasm/Reports/ActionFreeFlightCommandVerification.json').read_bytes())
    assert command['passed'] and command['total_cases']==66576
    memory=Memory(baseline);memory[0x6E72]=0xC9;memory[0xBFFE:0xC000]=[255,63]
    simulator=Simulator(memory);before=list(memory);cases=0
    # Проверка всех F и четырёх граничных R, команда уже доказала запись C9 в этот опкод.
    for flags in range(256):
        for initial_r in (0,127,128,255):
            initial=get_registers({'PC':0x6E72,'SP':0xBFFE,'AF':0xA500|flags,
                'HL':0x1357,'DE':0x2468,'BC':0x369C,'^AF':0xDEF0,'^HL':0x1234,
                '^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
            initial[14]=flags;initial[15]=initial_r;initial[26]=flags&1;initial[27]=flags%3
            wanted=list(initial);wanted[PC]=0x3FFF;wanted[SP]=0xC000;wanted[15]=refresh(initial_r,1)
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run();memory.recording=False
            assert all(simulator.registers[i]==wanted[i] for i in (*range(13),14,15,*range(16,24),PC,26,27))
            assert memory==before and memory.writes==[];cases+=1
    result=dict(passed=True,total_cases=cases,actual_ret_opcode_executed=True,
        initial_gate_from_proved_command=True,all_registers_except_T_checked=True,all_ram_checked=True,
        full_UpdateMotionFromControls_executed=False,preceding_calls_executed=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionFreeFlightReturnTailVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
