"""Исходные CE16 и скрытый CE5D, локальный R, фазовый байт и динамические CALL."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import respawn

PROFILES = {0xCE16:(0xCE17,0xCE1E,0xCE31),0xCE5D:(0xCE5E,0xCE65,0xCE78)}


def main():
    base = base_memory()
    memory = Memory(base)
    simulator = Simulator(memory)
    cases = {entry:0 for entry in PROFILES}
    def check(entry,phase,step,offset,refresh):
        memory.recording = False
        phase_address,step_address,offset_address = PROFILES[entry]
        memory[phase_address],memory[step_address],memory[offset_address] = phase,step,offset
        memory[0xBFFE:0xC000] = [255,63]
        expected = list(memory)
        result = respawn(entry,phase,step,offset,refresh)
        expected[phase_address] = result['phase']
        initial = get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27] = offset,refresh,refresh&1,refresh%3
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(1100):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',entry,phase,step,offset,refresh))
        memory.recording = False
        expected_registers = list(initial)
        expected_registers[0:2] = [result['x'],result['flags']]
        expected_registers[3:6] = [step,result['x'],result['y']]
        expected_registers[SP],expected_registers[15] = 0xC000,result['r']
        compared = (*range(13),14,15,*range(16,24),26,27)
        r = simulator.registers
        assert memory == expected and memory.writes == [(phase_address,result['phase'])]
        assert all(r[i] == expected_registers[i] for i in compared), (hex(entry),phase,step,offset,refresh,result,[(i,r[i],expected_registers[i]) for i in compared if r[i]!=expected_registers[i]])
        cases[entry] += 1
    # Проверка каждого ненулевого шага и R при обеих штатных фазах.
    for entry in PROFILES:
        for step in range(1,256):
            for refresh in range(256):
                for phase in (0,1):
                    check(entry,phase,step,(refresh*73+step)&255,refresh)
    # Проверка каждого сырого фазового байта и смещения при разных R и шагах.
    for entry in PROFILES:
        for phase in range(256):
            for offset in range(256):
                check(entry,phase,1+(phase*73+offset)%255,offset,(offset*31+phase)&255)
    print('Respawn cases',sum(cases.values()),flush=True)
    # Проверка ненулевого модуля C обязательна, иначе исходный цикл SUB 0 не продвигается.
    zero_cases = 0
    for entry,(phase_address,step_address,_) in PROFILES.items():
        for phase in (0,1):
            memory.recording = False
            memory[:] = base
            memory[phase_address],memory[step_address] = phase,0
            memory[0xBFFE:0xC000] = [255,63]
            simulator.registers[:] = get_registers({'SP':0xBFFE,'PC':entry},None,False)
            target = (0xCE23 if phase == 1 else 0xCE41) if entry == 0xCE16 else (0xCE6A if phase == 1 else 0xCE86)
            for _ in range(10):
                if simulator.registers[PC] == target:
                    break
                simulator.run()
            assert simulator.registers[PC] == target
            saved_a = simulator.registers[0]
            for _ in range(160):
                simulator.run()
            assert simulator.registers[PC] == target and simulator.registers[0] == saved_a and simulator.registers[3] == 0
            zero_cases += 1
    # Проверка реального выбора обоих CALL и фактического входа в CE5D из CB00.
    reachable = []
    for rotation,expected in ((1,0xCE5D),(255,0xCE16)):
        memory.recording = False
        memory[:] = base
        memory[0x9900:0x9A00] = [127]*256
        memory[0x9B95:0x9B98] = [0,0,rotation]
        memory[0xBFFE:0xC000] = [255,63]
        simulator.registers[:] = get_registers({'SP':0xBFFE,'PC':0xCB00},None,False)
        for _ in range(2000):
            if simulator.registers[PC] == expected:
                break
            simulator.run()
        else:
            raise AssertionError(('динамический вход',rotation))
        assert memory[0xCD31:0xCD33] == memory[0xCDFC:0xCDFE] == [expected&255,expected>>8]
        assert simulator.registers[SP] == 0xBFFC and memory[0xBFFC:0xBFFE] in ([0x33,0xCD],[0xFE,0xCD])
        reachable.append(dict(rotation=rotation,entry=expected))
    report = dict(passed=True,total_cases=sum(cases.values()),cases_by_entry={format(k,'04X'):v for k,v in cases.items()},
        all_nonzero_steps_and_refresh_values=True,both_standard_phases=True,all_raw_phase_and_offset_bytes=True,
        exact_registers_flags_refresh_and_memory=True,refresh_from_independent_m1_formula=True,
        zero_step_nonprogress_cases=zero_cases,dynamic_call_reachability=reachable,
        hidden_code_bytes=71,lookup_coefficients_are_test_fixture=True,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsPointRespawnVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
