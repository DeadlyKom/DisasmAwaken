"""Цепочка от измерителя карты до стоимости гиперперехода через настоящий перенос состояния."""
from collections import Counter
import json

from CheckActionOverlappingKeyClipReturns import run_to
from CheckCoordinateDistance import reference as distance_reference
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace, put
from ReferenceActionHyperJump import HyperJumpMachine
from TraceFlight import main as trace_flight
from skoolkit.pagingtracer import SliceableMemory


STATION_DISTANCE = 0x9908
ACTION_COST = 0x9C8A
SAVED_STATION_STATE = 0x983B
RESTORED_ACTION_STATE = 0x9BBD
CONTEXT_SIZE = 512


def main():
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()

    def original_file(slot):
        entry = next(row for row in manifest['entries'] if row['slot'] == slot)
        return disk[entry['offset']:entry['offset'] + entry['length']]

    _, map_code, banks = make_context()
    action = original_file(17)
    music = original_file(10)
    banks[3][0x1B00:0x1B00 + len(music)] = list(music)
    offset = STATION_DISTANCE - SAVED_STATION_STATE
    assert offset == ACTION_COST - RESTORED_ACTION_STATE == 0xCD
    samples = [(3 * value, 0) for value in range(86)] + [(1, 0), (255, 255), (256, 0), (0, 256)]
    reached_costs = set()
    paths = Counter()
    copied_counters = set()
    booted_costs = set()

    for x, y in samples:
        expected = distance_reference(map_code, 0, 0, x, y, 0)[0]
        profiles = [(255, 0), (0, 255), (1, 0), (0, 0)]
        for preferred, fallback in profiles:
            memory = SliceableMemory(banks=[bytearray(bank) for bank in banks], out7ffd=0x11)
            simulator = Simulator(memory)
            ports = PortTrace(simulator)
            simulator.set_tracer(ports)
            r = simulator.registers
            selected_low = (y & 255) << 8 | (x & 255)
            selected_high = (y & 0xFF00) | (x >> 8)
            put(memory, 0x983F, bytes(5))
            put(memory, 0x9844, selected_high.to_bytes(2, 'little') + selected_low.to_bytes(2, 'little') + b'\x00')
            r[:] = get_registers({'PC': 0xE7BA, 'SP': 0x7FFE, 'IY': 0x5C3A,
                                  'BC': selected_low, 'DE': selected_high}, None, False)
            put(memory, 0x7FFE, (255, 63))
            run_to(simulator, 0x3FFF, 20000)
            assert memory[STATION_DISTANCE] == expected

            # Исходный вход подготовки после допуска интерфейса, карта уже вычислила байт расстояния.
            memory[0x9849] = 0
            memory[0x6306] = 0x11
            memory[0x98AA] = 0 if preferred else 255
            assert memory[0x9906] == 100
            expected_counter = 130 if preferred else 100
            r[PC], r[SP] = 0x7E5A, 0x7FFE
            run_to(simulator, 0x4200, 10000)
            saved = bytes(memory[0x4000:0x4000 + CONTEXT_SIZE])
            assert saved[offset] == expected
            assert saved[0xCB] == memory[0x9906] == expected_counter
            run_to(simulator, 0x3D13, 10000)
            assert bytes(memory[0x5CDD:0x5CE6]) == b'ACTION  C'
            assert bytes(memory[r[SP]:r[SP] + 2]) == bytes.fromhex('36 42')

            # Постусловие успешной загрузки ACTION, собственное продолжение загрузчика исполняется.
            put(memory, 0x6000, action)
            r[PC], r[SP] = 0x4236, r[SP] + 2
            run_to(simulator, 0x6000, 10000)
            assert bytes(memory[RESTORED_ACTION_STATE:RESTORED_ACTION_STATE + CONTEXT_SIZE]) == saved
            assert memory[ACTION_COST] == expected
            assert memory[0x9C88] == expected_counter
            copied_counters.add(expected_counter)

            if preferred == 255 and expected in (0, 85, 255) and expected not in booted_costs:
                observed = []
                flight = trace_flight(['--verify-flight-cycle', '--frames', '2'],
                                     lambda _, ram, regs: observed.append(ram[ACTION_COST]),
                                     boot_simulator=simulator)
                assert observed == [expected] and flight['complete_frame_returns'] == 1
                booted_costs.add(expected)
            else:
                # Точное содержимое перенесённого ядра, без изменения доставленной стоимости и контекстов.
                put(memory, 0x6000, action[0x23D:0x21CC])
            for address, value in ((0xA85F, 0), (0x9C26, 0), (0x9C10, preferred), (0x9C11, fallback)):
                memory[address] = value
            r[PC], r[SP] = 0x70F6, 0xBFFE
            put(memory, r[SP], (255, 63))
            oracle = HyperJumpMachine(memory.banks, r)
            oracle.request()
            run_to(simulator, oracle.r[PC], 100)
            assert memory.banks == oracle.banks and memory[ACTION_COST] == expected
            compared = (*range(13), 14, *range(16, 25), 26, 27)
            assert all(r[index] == oracle.r[index] for index in compared)
            paths.update(oracle.path)
            reached_costs.add(expected)

    assert reached_costs == set(range(86)) | {255}
    assert booted_costs == {0, 85, 255}
    assert set(paths) == {'same_context_after_spend', 'accepted_before_message', 'insufficient_selected_byte'}
    result = dict(passed=True, total_cases=len(samples) * len(profiles), paths=dict(paths),
                  distance_values=sorted(reached_costs), state_offset=offset,
                  station_9906_copied_to_action_9C88=sorted(copied_counters),
                  original_distance_arithmetic_and_both_state_copies_executed=True,
                  whole_512_byte_copy_checked=True, explicit_disk_postcondition=True,
                  real_action_boot_and_complete_frame_costs=sorted(booted_costs),
                  other_profiles_use_original_relocation_fixture=True,
                  command_stock_and_gate_prepared=True, irq_injected_during_distance_transition_or_command=False,
                  assembly_executed=False, native_execution=False)
    report = ROOT / 'Tools/Disasm/Reports/StationHyperJumpCostTransferVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'distance_values'}, indent=2))


if __name__ == '__main__':
    main()
