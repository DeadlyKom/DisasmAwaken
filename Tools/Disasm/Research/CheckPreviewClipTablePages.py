"""Исходные lookup-хвосты контура и сегмента, все 256 сырых индексов."""
import json

from CheckUnpackResource import ROOT, Simulator, get_registers, SP


CODES = (0, 1, 2, 4, 5, 6, 8, 9, 10)


def main():
    source = (ROOT / 'Tools/Disasm/Extracted/Active/06_D3D.C.bin').read_bytes()
    memory = bytearray(65536)
    memory[0xC000:0xC000 + len(source)] = source
    simulator = Simulator(memory)
    cases = 0
    for entry, stop, return_address, frame_count in (
        (0xE1D7, 0xE1E1, 0xE1E2, 1),
        (0xEAFB, 0xEB07, 0xEB08, 3),
    ):
        for index in range(256):
            simulator.registers[:] = get_registers({'HL': index, 'SP': 0x7FFE}, None, False)
            simulator.run(start=entry, stop=stop)
            registers = simulator.registers
            target = source[0xC00 + index] + 256 * source[0xD00 + index]
            assert registers[6] * 256 + registers[7] == target
            assert registers[SP] == 0x7FFE - 2 * frame_count
            assert memory[registers[SP]:0x7FFE] == return_address.to_bytes(2, 'little') * frame_count
            cases += 1
    targets = {
        source[0xC00 + 16 * first + second] + 256 * source[0xD00 + 16 * first + second]
        for first in CODES for second in CODES
    }
    assert len(targets) == 71 and all(0xE1EB <= value <= 0xE85D for value in targets)
    report = dict(passed=True, cases=cases, normal_indices=81, normal_targets=71,
                  all_byte_indices_per_lookup=True, source_page_aliases_preserved=True,
                  out_of_domain_targets_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/PreviewClipTablePagesVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
