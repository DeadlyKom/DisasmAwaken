"""Полный проход UpdateObjects через реальные фазовые обработчики и геометрию."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from CheckActionObjectOffsetVector import table_reference, multiply


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    baseline[4][:len(objects)] = objects
    cases = 0
    for timer, slots in product(range(256), (0, 1, 3, 25)):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
        for address in (0xE5B0, 0xE5CF, 0xE5EA, 0xE5B3, 0xE5D2, 0xE5ED):
            put(memory, address, (0, 0))
        expected = []
        for index in range(slots):
            record = bytearray(64)
            record[:6] = b'\x20\x01\x02\x03\xa0\xfe'
            record[6], record[7], record[10], record[18] = 2 * index, timer ^ 0x55, 19 + index % 3, 16
            record[22], record[23], record[36] = 3, timer, 7
            put(memory, 0xA100 + 64 * index, record)
            state = record[10]
            record[7] = ((timer ^ 0x55) + (2 if state == 20 else -2 if state == 21 else 0)) & 255
            record[10] = 3 if state == 19 or state == 21 and timer == 1 else 21 if state == 20 and timer == 1 else state
            record[23] = timer if state == 19 else 30 if state == 20 and timer == 1 else (timer - 1) & 255
            if state == 19:
                record[36] = 0
            offsets = (record[7], (record[8] + 128) & 255, record[9])
            registers, coefficients, _, _ = table_reference(flat, [0] * 30, offsets)
            value = record[36] * 256
            for axis, coefficient in enumerate(coefficients):
                delta, _ = multiply(registers, coefficient, value)
                old = int.from_bytes(record[2 * axis:2 * axis + 2], 'little')
                record[2 * axis:2 * axis + 2] = ((old + delta) & 65535).to_bytes(2, 'little')
            expected.append(record)
        end = 0xA100 + slots * 64
        put(memory, end, (128, 128))
        put(memory, 0xBFFE, (255, 63))
        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0xF729, 'SP': 0xBFFE}, None, False)
        sim.run(0xF729, 0x3FFF)
        context = (timer, slots)
        assert sim.registers[SP] == 0xC000 and sim.registers[8:10] == [end >> 8, end & 255], context
        assert sim.registers[0:2] == [128, 0x42] and sim.registers[4:6] == [0, 64], context
        for index, record in enumerate(expected):
            address = 0xA100 + 64 * index
            assert bytes(memory[address:address + 64]) == record, (context, index, [(i,a,b) for i,(a,b) in enumerate(zip(memory[address:address + 64],record)) if a!=b])
        assert trace.writes == [(0x7FFD, page) for _ in range(slots) for page in (20, 16)]
        cases += 1
    result = dict(passed=True, total_cases=cases, record_counts=[0, 1, 3, 25],
                  real_handlers=[19, 20, 21], whole_records_compared=True,
                  full_scale_and_component_updates=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionObjectWalkCompositionVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
