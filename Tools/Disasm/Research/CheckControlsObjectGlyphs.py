"""Маскированные значки E5E5, все позиции разрешённого окна и двенадцать исходных форм."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory, xor_flags
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsPointMotion import block_cost
from CheckControlsRasterBackground import pixel_address

SHAPES = ((7,2,7),(2,2,7),(7,4,7),(7,7,7),(4,6,7),(7,0,7),
          (3,3,3),(7,5,7),(5,5,5),(1,2,4),(5,2,5),(2,7,2))


def phase_index_evidence(original):
    flow = next(row for row in json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
                if row['name']=='Controls')['instructions']
    code = {row['address']: row for row in flow}
    groups = [(0xE5E5, ['EXX','LD A,E','AND #07','ADD A,A','LD E,A','ADD A,A',
                         'ADD A,E','EXX','LD C,A','LD B,#00']),
              (0xE60A, ['ADD HL,BC','PUSH HL','LD HL,#E68D','ADD HL,BC',
                         'LD B,(HL)','INC HL','LD C,(HL)','POP HL'])]
    checked = []
    for start, operations in groups:
        address = start
        for operation in operations:
            row = code[address]
            assert row['operation']==operation
            raw = bytes.fromhex(row['hex'])
            assert bytes(original[address:address+len(raw)])==raw
            checked.append(dict(address=address, operation=operation, hex=row['hex']))
            address += len(raw)
    return dict(phase_multiplier=6, index_shared_by_shape_and_clear_mask=True,
                instructions_checked_against_original=checked)


def main(poison_clear_tails=False, boundary_only=False, report_name='ControlsObjectGlyphsVerification.json'):
    original = base_memory()
    index_evidence = phase_index_evidence(original)
    targets = [original[0xE65D+2*i] | original[0xE65E+2*i] << 8 for i in range(20)]
    # Проверка каждого физического байта фаз по независимому сдвигу исходных трёхбитовых строк.
    for shape, rows in enumerate(SHAPES):
        for phase in range(8):
            for row, bits in enumerate(rows):
                offset = 0xE6BD + shape*48 + phase*6 + row*2
                assert original[offset]*256+original[offset+1] == (bits << 13) >> phase
    for phase in range(8):
        offset = 0xE68D+phase*6
        assert original[offset:offset+6] == [((~(0xE000 >> phase)) >> 8) & 255,
            (~(0xE000 >> phase)) & 255, 0, 0, 0, 0]
        assert original[0xE685+phase] == 128 >> phase
    assert set(targets) == {0xE6BD+48*i for i in range(12)}
    if poison_clear_tails:
        # Подстановка затрагивает только четыре неизвестных байта каждой фазы в модельной RAM.
        for phase in range(8):
            for offset in range(2,6):
                original[0xE68D+phase*6+offset] = ((phase*37+offset*53)&255) or 255
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()

    def check(x, y, kind, mode, serial):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        memory[0xA112], memory[0x9C2B] = kind, mode
        destination = pixel_address(x, y)
        # Подготовка разных прежних пикселей проверяет сохранение битов за пределами маски 3 на 3.
        for row in range(3):
            address = pixel_address(x, y+row)
            memory[address], memory[address+1] = (serial+row*51)&255, (serial*73+row*13)&255
        initial = get_registers({'AF': 0xA55A, 'HL': 0xE685+(x&7), 'DE': destination,
            'BC': 0x3600 | (128 >> (x&7)), '^AF': 0xDEF0, '^HL': 0x1234,
            '^DE': 0x4000 | x, '^BC': 0x3600 | y, 'IX': 0xA100,
            'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xE5E5}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial&255, serial&255, serial&1, serial%3
        phase, forced = x&7, mode == 255
        target = targets[1 if forced else kind]
        shape = (target-0xE6BD)//48
        source = target+phase*6
        mask = (~(0xE000 >> phase)) & 65535
        left, right = mask >> 8, mask & 255
        writes = [(0xBFFD,source >> 8),(0xBFFC,source & 255)]
        for row,bits in enumerate(SHAPES[shape]):
            address = pixel_address(x,y+row)
            pattern = (bits << 13) >> phase
            writes += [(address,(memory[address] & left) | (pattern >> 8)),
                (address+1,(memory[address+1] & right) | (pattern & 255))]
        wanted = list(initial)
        last = writes[-1][1]
        final_destination = pixel_address(x,y+2)+1
        wanted[0:8] = [last,xor_flags(last),left,right,final_destination >> 8,
            final_destination & 255,(source+5) >> 8,(source+5) & 255]
        wanted[21] = 2*phase
        wanted[PC] = 0xE4B7
        m1 = block_cost(0xE5E5,0xE627)+block_cost(0xE632,0xE645)+block_cost(0xE650,0xE65D)-(not forced)
        for row_y in (y,y+1):
            if row_y & 7 == 7:
                m1 += 4 + (0 if row_y & 63 == 63 else 3)
        wanted[15] = refresh(initial[15],m1)
        expected = list(memory)
        for address,value in writes:
            expected[address] = value
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(110):
            if simulator.registers[PC] == wanted[PC]:
                break
            simulator.run()
        else:
            raise AssertionError(('граница',x,y,kind,mode))
        memory.recording = False
        compared = (*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (x,y,kind,mode,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i] != simulator.registers[i]])
        assert memory == expected and Counter(memory.writes) == Counter(writes), (x,y,kind,mode)
        touched = {address for address,_ in writes}
        counts['forced' if forced else 'ordinary'] += 1

    # Проверка всех разрешённых координат для каждого из двадцати указателей исходной таблицы.
    for kind in range(20):
        for x in (range(64,72) if boundary_only else range(64,141)):
            for y in ((107,111,179,180) if boundary_only else range(107,181)):
                check(x,y,kind,0,counts.total())
    # Проверка всего управляющего байта и принудительного указателя 1 на границах сдвигов.
    for mode in range(256):
        for phase in range(8):
            check(64+phase,111+(mode&1)*16,mode%20,mode,counts.total())
    report = dict(passed=True,total_cases=counts.total(),cases_by_mode=dict(counts),
        all_accepted_positions_each_20_pointer_entries=not boundary_only,all_control_bytes=True,
        physical_shape_count=12,physical_phase_count=96,physical_mask_records=8,
        original_resource_bytes_checked=672,exact_registers_flags_refresh_sp=True,
        every_ram_byte_and_write_checked=True,maximum_additional_stack_bytes=2,
        type_domain=[0,19],types_outside_table_proved=False,full_e291_proved=False,
        boundary_positions_only=boundary_only,nonzero_clear_tail_fixture=poison_clear_tails,
        clear_tail_fixture_bytes=32 if poison_clear_tails else 0,
        clear_tail_fixture_values=[[original[0xE68D+phase*6+offset] for offset in range(2,6)]
                                   for phase in range(8)],
        phase_index_evidence=index_evidence,
        global_tail_purpose_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports'/report_name).write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
