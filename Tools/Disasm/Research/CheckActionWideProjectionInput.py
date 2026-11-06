"""Уменьшение трёх широких компонент на входе 6B6B до вызова 6C19."""
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory


def main():
    memory = Memory(flat_action())
    sim = Simulator(memory)
    for word in range(65536):
        pointer = 0x9B27 + 12 * (word % 6)
        values = (word << 16 | (word ^ 0xAAAA), word << 16 | (word ^ 0x5555),
                  (word ^ 0x8000) << 16 | word)
        steps = []
        for index, value in enumerate(values):
            address = pointer + 4 * index
            memory[address:address + 4] = list(value.to_bytes(4, 'little'))
            signed = (value ^ 0x80000000) - 0x80000000
            steps.append((signed // 16) & 0xFFFFFFFF)
        bc = word ^ 0x7B82
        sim.registers[:] = get_registers({'PC': 0x6B6B, 'SP': 0xBFFE, 'BC': bc,
                                         'DE': 12, 'IY': pointer}, None, False)
        sim.run(0x6B6B, 0x6C19)
        expected = b''.join((value & 0xFFFFFF).to_bytes(3, 'little') for value in steps)
        assert bytes(memory[0x9B1E:0x9B27]) == expected, word
        frame = (0x6BFC, bc, pointer, 12)
        assert bytes(memory[0xBFF6:0xBFFE]) == b''.join(value.to_bytes(2, 'little') for value in frame)
        r = sim.registers
        assert r[SP] == 0xBFF6 and r[PC] == 0x6C19 and r[10:12] == [pointer >> 8, pointer & 255]
        assert (r[2], r[3], r[6], r[7], r[0]) == (steps[2] >> 24, bc & 255,
                                                   (steps[2] >> 16) & 255, (steps[2] >> 8) & 255, steps[2] & 255)
    report = dict(passed=True, total_cases=65536, six_record_positions=True,
                  stopped_before_transform=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionWideProjectionInputVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
