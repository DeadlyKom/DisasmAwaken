"""Архивная проверка старшего байта DALNO и соседние поля в текущем гиперпереходе."""
import argparse
import json
from pathlib import Path

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckIntro import ROOT
from CheckScreenUpdate import put
from CheckStationFlightCycle import payload
from ClassifyActionArchivedBodyContext import archive_inputs, check_distance, historical_memory
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, get_registers


ADJACENT = (0x9C89, 0x9C8B)
COST = 0x9C8A


class ContextTrace(RecordedBanks):
    registers = None

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.registers is not None and isinstance(address, int) and 0x9C88 <= address <= 0x9C8B:
            self.reads.append((address, self.registers[PC], value))
        return value


def execute(banks, preferred, fallback, cost, target, speed, high):
    memory = ContextTrace(banks=[bank.copy() for bank in banks], out7ffd=16)
    put(memory, 0x9BC1, b'ABCDE')
    put(memory, 0x9BC6, target)
    put(memory, 0xBFFE, b'\xFF\x3F')
    for address, value in ((0x9C10, preferred), (0x9C11, fallback), (COST, cost),
                           (0xA85F, 0), (0x9C26, 0), *zip(ADJACENT, (speed, high))):
        memory[address] = value
    cpu = Simulator(memory)
    cpu.registers[:] = get_registers({'PC': 0x70F6, 'SP': 0xBFFE, 'IY': 0x5C3A}, None, False)
    memory.registers = cpu.registers
    memory.reads, memory.writes = [], []
    memory.recording = True
    for _ in range(100):
        if cpu.registers[PC] in (0x7176, 0x3FFF):
            break
        cpu.run()
    else:
        raise AssertionError(hex(cpu.registers[PC]))
    memory.recording = False
    memory.registers = None
    assert memory.reads == [(COST, 0x7108 if preferred else 0x7127, cost)]
    assert tuple(memory[address] for address in ADJACENT) == (speed, high)
    # Перед сравнением RAM убираем только две намеренные разницы во входе.
    for address in ADJACENT:
        memory[address] = 0
    return cpu.registers, memory.banks, memory.writes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_archive', type=Path)
    args = parser.parse_args()
    sp = archive_inputs(args.source_archive)
    archive = check_distance(historical_memory(sp), sp, payload(17))
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    banks[5][:] = bytes(flat[0x4000:0x8000])
    banks[2][:] = bytes(flat[0x8000:0xC000])
    banks[0][:] = bytes(flat[0xC000:])
    profiles = []
    for preferred, fallback in ((48, 0), (0, 48)):
        for cost, target in ((12, b'abcde'), (12, b'ABCDE'), (85, b'abcde')):
            inputs = banks, preferred, fallback, cost, target
            expected = execute(*inputs, 0, 0)
            accepted = cost == 12 and target != b'ABCDE'
            assert expected[0][PC] == (0x7176 if accepted else 0x3FFF)
            for high in range(256):
                assert execute(*inputs, high ^ 0xFF, high) == expected
            profiles.append(dict(route='Preferred' if preferred else 'Fallback', cost=cost,
                                 equal_destination=target == b'ABCDE', stop=expected[0][PC],
                                 compared_registers=len(expected[0]), varied_adjacent_pairs=256))
    report = dict(passed=True, archive=archive, current_profiles=profiles,
                  current_adjacent_addresses=ADJACENT, current_cost_address=COST,
                  all_ram_and_write_order_compared=True, stops_before_message=True,
                  assembly_executed=False, native_execution=False)
    result = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/HyperJumpAdjacentStateVerification.json').write_text(result, encoding='utf-8')
    print('Сверены 1024 архивных и 1536 текущих сочетаний состояния гиперперехода.')


if __name__ == '__main__':
    main()
