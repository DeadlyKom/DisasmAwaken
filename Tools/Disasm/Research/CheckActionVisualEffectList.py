"""Покадровое обновление всех восьми записей и композиция их растра."""
from collections import Counter
from itertools import product
import json
from struct import pack

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionPatchedVector import COEFFICIENTS, OUTPUTS
from CheckActionVisualEffectTransfer import effect_raster
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from ReferenceActionLogRatio import EXP, LOG
from ReferenceActionPatchedVector import evaluate


class FrameCycleMemory(RecordedBanks):
    def __init__(self, banks):
        super().__init__(banks=[bank.copy() for bank in banks], out7ffd=0x13)
        self.voxel_tail_accesses = []

    def __getitem__(self, address):
        if isinstance(address, int) and self.o7ffd & 7 == 3 and 0xE1C0 <= address < 0xE500:
            self.voxel_tail_accesses.append(('read', address))
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.o7ffd & 7 == 3 and 0xE1C0 <= address < 0xE500:
            self.voxel_tail_accesses.append(('write', address))
        super().__setitem__(address, value)


def check_frame_cycles(banks, voxel, matrix):
    reports = []
    stack = 0xBFFE
    variants = ((0xEC00, 0xD800, 0xC0, 13, 12),
                (0xEC1B, 0xC400, 0x280, 8, 20))
    for entry, first, stride, count, size in variants:
        for index in (0, 7):
            memory = FrameCycleMemory(banks)
            sim = Simulator(memory)
            trace = PortTrace(sim)
            sim.set_tracer(trace)
            record = 0xA795 + index * 18
            vector = (0, 0, 0x0800)
            state = count * 2 + 1
            mode = 2
            put(memory, stack, (0xFF, 0x3F))
            sim.registers[:] = get_registers(
                {'PC': entry, 'SP': stack, 'IY': record - 18, 'A': mode,
                 '^A': state, '^HL': vector[0], '^DE': vector[1], '^BC': vector[2]},
                None, False)
            sim.run(entry, 0x3FFF)
            expected_record = bytearray(pack('<HHHBBHHBBHBB', *vector, mode, state,
                                             first, first, 1, count, stride, size, size))
            assert bytes(memory[record:record + 18]) == expected_record
            assert sim.registers[SP] == stack + 2 and not trace.writes

            memory.out7ffd(0x10)
            memory[0x6D39], memory[0x6D3D] = 1, state
            memory[0xBFFE], memory[0xBFFF] = 255, 63
            for address in (0xE5B3, 0xE5D2, 0xE5ED):
                put(memory, address, (0, 0))
            for addresses, values in zip(COEFFICIENTS, matrix):
                for address, value in zip(addresses, values):
                    memory[address] = value
            outputs = [memory[a] | memory[a + 1] << 8 for a in OUTPUTS]
            raster = list(memory.banks[2][:0xC00])
            frame_addresses, changed_ticks = [], 0
            for tick in range(state + 1):
                if tick < state:
                    phase = tick % count
                    frame = first + stride * phase
                    frame_addresses.append(frame)
                    expected_record[7] = state - tick - 1
                    expected_record[8:10] = pack('<H', frame)
                    expected_record[12] = count - phase
                    result = evaluate(vector, matrix, outputs)
                    outputs = result['outputs']
                    x, y, depth = outputs
                    assert not result['overflow'] and 0 < depth < 32768
                    previous_raster = raster
                    raster = effect_raster(raster, voxel, x, y, depth, mode, size, size, frame)
                    changed_ticks += raster != previous_raster
                    ports = [(0x7FFD, 0x13), (0x7FFD, 0x10)]
                else:
                    memory[0x6D39], memory[0x6D3D] = 1, 2
                    ports = []
                put(memory, stack, (0xFF, 0x3F))
                trace.writes.clear()
                sim.registers[:] = get_registers({'PC': 0x6D38, 'SP': stack}, None, False)
                sim.run(0x6D38, 0x3FFF)
                context = (hex(entry), index, tick)
                assert sim.registers[SP] == stack + 2 and memory.o7ffd == 0x10, context
                assert bytes(memory[record:record + 18]) == expected_record, context
                assert list(memory.banks[2][:0xC00]) == raster and trace.writes == ports, context
            assert changed_ticks and not memory.voxel_tail_accesses
            reports.append(dict(creator=hex(entry), record_index=index,
                                frame_addresses=[hex(value) for value in frame_addresses],
                                frame_bytes=stride, last_frame_end=hex(first + count * stride),
                                changed_raster_ticks=changed_ticks, voxel_tail_accesses=0,
                                inactive_tick_verified=True))
    return reports


