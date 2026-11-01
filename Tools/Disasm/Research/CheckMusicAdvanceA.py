"""Переходы позиций и использование SP в исходном AdvancePatternA, без сборки."""
from pathlib import Path
import collections, json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceMusicPhases import advance_a


def main():
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    base = [0xA5] * 65536
    base[0xDB00:0xDB00 + len(raw)] = raw
    m = Memory(base)
    s = Simulator(m)
    counts = collections.Counter()

    def check(row, seed, marker=None, module=0xE700, stream=None, group='counter'):
        m.recording = False
        m[:] = base
        def word(a, v):
            m[a:a + 2] = [v & 255, v >> 8]
        m[0xDE1E] = row
        m[0xDFC9] = seed
        word(0xDF89, 0x7000 if marker is None else 0x7300)
        word(0xDF98, 0x5000)
        word(0xDF9F, 0x5200)
        word(0xDFA7, 0x6000)
        word(0xDFAE, module)
        m[0x5000] = marker if marker is not None else 0
        m[0x5200] = seed
        m[0x7300] = 0
        if marker is not None:
            position = seed if marker == 255 else marker
            for offset, pointer in zip((0, 2, 4), (0x7000, 0x7100, 0x7200)):
                word(0x6000 + 2 * position + offset, (pointer - module) & 65535)
        data = stream or [0x50 + seed % 96]
        m[0x7000:0x7000 + len(data)] = data
        m[0xBFFE:0xC000] = [255, 63]
        initial = get_registers({'HL': 0x1357, 'DE': 0x0618 if seed & 2 else 0x1806,
            'BC': 0x369C, 'AF': 0x9800 | seed, 'IX': 0xABCD, 'IY': 0x5C3A,
            '^AF': 0xDEF0, '^BC': seed * 256 + 0xBC, '^DE': 0x5678, '^HL': 0x1234,
            'SP': 0xBFFE, 'PC': 0xDF7F}, None, False)
        expected = advance_a(m, initial[:8], initial[16:24])
        m.writes = []
        m.recording = True
        s.registers[:] = initial
        for _ in range(2000):
            if s.registers[PC] == 0xDFE3:
                break
            s.run()
        else:
            raise AssertionError(('advance_a_stop', row, seed, marker))
        m.recording = False
        assert m == expected['memory'], ('advance_a_memory', row, seed, marker,
            [(a, m[a], expected['memory'][a]) for a in range(65536) if m[a] != expected['memory'][a]][:20])
        assert sorted(m.writes) == sorted(expected['writes']), ('advance_a_writes', row, seed, marker)
        r = s.registers
        assert r[:8] == expected['main'] and r[16:24] == expected['alternate'], ('advance_a_registers', row, seed, marker, r[:8], expected['main'])
        assert r[SP] == expected['sp'] == 0xBFFE
        assert all(r[i] == initial[i] for i in (8, 9, 10, 11, 14, 26, 27))
        counts[group] += 1

    # Проверка всех байтов счётчика, входного рабочего B и флагов, в том числе нулевого счётчика.
    for row in range(256):
        for seed in (0, 1, 2, 3, 127, 128, 254, 255):
            check(row, seed)
    for seed in range(256):
        check(2, seed, group='retained_working_b')
        # Проверка каждого байта позиции и возврата по FF с шестью базами модуля.
        for module in (0, 1, 0x7FFF, 0x8000, 0xE700, 0xFFFF):
            check(1, seed, marker=seed, module=module, group='positions')
            check(1, seed, marker=255, module=module, group='loops')
    for effect in (1, 2, 3, 4, 5, 8, 9):
        for terminal in (0x50, 0xC0, 0xD0):
            for seed in range(0, 256, 17):
                check(1, seed, marker=0, stream=[effect, terminal, seed, 0, 128, 255, seed], group='effects_after_position')
    report = dict(passed=True, total_cases=sum(counts.values()), cases_by_group=dict(counts),
        all_counter_and_position_bytes=True, all_retained_working_b_bytes=True,
        original_position_times_two_preserved=True, six_module_base_values=True,
        actual_decoder_and_effects_executed=True, independent_semantic_reference=True,
        source_sp_save_and_three_pointer_pops_checked=True, all_memory_and_writes_and_registers_checked=True,
        stop_address=0xDFE3, irq_executed=False, synthesis_executed=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/MusicAdvanceAVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
