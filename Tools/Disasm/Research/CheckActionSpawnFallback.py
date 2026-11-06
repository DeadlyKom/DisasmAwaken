"""Проверка общего расчёта координат 7CDD до вызова геометрии."""
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from skoolkit.simutils import B, C, D, E, H, L

from CheckMusic import IYh, IYl, PC, SP, Simulator, get_registers
from ReferenceActionFoldedRandom import step


def scaled_components(vector):
    magnitudes = tuple(map(abs, vector))
    maximum = max(magnitude for magnitude in magnitudes if magnitude < 32768)
    shift = 15 - maximum.bit_length()
    stop_axis = next(axis for axis, magnitude in enumerate(magnitudes)
                     if magnitude < 32768 and magnitude << shift >= 16384)
    scaled = []
    for axis, (coordinate, magnitude) in enumerate(zip(vector, magnitudes)):
        if magnitude == 32768:
            magnitude = 0 if shift or axis < stop_axis else magnitude
        else:
            magnitude <<= shift
        scaled.append((-1 if coordinate < 0 else 1) * (magnitude & ~0x200))
    return scaled


def main():
    memory = flat_action()
    sim = Simulator(memory)
    streams = (0xEBFF, 0xEC02, 0xEC05)
    edges = (-32768, -16384, -513, -1, 0, 1, 513, 16384, 32767)
    cases = 0
    for vector in product(edges, repeat=3):
        if all(coordinate in (0, -32768) for coordinate in vector):
            continue
        for count in (0, 1, 2, 3, 4, 7, 8, 255):
            for axis, coordinate in enumerate(vector):
                address = 0x9B70 + axis * 3
                memory[address:address + 2] = (coordinate & 65535).to_bytes(2, 'little')
            memory[0x688B] = count
            record = 0xA180
            expected = bytearray((offset * 37 + cases) & 255 for offset in range(64))
            memory[record:record + 64] = expected
            for axis, (address, coordinate, mask, default) in enumerate(
                zip(streams, scaled_components(vector), (15, 15, 3), (7, 7, 1))
            ):
                seed = (cases * 719 + axis * 2953) & 65535
                fold = (cases * 7 + axis * 53) & 255
                memory[address:address + 3] = seed.to_bytes(2, 'little') + bytes((fold,))
                result = step(seed, fold)
                word = result['word']
                high = ((word >> 8) & mask) or default
                if word & 0x8000:
                    high ^= 255
                updated = (coordinate + (high << 8) + (word & 255)) & 65535
                expected[axis * 2:axis * 2 + 2] = updated.to_bytes(2, 'little')
            final = step(result['word'], result['fold'])
            expected[10] = 1
            if count:
                index = final['word'] & 7
                while index >= count:
                    index //= 2
                expected[38] = index
            sim.registers[:] = get_registers({'PC': 0x7CDD, 'SP': 0xBFFE, 'IX': record}, None, False)
            for _ in range(750):
                if sim.registers[PC] in (0x7DD1, 0x7DD4):
                    break
                sim.run()
            context = (vector, count)
            assert sim.registers[PC] == (0x7DD1 if count else 0x7DD4), context
            assert sim.registers[SP] == 0xBFFE and bytes(memory[record:record + 64]) == expected, context
            if count:
                iy = sim.registers[IYh] * 256 + sim.registers[IYl]
                assert iy == 0x9B1B + 12 * (index + 1), context
            assert bytes(memory[0xEC05:0xEC08]) == final['word'].to_bytes(2, 'little') + bytes((final['fold'],))
            cases += 1
    repeating_vectors = 0
    for vector in product((0, -32768), repeat=3):
        for axis, coordinate in enumerate(vector):
            address = 0x9B70 + axis * 3
            memory[address:address + 2] = (coordinate & 65535).to_bytes(2, 'little')
        sim.registers[:] = get_registers({'PC': 0x7CDD, 'SP': 0xBFFE}, None, False)
        zero_visits = 0
        for _ in range(120):
            if sim.registers[PC] == 0x7D09 and not any(sim.registers[r] for r in (H, L, D, E, B, C)):
                zero_visits += 1
                if zero_visits == 2:
                    break
            sim.run()
        assert zero_visits == 2, vector
        repeating_vectors += 1
    report = dict(passed=True, total_cases=cases, repeating_vectors=repeating_vectors, whole_object_record_compared=True,
                  stops_before_geometry_call=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnFallbackVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
