"""Отражение двух половин текстуры после возврата из RenderLookupTexture."""
import json
from random import Random

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT, original_memory
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace


def main():
    flat = original_memory()
    rng = Random(0x6DE6)
    for case in range(32):
        banks = [bytearray([bank] * 0x4000) for bank in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[2][0x3FFE:] = bytes((255, 63))
        source = bytes(rng.randrange(256) for _ in range(4096))
        banks[2][:4096] = source
        memory = RecordedBanks(banks=banks, out7ffd=17)
        expected = []
        for row in range(32):
            start = 0xD0 + row * 64
            half = [(value - 0x89) & 255 for value in source[start:start + 32]]
            expected.extend(half + half[::-1])
        expected += expected[::-1]
        simulator = Simulator(memory)
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        simulator.registers[:] = get_registers({'PC': 0x6DE6, 'SP': 0xBFFE, 'IX': 0xA55A, 'IY': 0xFEDC}, None, False)
        memory.writes = []
        memory.recording = True
        simulator.run(0x6DE6, 0x3FFF)
        memory.recording = False
        r = simulator.registers
        assert r[PC] == 0x3FFF and r[SP] == 0xC000 and r[26], case
        assert r[0] == 17 and r[2:12] == [127, 253, 208, 0, 144, 0, 165, 0, 254, 220], case
        assert bytes(memory.banks[2][:4096]) == bytes(expected) == bytes(memory.banks[4][:4096]), case
        assert trace.writes == [(0x7FFD, 20), (0x7FFD, 17)]
        counts = {bank: sum(item[0] == bank for item in memory.writes) for bank in (2, 4)}
        assert counts == {2: 5250, 4: 4096} and len(memory.writes) == 9346, (case, counts)
        assert all(bank == 2 and (index < 4096 or 0x3FFC <= index < 0x3FFE)
                   or bank == 4 and index < 4096 for bank, index, _ in memory.writes)
    report = dict(passed=True, total_cases=32, bytes_per_texture=4096,
                  first_entry=0x6DE6, source_renderer_executed=False,
                  write_counts_per_case={'fixed_bank_2': 5250, 'texture_bank_4': 4096},
                  irq_executed=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroMirroredTextureVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
