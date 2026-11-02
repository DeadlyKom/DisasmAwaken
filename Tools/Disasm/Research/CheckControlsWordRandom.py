"""Независимая формула четырёхбайтового генератора DD5D, точный стек и флаги."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsPointMotion import block_cost


def reference(first, second):
    # Расчёт двух сумм с отдельным переносом из первого сложения слова.
    incremented = (first+0x101)&65535
    total = incremented+second
    low_mix = ((second&255)+(total&255)+(total>>16))&255
    folded = ((total&65535)+((first&255)<<8)+low_mix)&65535
    next_second = (((folded>>8)^(first&255)^0xA7)<<8) | ((folded&255)^low_mix^0x75)
    output = (second>>8)^(second&255)^(next_second>>8)^(next_second&255)
    flags = (output&0xA8) | (0x40 if output==0 else 0) | (4 if output.bit_count()%2==0 else 0)
    return second, next_second, output, flags


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()
    cost = block_cost(0xDD5D, 0xDD87)

    def check(first, second, kind):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        memory[0x9B15:0x9B19] = [first&255, first>>8, second&255, second>>8]
        memory[0xBFFE:0xC000] = [0xFF, 0x3F]
        initial = get_registers({'AF': (first^second), 'HL': 0x1357, 'DE': 0x2468,
            'BC': (first*73+second)&65535, '^AF': 0xDEF0, '^HL': 0x1234,
            '^DE': 0x5678, '^BC': 0x9ABC, 'IX': 0xABCD, 'IY': 0x5C3A,
            'SP': 0xBFFE, 'PC': 0xDD5D}, None, False)
        initial[14], initial[15], initial[26], initial[27] = first&255, second&255, first&1, second%3
        next_first, next_second, output, flags = reference(first, second)
        wanted = list(initial)
        wanted[0:2] = [output, flags]
        wanted[4:8] = [next_second>>8, next_second&255, next_first>>8, next_first&255]
        wanted[SP], wanted[15] = 0xC000, refresh(initial[15], cost)
        writes = [(0xBFFC, initial[3]), (0xBFFD, initial[2]),
            (0x9B15, next_first&255), (0x9B16, next_first>>8),
            (0x9B17, next_second&255), (0x9B18, next_second>>8)]
        expected = list(memory)
        for address, value in writes:
            expected[address] = value
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(60):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат', first, second))
        memory.recording = False
        compared = (*range(13), 14, 15, *range(16,24), 26, 27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (first, second,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes), (first,second)
        touched = {address for address, _ in writes}
        counts[kind] += 1

    # Проверка каждого значения первого слова при меняющемся втором слове.
    for first in range(65536):
        check(first, (first*40503+0xA55A)&65535, 'all_first_words')
    print('Word random first words complete', flush=True)
    # Проверка каждого значения второго слова при другой связи с первым словом.
    for second in range(65536):
        check((second*25173+0x5AA5)&65535, second, 'all_second_words')
    # Проверка каждой пары младших байтов с независимо меняющимися старшими.
    for low_first in range(256):
        for low_second in range(256):
            check((((low_first+3*low_second)&255)<<8)|low_first,
                  (((7*low_first+low_second)&255)<<8)|low_second, 'all_low_byte_pairs')
    # Проверка крайних слов отдельно от регулярных связанных наборов.
    for first in (0, 1, 0xFF, 0x100, 0x7FFF, 0x8000, 0xFEFF, 0xFF00, 0xFFFE, 0xFFFF):
        for second in (0, 1, 0xFF, 0x100, 0x7FFF, 0x8000, 0xFEFF, 0xFF00, 0xFFFE, 0xFFFF):
            check(first, second, 'edge_pairs')
    report = dict(passed=True, total_cases=sum(counts.values()), cases_by_kind=dict(counts),
        independent_word_formula=True, exact_registers_flags_r_and_sp=True,
        every_ram_byte_and_write_checked=True, refresh_m1=cost,
        all_32_bit_states_exhausted=False, period_proved=False, statistical_quality_proved=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsWordRandomVerification.json').write_bytes(
        (json.dumps(report, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
