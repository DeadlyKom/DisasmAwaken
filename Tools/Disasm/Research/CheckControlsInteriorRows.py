"""Полосы внутренних 30 байтов строк линейного буфера, оба изменяемых направления."""
from pathlib import Path
from collections import Counter
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from CheckControlsEvenSpan import and_flags


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    counts = Counter()
    touched = set()

    def check(entry,y,rows,fill,toggle,mode,low):
        nonlocal touched
        memory.recording = False
        # Восстановление предыдущих записей и подготовка независимого режима.
        for address in touched:
            memory[address] = original[address]
        memory[0xD18C] = mode
        memory[0xBFFE:0xC000] = [0xFF,0x3F]
        initial = get_registers({'AF':y*256+0x5A,'HL':0x8B00+low,'DE':0x2468,'BC':rows*256+0x9C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':toggle*256+fill,'IY':0x5C3A,'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27] = mode,(fill+mode)&255,mode&1,mode%3
        expected = list(memory)
        wanted = list(initial)
        writes = []
        if entry == 0xD57B:
            value = (low&0xE0)|1
            wanted[0:2] = [value,and_flags(value)&~0x10]
            wanted[2:4] = [0,255]
            wanted[5] = value
            m1 = 9
        else:
            upward = entry == 0xD208
            delta = -32 if upward else 32
            n = min(rows,y+1 if upward else 96-y)
            final = (0x8000+32*y+31+delta*n)&65535
            boundary_exit = rows != 0 and n == (y+1 if upward else 96-y)
            writes += [(0xD5B5,0xE0 if upward else 0x20),(0xD5B6,0xFF if upward else 0),
                       (0xD600,0x80 if upward else 0x8C),(0xD601,0x38 if upward else 0x30),
                       (0xBFFD,0x24),(0xBFFC,0x68),(0xBFFB,y),(0xBFFA,and_flags(mode)),
                       (0xBFF9,rows),(0xBFF8,y)]
            for row in range(n):
                start = 0x8000+32*(y-row if upward else y+row)
                value = fill ^ (toggle if row&1 else 0)
                writes += [(start+column,value) for column in range(30,0,-1)]
            wanted[0:2] = [y,and_flags(mode)]
            wanted[2:4] = [rows,y]
            wanted[6:8] = [final>>8,final&255]
            wanted[9] = fill ^ (toggle if n&1 else 0)
            # Подсчёт M1 по фиксированным блокам, один DJNZ пропускается при выходе по границе.
            m1 = (29 if upward else 28) + (1+75*n-int(boundary_exit) if rows else 0)
        for address,value in writes:
            expected[address] = value
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],m1)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        measured_m1 = 0
        for _ in range(8000):
            if simulator.registers[PC] == 0x3FFF:
                break
            old_r = simulator.registers[15]
            simulator.run()
            increment = (simulator.registers[15]-old_r)&127
            assert increment in (1,2)
            measured_m1 += increment
        else:
            raise AssertionError(('возврат',entry,y,rows))
        memory.recording = False
        compared = (*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (entry,y,rows,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory == expected and Counter(memory.writes) == Counter(writes), (entry,y,rows)
        assert measured_m1 == m1
        touched = {a for a,_ in writes}
        counts[format(entry,'04X')] += 1

    # Проверка всех младших адресов и режимов подготовительного входа.
    for low in range(256):
        for mode in (0,1,0x55,0x80,0xFF):
            check(0xD57B,0,0,0xA5,0x60,mode,low)
    # Проверка каждой начальной строки, границ количества и пересечения верхнего и нижнего края.
    for entry in (0xD208,0xD211):
        for y in range(96):
            for rows in sorted({0,1,2,3,95,96,97,255,y,95-y,y+1,96-y}):
                check(entry,y,rows,(y*73+rows)&255,(y*31+rows)&255,(rows*17+y)&255,0x39)
    # Проверка всех байтов заливки, XOR-чередования, режима и количества на коротких полосах.
    for value in range(256):
        for entry in (0xD208,0xD211):
            for rows in range(256):
                check(entry,1 if entry==0xD208 else 94,rows,value,(value*73)&255,value,0x39)
        if value%64 == 63:
            print('Interior profiles',value+1,flush=True)
    result = dict(passed=True,total_cases=sum(counts.values()),cases_by_entry=dict(counts),
        all_start_rows=True,all_row_count_bytes=True,all_fill_toggle_and_mode_bytes=True,
        both_direction_patches=True,thirty_inner_bytes_only=True,boundaries_clamp_to_96_rows=True,
        every_ram_byte_and_write_checked=True,exact_registers_flags_and_r=True,
        prepare_mode_read_has_no_output_effect=True,zero_count_still_writes_patches_and_stack=True,
        direct_full_M1_count_checked=True,complete_joint_input_product_exhausted=False,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsInteriorRowsVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
