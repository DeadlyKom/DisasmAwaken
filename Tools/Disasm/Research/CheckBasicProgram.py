"""Независимое чтение токенов SkoolKit и обеих форм исходного числового USR."""
import hashlib
import json

from BasicProgramData import ROOT, ENTRY, PROGRAM_BASE, original_program
from skoolkit.basic import BasicLister, TOKENS, _get_number


def main():
    program, lines = original_program()
    assert TOKENS[0xEA] == 'REM' and TOKENS[0xF9] == 'RANDOMIZE' and TOKENS[0xC0] == 'USR'
    assert _get_number(list(program), 113) == ENTRY
    memory = [128] * 65536
    memory[23635:23637] = [PROGRAM_BASE & 255, PROGRAM_BASE >> 8]
    memory[PROGRAM_BASE:PROGRAM_BASE + len(program)] = program
    sectors=(ROOT / 'Tools/Disasm/Extracted/Active/03_AWAKEN.B.sectors.bin').read_bytes()
    assert sectors[119:123]==b'\x80\xAA\x14\x00'
    listing = BasicLister().list_basic(memory)
    assert listing.splitlines()[-1].strip() == '20 RANDOMIZE USR 23873', listing
    result = dict(passed=True, total_cases=len(lines), logical_program_size=len(program),
                  declared_line_lengths=[97, 14], ascii_usr=ENTRY, hidden_integer_usr=ENTRY,
                  intended_machine_entry=ENTRY, inferred_program_base=PROGRAM_BASE,
                  trdos_autostart_line=20, autostart_marker_offset=119,
                  program_sha256=hashlib.sha256(program).hexdigest(),
                  independent_token_decoder='SkoolKit BasicLister and numeric decoder',
                  basic_rom_interpreter_executed=False, trdos_rom_executed=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/BasicProgramVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
