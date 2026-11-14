"""Полётный кадр оригинала с одной замкнутой клавишей за проход сканера."""
from collections import Counter
import json
from struct import pack

from Analyze import payload
from CheckActionParameterActivation import flat_action
from TraceFlight import D, E, H, IFF, L, PC, SP, Memory, Ports, ROOT, Simulator, main as trace_flight


class ClipDispatchProbe:
    """Проверка старшей таблицы только при исполнении диспетчера в банке 0."""

    def __init__(self, high_page):
        self.high_page = high_page
        self.dispatches = Counter()
        self.targets = set()
        self.alias_entries = set()

    def observe(self, memory, registers):
        if memory.o7ffd & 7 != 0:
            return
        pc = registers[PC]
        if 0xCF08 <= pc < 0xCF0B:
            self.alias_entries.add(pc)
        if pc not in (0xC070, 0xC992):
            return
        # В двух диспетчерах проверяется страница, реально видимая при JP (HL).
        high_page = bytes(memory.banks[0][0x1000:0x1100])
        assert high_page == self.high_page
        target = registers[H] * 256 + registers[L]
        assert target >> 8 != 0xCF
        self.dispatches[f'{pc:04X}'] += 1
        self.targets.add(target)


class RelocatedOperandProbe:
    def __init__(self, relocated):
        self.relocated = relocated
        self.copied = set()
        self.operand_seen = False

    def observe(self, memory, registers):
        pc = registers[PC]
        if pc == 0x420A and memory[pc] == 0xED and memory[pc + 1] == 0xB0:
            target = registers[D] * 256 + registers[E]
            if target == 0x697D or 0x7B48 <= target < 0x7B58:
                source = registers[H] * 256 + registers[L]
                assert source == target + 0x23D and memory[source] == self.relocated[target]
                self.copied.add(target)
        if pc == 0x6BB9:
            # Проверка кода в той же RAM после переноса, байт 6BBA теперь принадлежит RR H.
            assert memory[0x6BB9] == 0xCB and memory[0x6BBA] == 0x1C
            assert memory[0x697D] == 0x7B
            self.operand_seen = True

    def result(self):
        assert self.copied == {0x697D, *range(0x7B48, 0x7B58)} and self.operand_seen
        return dict(ldir_copies_checked=len(self.copied), copied_byte_destination=0x697D,
                    runtime_operand_address=0x6BBA, runtime_operand_value=0x1C,
                    relocated_disk_byte=0x7B, runtime_operand_pc=0x6BB9)


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


class RenderTableMemory(Memory):
    recording = False

    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.table_writes = Counter()

    def __setitem__(self, address, value):
        if self.recording and self.o7ffd & 7 == 0 and (
                0xD000 <= address < 0xD100 or 0xCF08 <= address < 0xCF0B):
            self.table_writes[address] += 1
        super().__setitem__(address, value)


class ControlSourceMemory(Memory):
    watch_writes = False

    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.control_writes = []

    def __setitem__(self, address, value):
        if self.watch_writes and self.o7ffd & 7 == 1 and (
                0xC600 <= address < 0xCA00 or 0xDADE <= address < 0xDB5D):
            self.control_writes.append((address, value))
        super().__setitem__(address, value)


