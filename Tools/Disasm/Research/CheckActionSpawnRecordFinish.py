"""Инициализация полей записи 7DD4 до диспетчера класса."""
import json
from itertools import product

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionFoldedRandom import step
from ReferenceControlsPointRespawn import refresh


def main():
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks[4][:len(objects)] = objects
    memory = RecordedBanks(banks=banks, out7ffd=16)
    sim = Simulator(memory)
    cases = 0
    for cls, index in product(range(256), range(0, 256, 2)):
        address = 0xA100 + 64 * ((cls + index) % 25)
        initial = bytearray((offset * 37 + cls * 73 + index) & 255 for offset in range(64))
        initial[6], initial[18] = index, cls
        for offset, byte in enumerate(initial):
            memory[address + offset] = byte
        inputs = ((0xEBF0, (cls * 173 + index * 37) & 65535, cls),
                  (0xEBF3, (index * 281 + cls * 47) & 65535, index))
        for pointer, seed, fold in inputs:
            memory[pointer], memory[pointer + 1], memory[pointer + 2] = seed & 255, seed >> 8, fold
        seed_word = (cls * 211 + index * 97) & 65535
        memory[0xEBDB], memory[0xEBDC], memory[0xEBDD] = seed_word & 255, seed_word >> 8, 255
        expected = initial.copy()
        expected[7] = 0
        expected[11:17] = bytes((255, 0, seed_word & 255, seed_word >> 8, initial[15], 32))
        expected[17] = 32
        expected[20], expected[21] = 0, 255
        expected[22], expected[23] = initial[10], 0
        expected[32:34] = b'\xff\xff'
        rnd = step(*inputs[1][1:])['word']
        expected[19], expected[34] = min(99, (rnd & 255) | 50), (rnd >> 8) | 160
        if cls == 8:
            expected[19], expected[34] = 240, 250
            expected[13:16] = expected[7:10]
        model = flat[0x9E00 + index] | flat[0x9E01 + index] << 8
        expected[37] = 1 if objects[model - 0xC000 + 1] == 4 else 2
        sim.registers[:] = get_registers({'PC': 0x7DD4, 'SP': 0xBFFE, 'IX': address}, None, False)
        sim.registers[15] = (cls + index) & 255
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        for _ in range(280):
            pc = sim.registers[PC]
            if pc == 0x64DF:
                break
            sample = refresh(sim.registers[15], 2)
            if pc == 0x7E63:
                expected[24] = (sample + 1) & 15
            if pc == 0x7E72 and sample & 64:
                expected[24] |= 4
            sim.run()
        context = (cls, index)
        assert sim.registers[PC] == 0x64DF and sim.registers[SP] == 0xBFFE, context
        assert bytes(memory[address:address + 64]) == expected, context
        for pointer, seed, fold in inputs:
            result = step(seed, fold)
            assert bytes(memory[pointer:pointer + 3]) == result['word'].to_bytes(2, 'little') + bytes((result['fold'],))
        assert memory[0xEBDD] == 0 and trace.writes == [(0x7FFD, 20), (0x7FFD, 16)]
        cases += 1
    report = dict(passed=True, total_cases=cases, all_classes_and_even_model_indices=True,
                  whole_object_record_compared=True, stops_before_class_dispatch=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnRecordFinishVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
