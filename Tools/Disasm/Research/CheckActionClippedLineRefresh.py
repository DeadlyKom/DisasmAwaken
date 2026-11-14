"""Полный DBBD для B2,00,05,00, точные R, полные M1, регистры и RAM.

Документация: ../../../Docs/ActionOverlayPair.md#счёт-r-фиксированной-линии-с-отсечением
"""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action, RecordedBanks
from CheckMusic import Simulator, get_registers
from ReferenceActionPacketRenderer import PacketRenderer
from InspectZ80 import decoder


def main(unconditional_branch=False):
    flat = flat_action()
    baseline = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    if unconditional_branch:baseline[0][0xC94B-0xC000]=0x18
    memory = RecordedBanks(banks=[bytearray(b) for b in baseline], out7ffd=16)
    cpu = Simulator(memory)
    pairs = [((0, 0), (0, 0)), ((0, 0), (255, 95)), ((255, 0), (0, 95)),
             ((127, 0), (127, 95)), ((0, 47), (255, 47))]
    zones=[(x,y) for x in (-64,7,319) for y in (-64,11,159)]
    pairs += [(first,second) for first in zones for second in zones for seen in range(256)]
    pairs += [(((i*73)%1280-512,(i*109)%1280-512),((i*137)%1280-512,(i*197)%1280-512)) for i in range(4096)]
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    zero_code_start=len(pairs)
    pairs += [((0,0),(255,95))]*3
    refresh_values, costs = set(), set()
    for serial, (first, second) in enumerate(pairs):
        memory.recording = False
        for bank in (0, 2, 5):
            memory.banks[bank][:] = baseline[bank]
        pointer = (0xA000, 0xA0FE, 0x9FFE)[serial % 3]
        for i, byte in enumerate((0xB2, 0, 5, 0)):memory[pointer+i]=byte
        for i, (x, y) in enumerate((first, second)):
            region=(2 if x<0 else 1 if x>255 else 0)|(8 if y<0 else 4 if y>95 else 0)
            code=((region^15)<<4)|region
            if serial>=zero_code_start and (serial-zero_code_start==2 or i==serial-zero_code_start):code=0
            for j, byte in enumerate((x&255,(x>>8)&255,y&255,(y>>8)&255,code)):memory[0x8E00+5*i+j]=byte
        memory[0xBFFE],memory[0xBFFF]=255,63
        initial = get_registers({'PC': 0xDBBD, 'SP': 0xBFFE, 'HL': pointer,
            'DE': 0x2468, 'BC': 0x369C, 'AF': serial & 65535, 'IX': 0xABCD, 'IY': 0x5C3A,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial * 73 & 255, serial & 1, serial % 3
        refresh_values.add(initial[15])
        memory[0xCF07]=serial&255
        oracle = PacketRenderer(memory.banks, initial, ops, 24, 12)
        oracle.render(clipped=True)
        assert oracle.refresh_proved
        cpu.registers[:] = initial
        memory.writes, memory.recording = [], True
        measured = 0
        # Сверка полного числа M1, не только остатка R по модулю 128.
        for _ in range(10000):
            if cpu.registers[24] == 0x3FFF:
                break
            before = cpu.registers[15]
            cpu.run()
            increment = (cpu.registers[15] - before) & 127
            assert increment in (1, 2)
            measured += increment
        else:
            raise AssertionError(('нет внешнего возврата', serial))
        memory.recording = False
        compared = (*range(25), 26, 27)
        assert all(cpu.registers[i] == oracle.r[i] for i in compared), (serial, first, second, 'registers',
            [(i, oracle.r[i], cpu.registers[i]) for i in compared if oracle.r[i] != cpu.registers[i]])
        assert measured == oracle.refresh_m1, (serial, measured, oracle.refresh_m1)
        assert memory.banks == oracle.banks and Counter(memory.writes) == Counter(oracle.writes), (serial, 'RAM')
        costs.add(measured)
    assert refresh_values == set(range(256))
    result = dict(passed=True, total_cases=len(pairs), fixed_packet=[178, 0, 5, 0],
         M1_range=[min(costs), max(costs)],
        all_initial_R_values=True, exact_registers_including_R=True, full_M1_count_compared=True,
        all_eight_banks_and_write_multiplicity=True, fixed_clipped_packet_proved=True,explicit_zero_clip_code_branches=True,unconditional_C94B_branch=unconditional_branch,
        arbitrary_polygon_streams_proved=False, all_endpoint_pairs_exhausted=False,
        exact_T_claimed=False, irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / ('Tools/Disasm/Reports/ActionClippedLineUnconditionalRefreshVerification.json' if unconditional_branch else 'Tools/Disasm/Reports/ActionClippedLineRefreshVerification.json')).write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
