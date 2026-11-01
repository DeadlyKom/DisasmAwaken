"""Полная память и регистры инициализации, аппаратное глушение AY без очистки RAM."""
from pathlib import Path
import collections, json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, AyPorts, get_registers, PC, SP
from CheckMusicGateTicks import Memory


def main():
    raw = (ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes()
    base = [0xA5]*65536
    base[0xDB00:0xDB00+len(raw)] = raw
    m = Memory(base)
    s = Simulator(m)
    ports = AyPorts(raw)
    s.set_tracer(ports)
    expected_ports = [(port, value) for register in range(13, -1, -1)
                      for port, value in ((0xFFFD, register), (0xBFFD, 0))]
    counts = collections.Counter()

    def registers(entry, seed, module=0xE700):
        r = get_registers({'HL': module, 'DE': 0x2468, 'BC': 0x369C, 'AF': seed,
            'IX': 0xABCD, 'IY': 0x5C3A, '^AF': 0xDEF0, '^BC': 0x9ABC,
            '^DE': 0x5678, '^HL': 0x1234, 'SP': 0xBFFE, 'PC': entry}, None, False)
        r[14], r[26], r[27] = seed & 255, seed & 1, seed % 3
        return r

    def execute(initial):
        s.registers[:] = initial
        m.writes = []
        m.recording = True
        ports.events = []
        for _ in range(1000):
            if s.registers[PC] == 0x3FFF:
                break
            s.run()
        else:
            raise AssertionError('music_initialize_or_mute_return')
        m.recording = False
        assert [(event['port'], event['value']) for event in ports.events] == expected_ports
        assert s.registers[SP] == 0xC000

    # Проверка обоих входов глушения на всех 65536 AF, ни одна запись RAM не допускается.
    for entry in (0xDB08, 0xDB7C):
        m.recording = False
        m[:] = base
        m[0xBFFE:0xC000] = [255, 63]
        for seed in range(65536):
            initial = registers(entry, seed)
            execute(initial)
            r = s.registers
            assert not m.writes, ('mute_memory_write', entry, seed)
            assert r[:8] == [seed >> 8, 0x42 | (seed & 1), 0xBF, 0xFD, 0, 0, 0xE7, 0]
            assert all(r[i] == initial[i] for i in (8, 9, 10, 11, 14, 26, 27, *range(16, 24)))
            counts['mute.'+format(entry, '04X')] += 1
        print('Mute AF cases', format(entry, '04X'), sum(counts.values()), flush=True)

    def check_initialize(module, seed, public=False):
        m.recording = False
        m[:] = base
        # Подготовка заголовка в отдельной синтетической области, исходный код проигрывателя сохраняется.
        header = [(seed + index * 73) & 255 for index in range(201)]
        header[100], header[101], header[102] = seed, seed ^ 0xA5, seed ^ 0x5A
        m[module:module+201] = header
        m[0xDC00:0xDC0E] = [(seed + index * 31) & 255 for index in range(14)]
        m[0xBFFE:0xC000] = [255, 63]
        before = list(m)
        entry = 0xDB00 if public else 0xDB0A
        initial = registers(entry, 0x9800 | seed, 0x1357 if public else module)
        execute(initial)
        expected, writes = before.copy(), []
        def put(a, v):
            expected[a] = v
            writes.append((a, v))
        def word(a, v):
            put(a, v & 255)
            put(a+1, (v >> 8) & 255)
        def read_word(a):
            return before[a] + 256 * before[a+1]
        word(0xDB4D, 0xBFFE)
        word(0xDFAE, module)
        put(0xDF62, seed)
        word(0xDF98, (module+201) & 65535)
        word(0xDF9F, (module+201+header[102]) & 65535)
        word(0xDFA7, (module+read_word(module+103)) & 65535)
        for index in range(48):
            word(0xDBA0+2*index, (module+read_word(module+105+2*index)) & 65535)
        word(0xDE1E, 0x0101)
        word(0xDC0E, 0x0101)
        for address in (0xE037, 0xE136, 0xE235):
            put(address, 0)
        for address in (0xE078, 0xE178, 0xE276, 0xDE52, 0xDEE0, 0xE1F5, 0xDF89):
            word(address, 0xDC10)
        for address in (0xDE5D, 0xDEEB, 0xE22B):
            put(address, 0xF0)
        for address in (0xDFEF, 0xE1EE, 0xE0EE):
            put(address, 0xFF)
        assert m == expected, ('initialize_memory', module, seed)
        assert sorted(m.writes) == sorted(writes), ('initialize_writes', module, seed)
        r = s.registers
        assert r[:8] == [0xFF, 0x43, 0xBF, 0xFD, 0, 0, 0xDC, 0x10]
        assert r[26] == 0 and all(r[i] == initial[i] for i in (8, 9, 10, 11, 14, 27, *range(16, 24)))
        assert m[0xDC00:0xDC0E] == before[0xDC00:0xDC0E]
        counts['initialize.public' if public else 'initialize.module'] += 1

    # Проверка всех байтов задержки, числа позиций и петли, шести баз и обеих точек входа.
    for module in (0x4000, 0x5000, 0x6000, 0x7000, 0x8000, 0xE700):
        for seed in range(256):
            check_initialize(module, seed)
    for seed in range(256):
        check_initialize(0xE700, seed, True)
    report = dict(passed=True, total_cases=sum(counts.values()), cases_by_entry=dict(counts),
        all_mute_af_values=True, every_initialization_memory_byte_and_write_checked=True,
        exact_ay_port_order_checked=True, exact_final_af_checked=True,
        initialize_af=0xFF43, mute_f='42 OR input Carry', ay_ram_buffer_not_cleared=True,
        initialization_iff_cleared=True, mute_iff_preserved=True, all_48_relative_pointers_checked=True,
        partial_reset_only=True, irq_executed=False, native_audio_verified=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MusicInitializeAndMuteVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
