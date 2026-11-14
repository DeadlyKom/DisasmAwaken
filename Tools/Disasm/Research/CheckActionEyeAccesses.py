"""Наблюдение девяти байтов EYE/STP в ограниченном исходном полётном цикле.

Документация: ../../../Docs/ActionInputContextData.md#наблюдение-физических-полей-eye-и-stp
"""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import json

from CheckActionParameterActivation import flat_action
from CheckScreenUpdate import put
from CheckStationFlightCycle import payload
from TraceFlight import Memory, PC, ROOT, Simulator, main as trace_flight

START, END = 0x9B98, 0x9BA1


class EyeMemory(Memory):
    recording = False
    cpu = None

    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.accesses = Counter()

    def observe(self, address, operation):
        # Чтения исследовательской обвязки исключены, наблюдаются только вызовы Simulator.run.
        if self.recording and isinstance(address, int) and START <= address < END:
            self.accesses[operation, self.cpu.registers[PC], self.o7ffd & 7, address] += 1

    def __getitem__(self, address):
        self.observe(address, 'read')
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        self.observe(address, 'write')
        super().__setitem__(address, value)


class ObservedCPU(Simulator):
    def run(self, *args, **kwargs):
        self.memory.recording = True
        try:
            return super().run(*args, **kwargs)
        finally:
            self.memory.recording = False


def make_cpu(memory, entry=0x6000):
    cpu = ObservedCPU(memory, {'PC': entry, 'SP': 0x5FFF, 'IY': 0x5C3A},
        config={'fast_ldir': False, 'fast_djnz': False})
    memory.cpu = cpu
    return cpu


def main():
    # Положительный контроль выполняет настоящий двухбайтовый читатель через IX.
    functions = json.loads((ROOT / 'Tools/Disasm/Reports/Functions.json').read_bytes())
    entry = next(r['address'] for r in functions if r['region'] == 'Action' and r['name'] == 'ReadWordFromIX')
    control = EyeMemory()
    put(control, 0, flat_action())
    control[0x5FFD], control[0x5FFE] = 255, 63
    cpu = make_cpu(control, entry)
    expected = Counter()
    for address in range(START, END):
        cpu.registers[8:10] = [address >> 8, address & 255]
        cpu.registers[12], cpu.registers[24] = 0x5FFD, entry
        cpu.run(start=entry, stop=0x3FFF)
        expected[address] += 1
        if address + 1 < END:
            expected[address + 1] += 1
    actual = Counter()
    for (operation, pc, bank, address), count in control.accesses.items():
        assert operation == 'read'
        actual[address] += count
    assert actual == expected and len(actual) == 9
    profiles = []
    for sentinel in (False, True):
        memory = EyeMemory()
        original = payload(17)
        put(memory, 0x6000, original)
        cpu = make_cpu(memory)
        injected = False
        snapshot = None

        def observe(frame, current, registers):
            nonlocal injected, snapshot
            if registers[PC] == 0xA85E and snapshot is None:
                snapshot = bytes(current[a] for a in range(START, END))
                if sentinel:
                    for i, address in enumerate(range(START, END)):
                        current[address] = (0x35 + i * 29) & 255
                    injected = True

        with redirect_stdout(StringIO()):
            flight = trace_flight(['--verify-flight-cycle', '--frames', '65'],
                boot_simulator=cpu, save_reports=False, instruction_observer=observe)
        assert flight['complete_frame_returns'] == 64
        assert snapshot is not None and injected == sentinel
        rows = [dict(operation=op, pc=pc, execution_bank=bank, physical_bank=2,
                     address=address, count=count)
                for (op, pc, bank, address), count in sorted(memory.accesses.items())]
        # Проверка сохранения исходных либо искусственно заданных байтов после всех кадров.
        final_values = bytes(memory[a] for a in range(START, END))
        expected_values = bytes((0x35 + i * 29) & 255 for i in range(9)) if sentinel else snapshot
        assert final_values == expected_values
        profiles.append(dict(artificial_values_injected=sentinel,
            values_before_first_frame_hex=snapshot.hex(), complete_frame_returns=64,
            accesses=rows, final_values_hex=final_values.hex()))
        print('Eye profile', sentinel, '64 frames, watched events', sum(r['count'] for r in rows), flush=True)
    result = dict(passed=True, original_action_sha256=sha256(payload(17)).hexdigest(),
        watched_addresses=list(range(START, END)), positive_control_real_IX_reader=entry,
        positive_control_reads_by_address=dict(actual), CPU_accesses_only=True,
        profiles=profiles, no_keys=True, trdos_substituted=True,
        irq_injected=False, all_game_paths_exhausted=False,
        original_STP_purpose_proved=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionEyeAccessesVerification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Completed two original flight profiles; no semantic unusedness claim.')


if __name__ == '__main__':
    main()
