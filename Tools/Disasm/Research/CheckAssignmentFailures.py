"""Нелокальные ошибки присваивания на исходных байтах LANG, без сборки.

Документация: ../../../Docs/AssignmentPipeline.md#ошибка-поиска-и-утрата-прежнего-указателя
"""
from pathlib import Path
from hashlib import sha256
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry = next(e for e in manifest['entries'] if e['slot'] == 5)
    source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    # Проверка физического происхождения исполняемых байтов.
    assert sha256(disk).hexdigest() == manifest['sha256']
    assert source == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    assert sha256(source).hexdigest() == entry['sectors_sha256']
    profiles = []
    cases = (('unknown_writer', b'?', 0xCA7B),
             ('unknown_operator', b'c?', 0xCA7D),
             ('unknown_rhs', b'c:?', 0xCA7F),
             ('unknown_nested_rhs', b'c:(1+?)', 0xCA83))
    for name, text, expected_top in cases:
        memory = bytearray(65536)
        memory[0xC000:0xC000+len(source)] = source
        memory[0xB000:0xB000+len(text)+2] = text + bytes((13, 0))
        memory[0x7FFE:0x8000] = bytes((255, 63))
        memory[0xC01C:0xC01E] = (0x7FFE).to_bytes(2, 'little')
        memory[0xC028] = 0
        memory[0x984E:0x9850] = bytes((0x5A, 0xA5))
        cpu = Simulator(memory)
        cpu.registers[:] = get_registers({'SP':0x7FF0, 'IX':0xB000,
            'HL':0x1357, 'DE':0x2468, 'BC':0x369C, 'AF':0x47AD,
            '^HL':0xB800, '^DE':0x58BE, '^BC':0x69CF, '^AF':0x7AD0,
            'IY':0x5C3A}, None, False)
        # Проверка входа ошибки, без исполнения SkipLine и следующей команды.
        cpu.run(0xC09F, 0xC01B)
        r = cpu.registers
        top = 256*r[22]+r[23]
        assert top == expected_top and top != 0xB800
        assert r[12] < 0x7FEE
        assert memory[0x7FEE:0x7FF0] == (0xB800).to_bytes(2, 'little')
        assert memory[0x984E:0x9850] == bytes((0x5A, 0xA5))
        error_sp = r[12]
        # Проверка отбрасывания рамки до следующего символа сценария.
        cpu.run(0xC01B, 0xC010)
        assert r[12] == 0x7FFE and 256*r[22]+r[23] == top
        assert r[8]*256+r[9] == 0xB000+len(text)+1
        # Проверка возврата по NUL в исходный сценарный возврат, минуя Resume.
        cpu.run(0xC010, 0x3FFF)
        assert r[12] == 0x8000 and 256*r[22]+r[23] == top
        assert memory[0x7FEE:0x7FF0] == (0xB800).to_bytes(2, 'little')
        assert memory[0x984E:0x9850] == bytes((0x5A, 0xA5))
        profiles.append(dict(name=name, text_hex=text.hex(), error_SP=error_sp,
            unrecovered_expression_top=top, saved_old_top_still_in_RAM=True,
            money_not_written=True, root_return_reached=True))
    report = dict(passed=True, method='original_assignment_failure_skip_and_root_return',
        profiles=profiles, physical_disk_and_sector_hashes_checked=True,
        original_disk_sha256=sha256(disk).hexdigest(),
        old_HL_shadow_not_restored_on_failure=True,
        all_possible_invalid_texts_checked=False, arbitrary_stack_addresses_checked=False,
        irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/AssignmentFailuresVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

