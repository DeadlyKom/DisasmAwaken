"""Ветка 7C21, случайные координаты и настоящий CreateSmallEffect."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionFoldedRandom import step


def main():
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    banks[3][:] = bytes(memory_image()[0xC000:])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks[4][:len(objects)] = objects
    cases = 0
    for index, free, ttl in product(range(0, 256, 2), range(9), (0, 25, 26, 255)):
        memory = RecordedBanks(banks=[bank.copy() for bank in banks], out7ffd=16)
        coordinates = []
        for axis, address in enumerate((0xEC05, 0xEC02, 0xEBFF)):
            word = (index * 271 + free * 479 + axis * 18721) & 65535
            fold = (ttl + axis * 47) & 255
            memory[address], memory[address + 1], memory[address + 2] = word & 255, word >> 8, fold
            random_word = step(word, fold)['word']
            coordinates.append((((random_word ^ 32768) - 32768) // 2) & 65535)
        for slot in range(8):
            memory[0xA795 + 18 * slot + 7] = 0 if slot == free else 1
        record = b''.join(word.to_bytes(2, 'little') for word in coordinates)
        expected = bytearray(memory[0xA795:0xA82D])
        pointer = flat[0x9E00 + index] | flat[0x9E01 + index] << 8
        mode = objects[pointer - 0xC000 + 1]
        if free < 8:
            expected[18 * free:18 * (free + 1)] = record + bytes((mode, 26, 0, 0xD8, 0, 0xD8, 1, 13, 0xC0, 0, 12, 12))
        memory[0x6D39], memory[0x6D3D] = 0, ttl
        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0x7C21, 'SP': 0xBFFE, 'IX': 0xA100, 'HL': index}, None, False)
        sim.run(0x7C21, 0x7C6E)
        context = (index, free, ttl)
        assert sim.registers[PC] == 0x7C6E and sim.registers[SP] == 0xBFFE, context
        assert bytes(memory[0xA100:0xA106]) == record, context
        assert bytes(memory[0xA795:0xA82D]) == expected, context
        assert (memory[0x6D39], memory[0x6D3D]) == (1, max(ttl, 26)), context
        assert trace.writes == [(0x7FFD, page) for page in (20, 16, 19, 16)] and memory.o7ffd == 16
        cases += 1
    report = dict(passed=True, total_cases=cases, all_even_model_indices=True,
                  full_effect_pool_covered=True, stops_before_target_step=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnSmallEffectVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
