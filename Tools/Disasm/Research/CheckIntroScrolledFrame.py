"""Две реальные выборки прокручиваемого кадра до входа экранного переноса.

Документация: ../../../Docs/IntroScrolledFrame.md#независимые-приращения-и-граница-вывода
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from random import Random
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT, original_memory
from CheckIntroWaitInterrupt import Keyboard
from CheckIntroScrolledInitialization import IntroPorts
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import put
from ReferenceIntroFrame import Frame
from CheckStationFlightCycle import DISK, ENTRIES


def advance(phase, step, delta):
    step = (step + (-delta if phase & 0x8000 else delta)) & 65535
    return (phase + step) & 65535, step, delta


def main():
    flat = original_memory()
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    assert sha256(rom).hexdigest() == 'd55daa439b673b0e3f5897f99ac37ecb45f974d1862b4dadb85dec34af99cb42'
    body = bytes(flat[0x66A3:0x66E2])
    offset_in_disk = ENTRIES[3]['offset'] + 0x3A3
    assert body == DISK[offset_in_disk:offset_in_disk + len(body)]
    rng = Random(0x66A3)
    cases = 0
    wrapper_cases = 0
    directions = ((0,0), (1,1), (255,255), (1,255), (255,1))
    for page, offset, (dstep, estep), signs in product((17, 22), (0, 0x1F, 0x3F), directions, range(4)):
        banks = [bytearray([0xA0 + i] * 0x4000) for i in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[2][:] = rng.randbytes(0x4000)
        banks[page & 7][:] = rng.randbytes(0x4000)
        memory = RecordedBanks(banks=banks, out7ffd=17)
        memory.roms = (list(rom), list(rom))
        memory.out7ffd(17)
        memory[0x5C00] = memory[0x5C04] = 255
        memory[0x5FFE], memory[0x5FFF] = 255, 63
        memory.banks[5][0x3E00:0x3FC3] = bytes(flat[0x6722:0x6729]) * 64 + bytes.fromhex('c3f366')
        memory[0x66EC], memory[0x66ED] = offset, 128 + offset
        first = (0x9876 if signs & 1 else 0x1234, 0x0142, 0x0123)
        second = (0x8BCD if signs & 2 else 0x7D67, 0x0132, 0x0101)
        for address, words in ((0x662C, first), (0x6632, second)):
            memory.banks[5][address - 0x4000:address - 0x4000 + 6] = b''.join(word.to_bytes(2, 'little') for word in words)
        first_next = advance(*first)
        second_next = advance(*second)
        pointer_low = ((first_next[0] >> 8) - 0x60) * 2 & 255
        pointer_high = ((second_next[0] >> 8) + 0x50) & 255
        pointer_start = pointer_high * 256 + pointer_low
        pointers = []
        for row in range(32):
            values = [0x3000 | rng.randrange(4096) for _ in range(64)]
            pointer_address = pointer_start + row * 256 - 0xC000
            memory.banks[page & 7][pointer_address:pointer_address + 128] = b''.join(
                word.to_bytes(2, 'little') for word in values
            )
            pointers.append(values)
        frame_phase = 128 if signs & 1 else 0
        memory[0x67F2] = frame_phase
        writer = bytes(byte for row, col in product(range(8), range(4))
                       for byte in (0xE1, 0x22, 0x80 + 2 * col, 0x80 + row))
        put(memory, 0x68A9, writer)
        for half in range(2):
            for row in range(38):
                table = (0x7200 if half == 0 else 0xAD00) + 64 * row
                destination = (0x4000 if half == 0 else 0x5000) + 32 * row
                put(memory, 0x6000 + 256 * half + 4 * row,
                    table.to_bytes(2, 'little') + destination.to_bytes(2, 'little'))
                for col in range(32):
                    source = 0x80C0 + ((row + half * 13) % 32) * 256 + col
                    put(memory, table + 2 * col, source.to_bytes(2, 'little'))
            put(memory, 0x60C0 + 256 * half, rng.randbytes(64))
        expected = memory.banks[2].copy()
        offset_word = (128 + ((offset + estep) & 63)) * 256 + ((offset + dstep) & 63)
        for row, values in enumerate(pointers):
            for col, pointer in enumerate(values):
                source = ((pointer + offset_word) & 0xBFFF) - 0x8000
                expected[256 * row + 0xC0 + col] = expected[source]
        simulator = Simulator(memory)
        trace = IntroPorts(simulator)
        simulator.set_tracer(trace)
        wrapper = page == 22 and dstep == estep == 255
        entry = 0x661E if wrapper else 0x66A3
        initial = get_registers({'PC': entry, 'SP': 0x5FFE, 'IY': 0x5C3A, 'AF':page * 256 + 0xA5,
            'DE': dstep * 256 + estep, 'HL': 0x662C, 'BC': 0x6632, 'IX':0xABCD, 'I':0x3C,
            '^AF':0xA55A, '^HL':0x1357, '^DE':0x2468, '^BC':0x369A}, {'im':1, 'iff':0}, False)
        simulator.registers[:] = initial
        simulator.run(entry, 0x67F1, interrupts=True)
        context = (page, offset, dstep, estep, signs)
        assert simulator.registers[PC] == 0x67F1 and simulator.registers[SP] == 0x5FFE, context
        # Проверка сохраняемого контекста до первого действия вывода кадра.
        assert all(simulator.registers[i] == initial[i] for i in (*range(8,12),14,16,17,27)), context
        assert simulator.registers[26] == 0, context
        assert bytes(memory.banks[2]) == expected, context
        for address, words in ((0x662C, advance(*first)), (0x6632, advance(*second))):
            assert bytes(memory[address:address + 6]) == b''.join(word.to_bytes(2, 'little') for word in words), context
        assert (memory[0x66EC], memory[0x66ED]) == (offset_word & 255, offset_word >> 8)
        assert (memory[0x66D4], memory[0x66D5]) == (
            ((advance(*first)[0] >> 8) - 0x60) * 2 & 255, ((advance(*second)[0] >> 8) + 0x50) & 255
        )
        assert trace.writes == [(0x7FFD, page)] and memory.o7ffd == page
        assert int.from_bytes(bytes(memory[0x5C78:0x5C7B]), 'little') == 2, context
        physical = [bytearray(bank) for bank in memory.banks]
        writes = []

        def read(address):
            if address < 0x4000:
                return rom[address]
            bank = 5 if address < 0x8000 else 2 if address < 0xC000 else page & 7
            return physical[bank][address & 0x3FFF]

        def write(address, value):
            bank = 5 if address < 0x8000 else 2 if address < 0xC000 else page & 7
            physical[bank][address & 0x3FFF] = value
            writes.append((bank, address & 0x3FFF, value))

        oracle = Frame(read, write, list(simulator.registers))
        expected_ports = oracle.present(frame_phase, 128)
        keyboard = Keyboard()
        simulator.set_tracer(keyboard)
        memory.writes = []
        memory.recording = True
        simulator.run(0x67F1, 0x3FFF, interrupts=True)
        memory.recording = False
        checked = (*range(15), *range(16, 25), 26, 27)
        assert all(simulator.registers[i] == oracle.r[i] for i in checked), context
        assert all(actual == wanted for actual, wanted in zip(memory.banks, physical)), context
        assert keyboard.reads == expected_ports and not keyboard.writes, context
        assert Counter(memory.writes) == Counter(writes), context
        wrapper_cases += wrapper
        cases += 1
    report = dict(passed=True, total_cases=cases, actual_generated_chain_and_rom_executed=True,
                  exact_source_buffer_compared=True, irq_count_before_present=2, final_wrapper_cases=wrapper_cases,
                  final_screen_transfer_executed=True, all_physical_banks_compared=True, assembly_executed=False,
                  original_body_sha256=sha256(body).hexdigest(), rom_sha256=sha256(rom).hexdigest(),
                  nonzero_AF_alternate_IX_IY_preserved_before_present=True,
                  initial_I=0x3C, initial_IM=1, initial_IFF=0, IFF_before_present=0,
                  pointer_tables_prepared_by_model=True, native_original_pointer_graph_proved=False,
                  tested_D_E_pairs=[list(pair) for pair in directions],
                  exact_R_and_timing_proved=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/IntroScrolledFrameVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
