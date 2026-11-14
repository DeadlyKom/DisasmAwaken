"""Покупка X артефакта, финальная панель и загрузка FINALF с оригинальным ПЗУ."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckAwakenBasicRun import BasicReadPorts, model_rom_context
from CheckControlsLegacySectorRead import run_with_rom
from CheckFinalCycle import InputPorts
from CheckFinalExit import KeyboardTrace
from CheckStationFlightCycle import DISK, ENTRIES, payload, run_to
from CheckWorldSignature import signature
from ProbeShipPreviewCallbacks import Fixture, ROOT, make_context, put
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import H, I, IFF, IM, L, PC, SP


INDEX = 18
FIRST, SECOND = 0x4B37, 0x4E25
PRICE = 25000


class FinalSectorMemory(SliceableMemory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.watching_final_sector = False
        self.final_sector_buffer = None
        self.final_sector_writes = []
        self.final_sector_tail_reads = []

    def bind_registers(self, registers):
        self.registers = registers

    def __getitem__(self, address):
        if self.watching_final_sector and isinstance(address, int) and 0xAAA9 <= address < 0xAB00:
            self.final_sector_tail_reads.append((self.registers[PC], address))
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.watching_final_sector and isinstance(address, int) and 0xAA00 <= address < 0xAB00:
            if not self.final_sector_writes:
                self.final_sector_buffer = bytes(self[0x5D25:0x5E25])
            self.final_sector_writes.append((self.registers[PC], address, value))
        super().__setitem__(address, value)


class FinalCPU(Simulator):
    def __init__(self, memory):
        super().__init__(memory, config={'frame_duration': 70908, 'int_active': 36})
        self.artifact_writes = []

    def run(self, *args, **kwargs):
        registers = self.registers
        if (not args and not kwargs and registers[PC] == 0xC6E2
                and self.memory.o7ffd & 7 == 6 and registers[H] * 256 + registers[L] == 0x98A0):
            previous = self.memory[0x98A0]
            assert self.memory[0xC6E2] == 0x77
            result = super().run(*args, **kwargs)
            self.artifact_writes.append((previous, self.memory[0x98A0]))
            return result
        return super().run(*args, **kwargs)


def check_sources():
    station = payload(4)
    names = station[0xEE57 - 0x6000:0xF066 - 0x6000].split(b'\r')[1:]
    assert names[INDEX].decode('cp866') == 'X артефакт'
    assert 0x988E + INDEX == 0x98A0 and station[0x38A0] == 0xFF
    assert station[0x3592 + 2 * INDEX:0x3594 + 2 * INDEX] == PRICE.to_bytes(2, 'little')
    assert station[0x35F0 + 2 * INDEX:0x35F2 + 2 * INDEX] == bytes((15, 2))
    assert station[0x3400 + 4 * INDEX:0x3404 + 4 * INDEX] == bytes((5, 6, 4, 255))


def prepare_purchase(fixture, sysvars, variant):
    memory, cpu = fixture.memory, fixture.sim
    put(memory, 0x5C00, sysvars)
    memory[0x5D06] = 9
    memory.out7ffd(0x16)
    memory[0x6306] = 0x16
    memory[0x983A], memory[0x7217], memory[0x71B9] = 5, INDEX, 0
    memory[0x9849], memory[0x984A] = 0, 255
    starting_money = 0x7000
    put(memory, 0x984E, starting_money.to_bytes(2, 'little'))
    put(memory, 0x983F, FIRST.to_bytes(2, 'little') + SECOND.to_bytes(2, 'little') + bytes((variant,)))
    assert signature(FIRST, SECOND, variant)['size'] >= 15 and memory[0x98A0] == 0xFF
    cpu.registers[:] = fixture.initial
    cpu.registers[PC] = 0xC000
    run_to(cpu, 0x3FFF)
    assert memory[0x98A0] == 0xFE and cpu.artifact_writes == [(0xFF, 0xFE)]
    assert int.from_bytes(memory[0x984E:0x9850], 'little') == starting_money - PRICE


def check_sale(fixture):
    memory, cpu = fixture.memory, fixture.sim
    assert memory.o7ffd == 0x16
    memory[0x983A] = 6
    put(memory, 0x7FFE, (255, 63))
    cpu.registers[:] = fixture.initial
    cpu.registers[PC] = 0xC000
    run_to(cpu, 0x3FFF)
    assert memory[0x98A0] == 0xFF and cpu.artifact_writes == [(0xFF, 0xFE), (0xFE, 0xFF)]
    assert int.from_bytes(memory[0x984E:0x9850], 'little') == 0x7000


def play_final(fixture, basic, dos):
    memory, cpu = fixture.memory, fixture.sim
    memory.out7ffd(0x10)
    memory[0x6306] = 0x10
    put(memory, 0x6DD5, (24, 0))
    put(memory, 0xF0FD + 16 * 24, (4, 3, 24, 18, 0, 14))
    put(memory, 0x7FFE, (255, 63))
    cpu.registers[:] = fixture.initial
    registers = cpu.registers
    registers[PC] = 0x6DD4
    run_to(cpu, 0xC089)
    assert memory[0xC089] == 0x76
    fixture.wake(0xC089)
    keyboard = KeyboardTrace(cpu, [0xFF, 0xBE])
    cpu.set_tracer(keyboard)
    run_to(cpu, 0x3D13)
    assert not keyboard.values and memory.o7ffd == 0x1F
    assert bytes(memory[0x5CDD:0x5CE6]) == b'FINALF  C'
    assert (registers[SP], registers[IFF]) == (0x5FFD, 0)

    # Префикс последнего сектора должен затереть метку AAA9, хвост должен сохранить заполнение.
    tail_canary = bytes(range(0x57))
    put(memory, 0xAAA9, tail_canary)
    memory.watching_final_sector = True
    ports = BasicReadPorts(memory)
    cpu.set_tracer(ports)

    def set_rom(image):
        memory.memory[0] = image

    set_rom(basic)
    run_with_rom(cpu, basic, dos, set_rom, 0x6000)
    raw = payload(29)
    assert bytes(memory[0x6000:0x6000 + len(raw)]) == raw
    assert registers[SP] == 0x5FFF and memory.o7ffd == 0x1F
    full, partial = divmod(len(raw), 256)
    first = ENTRIES[29]['offset'] // 256
    assert (full, partial) == (74, 170)
    targets = [0x6000 + 256 * i for i in range(full)] + [0x5D25]
    expected = [(divmod(index, 16), address) for index, address in enumerate(targets, first)]
    data_reads = [(sector, address) for sector, address in ports.read_destinations if sector[0]]
    assert data_reads == [((track, sector + 1), address) for (track, sector), address in expected]
    last_disk_offset = (first + full) * 256
    last_sector = DISK[last_disk_offset:last_disk_offset + 256]
    assert last_sector[:partial] == raw[-partial:] and last_sector[partial - 1:] == b'\xA3' * 87
    assert memory.final_sector_buffer == last_sector
    assert bytes(memory[0xAAA9:0xAB00]) == b'\xA3' + tail_canary[1:]
    writes = tuple(memory.final_sector_writes)
    assert [(address, value) for _, address, value in writes] == [
        (0xAA00 + index, value) for index, value in enumerate(last_sector[:partial])
    ]
    writers = {pc for pc, _, _ in writes}
    assert len(writers) == 1
    (writer,) = writers
    assert dos[writer:writer + 2] == b'\xED\xB0'
    assert not memory.final_sector_tail_reads

    # Подтверждение обоих растров и исходной ветви Space после реальной дисковой загрузки.
    final_ports = InputPorts(cpu, None, True)
    cpu.set_tracer(final_ports)
    cpu.run(0x6000, 0x607A, interrupts=True)
    assert (registers[SP], registers[I], registers[IM]) == (0x5FFF, 0xBE, 2)
    bitmaps = [raw[0x2A9 + i * 0x1800:0x2A9 + (i + 1) * 0x1800] for i in range(3)]
    for bank, bitmap in zip((7, 0, 1), bitmaps):
        assert bytes(memory.banks[bank][:0x1800]) == bitmap
    cpu.run(0x607A, 0x60AC, interrupts=True)
    assert bytes(memory.banks[5][:0x1B00]) == bitmaps[1] + b'\x90' * 768
    cpu.run(0x60AC, 0x6111, interrupts=True)
    assert bytes(memory.banks[5][:0x1B00]) == bitmaps[2] + b'\xA0' * 768
    cpu.run(0x6111, 0x616B, interrupts=True)
    assert registers[SP] == 0x5FFF and registers[IM] == 0 and not registers[IFF]
    assert bytes(memory.banks[7][0x1800:0x1B00]) == bytes(768)
    assert tuple(memory.final_sector_writes) == writes and not memory.final_sector_tail_reads
    return dict(catalogue_reads=[sector for sector in ports.attempts if not sector[0]],
                data_sectors=len(data_reads), last_sector=data_reads[-1],
                last_sector_copy=dict(disk_offset=last_disk_offset, writer=writer,
                                      destination=0xAA00, copied_bytes=partial,
                                      last_logical_byte=[0xAAA9, last_sector[partial - 1]],
                                      untouched_destination_bytes=256 - partial,
                                      later_tail_reads=0, later_last_sector_writes=0),
                logical_file_bytes=len(raw), returned_entry=0x6000, halted_pc=registers[PC],
                rendered_bitmaps=[sha256(bitmap).hexdigest() for bitmap in bitmaps[1:]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    check_sources()
    basic, dos, sysvars = model_rom_context(args.dos_rom)
    _, _, banks = make_context()
    lang, music = payload(5), payload(10)
    banks[6][:len(lang)] = lang
    banks[3][0x1B00:0x1B00 + len(music)] = music
    profiles = []
    for variant in (0, 5):
        fixture = Fixture(banks, memory_type=FinalSectorMemory, cpu_type=FinalCPU)
        prepare_purchase(fixture, sysvars, variant)
        final = play_final(fixture, basic, dos)
        profiles.append(dict(variant=variant, key_size=signature(FIRST, SECOND, variant)['size'],
                             bought_equipment_index=INDEX, purchase_cost=PRICE,
                             item_code_before=0xFF, item_code_after=0xFE, **final))
    fixture = Fixture(banks, cpu_type=FinalCPU)
    prepare_purchase(fixture, sysvars, 0)
    check_sale(fixture)
    report = dict(passed=True, disk_sha256=sha256(DISK).hexdigest(), dos_rom_sha256=sha256(dos).hexdigest(),
                  profiles=profiles, shop_writer=dict(bank=6, pc=0xC6E2, address=0x98A0,
                                                      buy=[0xFF, 0xFE], sell=[0xFE, 0xFF]),
                  native_execution=False, assembly_executed=False,
                  original_dos_executed=True, controller_model=True, station_purchase_context_prepared=True)
    (ROOT / 'Tools/Disasm/Reports/ArtifactFinalPathVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
