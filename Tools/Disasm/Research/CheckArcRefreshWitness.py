"""Полные проходы дуги с независимым растром и пошаговой проверкой R.

Документация: ../../../Docs/ArcDispatcher.md#пошаговая-проверка-r
"""
from collections import Counter
from hashlib import sha256
import json
import argparse

from CheckArcDispatcher import ROOT, Simulator, get_registers, make_context, reference
from ReferenceControlsPointRespawn import refresh
from skoolkit.simutils import PC, SP, R, H, L, D, E, A, F, I, IM, IFF


def main(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pair-paths',action='store_true',help='отдельные полные пути Entry и UseLimit пары')
    pair_paths = parser.parse_args(arguments).pair_paths
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    for slot in (4,7):
        row = next(x for x in manifest['entries'] if x['slot'] == slot)
        assert (ROOT/(row['path']+'.sectors.bin')).read_bytes() == disk[row['offset']:row['offset']+row['allocated_length']]
    _,source,banks = make_context()
    memory = bytearray(65536)
    memory[0x4000:0x8000],memory[0x8000:0xC000] = bytes(banks[5]),bytes(banks[2])
    memory[0xC000:0xC000+len(source)] = source
    cpu = Simulator(memory)
    initial = get_registers(dict(SP=0x7FFE,HL=0x1357,DE=0x247A,BC=0x36C9,AF=0x5A5D,
        IX=0x2468,IY=0x5C3A,I=0x3C,IM=2,IFF=0,
        **{'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF}),None,False)
    memory[0x7FFE:0x8000] = bytes.fromhex('ff3f')
    # Подготовка таблиц настоящим кодом KARTA, снимок сохраняется отдельно от каждого прохода.
    cpu.registers[:] = initial
    cpu.registers[D] = cpu.registers[E] = 0
    cpu.run(start=0xC49B,stop=0x3FFF)
    initialized = memory[:]
    entries = {0xE2AB:'left',0xE357:'both',0xE46C:'right'}
    rows = []
    kernel_rows = []
    wrapper_rows = []
    pair_rows = []
    preparation_rows = []
    wrappers = dict(zip((0xE681,0xE688,0xE68F,0xE696,0xE69D,0xE6A4),
        ('left_down','left_up','right_down','right_up','both_down','both_up')))
    all_paths = Counter()
    for width,height in ((16,24),(64,64)):
        memory[:] = initialized
        cpu.registers[:] = initial
        cpu.registers[H],cpu.registers[L] = height-1,width-1
        cpu.registers[D] = cpu.registers[E] = 0
        cpu.run(start=0xD0C3,stop=0x3FFF)
        prepared = memory[:]
        # Выбор центра внутри, вне каждой оси и вне обеих, включая ранние отказы.
        fixtures = ((12,24,0),(40,48,0)) if pair_paths else ((8,0,0),(12,0,0),(40,0,0),(80,0,48),(80,48,0),
                           (80,48,48),(40,80,80),(255,32,32))
        for radius,x,y in fixtures:
            for quadrant in range(4):
                for mode in (0x30,0x38):
                    raw = bytes([0xA7])*0x1B00
                    expected,_,path = reference(raw,radius,x,y,quadrant,mode,width,height)
                    for initial_r in (0,0x95):
                        memory[:] = prepared
                        memory[0x4000:0x5B00] = raw
                        memory[0xDFAB:0xDFAF] = bytes((y,x,quadrant,radius))
                        memory[0xDFAF:0xDFB4] = bytes([0xA7])*5
                        memory[0xDFB6:0xDFBA] = bytes([0xA7])*4
                        memory[0xDFC4] = int(mode == 0x38)
                        memory[0x7FFE:0x8000] = bytes.fromhex('ff3f')
                        cpu.registers[:] = initial
                        cpu.registers[PC],cpu.registers[R] = 0xDFC3,initial_r
                        m1 = 0
                        active = None
                        active_wrapper = None
                        active_pair = None
                        active_preparation = None
                        # Сверка R после каждой инструкции, помощники исполняются без подмены.
                        for _ in range(100000):
                            pc = cpu.registers[PC]
                            if pc in wrappers:
                                assert active_wrapper is None
                                sp = cpu.registers[SP]
                                active_wrapper = dict(case=len(rows),entry=pc,name=wrappers[pc],input_SP=sp,
                                    return_PC=memory[sp] | memory[sp+1] << 8,input_AF=cpu.registers[A]*256+cpu.registers[F],
                                    initial_R=cpu.registers[R],start_M1=m1,kernel_index=len(kernel_rows))
                                if active_pair is not None:active_pair['children'].append(pc)
                            if active is not None and pc == active['return_PC']:
                                assert cpu.registers[SP] == active['input_SP']+4
                                assert cpu.registers[A]*256+cpu.registers[F] == active['saved_AF']
                                own_m1 = m1-active['start_M1']
                                assert cpu.registers[R] == refresh(active['initial_R'],own_m1)
                                active.update(final_R=cpu.registers[R],observed_M1=own_m1,
                                              final_SP=cpu.registers[SP])
                                kernel_rows.append(active)
                                active = None
                            if active_wrapper is not None and pc == active_wrapper['return_PC']:
                                assert cpu.registers[SP] == active_wrapper['input_SP']+2
                                assert cpu.registers[A]*256+cpu.registers[F] == active_wrapper['input_AF']
                                own_m1 = m1-active_wrapper['start_M1']
                                assert cpu.registers[R] == refresh(active_wrapper['initial_R'],own_m1)
                                active_wrapper.update(final_R=cpu.registers[R],observed_M1=own_m1,
                                    final_SP=cpu.registers[SP])
                                assert len(kernel_rows) == active_wrapper['kernel_index']+1
                                assert own_m1-kernel_rows[-1]['observed_M1'] == 11
                                wrapper_rows.append(active_wrapper)
                                active_wrapper = None
                            if active_preparation is not None and pc == active_preparation['return_PC']:
                                own_m1 = m1-active_preparation['start_M1']
                                assert own_m1 == active_preparation['expected_M1']
                                assert cpu.registers[SP] == active_preparation['input_SP']+2
                                assert cpu.registers[R] == refresh(active_preparation['initial_R'],own_m1)
                                active_preparation.update(final_R=cpu.registers[R],observed_M1=own_m1)
                                preparation_rows.append(active_preparation)
                                active_preparation = None
                            if active_pair is not None and pc == active_pair['return_PC']:
                                assert active is None and active_wrapper is None and active_preparation is None
                                preps = preparation_rows[active_pair['preparation_index']:]
                                wraps = wrapper_rows[active_pair['wrapper_index']:]
                                assert len(preps) == len(wraps) == 2
                                left = active_pair['input_E'] & 1
                                assert [p['entry'] for p in preps] == [0xE248 if left else 0xE260]*2
                                assert [w['entry'] for w in wraps] == ([0xE681,0xE688] if left else [0xE68F,0xE696])
                                assert active_pair['children'] == ([0xE248,0xE681,0xE248,0xE688] if left else [0xE260,0xE68F,0xE260,0xE696])
                                own_m1 = 10 if active_pair['entry'] == 0xE228 else 8
                                total_m1 = m1-active_pair['start_M1']
                                assert active_pair['own_M1'] == own_m1
                                assert total_m1 == own_m1+sum(p['observed_M1'] for p in preps)+sum(w['observed_M1'] for w in wraps)
                                assert cpu.registers[SP] == active_pair['input_SP']+2
                                active_pair.update(final_R=cpu.registers[R],observed_M1=total_m1,final_SP=cpu.registers[SP])
                                assert cpu.registers[R] == refresh(active_pair['initial_R'],total_m1)
                                pair_rows.append(active_pair)
                                active_pair = None
                            if pc == 0x3FFF:
                                break
                            if pc in (0xE228,0xE22B) and active_pair is None:
                                sp = cpu.registers[SP]
                                active_pair = dict(case=len(rows),entry=pc,input_SP=sp,input_E=cpu.registers[E],
                                    return_PC=memory[sp] | memory[sp+1] << 8,start_M1=m1,initial_R=cpu.registers[R],own_M1=0,children=[],
                                    preparation_index=len(preparation_rows),wrapper_index=len(wrapper_rows))
                            if active_pair is not None and pc in (0xE248,0xE260):
                                assert active_preparation is None
                                reference_x,offset_x,radius = memory[0xDFBF],memory[0xDFB0],memory[0xDFAE]
                                point_x = (reference_x+offset_x-radius)&255 if pc == 0xE248 else (reference_x+radius-offset_x)&255
                                sp = cpu.registers[SP]
                                active_preparation = dict(case=len(rows),entry=pc,input_SP=sp,
                                    return_PC=memory[sp] | memory[sp+1] << 8,start_M1=m1,initial_R=cpu.registers[R],X=point_x,
                                    expected_M1=47+4*(point_x&7) if pc == 0xE248 else 82-4*(point_x&7))
                                active_pair['children'].append(pc)
                            if pc in entries:
                                assert active is None
                                sp = cpu.registers[SP]
                                active = dict(case=len(rows),entry=pc,side=entries[pc],input_SP=sp,
                                    return_PC=memory[sp+2] | memory[sp+3] << 8,
                                    initial_R=cpu.registers[R],start_M1=m1,saved_AF=memory[sp] | memory[sp+1] << 8)
                            opcode = memory[pc]
                            if opcode in (0xDD,0xFD):
                                assert memory[(pc+1)&65535] not in (0xDD,0xFD,0xED,0xCB)
                            assert memory[pc:pc+2] not in (b'\xed\x4f',b'\xed\x5f')
                            increment = 2 if opcode in (0xCB,0xED,0xDD,0xFD) else 1
                            if active_pair is not None and 0xE228 <= pc < 0xE248:
                                active_pair['own_M1'] += increment
                            m1 += increment
                            cpu.opcodes[opcode]()
                            assert cpu.registers[R] == refresh(initial_r,m1)
                        else:
                            raise AssertionError(('instruction_limit',radius,x,y,path))
                        assert active is None and active_wrapper is None and active_pair is None and active_preparation is None and cpu.registers[SP] == 0x8000
                        assert memory[0x4000:0x5B00] == expected,(radius,x,y,quadrant,mode,path)
                        assert cpu.registers[8:12] == initial[8:12]
                        assert tuple(cpu.registers[i] for i in (I,IM,IFF)) == tuple(initial[i] for i in (I,IM,IFF))
                        all_paths[path] += 1
                        rows.append(dict(window=[width,height],radius=radius,offset_x=x,offset_y=y,
                            quadrant=quadrant,mode=mode,path=path,initial_R=initial_r,
                            final_R=cpu.registers[R],observed_M1=m1))
    expected_sides = {'left','right'} if pair_paths else set(entries.values())
    expected_wrappers = {0xE681,0xE688,0xE68F,0xE696} if pair_paths else set(wrappers)
    assert {x['side'] for x in kernel_rows} == expected_sides
    assert all(any(x['side'] == side and x['initial_R'] != x['final_R'] for x in kernel_rows) for side in expected_sides)
    assert {x['entry'] for x in wrapper_rows} == expected_wrappers
    assert all(any(x['entry'] == entry and x['initial_R'] != x['final_R'] for x in wrapper_rows) for entry in expected_wrappers)
    if pair_paths:
        assert {p['entry'] for p in pair_rows} == {0xE228,0xE22B}
        assert all(any(p['entry'] == e and p['initial_R'] != p['final_R'] for p in pair_rows) for e in (0xE228,0xE22B))
    result = dict(passed=True,method='original_arc_dispatcher_and_kernel_per_instruction_refresh_full_bitmap_witnesses',
        original_disk_sha256=manifest['sha256'],cases=len(rows),paths=dict(all_paths),profiles=rows,
        wrapper_calls=wrapper_rows,wrapper_extra_M1=11,all_six_wrappers_observed=set(wrappers)==expected_wrappers,
        kernel_calls=kernel_rows,all_three_kernel_entries_observed=set(entries.values())==expected_sides,R_checked_after_every_instruction=True,
        independent_bitmap_compared=True,all_input_values_proved=False,all_runtime_phases_proved=False,
        IRQ_executed=False,calls_stubbed=False,native_execution=False,assembly_executed=False)
    if pair_paths:
        result.update(method='original_arc_pair_paths_full_dispatch_per_instruction_refresh_and_child_composition',
            pair_calls=pair_rows,preparation_calls=preparation_rows,both_pair_entries_observed=True,
            pair_own_M1_Entry=10,pair_own_M1_UseLimit=8)
    path = ROOT/('Tools/Disasm/Reports/ArcPairRefreshWitnessVerification.json' if pair_paths else 'Tools/Disasm/Reports/ArcRefreshWitnessVerification.json')
    data = (json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    if path.exists():
        old = json.loads(path.read_bytes())
        for key,value in old.items():
            if key not in ('kernel_calls','pair_calls'):
                assert value == json.loads(data)[key],key
        for key,records in (('kernel_calls',kernel_rows),('pair_calls',pair_rows)):
            if key in old:
                assert len(old[key]) == len(records)
                for before,after in zip(old[key],records):
                    assert all(after[k] == v for k,v in before.items())
        if path.read_bytes() != data:
            path.write_bytes(data)
    else:
        path.write_bytes(data)
    print(json.dumps(dict(passed=True,cases=len(rows),kernel_calls=len(kernel_rows),wrapper_calls=len(wrapper_rows),pair_calls=len(pair_rows),paths=dict(all_paths)),ensure_ascii=False))


if __name__ == '__main__':
    main()
