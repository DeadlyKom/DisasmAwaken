"""Связка 6D38, AF43, восстановления SP и перехода в страницу 3."""
from collections import Counter
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionPatchedVector import COEFFICIENTS, OUTPUTS
from CheckActionPrepareBodyTransform import profiles
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from CheckVoxelEffectDrawEntry import project, signed_quarter
from CheckVoxelSpriteSampleRaster import raster
from ReferenceActionLogRatio import EXP, LOG
from ReferenceActionPatchedVector import evaluate


def effect_raster(background, voxel, x, y, depth, mode, width, height, resource_address):
    horizontal, vertical = (x - width // 2) & 65535, (y - height // 2) & 65535
    scale = 1 << (mode + 3)
    positive = height * 512 + width * 2
    negative = ((-height * 2 & 255) << 8) | (-width * 2 & 255)
    first = project(horizontal, vertical, depth, negative, scale)
    second = project(horizontal, vertical, depth, positive, scale) if first else None
    if second is not None:
        dx, dy = ((b - a) & 65535 for a, b in zip(first, second))
        if 4 <= dx < 1024 and 4 <= dy < 1024:
            x0, y0 = ((signed_quarter(value) ^ 0x8000) - 0x8000 for value in first)
            return raster(background, voxel, voxel[resource_address:resource_address + 1024],
                          x0, y0, dx >> 2, dy >> 2, width, height)
    return background


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
    memory = RecordedBanks(banks=[bank.copy() for bank in banks], out7ffd=16)
    sim = Simulator(memory)
    counts, raster_counts = Counter(), Counter()

    def put(addr, word):
        memory[addr] = word & 255
        memory[addr + 1] = word >> 8

    for serial, (vector, matrix) in enumerate(profiles()):
        for bank in (5, 2, 0, 3):
            memory.banks[bank][:] = banks[bank]
        memory.out7ffd(16)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        effect = 0xA795 + 18 * (serial & 7)
        stack = 0xBFFE
        put(stack, 0x3FFF)
        memory[0x6D39] = 1
        memory[0x6D3D] = serial & 255
        for offset, word in zip((0, 2, 4), vector):
            put(effect + offset, word)
        mode = serial % 7
        width = height = (12, 20)[serial & 1]
        resource_address = (0xD800, 0xC400)[serial & 1]
        memory[effect + 6] = mode
        memory[effect + 7] = 1
        memory[effect + 12] = 1
        put(effect + 10, resource_address)
        put(effect + 16, height * 256 + width)
        for addresses, values in zip(COEFFICIENTS, matrix):
            for address, value in zip(addresses, values):
                memory[address] = value
        old_outputs = [memory[address] | memory[address + 1] << 8 for address in OUTPUTS]
        result = evaluate(vector, matrix, old_outputs)
        x, y, depth = result['outputs']
        outcome = 'overflow' if result['af'][1] & 4 else 'nonpositive_depth'
        if not result['af'][1] & 4 and 0 < depth < 32768:
            outcome = 'bank3'
        sim.registers[:] = get_registers({'PC': 0x6D38, 'SP': stack}, None, False)
        for _ in range(900):
            if sim.registers[PC] in (0x3FFF, 0xFA3A):
                break
            sim.run()
        r = sim.registers
        assert bytes(memory[0x6DD2:0x6DD4]) == stack.to_bytes(2, 'little'), (serial, outcome)
        if outcome == 'bank3':
            assert r[PC] == 0xFA3A and r[SP] == stack - 4 and memory.o7ffd == 0x13
            assert trace.writes == [(0x7FFD, 0x13)]
            assert r[0] == mode and r[8:10] == [effect >> 8, effect & 255]
            assert r[2] * 256 + r[3] == depth
            assert r[4] * 256 + r[5] == (y - height // 2) & 65535
            assert r[6] * 256 + r[7] == (x - width // 2) & 65535
            assert r[20:24] == [resource_address >> 8, resource_address & 255, height, width]
            assert list(memory[stack - 4:stack]) == [0x21, 0x6E, effect & 255, effect >> 8]
            expected = effect_raster(list(banks[2][:0xC00]), voxel, x, y, depth, mode, width, height, resource_address)
            for _ in range(120000):
                if sim.registers[PC] == 0x3FFF:
                    break
                sim.run()
            assert r[PC] == 0x3FFF and r[SP] == stack + 2 and memory.o7ffd == 0x10, (
                serial, hex(r[PC]), hex(r[SP]), trace.writes)
            assert trace.writes == [(0x7FFD, 0x13), (0x7FFD, 0x10)]
            actual = list(memory.banks[2][:0xC00])
            assert actual == expected, (serial, mode, width, height,
                                        [(i, a, b) for i, (a, b) in enumerate(zip(actual, expected)) if a != b][:8])
            raster_counts['changed' if expected != list(banks[2][:0xC00]) else 'unchanged'] += 1
        else:
            assert r[PC] == 0x3FFF and r[SP] == stack + 2 and memory.o7ffd == 0x10
            assert not trace.writes
        counts[outcome] += 1
    assert len(counts) == 3, counts
    assert set(raster_counts) == {'changed', 'unchanged'}, raster_counts
    report = dict(passed=True, total_cases=counts.total(), outcomes=dict(counts),
                  raster_outcomes=dict(raster_counts), actual_voxel_draw_executed=True,
                  all_3072_raster_bytes_compared=True,
                  whole_procedure_proved=False, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionVisualEffectTransferVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
