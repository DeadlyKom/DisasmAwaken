"""Распределение фаз B/C, включая оригинальные CALL декодеров и все записи ворот."""
from pathlib import Path
import collections, json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceMusicPhases import advance_bc
from ReferenceMusicPattern import HANDLERS
from CheckMusicPatternRows import command


def main():
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    base = [0xA5] * 65536
    base[0xDB00:0xDB00 + len(raw)] = raw
    m = Memory(base)
    s = Simulator(m)
    counts = collections.Counter()

    def check(phase, row, stream, seed, alt_b, group):
        m.recording = False
        m[:] = base
        m[0xE37D] = phase
        m[0xDC0E] = m[0xDC0F] = row
        m[0x7000:0x7000 + len(stream)] = stream
        m[0xE393:0xE395] = m[0xE3C4:0xE3C6] = [0, 0x70]
        m[0xE39F] = seed
        m[0xE3D0] = seed ^ 0xA5
        m[0xBFFE:0xC000] = [255, 63]
        initial = get_registers({'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
            'AF': 0x9800 | seed, 'IX': 0xABCD, 'IY': 0x5C3A, '^AF': 0xDEF0,
            '^BC': alt_b * 256 + 0xBC, '^DE': 0x5678, '^HL': 0x1234,
            'SP': 0xBFFE, 'PC': 0xE37C}, None, False)
        expected = advance_bc(m, initial[:8], initial[16:24])
        s.registers[:] = initial
        m.writes = []
        m.recording = True
        for _ in range(2000):
            if s.registers[PC] == 0x3FFF:
                break
            s.run()
        else:
            raise AssertionError(('phase_return', phase, row, stream))
        m.recording = False
        assert m == expected['memory'], ('phase_memory', phase, row, stream, seed,
            [(a, m[a], expected['memory'][a]) for a in range(65536) if m[a] != expected['memory'][a]][:20])
        assert sorted(m.writes) == sorted(expected['writes']), ('phase_writes', phase, row, stream, m.writes, expected['writes'])
        r = s.registers
        assert r[:8] == expected['main'], ('phase_main', phase, row, stream, r[:8], expected['main'])
        assert r[16:24] == expected['alternate'], ('phase_alt', phase, row, stream, r[16:24], expected['alternate'])
        assert r[SP] == expected['sp'] == 0xC000
        assert all(r[i] == initial[i] for i in (8, 9, 10, 11, 14, 26, 27))
        counts[group] += 1

    # Проверка всех байтов фазы с обоими Carry, вызовы для фаз 1 и 2 также исполняются.
    for phase in range(256):
        for carry in (0, 1):
            check(phase, 1, [0xD0], carry, 1, 'phase_bytes')
    # Проверка всех счётчиков и альтернативного B, включая DJNZ без вызова декодера.
    for row in range(256):
        for alt_b in (0, 1, 2, 255):
            for carry in (0, 1):
                for phase in (1, 2):
                    check(phase, row, [0xD0], carry, alt_b, 'row_bytes')
    for alt_b in range(256):
        check(2, 2, [0xD0], alt_b, alt_b, 'retained_working_b')
    for channel, phase in (('B', 2), ('C', 1)):
        for op in range(0x10, 256):
            for seed in range(0, 256, 17):
                stream = [op] if channel == 'B' and 0x20 <= op < 0x40 else command(op, seed)
                if not (op in (0xC0, 0xD0) or 0x50 <= op < 0xB0):
                    stream += [0x50 + seed % 96]
                check(phase, 1, stream, seed, seed, channel + '.ordinary')
        for effect in HANDLERS[channel]:
            for terminal in (0x50, 0xC0, 0xD0):
                for seed in range(0, 256, 17):
                    check(phase, 1, [effect, terminal, seed, 0, 128, 255, seed], seed, seed, channel + '.effects')
        print('Pattern phase', channel, sum(counts.values()), flush=True)
    report = dict(passed=True, total_cases=sum(counts.values()), cases_by_group=dict(counts),
        all_phase_and_counter_bytes=True, all_retained_working_b_bytes=True,
        actual_decoder_calls_executed=True, independent_parser_reference=True,
        every_memory_byte_and_write_checked=True, main_and_alternate_registers_checked=True,
        source_call_frames_checked=True, irq_executed=False, native_audio_verified=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/MusicPatternPhasesVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