def check_nonempty_flight_render(high_page):
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    memory = RenderTableMemory()
    for address, value in enumerate(source, 0x6000):
        memory[address] = value
    sim = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A},
                    config={'fast_ldir': False, 'fast_djnz': False})
    clip = ClipDispatchProbe(high_page)
    counts = Counter()
    models = set()
    records_start = 0xA100
    marker = 0xA1C0
    snapshot = None
    entry_sp = None

    def write_bytes(address, data):
        for offset, value in enumerate(data):
            memory[address + offset] = value

    def observe(frame, memory, registers):
        nonlocal snapshot, entry_sp
        pc = registers[PC]
        clip.observe(memory, registers)
        if pc == 0xE020 and memory.o7ffd & 7 == 0:
            assert snapshot is None
            assert memory[registers[SP]] == 0x80 and memory[registers[SP] + 1] == 0xA8
            entry_sp = registers[SP]
            snapshot = bytes(memory[address] for address in range(records_start, marker + 2))
            # Подготовка трёх входных записей только на время настоящего вызова рисователя.
            for index, depth in enumerate((0x2000, 0x3000, 0x2200)):
                model = (frame * 8 + index * 4) & 0xFE
                data = pack('<HHHBBBB', depth // 2 - 64, 0, depth, model, 0, 0, 0)
                write_bytes(records_start + index * 64, data + bytes(64 - len(data)))
                models.add(model)
            write_bytes(marker, b'\xFF\x80')
            memory.recording = True
            counts['render_entries'] += 1
        if snapshot is None:
            return
        assert not registers[IFF], (frame, pc, registers[SP])
        if pc == 0xA880:
            assert registers[SP] == entry_sp + 2 and memory.o7ffd == 0x10
            memory.recording = False
            write_bytes(records_start, snapshot)
            snapshot = None
            counts['render_returns'] += 1
            return
        counts['render_instructions_with_iff_clear'] += 1
        if pc == 0xE4B1:
            counts['queue_nodes'] += 1
        elif pc == 0xE4FA:
            counts['clipped_nodes'] += 1

    flight = trace_flight(['--frames', '18'], boot_simulator=sim, save_reports=False,
                          instruction_observer=observe)
    assert flight['frame_entries'] == 18 and flight['reason'] == 'requested_frame_entries'
    assert counts['render_entries'] == counts['render_returns'] == 17 and snapshot is None
    assert counts['queue_nodes'] == counts['clipped_nodes'] == 51
    assert clip.dispatches and not clip.alias_entries and not memory.table_writes
    assert 24 in {entry.get('slot') for entry in flight['loads']}
    return dict(counts, fixture_model_offsets=sorted(models), dispatches=dict(clip.dispatches),
                targets=sorted(clip.targets), table_writes=0, clip_alias_entries=0,
                all_render_instructions_executed_with_iff_clear=True,
                fixture_records_restored_after_render=True)


def check_station_settings(keys, targets):
    station = payload(4)
    labels = station[0x7F3C:0x80E3].split(b'\r')[1:]
    assert labels[0].decode('cp866') == 'Мышка'
    assert station[0x39C8:0x39CA] == bytes((0x81, 0))
    rows = []
    for index, ((row, mask), target) in enumerate(zip(keys, targets), start=1):
        address = 0x99C8 + 2 * index
        offset = address - 0x6000
        assert station[offset:offset + 2] == bytes((row, mask))
        assert address - 0x983B == 0x9D4C + 2 * (index - 1) - 0x9BBD
        rows.append(dict(station_row=index, text=labels[index].decode('cp866'), station_address=address,
                         action_address=0x9D4C + 2 * (index - 1), row_select=row, mask=mask, target=target))
    assert [(rows[index - 1]['text'], rows[index - 1]['target']) for index in (8, 9, 10, 25, 27)] == [
        ('Набор скорости', 0x7680), ('Сброс скорости', 0x76A3), ('Бортовой компьютер', 0xACAB),
        ('Включение неона', 0x704B), ('Защита от косм.излучений', 0xC0C9)]
    return rows


def main():
    original = flat_action()
    high_page = bytes(original[0xD000:0xD100])
    keys = [tuple(original[address:address + 2]) for address in range(0x9D4C, 0x9D82, 2)]
    targets = [original[address] | original[address + 1] << 8 for address in range(0x7017, 0x704D, 2)]
    assert len(keys) == len(targets) == 27 and len(set(keys)) == 26
    assert keys[0] == keys[-1] == (0xFD, 0x02) and targets[-1] == 0xC0C9
    settings = check_station_settings(keys, targets)
    cases = []
    clip_cases = []
    relocations = RelocatedOperandProbe(original)
    action_boot = payload(17)
    assert len(action_boot) == 0xA000
    source_window = payload(22)[0x600:0xA00]
    temporary_template = payload(23)[:127]
    for key in dict.fromkeys(keys):
        probe = None
        clip = ClipDispatchProbe(high_page)
        memory = ControlSourceMemory()
        for address, value in enumerate(action_boot, 0x6000):
            memory[address] = value
        sim = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A},
                        config={'fast_ldir': False, 'fast_djnz': False})
        temporary_entries = set()

        def ports(memory):
            nonlocal probe
            probe = KeyProbe(memory, key)
            return probe

        def observe(frame, memory, registers):
            probe.observe(frame, memory, registers)
            clip.observe(memory, registers)
            relocations.observe(memory, registers)
            pc = registers[PC]
            if (memory.o7ffd & 7 == 1 and 0xDADE <= pc < 0xDB5D) or 0x5DA0 <= pc < 0x5EDB:
                temporary_entries.add((memory.o7ffd & 7, pc))
            if pc == 0xA85E:
                assert bytes(memory.banks[1][0x600:0xA00]) == source_window
                assert bytes(memory.banks[1][0x1ADE:0x1B5D]) == temporary_template
                memory.watch_writes = True

        flight = trace_flight(['--frames', '2'], boot_simulator=sim, ports_factory=ports, instruction_observer=observe,
                              save_reports=False)
        expected = [(index, 0, targets[index]) for index, pair in enumerate(keys) if pair == key]
        expected_reads = [(row * 256 + 0xFE, 255 ^ key[1] if row == key[0] else 255) for row, _ in keys]
        assert probe.reads == expected_reads
        assert probe.handlers == expected, (key, probe.handlers, expected)
        assert probe.finished and probe.returns == len(expected) and probe.pending_target is None
        assert flight['frame_entries'] == 2 and flight['reason'] == 'requested_frame_entries'
        assert not probe.special_entries
        assert not clip.alias_entries
        assert not temporary_entries and not memory.control_writes
        clip_cases.append(dict(row=key[0], mask=key[1], dispatches=dict(clip.dispatches),
                               targets=sorted(clip.targets)))
        cases.append(dict(row=key[0], mask=key[1], read_count=len(probe.reads), handlers=probe.handlers,
                          keyboard_frame_returns=probe.returns, decay_reached=probe.finished,
                          next_flight_frame_reached=flight['frame_entries'] == 2,
                          stop_reason=flight['reason'], watched_entries=sorted(probe.special_entries)))
    result = dict(passed=True, total_cases=len(cases), matrix_steps_reached=sum(len(case['handlers']) for case in cases),
                  cases=cases, irq_scheduled_by_flight_model=True, trdos_stub=True,
                  station_settings_rows=settings,
                  temporary_module_watch=dict(bank=1, font=[0xC600, 0xC870], viewport_code=[0xC870, 0xCA00],
                                              template=[0xDADE, 0xDB5D],
                                              candidate_fixed_pc_range=[0x5DA0, 0x5EDB],
                                              both_frame_entries_match_disk=True, bank_writes_between_frames=0,
                                              temporary_pc_entries_in_profiles=0),
                  disk_byte_and_runtime_operand=relocations.result(),
                  continuous_key_hold_verified=False, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/FlightKeyPathsVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    idle = ClipDispatchProbe(high_page)
    flight = trace_flight(['--frames', '65'], save_reports=False,
                          instruction_observer=lambda frame, memory, registers: idle.observe(memory, registers))
    assert flight['frame_entries'] == 65 and flight['reason'] == 'requested_frame_entries'
    assert not idle.alias_entries
    populated_render = check_nonempty_flight_render(high_page)
    clip_result = dict(passed=True, idle_frames=65, idle_dispatches=dict(idle.dispatches),
                       idle_targets=sorted(idle.targets), single_key_profiles=clip_cases,
                       populated_flight_render=populated_render,
                       bank=0, watched_entry_bytes=[0xCF08, 0xCF09, 0xCF0A],
                       observed_clip_dispatches=sum(idle.dispatches.values()) +
                           sum(sum(case['dispatches'].values()) for case in clip_cases) +
                           sum(populated_render['dispatches'].values()),
                       alias_execution_seen=False, all_runtime_profiles_proved=False,
                       trdos_stub=True, assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ActionClipAliasFlightPathsVerification.json'
    path.write_text(json.dumps(clip_result, indent=2) + '\n', encoding='utf-8')
    print(f"{len(cases)} проходов матрицы, {result['matrix_steps_reached']} вызовов и возвратов")


if __name__ == '__main__':
    main()
