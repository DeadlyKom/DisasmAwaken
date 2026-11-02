"""D515/D53C, адрес линейного байта и включающие край битовые маски."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory


def main():
    memory = Memory(base_memory())
    simulator = Simulator(memory)
    cases = {0xD515:0,0xD53C:0}
    def check(entry,x,y,mode):
        memory.recording = False
        memory[0xD18A],memory[0xD18C] = 0xA5,mode
        memory[0xBFFE:0xC000] = [255,63]
        before = list(memory)
        saved_b = (x*73+y*31+mode)&255
        saved_f = (x*29+y*13+mode)&255
        initial = get_registers({'AF':x*256+saved_f,'BC':saved_b*256+y,'HL':0x1357,'DE':0x2468,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[26],initial[27] = mode,mode & 1,mode % 3
        simulator.registers[:] = initial
        expected = list(initial)
        address = 0x8000+32*y+x//8
        expected[6:8] = [address >> 8,address & 255]
        if entry == 0xD515:
            mask = (255 << (7-(x&7))) & 255
            expected[0:2] = [mask,0x53 | (mask & 0x28)]
            expected[2:4] = [mask,x//8]
            expected[5] = address & 255
            writes = []
        else:
            mask = 255 >> (x&7)
            expected[0:2] = [saved_b,0x42]
            expected[3] = mask
            writes = [(0xBFFC,saved_f),(0xBFFD,x),(0xD18A,saved_b)]
        for a,value in writes:
            before[a] = value
        expected[SP] = 0xC000
        memory.writes = []
        memory.recording = True
        for _ in range(80):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',entry,x,y,mode))
        memory.recording = False
        r = simulator.registers
        assert memory == before and sorted(memory.writes) == sorted(writes), ('память',entry,x,y,mode)
        compared = (*range(13),14,*range(16,24),26,27)
        assert all(r[i] == expected[i] for i in compared), ('регистры',entry,x,y,mode,[(i,r[i],expected[i]) for i in compared if r[i] != expected[i]])
        cases[entry] += 1
    # Проверка всех координат байтового X,Y в обоих направлениях включающей край маски.
    for entry in cases:
        for y in range(256):
            for x in range(256):
                check(entry,x,y,0)
    # Проверка отсутствия влияния общего байта D18C для каждой фазы маски.
    for entry in cases:
        for mode in range(256):
            for phase in range(8):
                check(entry,phase+128,(mode*73)&255,mode)
    report = dict(passed=True,total_cases=sum(cases.values()),cases_by_entry={format(k,'04X'):v for k,v in cases.items()},
        all_x_y_bytes=True,all_shared_mode_bytes_and_bit_phases=True,shared_mode_has_no_output_effect=True,
        exact_registers_and_flags=True,every_ram_byte_and_write_checked=True,
        original_instructions=True,right_mask_saved_b_and_stack_checked=True,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsSpanMasksVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
