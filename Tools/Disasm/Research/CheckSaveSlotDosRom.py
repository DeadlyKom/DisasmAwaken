"""Запись и чтение SAVE оригинальным ПЗУ через контроллер в памяти."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckAwakenBasicRun import model_rom_context
from CheckBasicIntroDiskRead import FileReadPorts
from CheckControlsLegacySectorRead import run_with_rom
from CheckSaveSlotProtocol import MODES
from CheckScreenUpdate import PortTrace
from CheckStationFlightCycle import DISK, ENTRIES, ROOT, payload
from ProbeShipPreviewCallbacks import Fixture, make_context, put
from skoolkit.simulator import Simulator
from skoolkit.simutils import A, B, C, D, E, H, I, IFF, IM, L, PC, SP


class SaveSlotPorts(FileReadPorts):
    def __init__(self, memory, disk):
        super().__init__(0)
        self.memory = memory
        self.disk = disk
        self.pending_offset = None
        self.output = bytearray()
        self.written_sectors = []

    def write_port(self, registers, port, value, offset):
        if registers[PC] >= 0x4000 and port == 0x7FFD:
            self.memory.out7ffd(value)
            return
        low = port & 0xFF
        if low == 0x1F and value == 0xA0:
            assert self.pending_offset is None
            track = self.track * 2 + self.side
            self.pending_offset = (track * 16 + self.sector - 1) * 256
            self.output.clear()
            self.written_sectors.append((track, self.sector))
        elif low == 0x7F and self.pending_offset is not None:
            self.output.append(value)
            if len(self.output) == 256:
                start = self.pending_offset
                self.disk[start:start + 256] = self.output
                self.pending_offset = None
        super().write_port(registers, port, value, offset)

    def read_port(self, registers, port, offset=0):
        low = port & 0xFF
        if self.commands[-1:] == [0xA0]:
            if low == 0xFF:
                return 0x40 if self.pending_offset is not None else 0x80
            if low == 0x1F:
                return 0
        return super().read_port(registers, port, offset)


class SlotCPU(Simulator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dos_calls = []
        self.transfer_requests = []
        self.rom_interrupt_enablers = set()

    def run(self, *args, **kwargs):
        registers = self.registers
        pc, iff = registers[PC], registers[IFF]
        single_step = not args and not kwargs
        if single_step and pc == 0x3D13:
            self.dos_calls.append((registers[C], registers[A]))
            if registers[C] in (5, 6):
                self.transfer_requests.append(dict(
                    track=registers[D], sector=registers[E], count=registers[B],
                    buffer=registers[H] * 256 + registers[L],
                    descriptor=bytes(self.memory[0x5CDD:0x5CED]).hex()))
        result = super().run(*args, **kwargs)
        if single_step and pc < 0x4000 and not iff and registers[IFF]:
            assert self.memory[pc] == 0xFB
            self.rom_interrupt_enablers.add(pc)
        return result


def prepare_slot(banks, sysvars, mode, row, disk, block):
    entry, _, draw, key, hover, _, _ = mode
    fixture = Fixture(banks, cpu_type=SlotCPU)
    memory, cpu = fixture.memory, fixture.sim
    registers = cpu.registers
    record = 0xF0FD + 16 * key
    put(memory, record, (0, 0, 12, 8, 6, memory[record + 5]))
    put(memory, draw + 1, (key, 0))
    put(memory, 0x9CA6, (0xDE, 0xF3))
    put(memory, 0xF3DE, (*draw.to_bytes(2, 'little'), 1, 1))
    put(memory, 0x5C00, sysvars)
    put(memory, 0x983B, block)
    memory[hover] = row
    memory[0x9E78], memory[0xCA20], memory[0x9A82] = 0, 6, 0xA7
    memory[0x5D06] = 9
    registers[6:8] = [draw >> 8, draw & 255]
    registers[4:6] = [0, key]
    registers[8:12] = [record >> 8, record & 255, 0x13, 0x57]
    registers[A], registers[I], registers[PC] = 1, 0x80, entry
    ports = SaveSlotPorts(memory, disk)
    cpu.set_tracer(ports)
    return cpu, ports


def run_slot(cpu, basic, dos):
    memory = cpu.memory

    def set_rom(image):
        memory.memory[0] = image

    set_rom(basic)
    run_with_rom(cpu, basic, dos, set_rom, 0x3FFF, step_limit=250000)


def transfer(banks, sysvars, basic, dos, mode, row, disk, block, slot):
    cpu, ports = prepare_slot(banks, sysvars, mode, row, disk, block)
    memory, registers, command = cpu.memory, cpu.registers, mode[-1]
    try:
        run_slot(cpu, basic, dos)
    except (AssertionError, IndexError) as error:
        raise AssertionError((row, command, hex(registers[PC]), ports.commands[-20:],
                              ports.attempts[-10:], ports.written_sectors)) from error
    assert [number for number, _ in cpu.dos_calls] == [0x0A, 0x08, command]
    assert cpu.dos_calls[1] == (0x08, slot)
    assert (registers[SP], registers[I], registers[IM], memory.o7ffd) == (0x8000, 0x80, 2, 0x10)
    assert bytes(memory[0x7530:0x7539]) == f'SAVE{row}   s'.encode('ascii')
    assert bytes(memory[0xF3DE:0xF3E0]) == b'\x01\x01' and memory[0x9A82] == 0
    assert registers[IFF] == 1 and cpu.rom_interrupt_enablers == {0x3EFB, 0x3F32}
    descriptor = bytes(disk[slot * 16:slot * 16 + 16])
    assert cpu.transfer_requests == [dict(track=descriptor[15], sector=descriptor[14],
                                          count=2, buffer=0x983B, descriptor=descriptor.hex())]
    return bytes(memory[0x983B:0x9A3B]), ports


def check_missing_slot(banks, sysvars, basic, dos, row, *, deleted_slot=None):
    original = bytearray(DISK)
    if deleted_slot is not None:
        original[deleted_slot * 16] = 1
    pattern = bytes((index * 37 + row * 11 + 0x80) & 255 for index in range(512))
    results = []
    for mode in MODES:
        command = mode[-1]
        disk = original.copy()
        cpu, ports = prepare_slot(banks, sysvars, mode, row, disk, pattern)
        run_slot(cpu, basic, dos)
        memory, registers = cpu.memory, cpu.registers
        assert [number for number, _ in cpu.dos_calls] == [0x0A, 0x08, command]
        assert cpu.dos_calls[1] == (0x08, 0xFF)
        assert len(cpu.transfer_requests) == 1
        request = cpu.transfer_requests[0]
        assert request == dict(track=0, sector=0, count=2, buffer=0x983B, descriptor='00' * 16)
        assert (0, 16) in ports.attempts
        assert (registers[SP], registers[I], registers[IM], registers[IFF]) == (0x8000, 0x80, 2, 1)
        assert bytes(memory[0xF3DE:0xF3E0]) == b'\x01\x01' and memory[0x9A82] == 0
        if command == 6:
            assert ports.written_sectors == [(0, 1), (0, 2)] and ports.pending_offset is None
            assert disk[:512] == pattern and disk[512:] == original[512:]
            assert bytes(memory[0x983B:0x9A3B]) == pattern
        else:
            assert ports.attempts[-2:] == [(0, 1), (0, 2)] and not ports.written_sectors
            assert disk == original and bytes(memory[0x983B:0x9A3B]) == original[:512]
        results.append(dict(command=command, descriptor_index=0xFF, transfer_request=request,
                            actual_sectors=[(0, 1), (0, 2)], final_iff=registers[IFF]))
    return dict(row=row, deleted_slot=deleted_slot, transfers=results)


def check_panel_selection(banks, sysvars, basic, dos):
    # Пять подписей начинаются на третьем пикселе относительно верхней границы.
    entries = {entry['name']: entry for entry in ENTRIES.values()}
    station_state = payload(4)[0x383B:0x3A3B]
    profiles = []
    redraws = []
    for mode, hover_entry in zip(MODES, (0x741E, 0x74A7), strict=True):
        action, _, _, _, hover_operand, _, command = mode
        for pixel in range(40):
            line = pixel // 8
            entry = entries[f'SAVE{line}']
            disk = bytearray(DISK)
            cpu, ports = prepare_slot(banks, sysvars, mode, 0xFF, disk, station_state)
            memory, registers = cpu.memory, cpu.registers
            action_registers = registers[:]
            put(memory, 0x6307, (32, 3 + pixel))
            cpu.set_tracer(PortTrace(cpu))
            cpu.run(start=hover_entry, stop=0x3FFF)
            assert registers[SP] == 0x8000 and memory[hover_operand] == line
            assert not cpu.dos_calls and memory.o7ffd == 0x10

            # Действие получает свою рамку диспетчера и уже вычисленный байт строки.
            registers[:] = action_registers
            assert registers[PC] == action
            put(memory, registers[SP], b'\xFF\x3F')
            cpu.set_tracer(ports)
            run_slot(cpu, basic, dos)
            assert registers[PC] == 0x3FFF and registers[SP] == 0x8000
            assert bytes(memory[0x7530:0x7539]) == f'SAVE{line}   s'.encode('ascii')
            assert [number for number, _ in cpu.dos_calls] == [0x0A, 0x08, command]
            assert cpu.dos_calls[1] == (0x08, entry['slot']) and memory[0x9A82] == 0
            offset = entry['offset']
            if command == 5:
                assert bytes(memory[0x983B:0x9A3B]) == payload(entry['slot']) and disk == DISK
            else:
                assert disk == DISK[:offset] + station_state + DISK[offset + 512:]
            if pixel % 8 == 0:
                profiles.append(dict(command=command, printed_position=line + 1, hover_value=line,
                                     file=entry['name'], directory_slot=entry['slot']))
                if command == 5:
                    loaded = payload(entry['slot'])
                    assert bytes(memory[0xF3DE:0xF3E0]) == b'\x01\x01'
                    assert loaded[0x187:0x18D] == bytes.fromhex('00 00 05 00 00 00')
                    memory[0x9D48] = 0xA5
                    cpu.run(start=0x9A81, stop=0x9A87)
                    assert registers[SP] == 0x8000 and memory.o7ffd == 0x10
                    assert memory[0x9A82] == 1 and memory[0x9D48] == 0x28
                    assert bytes(memory[0x983B:0x9A3B]) == loaded and disk == DISK
                    redraws.append(dict(file=entry['name'], event_enabled=1, item_attribute=0x28))
    return dict(executions=80, stable_pointer_y=True, input_geometry_prepared=True,
                action_selector_prepared=1, profiles=profiles,
                rebuild_before_next_halt=dict(entry=0x9A81, halt=0x9A87, empty_draw_list=True,
                                              loaded_state_unchanged=True, profiles=redraws))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    basic, dos, sysvars = model_rom_context(args.dos_rom)
    _, _, banks = make_context()
    profiles = []
    for row in range(6):
        entry = next(entry for entry in ENTRIES.values() if entry['name'] == f'SAVE{row}')
        offset = entry['offset']
        sectors = [divmod(offset // 256 + index, 16) for index in range(2)]
        sectors = [(track, sector + 1) for track, sector in sectors]
        disk = bytearray(DISK)
        pattern = bytes((index * 37 + row * 11 + 0x80) & 255 for index in range(512))
        slot = entry['slot']
        data, reads = transfer(banks, sysvars, basic, dos, MODES[1], row, disk, pattern, slot)
        assert data == payload(entry['slot']) and bytes(disk) == DISK
        assert reads.attempts[-2:] == sectors and not reads.written_sectors
        data, writes = transfer(banks, sysvars, basic, dos, MODES[0], row, disk, pattern, slot)
        assert data == pattern and bytes(disk) == DISK[:offset] + pattern + DISK[offset + 512:]
        assert writes.written_sectors == sectors and writes.pending_offset is None
        data, reload = transfer(banks, sysvars, basic, dos, MODES[1], row, disk, bytes(512), slot)
        assert data == pattern and reload.attempts[-2:] == sectors and not reload.written_sectors
        profiles.append(dict(row=row, slot=slot, sectors=sectors, bytes_transferred=512, final_iff=1))
    save2 = next(entry['slot'] for entry in ENTRIES.values() if entry['name'] == 'SAVE2')
    missing = [check_missing_slot(banks, sysvars, basic, dos, 0xFF),
               check_missing_slot(banks, sysvars, basic, dos, 2, deleted_slot=save2)]
    panel_selection = check_panel_selection(banks, sysvars, basic, dos)
    report = dict(passed=True, original_disk_sha256=sha256(DISK).hexdigest(),
                  dos_rom_sha256=sha256(dos).hexdigest(), basic_rom_sha256=sha256(basic).hexdigest(),
                  profiles=profiles, missing_file_profiles=missing, panel_selection=panel_selection,
                  rom_interrupt_enablers=[0x3EFB, 0x3F32], real_dos_entry=True,
                  controller_model=True, writes_in_memory_only=True,
                  original_files_unchanged=True, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/SaveSlotDosRomVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
