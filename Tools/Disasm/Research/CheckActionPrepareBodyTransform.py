"""6A6E → AF43 → 6AAD → 6AB0, копирование компонент и восстановление настоящего SP."""
from collections import Counter
from itertools import product
import json
import random

from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionPatchedVector import COEFFICIENTS, INPUTS, OUTPUTS
from CheckMusic import Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionPatchedVector import evaluate as transform
from ReferenceControlsPointRespawn import refresh


def profiles():
    for vector in product((0, 1, 0x7FFF, 0x8000, 0x8001, 0xFFFF), repeat=3):
        for matrix in (((0, 0, 0),) * 3, ((127, 0, 0), (0, 127, 0), (0, 0, 127)), ((127, 127, 127),) * 3):
            yield vector, matrix
    for row in range(3):
        for term in (1, 2):
            matrix = [[0, 0, 0] for _ in range(3)]
            matrix[row][:term + 1] = [127] * (term + 1)
            vector = (0x7FFF, 0x7FFF, 0x7FFF) if term == 1 else (0x4FFF, 0x4FFF, 0x4FFF)
            yield vector, matrix
    generator = random.Random(0x6A6E)
    for _ in range(8192):
        yield tuple(generator.randrange(65536) for _ in range(3)), tuple(tuple(generator.randrange(256) for _ in range(3)) for _ in range(3))


def main():
    flat = flat_action()
    baseline = [bytearray([0xA0 + index] * 0x4000) for index in range(8)]
    baseline[5], baseline[2], baseline[0] = bytearray(flat[0x4000:0x8000]), bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:])
    memory = RecordedBanks(banks=[bytearray(bank) for bank in baseline], out7ffd=16)
    simulator = Simulator(memory)
    assert bytes(memory[0x6AAD:0x6AB0]) == b'\x31\x00\x00'
    outcomes = Counter()
    touched = set()
    for vector, matrix in profiles():
        serial = outcomes.total()
        stack = (0x9008, 0xBFFE)[serial & 1]
        memory.recording = False
        for bank, offset in touched:
            memory.banks[bank][offset] = baseline[bank][offset]
        for addresses, values in zip(COEFFICIENTS, matrix):
            for address, value in zip(addresses, values):
                memory[address] = value
        vector_bytes = bytearray()
        for index, value in enumerate(vector):
            vector_bytes.extend(((serial * 73 + index * 29) & 255, value & 255, value >> 8))
        for index, value in enumerate(vector_bytes):
            memory[0x9B6F + index] = value
        old_outputs = [(memory[address + 1] << 8) | memory[address] for address in OUTPUTS]
        bc = (serial * 307) & 65535
        initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': 0x2468, 'BC': bc,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x5C3A,
            'SP': stack, 'PC': 0x6A6E}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        writes = [(0x9B1E + index, value) for index, value in enumerate(vector_bytes)]

        def word(address, value):
            writes.extend(((address, value & 255), (address + 1, value >> 8)))

        for address, value in zip(INPUTS, vector):
            word(address, value)
        word(0x6AAE, stack)
        writes.extend(((0x9B1E, 0), (0x9B21, 0), (0x9B24, 0)))
        word(0xAFF1, 0xABCD)
        result = transform(vector, matrix, old_outputs)
        for row in result['performed']:
            word(OUTPUTS[row], result['outputs'][row])
        wanted = list(initial)
        wanted[:8] = [*result['af'], ((bc - 9) & 65535) >> 8, 0, result['de'] >> 8, result['de'] & 255,
                      result['hl'] >> 8, result['hl'] & 255]
        wanted[10:12] = [0x6A, 0xAD]
        wanted[15] = refresh(initial[15], 36 + result['refresh_m1'])
        wanted[16:18] = result['alternate_af']
        wanted[24] = 0x6AB0
        expected = [bytearray(bank) for bank in memory.banks]
        physical_writes = []
        for address, value in writes:
            bank = 0 if address >= 0xC000 else 2 if address >= 0x8000 else 5
            offset = address & 0x3FFF
            expected[bank][offset] = value
            physical_writes.append((bank, offset, value))
        simulator.registers[:] = initial
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        simulator.run(start=0x6A6E, stop=0x6AAD)
        simulator.run(start=0x6AAD, stop=0x6AB0)
        memory.recording = False
        compared = (*range(25), 26, 27)
        assert all(wanted[reg] == simulator.registers[reg] for reg in compared), (serial, vector, matrix,
            [(reg, wanted[reg], simulator.registers[reg]) for reg in compared if wanted[reg] != simulator.registers[reg]])
        assert Counter(physical_writes) == Counter(memory.writes), (serial, 'writes')
        assert all(a == b for a, b in zip(expected, memory.banks)), (serial, 'RAM')
        assert not trace.writes and memory.o7ffd == 16
        touched = {(bank, offset) for bank, offset, _ in memory.writes}
        outcomes[str(result['stop_position']) if result['overflow'] else 'complete'] += 1
    assert len(outcomes) == 7, outcomes
    report = dict(passed=True, total_cases=outcomes.total(), outcomes=dict(outcomes), exact_registers_including_R=True,
        actual_arithmetic_and_restore_instruction=True, restored_SP_at_6AB0=True, no_cpu_stack_writes=True,
        all_physical_ram_bytes_proved=True, nonpixel_write_multiplicity_proved=True, stopped_before_6AB0=True,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionPrepareBodyTransformVerification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
