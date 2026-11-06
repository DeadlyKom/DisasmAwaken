"""Выбор исходного шаблона на 7859 с настоящим банковым вызовом DE9A."""
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckControlsWordRandom import reference as random_step
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from CheckActionSpawnTemplateLoop import word
from skoolkit.simutils import IXh, IXl


def main():
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    banks[1][:] = bytes(base_memory()[0xC000:])
    memory = RecordedBanks(banks=banks, out7ffd=16)
    sim = Simulator(memory)
    indices = set()
    cases = 0
    for first in (0, 0x4A36, 0x4734, 0x4738):
        for control in range(256):
            second = (control * 25173 + first) & 65535
            coordinates = (0xAAAA, 0xBBBB, 0xCCCC)
            put(memory, 0x9BC1, first.to_bytes(2, 'little') + second.to_bytes(2, 'little') + bytes((control,)))
            for axis, coordinate in enumerate(coordinates):
                put(memory, 0x9B78 + axis * 3, coordinate.to_bytes(2, 'little'))
            memory[0x9B82] = memory[0x9B83] = memory[0x792E] = 0
            x, y = first, second
            for _ in range(control + 1):
                x, y, output, _ = random_step(x, y)
            index = ((output ^ 255) >> 2) & 15
            pointer = word(flat, 0x7799 + index * 2)
            sim.registers[:] = get_registers({'PC': 0x7859, 'SP': 0xBFFE}, None, False)
            trace = PortTrace(sim)
            sim.set_tracer(trace)
            sim.run(0x7859, 0x78A1)
            context = (first, second, control, index)
            assert sim.registers[PC] == 0x78A1 and sim.registers[SP] == 0xBFFE, context
            assert sim.registers[IXh] * 256 + sim.registers[IXl] == pointer, context
            assert sim.registers[18:24] == [0xCC, 0xCC, 0xBB, 0xBB, 0xAA, 0xAA], context
            assert (memory[0x9B82], memory[0x9B83], memory[0x792E]) == (1, 1, 16), context
            assert (word(memory, 0x9B15), word(memory, 0x9B17)) == (x, y), context
            assert trace.writes == [(0x7FFD, 17), (0x7FFD, 16)] and memory.o7ffd == 16, context
            indices.add(index)
            cases += 1
    assert indices == set(range(16))
    report = dict(passed=True, total_cases=cases, original_banked_seeded_indices=True,
                  all_original_template_pointers=True, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionSpawnTemplateEntryVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
