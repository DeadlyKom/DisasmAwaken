"""Независимая проверка полных строк трёх исходных декодеров и их RET-цепочек."""
from pathlib import Path
import collections, itertools, json, random, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceMusicPattern import PROFILES, HANDLERS, decode


def command(op, seed):
    if op >= 0xF0:
        return [op, seed]
    if 0xB0 <= op < 0xC0:
        return [op] + ([] if op == 0xB0 else [seed] if op == 0xB1 else [seed, seed ^ 0xA5])
    if 0x10 <= op < 0x40:
        return [op] + ([] if seed is None else [seed] if op == 0x10 else [seed, seed ^ 0xA5, seed ^ 0x5A])
    return [op]


def main():
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    baseline = [0xA5] * 65536
    baseline[0xDB00:0xDB00 + len(raw)] = raw
    memory = Memory(baseline)
    simulator = Simulator(memory)
    counts = collections.Counter()
    route_counts = collections.Counter()
    rng = random.Random(0xE439E583)

    def check(channel, stream, seed, group):
        p = PROFILES[channel]
        memory.recording = False
        memory[:] = baseline
        memory[0x7000:0x7000 + len(stream)] = stream
        memory[0xBFFE:0xC000] = [255, 63]
        # Подготовка синтетических значений исходной изменяемой таблицы указателей.
        for index in range(48):
            value = ((seed * 257) ^ (index * 733)) & 65535
            memory[0xDBA0 + 2 * index:0xDBA2 + 2 * index] = [value & 255, value >> 8]
        memory[p['pending']] = seed ^ 0x5A
        memory[p['current']] = seed ^ 0xA5
        memory[0xE2B9] = (seed * 17) & 255
        alt = [0xDE, 0xF0, 0x9A, 0xBC, 6 if seed & 1 else 0x18, 0x18, 0x12, 0x34]
        expected = decode(memory, channel, alternate=alt)
        initial = get_registers({'HL': 0xDB57, 'DE': 0x7000, 'BC': 0x2468,
            'AF': 0x9800 | seed, 'IX': 0xABCD, 'IY': 0x5C3A, '^AF': 0xDEF0,
            '^BC': 0x9ABC, '^DE': alt[4] * 256 + alt[5], '^HL': 0x1234,
            'SP': 0xBFFE, 'PC': p['entry']}, None, False)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(4000):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('row_return', channel, stream, seed))
        memory.recording = False
        assert memory == expected['memory'], ('row_memory', channel, stream, seed,
            [(a, memory[a], expected['memory'][a]) for a in range(65536) if memory[a] != expected['memory'][a]][:20])
        assert sorted(memory.writes) == sorted(expected['writes']), ('row_writes', channel, stream, seed, memory.writes, expected['writes'])
        r = simulator.registers
        assert r[:8] == expected['main'], ('row_main', channel, stream, seed, r[:8], expected['main'])
        assert r[16:24] == expected['alternate'], ('row_alternate', channel, stream, seed, r[16:24], expected['alternate'])
        assert r[SP] == expected['sp'] == 0xC000
        assert all(r[i] == initial[i] for i in (8, 9, 10, 11, 14, 26, 27))
        counts[channel + '.' + group] += 1
        for op in expected['commands']:
            route_counts[channel + '.' + format(op, '02X')] += 1

    for channel in PROFILES:
        for op in range(0x10, 256):
            # Проверка всех обычных команд с несколькими байтами данных и завершающей нотой.
            for seed in range(0, 256, 17):
                stream = command(op, seed)
                if channel == 'B' and 0x20 <= op < 0x40:
                    stream = [op]
                if not (op in (0xC0, 0xD0) or 0x50 <= op < 0xB0):
                    stream += [0x50 + seed % 96]
                check(channel, stream, seed, 'ordinary')
        for effect in HANDLERS[channel]:
            for terminal in (0x50, 0xC0, 0xD0):
                # Проверка каждого байта первого параметра после ноты, выключения и конца строки.
                for seed in range(256):
                    check(channel, [effect, terminal, seed, seed ^ 0xA5, seed ^ 0x5A, seed, 255 - seed], seed, 'single_effect')
        for first, second in itertools.product(HANDLERS[channel], repeat=2):
            for terminal in (0x50, 0xC0, 0xD0):
                for seed in range(0, 256, 17):
                    data = [(seed + index * 73) & 255 for index in range(10)]
                    check(channel, [first, second, terminal] + data, seed, 'effect_pairs')
        # Проверка смешанных последовательностей, включая смену страницы H после отложенного эффекта.
        choices = list(range(0x10, 0x50)) + list(range(0xB0, 0xC0)) + list(range(0xC1, 0xD0)) + list(range(0xD1, 256)) + list(HANDLERS[channel])
        for index in range(4096):
            seed = rng.randrange(256)
            stream = []
            for _ in range(rng.randrange(1, 12)):
                op = rng.choice(choices)
                stream += [op] if op < 0x10 or channel == 'B' and 0x20 <= op < 0x40 else command(op, rng.randrange(256))
            stream += [rng.choice((0x50 + seed % 96, 0xC0, 0xD0))]
            stream += [rng.randrange(256) for _ in range(64)]
            check(channel, stream, seed, 'mixed')
        print('Pattern rows', channel, sum(counts.values()), flush=True)
    report = dict(passed=True, total_cases=sum(counts.values()), cases_by_group=dict(counts),
        opcodes_observed=dict(route_counts), independent_semantic_reference=True,
        every_memory_byte_and_write_checked=True, main_and_alternate_registers_checked=True,
        all_supported_effect_pairs=True, note_release_end_terminals=True,
        low_byte_pointer_wrap_and_current_h_preserved=True, all_streams_proved=False,
        reserved_effects_executed=False, irq_executed=False, native_audio_verified=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/MusicPatternRowsVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'opcodes_observed'}, indent=2))


if __name__ == '__main__':
    main()
