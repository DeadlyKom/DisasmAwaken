"""Перенос станционного загрузчика и ядра до первого обращения к диску."""
from itertools import product
import json
from hashlib import sha256

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh
from skoolkit.simutils import R
from CheckStationFlightCycle import DISK, ENTRIES


def main():
    data = (ROOT / 'Tools/Disasm/Extracted/Active/04_STATIONF.C.bin').read_bytes()
    assert data == DISK[ENTRIES[4]['offset']:ENTRIES[4]['offset'] + len(data)]
    cases = 0
    refresh_profiles = []
    for page, stack in product((0, 8, 16, 24), (0x5FFF, 0x5DF0, 0xBFFE)):
        banks = [bytearray([0xA0 + bank] * 0x4000) for bank in range(8)]
        banks[5][0x2000:] = data[:0x2000]
        banks[2][:len(data) - 0x2000] = data[0x2000:]
        memory = RecordedBanks(banks=banks, out7ffd=page)
        simulator = Simulator(memory)
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        initial = get_registers({'PC': 0x6300, 'SP': stack, 'IX': 0x1234, 'IY': 0xABCD,
                                 '^HL': 0x2345, '^DE': 0x3456, '^BC': 0x4567, '^AF': 0x5678,
                                 'I': cases * 17, 'R': cases * 23}, {'im':cases % 3, 'iff':cases & 1}, False)
        simulator.registers[:] = initial
        simulator.run(0x6300, 0x4000)
        assert bytes(memory[0x4000:0x42B5]) == data[0x319:0x5CE]
        entry_stack = simulator.registers[SP]
        entry_r = simulator.registers[R]
        measured_m1, min_sp = 0, entry_stack
        # Проверка исходных команд перенесённого загрузчика и селектора уже перемещённого ядра.
        assert bytes(memory[0x4000:0x402A]) == data[0x319:0x343]
        for _ in range(15000):
            pc = simulator.registers[PC]
            if pc == 0x4070:
                break
            assert 0x4000 <= pc < 0x402A or 0x639F <= pc < 0x63AA, hex(pc)
            if pc == 0x639F:
                assert bytes(memory[pc:pc + 11]) == data[0x64B:0x656]
            opcode = memory[pc]
            assert opcode not in (0xDD, 0xFD, 0xCB)
            measured_m1 += 2 if opcode == 0xED else 1
            simulator.run()
            assert simulator.registers[R] == refresh(entry_r, measured_m1)
            min_sp = min(min_sp, simulator.registers[SP])
        else:
            raise AssertionError('station_bootstrap_instruction_limit')
        r = simulator.registers
        context = (page, stack)
        assert bytes(memory[0x6322:0x7F8C]) == data[0x5CE:0x2238], context
        assert r[PC] == 0x4070 and r[SP] == entry_stack and memory.o7ffd == 0x18, context
        assert r[0] == 0x18 and r[2:8] == [0, 0, 0xDB, 0, 0xDA, 0xFF], context
        assert r[1] == 0x60 and measured_m1 == 16 + 2 * (0x1C6A + 0x1AFF) + 2 * 7 == 28400
        assert min_sp == entry_stack - 4
        assert r[8:12] == initial[8:12] and r[16:24] == initial[16:24], context
        assert r[14] == initial[14] and r[27] == initial[27]
        assert not r[26] and memory[0x6306] == 0x18 and memory[0x9E78] == 0, context
        assert bytes(memory.banks[7][:0x1B00]) == bytes(0x1B00), context
        assert trace.writes == [(0x00FE, 0), (0x7FFD, 0x17), (0x7FFD, 0x18)], context
        refresh_profiles.append(dict(initial_page=page, entry_SP=entry_stack, minimum_SP=min_sp,
                                     entry_R=entry_r, final_R=r[R], M1=measured_m1, final_AF=0x1860,
                                     preserved_I=r[14], preserved_IM=r[27], initial_IFF=initial[26]))
        cases += 1
    report = dict(passed=True, total_cases=cases, actual_banked_bootstrap=True,
                  bootstrap_bytes=0x2B5, core_bytes=0x1C6A,
                  original_initialize_code_sha256=sha256(data[0x319:0x343]).hexdigest(),
                  refresh_profiles=refresh_profiles, independent_M1_formula_checked=True,
                  r_checked_after_every_instruction=True, exact_final_AF=0x1860,
                  maximum_temporary_stack_bytes=4,
                  I_IM_preserved_and_IFF_cleared=True, IRQ_executed=False, native_execution=False,
                  stops_before_station_file_loads=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/StationBootstrapVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
