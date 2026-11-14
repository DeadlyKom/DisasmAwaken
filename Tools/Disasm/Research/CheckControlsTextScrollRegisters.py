"""Точные регистры, восемь банков, стек и M1 настоящей прокрутки ED28..EFC3."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckControlsTextDisplay import execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator, get_registers, PC, SP
from CheckScreenUpdate import PortTrace, put
from ReferenceControlsTextDisplay import initialize, pixel_address
from ReferenceControlsPointRespawn import refresh


def main():
    flat = list(base_memory())
    reference = list(flat)
    initialize(reference)
    execute(flat, 0xEC0E)
    assert flat[0xC000:] == reference[0xC000:]
    base = [bytearray([0xA0 + i] * 16384) for i in range(8)]
    base[5], base[2], base[1] = (bytearray(flat[0x4000:0x8000]),
                               bytearray(flat[0x8000:0xC000]), bytearray(flat[0xC000:]))
    memory = RecordedBanks(banks=[bytearray(b) for b in base], out7ffd=17)
    sim = Simulator(memory)
    cases = 0
    final_f_values = set()
    for stack in (0x7FFE, 0x8002, 0x9FFE, 0xBFFE):
        for pattern in range(256):
            memory.recording = False
            for bank, original in zip(memory.banks, base):
                bank[:] = original
            memory.banks[5][:0x1B00] = bytes(
                (pattern + i * 73 + (i >> 8) * 29) & 255 for i in range(0x1B00))
            put(memory, stack, (255, 63))
            initial = get_registers({
                'AF': 0xA500 | pattern, 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
                '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0,
                'IX': 0xABCD, 'IY': 0x5C3A, 'SP': stack, 'PC': 0xED28,
            }, None, False)
            initial[14], initial[15] = pattern, pattern
            initial[26], initial[27] = pattern & 1, pattern % 3
            wanted = list(initial)
            # Расчёт регистров из исходной последней строки, до её очистки.
            source = pixel_address(189, 20)
            assert source == 0x55F4
            wanted[0:8] = [memory[source + 7], memory[source + 6],
                           memory[source + 5], memory[source + 4], 1, 0, 0, 0]
            wanted[18:22] = [memory[source + 9], memory[source + 8],
                             memory[source + 11], memory[source + 10]]
            wanted[PC], wanted[SP], wanted[15] = 0x3FFF, stack + 2, refresh(pattern, 528)
            writes = [(1, 0x2FC1, stack & 255), (1, 0x2FC2, stack >> 8)]
            # Копирование ожидаемых строк по координатам, независимо от POP/PUSH и временного SP.
            for row in range(5):
                for scan in range(6):
                    src = pixel_address(152 + 8 * row + scan, 20)
                    dst = pixel_address(144 + 8 * row + scan, 20)
                    writes.extend((5, dst + i - 0x4000, memory[src + i]) for i in range(12))
            for scan in range(6):
                dst = pixel_address(184 + scan, 20)
                writes.extend((5, dst + i - 0x4000, (scan & 1) if i == 11 else 0)
                              for i in range(12))
            expected = [bytearray(b) for b in memory.banks]
            for bank, offset, value in writes:
                expected[bank][offset] = value
            sim.registers[:] = initial
            trace = PortTrace(sim)
            sim.set_tracer(trace)
            memory.writes = []
            memory.recording = True
            measured_m1 = steps = 0
            while sim.registers[PC] != 0x3FFF:
                assert steps < 528
                old_r = sim.registers[15]
                sim.run()
                increment = (sim.registers[15] - old_r) & 127
                assert increment in (1, 2)
                measured_m1 += increment
                steps += 1
            memory.recording = False
            # Проверка всех регистров, физической RAM, кратности записей и восстановленного стека.
            assert all(wanted[i] == sim.registers[i] for i in (*range(25), 26, 27)), (stack, pattern)
            assert memory.banks == expected and Counter(memory.writes) == Counter(writes)
            assert not trace.writes and memory.o7ffd == 17
            assert measured_m1 == 528 and steps == 527
            final_f_values.add(sim.registers[1])
            cases += 1
    assert len(final_f_values) == 256
    report = dict(
        passed=True, total_cases=cases, source_last_row_address=0x55F4,
        exact_registers_including_R=True, all_256_output_F_bytes=True,
        all_physical_ram_and_write_multiplicity_checked=True,
        real_initializer_executed=True, original_scroll_instructions_executed=True,
        instruction_count=527, full_M1_count=528, screen_byte_writes=432,
        saved_SP_byte_writes=2, stack_positions=[0x7FFE, 0x8002, 0x9FFE, 0xBFFE],
        external_return_preserved=True, no_ports_or_paging_changes=True,
        complete_screen_product_exhausted=False, irq_executed=False,
        native_execution=False, assembly_executed=False, timing_proved=False,
    )
    (ROOT / 'Tools/Disasm/Reports/ControlsTextScrollRegistersVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
