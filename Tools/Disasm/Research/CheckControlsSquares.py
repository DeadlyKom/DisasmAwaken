"""Чтение двух плоскостей по D30B и корень разности квадратов по D609, только эти входы."""
from pathlib import Path
from collections import Counter
from math import isqrt
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    counts = Counter()
    touched = set()

    def check(entry,index,flags,radius=0):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        memory[0xBFFE:0xC000] = [0xFF,0x3F]
        initial = get_registers({'AF':index*256+flags,'HL':0x1357,'DE':radius*256+0x68,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27] = flags,index,flags&1,flags%3
        expected = list(memory)
        wanted = list(initial)
        if entry == 0xD30B:
            wanted[1] = 0x80 | (flags&1)
            wanted[4:6] = [memory[0xC400+index],memory[0xC300+index]]
            writes = [(0xBFFD,0x13),(0xBFFC,0x57)]
            wanted[15] = refresh(index,8)
        else:
            # Вычисление результата через целочисленный корень, а не воспроизведение двоичного поиска CPU.
            difference = (radius*radius-index*index-(flags&1))&65535
            wanted[0:2] = [isqrt(difference),0x45]
            wanted[15] = refresh(index,179-isqrt(difference).bit_count())
            writes = [(0xBFFD,0x36),(0xBFFC,0x9C),(0xBFFB,radius),(0xBFFA,0x68),
                (0xBFF9,0x13),(0xBFF8,0x57),(0xBFF7,index),(0xBFF6,flags),
                (0xBFF5,0xD6),(0xBFF4,0x11),(0xBFF3,0x13),(0xBFF2,0x57),
                (0xBFF7,0xD6),(0xBFF6,0x17),(0xBFF5,(radius*radius)>>8),(0xBFF4,(radius*radius)&255),
                (0xD188,difference&255),(0xD189,difference>>8)]
            for _ in range(8):
                writes += [(0xBFF7,0xD6),(0xBFF6,0x26),(0xBFF5,difference>>8),(0xBFF4,difference&255)]
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(400):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',entry,index,radius,flags))
        memory.recording = False
        compared = (*range(13),14,15,*range(16,24),26,27)
        for address,value in writes:
            expected[address] = value
        assert memory == expected and Counter(memory.writes) == Counter(writes), (entry,index,radius,flags)
        wanted[SP] = 0xC000
        assert all(wanted[i] == simulator.registers[i] for i in compared), (entry,index,radius,flags,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        touched = {address for address,_ in memory.writes}
        counts[format(entry,'04X')] += 1

    # Проверка всех входных AF чтения таблицы, включая сохранение Carry через INC H.
    for index in range(256):
        for flags in range(256):
            check(0xD30B,index,flags)
    # Проверка каждого радиуса и смещения при обоих входных Carry, включая байтовое переполнение разности.
    for radius in range(256):
        for index in range(256):
            for carry in (0,1):
                check(0xD609,index,0x5A|carry,radius)
        if radius%64 == 63:
            print('Square root radii',radius+1,flush=True)
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_entry=dict(counts),
        lookup_all_af=True,lookup_exact_registers_flags_memory_writes_and_r=True,
        square_root_all_radius_offset_carry=True,square_root_formula='isqrt((radius**2-offset**2-Carry) AND FFFF)',
        square_root_exact_output_registers=True,square_root_internal_stack_values_proved=True,
        square_root_exact_r=True,every_ram_byte_and_write_checked=True,
        whole_d30b_fragment_proved=False,whole_d609_fragment_proved=False,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsSquaresVerification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
