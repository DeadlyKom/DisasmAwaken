"""Полный перебор координат прямоугольного классификатора, ядро загружено с реальным переносом."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import cp_flags, refresh


def reference(high, low):
    cost = 0
    # Проверка двух первых непересекающихся прямоугольников в исходном порядке.
    for kind, hmin, hmax, lmin, lmax in ((0,0x4A,0x4E,0x36,0x3A),(1,0x47,0x4A,0x34,0x38)):
        if high<hmin:
            cost += 3
        elif high>=hmax:
            cost += 5
        elif low<lmin:
            cost += 8
        elif low<lmax:
            return kind, cp_flags(low,lmax), cost+11
        else:
            cost += 11
    # Проверка последней области, флаги каждого раннего выхода принадлежат последнему CP.
    if high<0x47:
        return 3, cp_flags(high,0x47), cost+4
    if high>=0x4A:
        return 3, cp_flags(high,0x4A), cost+8
    if low<0x38:
        return 3, cp_flags(low,0x38), cost+12
    if low<0x3B:
        return 2, cp_flags(low,0x3B), cost+16
    return 3, cp_flags(low,0x3B), cost+18


def main():
    source = (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    original = base_memory()
    original[0x6000:0x10000] = source
    # Перенос только ядра, старшие данные ACTION сохраняют исходное смещение от 6000.
    original[0x6000:0x7F8F] = source[0x23D:0x21CC]
    original[0xBFFE:0xC000] = [0xFF,0x3F]
    memory = Memory(original)
    simulator = Simulator(memory)
    outputs = Counter()
    costs = Counter()
    for coordinate in range(65536):
        initial = get_registers({'AF':coordinate^0xA55A,'HL':coordinate,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6E2B},None,False)
        initial[14],initial[15],initial[26],initial[27] = coordinate&255,(73*coordinate+101)&255,coordinate&1,coordinate%3
        kind,flags,cost = reference(coordinate>>8,coordinate&255)
        wanted = list(initial)
        wanted[0:2] = [kind,flags]
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],cost)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(60):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',coordinate))
        memory.recording = False
        compared = (*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (coordinate,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert not memory.writes and memory==original
        outputs[kind] += 1
        costs[cost] += 1
    assert dict(outputs)=={3:65499,1:12,2:9,0:16}
    report = dict(passed=True,total_cases=65536,all_hl_coordinates=True,outputs=dict(outputs),
        refresh_m1_histogram=dict(sorted(costs.items())),real_action_core_relocation=True,
        exact_registers_flags_r_and_sp=True,every_ram_byte_unchanged=True,
        full_caller_de9a_proved=False,game_region_meaning_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRegionTypeVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
