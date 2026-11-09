"""Полётный кадр оригинала с одной замкнутой клавишей за проход сканера."""
import json

from CheckActionParameterActivation import flat_action
from TraceFlight import H, L, PC, SP, Ports, ROOT, main as trace_flight


class KeyProbe(Ports):
    def __init__(self, memory, key):
        super().__init__(memory)
        self.key = key
        self.active = False
        self.scan_sp = None
        self.reads = []
        self.handlers = []
        self.returns = 0
        self.finished = False
        self.pending_target = None
        self.special_entries = set()

    def read_port(self, registers, port):
        if not self.active or registers[PC] != 0x6F34:
            return super().read_port(registers, port)
        row, mask = self.key
        value = 255 ^ mask if port == row * 256 + 0xFE else 255
        self.reads.append((port, value))
        return value

    def observe(self, frame, memory, registers):
        pc, sp = registers[PC], registers[SP]
        bank = memory.o7ffd & 7
        if (pc == 0xCF08 and bank == 0) or 0x5E1F <= pc < 0x5EDB:
            self.special_entries.add((bank, pc))
        if pc == 0x6F1D and frame == 1 and self.scan_sp is None:
            assert bank == 0
            self.scan_sp = sp
            self.active = True
        if not self.active:
            return
        if self.pending_target is not None:
            assert pc == self.pending_target
            self.pending_target = None
        if pc == 0x6F4D:
            target = registers[H] * 256 + registers[L]
            assert sp == self.scan_sp - 10 and memory[sp] == 0x4E and memory[sp + 1] == 0x6F
            self.handlers.append((len(self.reads) - 1, bank, target))
            self.pending_target = target
        elif pc == 0x6F4E:
            assert sp == self.scan_sp - 8
            self.returns += 1
        elif pc == 0x6F55:
            assert sp == self.scan_sp
            self.finished = True
            self.active = False


def main():
    original = flat_action()
    keys = [tuple(original[address:address + 2]) for address in range(0x9D4C, 0x9D82, 2)]
    targets = [original[address] | original[address + 1] << 8 for address in range(0x7017, 0x704D, 2)]
    assert len(keys) == len(targets) == 27 and len(set(keys)) == 26
    assert keys[0] == keys[-1] == (0xFD, 0x02) and targets[-1] == 0xC0C9
    cases = []
    for key in dict.fromkeys(keys):
        probe = None

        def ports(memory):
            nonlocal probe
            probe = KeyProbe(memory, key)
            return probe

        def observe(frame, memory, registers):
            probe.observe(frame, memory, registers)

        flight = trace_flight(['--frames', '2'], ports_factory=ports, instruction_observer=observe,
                              save_reports=False)
        expected = [(index, 0, targets[index]) for index, pair in enumerate(keys) if pair == key]
        expected_reads = [(row * 256 + 0xFE, 255 ^ key[1] if row == key[0] else 255) for row, _ in keys]
        assert probe.reads == expected_reads
        assert probe.handlers == expected, (key, probe.handlers, expected)
        assert probe.finished and probe.returns == len(expected) and probe.pending_target is None
        assert flight['frame_entries'] == 2 and flight['reason'] == 'requested_frame_entries'
        assert not probe.special_entries
        cases.append(dict(row=key[0], mask=key[1], read_count=len(probe.reads), handlers=probe.handlers,
                          keyboard_frame_returns=probe.returns, decay_reached=probe.finished,
                          next_flight_frame_reached=flight['frame_entries'] == 2,
                          stop_reason=flight['reason'], watched_entries=sorted(probe.special_entries)))
    result = dict(passed=True, total_cases=len(cases), matrix_steps_reached=sum(len(case['handlers']) for case in cases),
                  cases=cases, irq_scheduled_by_flight_model=True, trdos_stub=True,
                  continuous_key_hold_verified=False, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/FlightKeyPathsVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f"{len(cases)} проходов матрицы, {result['matrix_steps_reached']} вызовов и возвратов")


if __name__ == '__main__':
    main()
