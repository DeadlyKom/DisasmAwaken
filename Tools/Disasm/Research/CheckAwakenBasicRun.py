"""Исходная команда RUN, чтение первого сектора AWAKEN и переход BASIC на USR."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from BasicProgramData import detached_line_suffix, line_token_from_rom
from CheckBasicIntroDiskRead import FileReadPorts, prepare_memory
from CheckControlsLegacySectorRead import run_with_rom
from CheckMusic import PC, SP, Simulator
from CheckScreenUpdate import put
from CheckStationFlightCycle import DISK, ENTRIES, ROOT
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import H, L


class BasicLoadMemory(SliceableMemory):
    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.registers = None
        self.load_writes = []
        self.watched_addresses = frozenset()
        self.watched_upper_bank = None
        self.watched_accesses = []

    def is_watched(self, address):
        if not isinstance(address, int) or address not in self.watched_addresses:
            return False
        bank = self.watched_upper_bank
        if isinstance(bank, dict):
            bank = bank[address]
        return address < 0xC000 or bank is None or self.o7ffd & 7 == bank

    def __getitem__(self, address):
        if self.is_watched(address):
            self.watched_accesses.append(('read', address, self.registers[PC]))
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if isinstance(address, int) and self.registers is not None and self.registers[PC] == 0x2FF0:
            self.load_writes.append((address, value))
        if self.is_watched(address):
            self.watched_accesses.append(('write', address, self.registers[PC]))
        super().__setitem__(address, value)


class BasicReadPorts(FileReadPorts):
    def __init__(self, memory):
        super().__init__(0)
        self.memory = memory
        self.read_destinations = []
        self.watched_sector = None

    def write_port(self, registers, port, value, offset):
        if port == 0x7FFD and registers[PC] >= 0x4000:
            self.memory.out7ffd(value)
        else:
            super().write_port(registers, port, value, offset)

    def read_port(self, registers, port, offset=0):
        if registers[PC] >= 0x4000:
            return 0 if port & 255 in (0x1F, 0xDF) else 255
        if port & 255 == 0x7F and self.commands[-1:] == [0x80] and not self.cursor:
            self.read_destinations.append((self.attempts[-1], registers[H] * 256 + registers[L]))
            if self.attempts[-1] == self.watched_sector:
                self.memory.watched_accesses.clear()
        return super().read_port(registers, port, offset)


def load_basic(basic, dos, *, memory_factory=None):
    entry = ENTRIES[3]
    offset = entry['offset']
    length = entry['length']
    raw = DISK[offset:offset + 256]
    detached_line = detached_line_suffix(raw)
    assert detached_line[4] == line_token_from_rom(basic)
    origin = 0x5D3B
    buffer_size = 0x101
    stack = 0xFEFE

    memory = (memory_factory or BasicLoadMemory)()
    memory.roms = (basic, basic)
    memory.out7ffd(0x10)
    flat = prepare_memory(basic)
    put(memory, 0x5C00, flat[0x5C00:0x5D3E])
    # Фикстура редактора начинается с пустой программы и уже набранного RUN.
    header = DISK[3 * 16:4 * 16]
    line = b'\xf7"' + header[:8].rstrip(b' ') + b'"\r\x80'
    edit_line = origin + 1
    put(memory, edit_line, line)
    for address in (0x5C61, 0x5C63, 0x5C65):
        put(memory, address, (edit_line + len(line)).to_bytes(2, 'little'))
    memory[0x5CB6], memory[0x5D0C], memory[0x5CF8], memory[0x5C3B] = 0xF4, 0xFF, 0, 0x80
    put(memory, 0x5D13, b'\x54\xff')
    put(memory, 0x5D1A, b'\xcb\x02')
    put(memory, 0x5D1C, stack.to_bytes(2, 'little'))
    ports = BasicReadPorts(memory)
    cpu = Simulator(memory, {'PC': 0x02FC, 'SP': stack, 'IY': 0x5C3A}, state={'im': 1},
                    config={'fast_ldir': False, 'fast_djnz': True})
    cpu.set_tracer(ports)
    memory.registers = cpu.registers

    def set_rom(image):
        memory.memory[0] = image

    # Разбор RUN и загрузка файла завершаются на входе обработчика автозапуска.
    tail_offset = length + 5
    tail_start = 0x5D25 + tail_offset
    tail_end = 0x5D25 + 0x0100
    first_sector = (entry['first_track'], entry['first_sector'] + 1)
    ports.watched_sector = first_sector
    memory.watched_addresses = frozenset(range(tail_start, tail_end))
    run_with_rom(cpu, basic, dos, set_rom, 0x012A, initial_dos=True)
    ports.watched_sector = None
    tail_accesses = memory.watched_accesses.copy()
    memory.watched_addresses = frozenset()
    memory.watched_accesses.clear()
    tail_reads = [address for operation, address, _ in tail_accesses if operation == 'read']
    tail_writes = [address for operation, address, _ in tail_accesses if operation == 'write']
    assert not tail_reads, tail_accesses
    assert tail_writes == list(range(tail_start, tail_end)), tail_accesses
    catalogue = [(0, 9), (0, 1), (0, 1)]
    assert ports.attempts == catalogue + [first_sector]
    assert ports.read_destinations == [(sector, 0x5D25) for sector in ports.attempts]
    assert bytes(memory[0x5CDD:0x5CED]) == header
    staged = int.from_bytes(memory[0x5C53:0x5C55], 'little')
    assert staged == origin + buffer_size
    assert memory.load_writes == [(staged + index, value) for index, value in enumerate(raw[:length + 5])]
    memory.registers = None
    assert bytes(memory[0x5D25:0x5E25]) == raw
    assert bytes(memory[staged:staged + length + 5]) == raw[:length + 5]
    assert bytes(memory[staged + length:staged + length + 4]) == b'\x80\xaa\x14\x00'
    usr = int.from_bytes(raw[115:117], 'little')
    memory.registers = cpu.registers
    memory.watched_addresses = frozenset(range(tail_start, tail_end))
    run_with_rom(cpu, basic, dos, set_rom, usr, initial_dos=True)
    memory.watched_addresses = frozenset()
    memory.registers = None
    overwritten = set()
    original_reads = []
    for operation, address, pc in memory.watched_accesses:
        if operation == 'write':
            overwritten.add(address)
        elif address not in overwritten:
            original_reads.append((address, pc))
    memory.watched_accesses.clear()
    assert not original_reads, original_reads
    assert usr == 0x5D41 and bytes(memory[origin:origin + length]) == raw[:length]
    assert int.from_bytes(memory[0x5C53:0x5C55], 'little') == origin
    assert bytes(memory[0x5C45:0x5C47]) == b'\x14\x00'
    next_track, next_sector = divmod(offset // 256 + 1, 16)
    assert bytes(memory[0x5CF4:0x5CF6]) == bytes((next_sector, next_track))
    return cpu, ports, dict(logical_basic_bytes=length, copied_bytes_before_buffer_release=length + 5,
                            copied_byte_after_autostart=raw[length + 4],
                            detached_line_suffix=dict(token=detached_line[4], token_text='LINE',
                                                      decimal_digits=detached_line[5:7].decode('ascii'),
                                                      original_command_established=False),
                            first_sector_tail=dict(file_offsets=[tail_offset, 0x0100],
                                                   buffer_addresses=[tail_start, tail_end],
                                                   reads_before_autostart=len(tail_reads),
                                                   writes_before_autostart=len(tail_writes),
                                                   original_reads_until_usr=len(original_reads),
                                                   overwritten_before_usr=len(overwritten)),
                            directory_and_service_reads=catalogue, first_sector=first_sector,
                            sector_read_destination=ports.read_destinations[-1][1],
                            autostart_line=20, actual_basic_usr_entry=usr,
                            next_intro_sector_word=next_track * 256 + next_sector,
                            catalogue_header_supplied=False, editor_command_parsing_executed=True,
                            input_line_supplied_as_basic_tokens=True)


def model_rom_context(dos_rom):
    """ПЗУ и системные переменные после настоящего входа BASIC в загрузчик."""
    basic = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    dos = dos_rom.read_bytes()
    assert len(basic) == len(dos) == 0x4000
    cpu, _, _ = load_basic(basic, dos)
    return basic, dos, bytes(cpu.memory[0x5C00:0x5D25])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    basic = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    dos = args.dos_rom.read_bytes()
    assert len(basic) == len(dos) == 16384
    _, _, trace = load_basic(basic, dos)
    report = dict(passed=True, **trace, dos_rom_sha256=sha256(dos).hexdigest(),
                  basic_rom_sha256=sha256(basic).hexdigest(), assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/AwakenBasicRunVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
