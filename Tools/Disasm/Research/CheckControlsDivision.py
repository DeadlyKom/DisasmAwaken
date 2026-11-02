"""D165/D167, независимая проверка деления divmod для 8-битового частного."""
from pathlib import Path
import collections
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory


def main():
    memory = Memory(base_memory())
    memory[0xBFFE:0xC000] = [255,63]
    simulator = Simulator(memory)
    initial_memory = list(memory)
    counts = collections.Counter()
    max_steps = 0
    def check(entry,numerator,divisor):
        nonlocal max_steps
        if divisor and numerator >> 8 < divisor:
            quotient,remainder = divmod(numerator,divisor)
        elif divisor == 0:
            # Вычисление полного восьмиразрядного частного при всегда истинном сравнении u>=0.
            quotient,remainder = 255,numerator & 255
        else:
            # Арифметическая модель восьми шагов с исходным байтовым ограничением промежуточного остатка.
            quotient,remainder = 0,numerator >> 8
            for bit in range(7,-1,-1):
                expanded = 2*remainder + ((numerator >> bit) & 1)
                accepted = expanded >= divisor
                remainder = (expanded-divisor) & 255 if accepted else expanded
                quotient = 2*quotient+accepted
        initial = get_registers({'AF':(numerator >> 8)*256+((numerator+divisor*73)&255),
            'HL':0x1357,'DE':0xA500 | (((numerator >> 8)*73+divisor*17)&255 if entry == 0xD165 else numerator & 255),'BC':divisor*256+((numerator*17+divisor)&255),
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'PC':entry,'SP':0xBFFE},None,False)
        initial[14],initial[26],initial[27] = numerator & 255,numerator & 1,numerator % 3
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for steps in range(100):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',entry,numerator,divisor))
        memory.recording = False
        max_steps = max(max_steps,steps)
        expected = list(initial)
        expected[0:2] = [remainder,(quotient & 0xA8) | (0x40 if quotient == 0 else 0) | (4 if quotient.bit_count()%2 == 0 else 0)]
        expected[4:6] = [quotient,0]
        expected[SP] = 0xC000
        compared = (*range(13),14,*range(16,24),26,27)
        assert not memory.writes and all(simulator.registers[i] == expected[i] for i in compared), (entry,numerator,divisor,simulator.registers[:8],expected[:8])
        counts[format(entry,'04X')] += 1
    # Проверка каждой возможной пары делитель-частное при граничных и средних остатках.
    for divisor in range(1,256):
        for quotient in range(256):
            for remainder in sorted({0,divisor//2,divisor-1}):
                check(0xD167,quotient*divisor+remainder,divisor)
    # Проверка всех старших байтов и всех ненулевых делителей при переполнении байтового частного.
    for divisor in range(1,256):
        for high in range(divisor,256):
            for low in (0,1,127,128,254,255):
                check(0xD167,high*256+low,divisor)
    # Проверка нулевого делителя на всём диапазоне 16-битового делимого.
    for numerator in range(65536):
        check(0xD167,numerator,0)
    # Проверка каждого A и B для входа с нулевым младшим байтом, включая нуль и переполнение.
    for divisor in range(256):
        for high in range(256):
            check(0xD165,high*256,divisor)
    assert memory == initial_memory
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_entry=dict(counts),
        all_nonzero_divisors=True,all_byte_quotients=True,boundary_and_middle_remainders=True,
        all_valid_fraction_inputs=True,exact_registers_and_flags=True,no_memory_writes=True,
        original_instructions=True,max_instruction_steps=max_steps,
        zero_divisor_all_words=True,quotient_overflow_boundary_low_bytes=True,
        overflow_is_original_byte_recurrence=True,all_fraction_a_b_pairs=True,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsDivisionVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
