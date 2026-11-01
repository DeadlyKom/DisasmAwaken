"""Очередь банка 1 и доказательство числового значения типа 2 на оригинальных инструкциях."""
from pathlib import Path
import collections, json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsTextQueue import QUEUE, PRODUCER, insert, push_word


def payload(slot):
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry = next(item for item in manifest['entries'] if item['slot'] == slot)
    return (ROOT/(entry['path']+'.bin')).read_bytes()


def base_memory():
    result = [0xA5]*65536
    for slot, origin in ((22, 0xC000), (23, 0xDADE)):
        raw = payload(slot)
        result[origin:origin+len(raw)] = raw
    return result


def main():
    base = base_memory()
    assert bytes(base[QUEUE:QUEUE+34]) == bytes((1, 1))*16 + bytes(2)
    m = Memory(base)
    s = Simulator(m)
    counts = collections.Counter()
    failures = collections.Counter()
    def check(entry, seed, mask, head, occupied=0x80):
        m.recording = False
        m[:] = base
        for index in range(16):
            m[QUEUE+2*index] = 1 if mask & (1 << index) else occupied
            m[QUEUE+2*index+1] = (seed+index*73) & 255
        cursor = QUEUE+2*head
        m[PRODUCER:PRODUCER+2] = [cursor & 255, cursor >> 8]
        m[0xBFFE:0xC000] = [255, 63]
        initial = get_registers({'HL': 0x1357, 'DE': seed ^ 0xA55A, 'BC': 0x369C,
            'AF': seed, 'IX': 0xABCD, 'IY': 0x5C3A, '^AF': 0xDEF0,
            '^BC': 0x9ABC, '^DE': 0x5678, '^HL': 0x1234, 'SP': 0xBFFE, 'PC': entry}, None, False)
        initial[14], initial[26], initial[27] = seed & 255, seed & 1, seed % 3
        value = 0x200 | (seed >> 8) if entry == 0xEC56 else seed ^ 0xA55A
        result = insert(m, value)
        writes = push_word(0xBFFE, 0x1357)+push_word(0xBFFC, 0x369C)+push_word(0xBFFA, seed)+result['writes']
        expected = list(m)
        for address, byte in writes:
            expected[address] = byte
        m.writes = []
        m.recording = True
        s.registers[:] = initial
        for _ in range(180):
            if s.registers[PC] == 0x3FFF:
                break
            s.run()
        else:
            raise AssertionError(('queue_return', entry, seed, mask, head))
        m.recording = False
        assert m == expected and sorted(m.writes) == sorted(writes), ('queue_memory', entry, seed, mask, head, m.writes, writes)
        if result['accepted']:
            assert m.writes[-4:] == result['writes']
        expected_registers = initial[:8]
        expected_registers[4:6] = [value >> 8, value & 255]
        r = s.registers
        assert r[:8] == expected_registers and r[SP] == 0xC000, ('queue_registers', entry, seed)
        assert all(r[i] == initial[i] for i in (8, 9, 10, 11, 14, 26, 27, *range(16, 24)))
        assert bytes(m[0xBFF8:0xC000]) == seed.to_bytes(2, 'little')+bytes((0x9C,0x36,0x57,0x13,255,63))
        counts[format(entry, '04X')] += 1
        failures['accepted' if result['accepted'] else 'silent_drop'] += 1
        return result

    # Проверка всех масок свободных записей, всех DE и всех AF в одном полном наборе.
    for seed in range(65536):
        check(0xEC59, seed, seed, seed % 17)
    # Проверка подготовки типа 2 с каждым A и каждым входным F.
    for seed in range(65536):
        check(0xEC56, seed, 1 << ((seed >> 8) % 16), seed % 17)
    # Проверка каждого курсора и единственного свободного места при разных занятых кодах.
    for head in range(17):
        for free in range(17):
            for occupied in (2, 3, 0x7F, 0x80, 0xFE, 0xFF):
                check(0xEC59, (head*379+free*73)&65535, 0 if free == 16 else 1 << free, head, occupied)
    missed = check(0xEC59, 0x1234, 1 << 15, 16)
    assert not missed['accepted'] and missed['probes'] == [0xECA0]+list(range(0xEC80, 0xEC9E, 2))
    print('Queue insertion cases', sum(counts.values()), flush=True)

    # Проверка назначения типа 2, числовой обработчик исполняет настоящий рисователь без прокрутки.
    numeric = 0
    for value in range(256):
        m.recording = False
        m[:] = base
        m[0xEFD6] = 0
        m[0xBFFE:0xC000] = [255, 63]
        s.registers[:] = get_registers({'AF': value*256+((value*73)&255), 'HL': 0x1357,
            'DE': 0x2468, 'BC': 0x369C, '^AF': 0xDEF0, 'SP': 0xBFFE, 'PC': 0xECF3}, None, False)
        digits = []
        for _ in range(1200):
            pc = s.registers[PC]
            if pc == 0x3FFF:
                break
            assert pc != 0xED28, 'unexpected_scroll_in_numeric_role_check'
            if pc == 0xEFC4:
                digits.append(s.registers[0])
            s.run()
        else:
            raise AssertionError(('numeric_return', value))
        assert bytes(digits) == format(value, '02d').encode('ascii') and m[0xEFD6] == len(digits)
        assert s.registers[SP] == 0xC000
        numeric += 1
    report = dict(passed=True, insertion_cases=sum(counts.values()), cases_by_entry=dict(counts), outcomes=dict(failures),
        all_free_masks=True, all_raw_de_words=True, all_number_af_values=True,
        all_head_and_single_free_slot_pairs=True, every_memory_byte_and_write_checked=True,
        exact_saved_register_frame_checked=True, all_registers_except_r_preserved_as_documented=True,
        silent_full_failure=True, sentinel_consumes_search_probe=True, last_slot_missed_after_wrap_preserved=True,
        numeric_role_cases=numeric, actual_numeric_and_glyph_instructions_executed=True,
        byte_number_minimum_width_two=True, numeric_bitmap_independently_proved=False,
        consumer_whole_contract_proved=False, irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsTextQueueVerification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
