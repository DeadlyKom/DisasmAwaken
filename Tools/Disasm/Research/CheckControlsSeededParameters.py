"""Полная цепочка DE9A с настоящими классификатором и генератором, без заглушек."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from CheckControlsWordRandom import reference as random_step
from CheckActionRegionType import reference as region_type
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsPointMotion import block_cost


def main():
    source = (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    original = base_memory()
    original[0x6000:0xC000] = source[:0x6000]
    original[0x6000:0x7F8F] = source[0x23D:0x21CC]
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()
    region_counts = Counter()
    total_calls = 0

    def check(first, second, control, kind):
        nonlocal touched, total_calls
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        memory[0xBFFE:0xC000] = [0xFF,0x3F]
        initial = get_registers({'AF': (control<<8)|((first+second)&255),'HL':first,'DE':second,
            'BC':(first*73+second)&65535,'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,
            '^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xDE9A},None,False)
        initial[14],initial[15],initial[26],initial[27] = control,second&255,control&1,first%3
        seed_hash = ((first>>8)^(first&255)^(second>>8)^(second&255))&7
        region,_,region_cost = region_type(first>>8,first&255)
        outside = int(region==3)
        iterations = control+1
        writes = [(0xBFFD,initial[2]),(0xBFFC,initial[3]),
            (0x9B15,first&255),(0x9B16,first>>8),(0x9B17,second&255),(0x9B18,second>>8),
            (0xBFFB,0xDE),(0xBFFA,0xB4)]
        x,y = first,second
        for iteration in range(iterations):
            loop_b = (iterations-iteration)&255
            x,y,output,_ = random_step(x,y)
            writes += [(0xBFFB,0xDE),(0xBFFA,0xC0),(0xBFF9,loop_b),(0xBFF8,outside),
                (0x9B15,x&255),(0x9B16,x>>8),(0x9B17,y&255),(0x9B18,y>>8)]
        complement = output^255
        low_index = complement&3
        wanted = list(initial)
        wanted[0:2] = [max(seed_hash-1,0),0x44 if seed_hash==0 else 0x42 if seed_hash==1 else 2]
        wanted[4:8] = [y>>8,low_index,4 if outside else complement>>6,((complement>>2)&15)+1]
        wanted[16:18] = [low_index,0x10|(0x40 if low_index==0 else 0)|(4 if low_index.bit_count()%2==0 else 0)]
        cost = (block_cost(0xDE9A,0xDEA6)+int(seed_hash==0)+block_cost(0xDEA7,0xDEBD)
            -(1-outside)+region_cost+iterations*(block_cost(0xDEBD,0xDEC2)+32)
            +block_cost(0xDEC2,0xDED2)+outside+block_cost(0xDED4,0xDEDC))
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],cost)
        expected = list(memory)
        for address,value in writes:
            expected[address] = value
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(20000):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',first,second,control))
        memory.recording = False
        compared = (*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (first,second,control,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes), (first,second,control)
        touched = {address for address,_ in writes}
        counts[kind] += 1
        region_counts[region] += 1
        total_calls += iterations

    # Проверка каждого первого слова зерна и всех координатных областей при одном шаге.
    for first in range(65536):
        check(first,(first*40503+0xA55A)&65535,0,'all_first_words')
    print('Seeded parameters first words complete',flush=True)
    # Проверка всех управляющих байтов для каждой из четырёх областей, FF означает 256 шагов.
    for first in (0x4A36,0x4734,0x4738,0):
        for control in range(256):
            check(first,(control*25173+first)&65535,control,'all_counts_by_region')
    # Проверка всех младших трёхбитных свёрток отдельно для каждого числа шагов.
    for seed_hash in range(8):
        for control in range(256):
            check(0x4A36,0x4A^0x36^seed_hash,control,'all_seed_hashes_and_counts')
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),
        calls_to_original_random=total_calls,coordinate_regions=dict(region_counts),
        all_first_seed_words=True,all_control_bytes_in_every_region=True,all_hashes_and_counts=True,
        real_action_relocation_and_calls_without_stubs=True,exact_registers_flags_r_and_sp=True,
        every_ram_byte_and_write_checked=True,all_input_combinations_exhausted=False,
        game_meaning_of_indices_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsSeededParametersVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