def main():
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    voxel = memory_image()
    banks[3][:] = bytes(voxel[0xC000:])
    banks[2][0x1100:0x1200] = bytes(word & 255 for word in LOG)
    banks[2][0x1200:0x1300] = bytes(word >> 8 for word in LOG)
    banks[2][0x1300:0x1400] = bytes(EXP)
    matrix = ((127, 0, 0), (0, 127, 0), (0, 0, 127))
    counts = Counter()
    for enable, ttl, serial in product((0, 1, 255), (0, 1, 2, 255), range(32)):
        memory = RecordedBanks(banks=[bank.copy() for bank in banks], out7ffd=16)
        memory[0x6D39], memory[0x6D3D] = enable, ttl
        memory[0xBFFE], memory[0xBFFF] = 255, 63
        deltas = (7, 0xFFFF, serial * 13)
        for address, value in zip((0xE5B3, 0xE5D2, 0xE5ED), deltas):
            memory[address], memory[address + 1] = value & 255, value >> 8
        for addresses, values in zip(COEFFICIENTS, matrix):
            for address, value in zip(addresses, values):
                memory[address] = value
        outputs = [memory[address] | memory[address + 1] << 8 for address in OUTPUTS]
        raster = list(banks[2][:0xC00])
        records = bytearray()
        ports = []
        for index in range(8):
            vector = (serial * 29, (index * 97 - 300) & 65535, (256 + index * 471 - serial * 37) & 65535)
            mode = (index + serial) % 7
            state = (index + serial) % 5
            width = height = 12 if index & 1 else 20
            resource = 0xD800 if index & 1 else 0xC400
            phase = (index + serial) % 3
            step = 0xC0 if index & 1 else 0x280
            fields = bytearray(b''.join(value.to_bytes(2, 'little') for value in vector))
            fields += bytes((mode, state))
            fields += resource.to_bytes(2, 'little') * 2 + bytes((phase, 4)) + step.to_bytes(2, 'little') + bytes((width, height))
            for offset, byte in enumerate(fields):
                memory[0xA795 + index * 18 + offset] = byte
            if enable and state:
                for axis, value in enumerate(vector):
                    fields[2 * axis:2 * axis + 2] = ((value - deltas[axis]) & 65535).to_bytes(2, 'little')
                fields[7] -= 1
                cursor = resource if phase == 1 else resource + step
                fields[8:10] = cursor.to_bytes(2, 'little')
                fields[12] = 4 if phase == 1 else (phase - 1) & 255
                result = evaluate(vector, matrix, outputs)
                outputs = result['outputs']
                x, y, depth = outputs
                if not result['overflow'] and 0 < depth < 32768:
                    raster = effect_raster(raster, voxel, x, y, depth, mode, width, height, cursor)
                    ports.extend(((0x7FFD, 19), (0x7FFD, 16)))
                    counts['draws'] += 1
                counts['active_records'] += 1
            records.extend(fields)
        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0x6D38, 'SP': 0xBFFE}, None, False)
        sim.run(0x6D38, 0x3FFF)
        context = (enable, ttl, serial)
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000 and memory.o7ffd == 16, context
        assert bytes(memory[0xA795:0xA825]) == records, context
        assert list(memory.banks[2][:0xC00]) == raster and trace.writes == ports, context
        assert memory[0x6D39] == (0 if enable and ttl == 1 else enable)
        assert memory[0x6D3D] == ((ttl - 1) & 255 if enable else ttl)
        counts['cases'] += 1
    report = dict(passed=True, total_cases=counts['cases'], outcomes=dict(counts),
                  all_eight_record_positions=True, whole_raster_compared=True,
                  original_creator_frame_cycles=check_frame_cycles(banks, voxel, matrix),
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionVisualEffectListVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
