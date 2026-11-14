"""Точные выходы ConsumeTextQueue по Free и LF, без подмены инструкций и сборки."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusicGateTicks import Memory
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceControlsTextDisplay import QUEUE, ACTIVE, READER, put_word
from ReferenceControlsPointRespawn import refresh


class NoPorts:
    def __init__(self):
        self.writes = []

    def write_port(self, registers, port, value, offset):
        raise AssertionError(('неожиданный OUT', port, value))

    def read_port(self, registers, port):
        raise AssertionError(('неожиданный IN', port))


def main():
    baseline = base_memory()
    memory = Memory(baseline)
    sim = Simulator(memory)
    counts = Counter()

    def check(kind, flags, slot_index=0, wrap=False):
        memory.recording = False
        memory[:] = baseline
        slot = QUEUE + 2 * slot_index
        pointer = 0x9000 + flags
        reader = QUEUE + 30 if wrap else slot - 2
        put_word(memory, ACTIVE, pointer if kind == 'active_lf' else 0)
        put_word(memory, READER, reader)
        memory[QUEUE + 32] = 0
        memory[slot:slot + 2] = [1, 0xA5] if kind == 'free' else [0x90, flags]
        memory[pointer] = 10
        put_word(memory, 0xBFFE, 0x3FFF)
        initial = get_registers({
            'AF': ((flags ^ 0xA5) << 8) | flags, 'HL': 0x1357, 'DE': 0x2468,
            'BC': 0x369C, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x5C3A,
            'SP': 0xBFFE, 'PC': 0xECA2,
        }, None, False)
        initial[14], initial[15] = flags, flags ^ slot_index
        initial[26], initial[27] = flags & 1, flags % 3
        wanted = list(initial)
        writes = []

        def word(address, value):
            writes.extend(((address, value & 255), (address + 1, value >> 8)))

        # Расчёт ожидаемых записей только из условий входа, без исполнения эталона потребителя.
        if kind != 'active_lf':
            if wrap:
                word(READER, QUEUE + 32)
            word(READER, slot)
        if kind == 'free':
            wanted[0:2] = [1, 0]
            wanted[6:8] = [slot >> 8, slot & 255]
            m1 = 21 if wrap else 13
        else:
            if kind == 'queued_lf':
                writes.append((slot, 1))
                wanted[4:6] = [(slot + 1) >> 8, (slot + 1) & 255]
            word(ACTIVE, pointer + 1)
            word(ACTIVE, 0)
            wanted[0:2] = [10, 0x4A]
            wanted[6:8] = [0, 0]
            m1 = 12 if kind == 'active_lf' else 33 if wrap else 25
        wanted[PC], wanted[SP] = 0x3FFF, 0xC000
        wanted[15] = refresh(initial[15], m1)
        expected = list(memory)
        for address, value in writes:
            expected[address] = value
        sim.registers[:] = initial
        trace = NoPorts()
        sim.set_tracer(trace)
        memory.writes = []
        memory.recording = True
        measured_m1 = 0
        for _ in range(64):
            if sim.registers[PC] == 0x3FFF:
                break
            old_r = sim.registers[15]
            sim.run()
            increment = (sim.registers[15] - old_r) & 127
            assert increment == 1
            measured_m1 += increment
        else:
            raise AssertionError(('нет возврата', kind, flags, slot_index, wrap))
        memory.recording = False
        # Проверка всех регистров, полной памяти, кратности записей и полного M1, порты не используются.
        assert all(sim.registers[i] == wanted[i] for i in (*range(25), 26, 27)), (
            kind, flags, slot_index, wrap,
            [(i, wanted[i], sim.registers[i]) for i in (*range(25), 26, 27)
             if wanted[i] != sim.registers[i]])
        assert memory == expected and Counter(memory.writes) == Counter(writes)
        assert measured_m1 == m1 and not trace.writes
        counts[kind + ('_wrap' if wrap else '')] += 1

    # Проверка всех слотов и F, активная строка должна обходить занятую запись очереди.
    for flags in range(256):
        for slot_index in range(16):
            check('free', flags, slot_index)
            check('queued_lf', flags, slot_index)
        check('active_lf', flags)
        check('free', flags, wrap=True)
        check('queued_lf', flags, wrap=True)
    report = dict(
        passed=True, total_cases=counts.total(), cases_by_kind=dict(counts),
        exact_registers_including_R=True, full_M1_count_checked=True,
        all_16_slots_and_all_input_F=True, all_256_string_pointer_low_bytes=True,
        active_string_priority_checked=True, full_memory_and_write_multiplicity=True,
        flat_bank1_mapping=True, scroll_and_glyph_paths_executed=False,
        complete_context_product_exhausted=False, irq_executed=False,
        native_execution=False, assembly_executed=False, timing_proved=False,
    )
    (ROOT / 'Tools/Disasm/Reports/ControlsTextConsumerExitsVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
