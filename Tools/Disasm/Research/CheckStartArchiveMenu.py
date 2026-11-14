"""Меню Start/Options из внекаталожных секторов и его вызов START.C."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckAwakenBasicRun import BasicReadPorts, model_rom_context
from CheckBankStripArchiveConsumer import ArchivePorts, ExtendedMemory
from CheckControlsLegacySectorRead import run_with_rom
from CheckStationFlightCycle import DISK, ENTRIES, put, run_to
from TraceFlight import A, C, H, IFF, L, PC, SP, T, ROOT, Simulator
from skoolkit.simutils import I, IM


DISK_OFFSET = 0x87400
MENU_ENTRY = 0x6000
MENU_HALT = 0x6029
FIRST_SCREEN = 0x63DD
SECOND_SCREEN = 0x7EDD
SCREEN_SIZE = 0x1B00
FONT = 0x99DD
FONT_BYTES = 96 * 8
ADVANCE = (0xFDFE, 1)
ENTER = (0xBFFE, 1)


class PagingPorts:
    def __init__(self, memory):
        self.memory = memory
        self.writes = []

    def write_port(self, registers, port, value, offset):
        self.writes.append((port, value))
        if port == 0x7FFD:
            self.memory.out7ffd(value)


def check_mode_readers(basic, dos, mode):
    readers = (
        ('scene1', 0x8B100, 0x4000, 0x1100, 0x4024, 0x4FB6, 0x4FB4, (0x4FB8, 0x4FCF, 0x4FE5)),
        ('bank_strips', 0x8C200, 0x6000, 0x6000, 0x6018, 0x6359, 0x6358, (0x63AE, 0x635B, 0x637E)),
    )
    results = []
    for name, offset, entry, size, stop, operand, selector, targets in readers:
        memory = ExtendedMemory()
        put(memory, entry, DISK[offset:offset + size])
        if name == 'bank_strips':
            put(memory, 0xC000, DISK[0x92200:0x96200])
        # Подстановка измеренного байта, поскольку START.C не найден в каталоге.
        memory[0x5F5E] = mode
        cpu = Simulator(memory, {'PC': entry})
        memory.cpu = cpu
        ports = PagingPorts(memory)
        cpu.set_tracer(ports)
        registers = cpu.registers
        run_to(cpu, stop)
        target = int.from_bytes(memory[operand:operand + 2], 'little')
        assert target == targets[mode]
        if name == 'bank_strips':
            memory[0x6641] = 1

        def set_rom(image):
            memory.memory[0] = image

        profiles = []
        for page in range(8, 14):
            registers[PC] = selector
            registers[SP] = 0x5FFE
            registers[A] = page
            put(memory, 0x5FFE, b'\xFF\x5B')
            ports.writes.clear()
            set_rom(basic)
            run_with_rom(cpu, basic, dos, set_rom, 0x5BFF)
            low_page = 0x18 | (page & 7)
            expected = (
                [(0x7FFD, low_page | 0x40)],
                [(0x1FFD, 0x10), (0x7FFD, low_page)],
                [(0x7FFD, low_page), (0xFFF7, (page ^ 0xFF) | 0xC0)],
            )[mode]
            assert ports.writes == expected and registers[SP] == 0x6000
            profiles.append(dict(page_code=page, writes=list(ports.writes)))
        results.append(dict(name=name, patched_operand=operand, target=target, selector_profiles=profiles))
    return results


def check_menu(basic, dos, system, mode, *, handoff=None, bootstrap=None, memory=None):
    if memory is None:
        memory = ExtendedMemory()
    size = FONT + FONT_BYTES - MENU_ENTRY
    raw = DISK[DISK_OFFSET:DISK_OFFSET + size]
    font = raw[FONT - MENU_ENTRY:]
    assert len(font) == FONT_BYTES and any(font)
    if bootstrap is None:
        put(memory, MENU_ENTRY, raw)
        put(memory, 0x5C00, system)
        cpu = Simulator(memory, {'PC': MENU_ENTRY, 'SP': 0x5FFF, 'IY': 0x5C3A},
                        config={'fast_ldir': False, 'fast_djnz': False})
    else:
        cpu = bootstrap(memory)
        assert cpu.registers[PC] == MENU_ENTRY and bytes(memory[MENU_ENTRY:MENU_ENTRY + size]) == raw
    memory.cpu = cpu
    ports = ArchivePorts(memory)
    cpu.set_tracer(ports)
    registers = cpu.registers
    # Снимок обеих физических копий до вывода пунктов меню.
    run_to(cpu, 0x601D)
    screens = {}
    for bank, address in ((5, FIRST_SCREEN), (7, SECOND_SCREEN)):
        begin = address - MENU_ENTRY
        assert bytes(memory.banks[bank][:SCREEN_SIZE]) == raw[begin:begin + SCREEN_SIZE]
        screens[bank] = bytearray(raw[begin:begin + SCREEN_SIZE])
    run_to(cpu, 0x6023)
    # Независимое наложение исходных восьми строк каждого глифа до подсветки.
    for bank, screen in screens.items():
        for start, label in ((0x08EE, b'Start'), (0x100E, b'Options')):
            for column, code in enumerate(label):
                for y in range(8):
                    screen[start + column + y * 256] ^= font[(code - 32) * 8 + y]
        assert bytes(memory.banks[bank][:SCREEN_SIZE]) == screen
    run_to(cpu, MENU_HALT)
    assert (registers[I], registers[IM], registers[IFF], registers[SP]) == (0x5E, 2, 1, 0x6000)
    assert bytes(memory[0x5F5F:0x5F62]) == bytes.fromhex('C3 79 61')

    def frame(key=None, stop=MENU_HALT):
        assert registers[PC] == MENU_HALT and registers[IFF]
        ports.menu_key = key
        registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
        cpu.run()
        assert registers[PC] == MENU_HALT + 1
        assert cpu.accept_interrupt(registers, memory, MENU_HALT) and registers[PC] == 0x5F5F
        visited = set()
        run_to(cpu, stop, visited.add)
        assert 0x6179 in visited
        return visited

    frame(ADVANCE)
    assert memory[0x62C8] == 2
    frame()
    assert 0x62CC in frame(ENTER)
    assert bytes(memory[0x62CA:0x62CC]) == bytes.fromhex('55 63')
    cycle = [memory[0x6330]]
    for expected in list(range(1, mode + 1)) + ([1, 2, 0] if mode == 0 else []):
        # Удержание Enter не повторяет смену, следующий фронт требует пустой кадр.
        assert 0x62E6 not in frame(ENTER)
        frame()
        assert 0x62E6 in frame(ENTER)
        assert memory[0x6330] == expected
        pointer = (0x6369, 0x6373, 0x637E)[expected]
        assert bytes(memory[0x6359:0x635B]) == pointer.to_bytes(2, 'little')
        cycle.append(expected)
    frame()
    frame(ADVANCE)
    assert 0x62D9 in frame(ENTER)
    assert bytes(memory[0x62CA:0x62CC]) == bytes.fromhex('39 63') and memory[0x62C8] == 1
    frame()
    assert 0x610A in frame(ENTER, 0x3D13)
    key = bytes(memory[0x5CDD:0x5CE6])
    assert key == b'START   C'
    assert all(DISK[slot * 16:slot * 16 + 9] != key for slot in ENTRIES)
    assert (registers[A], registers[C], registers[H], registers[L], registers[IM]) == (255, 0x0E, 0x60, 0, 1)
    assert registers[SP] == 0x5FFE and bytes(memory[0x5FFE:0x6000]) == b'\0\x60'
    assert memory[0x5F5E] == mode and memory.o7ffd == 0x10

    if handoff is not None:
        return handoff(cpu)

    disk_ports = BasicReadPorts(memory)
    cpu.set_tracer(disk_ports)

    def set_rom(image):
        memory.memory[0] = image

    set_rom(basic)
    destination_before = bytes(memory[MENU_ENTRY:MENU_ENTRY + size])
    run_with_rom(cpu, basic, dos, set_rom, MENU_ENTRY)
    assert disk_ports.attempts == [(0, 1), (0, 2), (0, 3)] and memory[0x5D0F] == 1
    assert bytes(memory[MENU_ENTRY:MENU_ENTRY + size]) == destination_before
    assert registers[SP] == 0x6000 and memory[0x5F5E] == mode
    return dict(mode=mode, option_cycle=cycle, dos_key=key.decode('ascii'), dos_status=memory[0x5D0F],
                sector_reads=disk_ports.attempts, return_pc=registers[PC],
                destination_unchanged=True, mode_handoff_address=0x5F5E,
                separate_mode_readers=check_mode_readers(basic, dos, memory[0x5F5E]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    basic, dos, system = model_rom_context(args.dos_rom)
    profiles = [check_menu(basic, dos, system, mode) for mode in range(3)]
    result = dict(passed=True, original_disk_sha256=sha256(DISK).hexdigest(),
                  dos_rom_sha256=sha256(dos).hexdigest(), model_disk_offset=DISK_OFFSET,
                  menu_entry=MENU_ENTRY, screens=[FIRST_SCREEN, SECOND_SCREEN], screen_bytes=SCREEN_SIZE,
                  font_address=FONT, font_bytes=FONT_BYTES, initial_text_bitmaps_checked=True,
                  profiles=profiles, active_game_entry_proved=False,
                  native_execution=False, assembly_executed=False)
    report = ROOT / 'Tools/Disasm/Reports/StartArchiveMenuVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
