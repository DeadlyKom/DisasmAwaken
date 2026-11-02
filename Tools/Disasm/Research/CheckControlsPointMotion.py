"""Полная CB00 с настоящими генератором и двумя динамическими возвратами точки."""
from pathlib import Path
import collections
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory,payload
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointMotion import Motion,NoProgress

SAMPLES={0xCB1A,0xCB61,0xCBC6,0xCC11,0xCE21,0xCE33,0xCE3F,0xCE53,0xCE68,0xCE7A,0xCE84,0xCE98}


def main():
    base=base_memory()
    original_sine=payload(17)[0x3900:0x3A00]
    counts=collections.Counter()
    frames=0
    interrupted=0
    def prepare(seed,page=0):
        memory=Memory(base)
        memory[0xCA8F:0xCA91]=[seed&255,(seed>>8)&255]
        memory[0x9900:0x9A00]=list(original_sine) if page==3 else [0 if page==0 else 127 if page==1 else ((i*73+seed)&255) for i in range(256)]
        for point in range(35):
            memory[0xC500+2*point:0xC502+2*point]=[(point*7+seed)%96,(point*37+seed)&255]
        return memory

    def check(memory,controls,refresh,label):
        nonlocal frames,interrupted
        memory.recording=False
        memory[0x9B95:0x9B98]=controls
        memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xCB00},None,False)
        initial[14],initial[15],initial[26],initial[27]=refresh^0x55,refresh,refresh&1,refresh%3
        expected=list(memory)
        reference=Motion(expected,refresh)
        stalled=None
        try:
            rotated=reference.run()
        except NoProgress as error:
            stalled=error
            rotated=None
        simulator=Simulator(memory)
        simulator.registers[:]=initial
        observed=[]
        memory.writes=[]
        memory.recording=True
        stop=stalled.loop if stalled else 0x3FFF
        for _ in range(100000):
            pc=simulator.registers[PC]
            if pc==stop:
                break
            simulator.run()
            if pc in SAMPLES:
                observed.append((pc,simulator.registers[0]))
        else:
            raise AssertionError(('граница',controls,refresh,label,hex(simulator.registers[PC])))
        memory.recording=False
        assert observed==reference.samples, ('R samples',controls,refresh,label,observed[:8],reference.samples[:8])
        assert memory==expected, ('RAM',controls,refresh,label,[(hex(i),a,b) for i,(a,b) in enumerate(zip(memory,expected)) if a!=b][:12])
        assert collections.Counter(memory.writes)==collections.Counter(reference.writes), ('writes',controls,refresh,label)
        if stalled:
            assert simulator.registers[SP]==0xBFFC and simulator.registers[15]==reference.r
            saved_a=simulator.registers[0]
            for _ in range(160):
                simulator.run()
            assert simulator.registers[PC]==stop and simulator.registers[0]==saved_a and simulator.registers[3]==0
            interrupted+=1
        else:
            wanted=reference.registers(initial,rotated)
            compared=(*range(13),14,15,*range(16,24),26,27)
            assert all(simulator.registers[i]==wanted[i] for i in compared), ('registers',controls,refresh,label,
                [(i,simulator.registers[i],wanted[i]) for i in compared if simulator.registers[i]!=wanted[i]])
            frames+=1
        counts[label]+=1
        return simulator.registers[15]

    # Начальная проверка каждой управляющей оси до расширения набора взаимодействий.
    for control in range(256):
        for refresh in (0,127,128,255):
            check(prepare(control),[control,0,0],refresh,'translate_y')
            check(prepare(control),[0,control,0],refresh,'translate_x')
    print('Translations',frames,flush=True)
    # Проверка всех управляющих байтов последней фазы, в том числе нулевого шага.
    for control in range(256):
        for page in range(3):
            check(prepare(control*257,page),[0,0,control],(control*73)&255,'turn')
    # Проверка каждого управляющего байта с реальной страницей синуса из исходного ACTION.
    for control in range(256):
        for refresh in (0,255):
            check(prepare(control*257,3),[0,0,control],refresh,'original_sine')
    # Проверка совместного действия переносов и пересоздания точек на границах.
    values=(0,1,63,64,127,128,192,255)
    for y in values:
        for x in values:
            for page in range(3):
                turn=(1,64,128,255)[(x+y+page)%4]
                check(prepare(y*256+x,page),[y,x,turn],(y*31+x)&255,'combined')
    # Проверка сохранения Seed, фаз и изменяемых операндов между последовательными кадрами.
    for seed in range(32):
        memory=prepare(seed*1237,2)
        refresh=seed*7
        for controls in ([1,0,0],[0,255,1],[128,1,255],[0,0,0],[64,192,128],[255,127,64]):
            refresh=check(memory,controls,refresh,'persistent_sequence')
    report=dict(passed=True,returning_frames=frames,nonprogress_frames=interrupted,cases_by_kind=dict(counts),
        every_ram_byte_and_write_checked=True,exact_main_alternate_index_and_refresh_registers=True,
        real_rng_and_both_respawn_entries=True,no_call_stubs=True,
        arithmetic_reference_independent=True,refresh_counts_from_original_opcode_m1_profile=True,
        entropy_samples_independently_predicted=True,coefficient_pages_are_supplied_fixtures=True,
        original_action_sine_page_additionally_checked=True,original_sine_file_offset=0x3900,
        all_control_bytes_per_axis=True,persistent_seed_and_phases=True,
        zero_step_nonprogress_preserved=True,whole_cb00_in_documented_domain=True,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsPointMotionVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
