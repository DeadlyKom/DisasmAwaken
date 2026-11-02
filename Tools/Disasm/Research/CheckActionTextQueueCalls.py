"""Оригинальные межбанковые обёртки Action, очередь банка 1 и все физические банки памяти."""
from pathlib import Path
import collections, json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'Tools/Disasm/Research'))
from CheckControlsTextQueue import payload
from ReferenceControlsTextQueue import QUEUE, PRODUCER, insert, push_word
from CheckMusic import Simulator, get_registers, PC, SP
from skoolkit.pagingtracer import SliceableMemory


class Memory(SliceableMemory):
    def __setitem__(self, address, value):
        if getattr(self, 'recording', False):
            assert isinstance(address, int) and address >= 0x4000
            bank = 5 if address < 0x8000 else 2 if address < 0xC000 else self.o7ffd & 7
            self.writes.append((bank, address & 0x3FFF, value))
        super().__setitem__(address, value)


class Ports:
    def __init__(self, memory):
        self.memory = memory
        self.events = []

    def write_port(self, registers, port, value, offset):
        assert port == 0x7FFD
        self.events.append((port, value))
        assert not self.memory.o7ffd & 32
        self.memory.out7ffd(value)


def main():
    m = Memory(banks=[[0xA5]*16384 for _ in range(8)], out7ffd=0x10)
    action = payload(17)
    for index, value in enumerate(action):
        m[0x6000+index] = value
    # Подготовка исходного перемещённого блока по установленной разметке ActionBoot.
    for index, value in enumerate(action[0x23D:0x21CC]):
        m[0x6000+index] = value
    for slot, offset in ((22, 0), (23, 0x1ADE)):
        raw = payload(slot)
        m.banks[1][offset:offset+len(raw)] = raw
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    # Проверка всех исполняемых байтов обёрток и настоящего помощника paging до запуска.
    for group in flow:
        page = 0x10 if group['name'] == 'Action' else 0x11
        if group['name'] not in ('Action', 'Controls'):
            continue
        m.out7ffd(page)
        for instruction in group['instructions']:
            a = instruction['address']
            selected = (group['name'] == 'Action' and (0x6000 <= a < 0x6010 or 0x6040 <= a < 0x6054 or 0xAB1B <= a < 0xAB23)
                        or group['name'] == 'Controls' and 0xEC56 <= a < 0xEC80)
            if selected:
                raw = bytes.fromhex(instruction['hex'])
                assert bytes(m[a:a+len(raw)]) == raw
    base = [bank.copy() for bank in m.banks]
    s = Simulator(m)
    ports = Ports(m)
    s.set_tracer(ports)
    counts = collections.Counter()

    def check(entry, value, flags, alt_flags, page):
        m.recording = False
        for bank, original in zip(m.banks, base):
            bank[:] = original
        mask = (value*257) & 65535
        head = value % 17
        for index in range(16):
            m.banks[1][0x2C80+2*index] = 1 if mask & (1 << index) else 0x80
            m.banks[1][0x2C81+2*index] = (value+index*73) & 255
        cursor = QUEUE+2*head
        m.banks[1][0x2C5D:0x2C5F] = [cursor & 255, cursor >> 8]
        m.out7ffd(page)
        m[0xBFFE], m[0xBFFF] = 255, 63
        number = entry == 0x6000
        a = value & 255
        de = (0xA500 | a) if number else value
        af = a*256+flags
        initial = get_registers({'HL': 0x1357, 'DE': de, 'BC': 0x369C, 'AF': af,
            'IX': 0xABCD, 'IY': 0x5C3A, '^AF': 0x6900 | alt_flags, '^BC': 0x9ABC,
            '^DE': 0x5678, '^HL': 0x1234, 'SP': 0xBFFE, 'PC': entry}, None, False)
        initial[14], initial[26], initial[27] = a, flags & 1, a % 3
        virtual = {address: m.banks[1][address-0xC000] for address in range(QUEUE, QUEUE+34)}
        virtual[PRODUCER], virtual[PRODUCER+1] = cursor & 255, cursor >> 8
        item_value = 0x200 | a if number else value
        queue = insert(virtual, item_value)
        writes, stack = [], 0xBFFE
        def push(value):
            nonlocal stack
            writes.extend((2, address-0x8000, byte) for address, byte in push_word(stack, value))
            stack -= 2
        def select(return_address):
            nonlocal stack
            push(return_address)
            push(0x369C)
            stack += 4
        if not number:
            push(af)
            push(0x369C)
            push(0x1357)
        select(0x6006 if number else 0x6048)
        push(0x600A if number else 0x604B)
        push(0x1357)
        push(0x369C)
        push(af if number else 0x1100 | flags)
        writes.extend((1, address-0xC000, byte) for address, byte in queue['writes'])
        stack += 8
        select(0x600F if number else 0x6050)
        expected = [bank.copy() for bank in m.banks]
        for bank, offset, byte in writes:
            expected[bank][offset] = byte
        m.writes = []
        m.recording = True
        ports.events = []
        s.registers[:] = initial
        for _ in range(260):
            if s.registers[PC] == 0x3FFF:
                break
            s.run()
        else:
            raise AssertionError(('banked_queue_return', entry, value, page))
        m.recording = False
        assert m.banks == expected and sorted(m.writes) == sorted(writes), ('banked_queue_memory', entry, value, page)
        assert ports.events == [(0x7FFD, 0x11), (0x7FFD, 0x10)] and m.o7ffd == 0x10
        r = s.registers
        expected_main = initial[:8]
        expected_alt = initial[16:24]
        if number:
            expected_main[0] = 0x10
            expected_main[4:6] = [2, a]
            expected_alt[0] = 0x11
        assert r[:8] == expected_main and r[16:24] == expected_alt and r[SP] == 0xC000, ('banked_queue_registers', entry, value, r[:24])
        assert all(r[index] == initial[index] for index in (8, 9, 10, 11, 14, 26, 27))
        counts[format(entry, '04X')] += 1

    # Проверка каждого числового байта и важных F/F′ при настоящем обмене AF и переключении банка.
    for value in range(256):
        for flags in (0, 1, 0x80, 0xFF):
            for alt_flags in (0, 0xFF):
                check(0x6000, value, flags, alt_flags, 0x10)
    # Проверка каждого младшего байта и всех семантических границ HighKind для обёртки записи DE.
    for high in (0, 1, 2, 3, 0x7F, 0x80, 0xFE, 0xFF):
        for low in range(256):
            check(0x6040, high*256+low, low, low ^ 0xA5, 0x10)
    # Проверка каждого незаблокированного исходного paging-байта, результат всегда 10, не прежний байт.
    for page in range(32):
        for entry in (0x6000, 0x6040):
            check(entry, 0x1234, page, page ^ 0xA5, page)
    report = dict(passed=True, total_cases=sum(counts.values()), cases_by_entry=dict(counts),
        original_wrappers_paging_helper_and_queue_executed=True, eight_physical_banks_compared=True,
        every_memory_write_checked=True, real_7ffd_sequence=[0x11, 0x10],
        all_unlocked_initial_page_values=True, previous_page_not_restored=True,
        numeric_af_prime_a_becomes_11=True, numeric_input_f_and_alternate_f_preserved=True,
        word_wrapper_all_registers_preserved=True, silent_drop_paths_included=True,
        full_tail_after_6054_proved=False, irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ActionTextQueueCallsVerification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
