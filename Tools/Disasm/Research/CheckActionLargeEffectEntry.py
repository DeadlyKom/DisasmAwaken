"""Вход EA29 до продолжения EA3D с настоящим чтением OBJECT3D."""
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace


def main():
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks[4][:len(objects)] = objects
    banks[3][:] = bytes(memory_image()[0xC000:])
    memory = RecordedBanks(banks=banks, out7ffd=16)
    sim = Simulator(memory)
    cases = 0
    for class_code, offset in product(range(256), range(0, 256, 2)):
        memory[0xA106], memory[0xA112] = offset, class_code
        sim.registers[:] = get_registers({'PC': 0xEA29, 'SP': 0xBFFE, 'IX': 0xA100}, None, False)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.run(0xEA29, 0xEA3D)
        pointer = flat[0x9E00 + offset] | flat[0x9E01 + offset] << 8
        header = objects[pointer - 0xC000:pointer - 0xC000 + 2]
        r = sim.registers
        assert r[6:8] == [header[1], header[0]] and r[8:10] == [0xA1, 0]
        assert memory[0xEAC4] == (0x40 if class_code == 8 else 0xA0)
        assert r[SP] == 0xBFFE and r[PC] == 0xEA3D and memory.o7ffd == 16
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 16)]
        cases += 1
    allocation_cases = 0
    for free, ttl in product(range(9), range(256)):
        memory.banks[3][:] = banks[3]
        for index in range(8):
            address = 0xA795 + 18 * index
            for byte in range(18):
                memory[address + byte] = 0x21
            memory[address + 7] = 0 if index == free else 1
        memory[0xA106], memory[0xA112] = 0, 8
        memory[0x6D39], memory[0x6D3D] = 0, ttl
        vector = b'\x34\x12\xcd\xab\x80\x00'
        for index, byte in enumerate(vector):
            memory[0xA100 + index] = byte
        expected = bytearray(memory[0xA795:0xA82D])
        pointer = flat[0x9E00] | flat[0x9E01] << 8
        mode = objects[pointer - 0xC000 + 1]
        if free < 8:
            expected[18 * free:18 * (free + 1)] = vector + bytes((mode, 8, 0, 0xC4, 0, 0xC4, 1, 8, 0x80, 2, 20, 20))
        sim.registers[:] = get_registers({'PC': 0xEA29, 'SP': 0xBFFE, 'IX': 0xA100}, None, False)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.run(0xEA29, 0xEA6F)
        assert bytes(memory[0xA795:0xA82D]) == expected, (free, ttl)
        assert memory[0x6D39] == 1 and memory[0x6D3D] == max(ttl, 16), (free, ttl)
        assert sim.registers[SP] == 0xBFFE and sim.registers[8:10] == [0xA1, 0]
        assert trace.writes == [(0x7FFD, value) for value in (20, 16, 19, 16)]
        allocation_cases += 1
    report = dict(passed=True, total_cases=cases, all_even_object_indices=True,
                  allocation_cases=allocation_cases, allocation_stopped_before_ea6f=True,
                  assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionLargeEffectEntryVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
