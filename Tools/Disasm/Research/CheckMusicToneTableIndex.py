"""Смысл индекса PT3 по полной таблице периодов и независимость инициализации от байта заголовка."""
from hashlib import sha256
import json

from CheckMusic import ROOT, Simulator, AyPorts, get_registers, PC
from CheckMusicGateTicks import Memory


# Фактические периоды PT3NoteTable_ASM из исходников Vortex Tracker II, ссылка сохранена в отчёте.
ASM_PERIODS = tuple(int(value, 16) for value in '''
0D10 0C55 0BA4 0AFC 0A5F 09CA 093D 08B8 083B 07C5 0755 06EC
0688 062A 05D2 057E 052F 04E5 049E 045C 041D 03E2 03AB 0376
0344 0315 02E9 02BF 0298 0272 024F 022E 020F 01F1 01D5 01BB
01A2 018B 0174 0160 014C 0139 0128 0117 0107 00F9 00EB 00DD
00D1 00C5 00BA 00B0 00A6 009D 0094 008C 0084 007C 0075 006F
0069 0063 005D 0058 0053 004E 004A 0046 0042 003E 003B 0037
0034 0031 002F 002C 0029 0027 0025 0023 0021 001F 001D 001C
001A 0019 0017 0016 0015 0014 0012 0011 0010 000F 000E 000D
'''.split())


def main():
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    reference = b''.join(value.to_bytes(2, 'little') for value in ASM_PERIODS)
    assert len(ASM_PERIODS) == 96 and raw[0x200:0x2C0] == reference
    assert raw[0xC00:0xC1E] == b'ProTracker 3.6 compilation of '
    assert raw[0xC63:0xC69] == bytes.fromhex('02 03 1C 04 E6 00')
    base = [0xA5] * 65536
    base[0xDB00:0xDB00 + len(raw)] = raw
    memory = Memory(base)
    cpu = Simulator(memory)
    ports = AyPorts(raw)
    cpu.set_tracer(ports)
    initial = get_registers(dict(PC=0xDB00, SP=0xBFFE, HL=0x1357,
                                DE=0x2468, BC=0x369C, AF=0xA55A,
                                IX=0xABCD, IY=0x5C3A,
                                **{'^AF': 0xDEF0, '^HL': 0x1234,
                                   '^DE': 0x5678, '^BC': 0x9ABC}), None, False)
    baseline = None
    for index in range(256):
        memory.recording = False
        memory[:] = base
        memory[0xBFFE:0xC000] = [255, 63]
        memory[0xE763] = index
        cpu.registers[:] = initial
        memory.writes = []
        memory.recording = True
        ports.events = []
        for _ in range(1000):
            if cpu.registers[PC] == 0x3FFF:
                break
            cpu.run()
        else:
            raise AssertionError(('Не завершён Initialize', index))
        memory.recording = False
        final = list(memory)
        assert final[0xE763] == index and bytes(final[0xDD00:0xDDC0]) == reference
        final[0xE763] = 2
        result = (list(cpu.registers), final, list(memory.writes), list(ports.events))
        if baseline is None:
            baseline = result
        assert result == baseline, index
    report = dict(passed=True, compared_period_words=96, compared_period_bytes=192,
                  period_table_address=0xDD00, player_relative_period_offset=512,
                  header_address=0xE763, module_relative_field_offset=99, original_index=2,
                  table_name='ASM/PSC', period_sha256=sha256(reference).hexdigest(),
                  initialization_cases=256, exact_registers_r_t_ram_writes_and_ports=True,
                  original_module_initialization_only=True,
                  format_reference='https://groups.google.com/g/fido7.zx.spectrum/c/StZ1c9uHVnc/m/cVQD3SrNZ80J',
                  period_reference='https://github.com/oisee/vti/blob/master/trfuncs.pas',
                  reference_constant='PT3NoteTable_ASM', assembly_executed=False,
                  native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/MusicToneTableIndexVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Совпали все 96 периодов ASM/PSC, 256 значений индекса не меняют результат исходной инициализации.')


if __name__ == '__main__':
    main()
