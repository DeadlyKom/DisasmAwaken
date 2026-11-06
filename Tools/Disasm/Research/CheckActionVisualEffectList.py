"""Покадровое обновление всех восьми записей и композиция их растра."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionPatchedVector import COEFFICIENTS, OUTPUTS
from CheckActionVisualEffectTransfer import effect_raster
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import EXP, LOG
from ReferenceActionPatchedVector import evaluate


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
                  assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionVisualEffectListVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
