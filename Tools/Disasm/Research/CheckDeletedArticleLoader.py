"""Загрузчик из секторов за потоком ZXTime, четыре чтения ROM и три распаковки hr2."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckAwakenBasicRun import BasicReadPorts, model_rom_context
from CheckControlsLegacySectorRead import run_with_rom
from CheckStationFlightCycle import DISK, put, run_to
from TraceFlight import B, C, D, E, H, L, PC, SP, T, ROOT, Simulator
from skoolkit.pagingtracer import SliceableMemory


LOADER_OFFSET = 0x3800
LOADER_ENTRY = 0x811F
ARCHIVE_BASE = 0x3A00
DIRECTORY = ((0x81BC, 0x81CC, 16), (0x81EC, 0x821C, 24), (0x8204, 0x824C, 24))
STAGES = ((0x10, 1, 0x7F00, 0, ''),
          (0x16, 6, 0xC000, 0x1000, 'b42f0338a271dd9355c90c57f924e9eef87276717f7a2a4d1ecc689a01abe0cd'),
          (0x14, 8, 0xC000, 0x1000, '7c704e8d734ef99e2419879deef7da7b55683bde7be53e0eb1f079311c32c65b'),
          (0x10, 14, 0x6164, 0x1C9C, '316e24fbafcd8cadb41ce9040cc6194b2c48f4e635901e064f7e5103725df6fd'))


class ArticlePorts(BasicReadPorts):
    key = None

    def read_port(self, registers, port, offset=0):
        if self.key and port == self.key[0]:
            return 255 ^ self.key[1]
        return super().read_port(registers, port, offset)


def track_sector_word(offset):
    track, sector = divmod(offset // 256, 16)
    return bytes((sector, track))


def decode_hr21(raw):
    assert raw[:4] == b'hr21'
    output_size = int.from_bytes(raw[4:6], 'little')
    packed_size = int.from_bytes(raw[6:8], 'little')
    stream = raw[:8 + packed_size]
    position, control, bits_left = 14, 0, 0

    def read_byte():
        nonlocal position
        value = stream[position]
        position += 1
        return value

    def read_bit():
        nonlocal control, bits_left
        if bits_left == 0:
            control, bits_left = read_byte(), 8
        bits_left -= 1
        return (control >> bits_left) & 1

    def expand_prefix(prefix):
        while prefix < 0x80:
            prefix = (prefix << 1) | read_bit()
        return ((prefix << 1) | read_bit()) & 0xFF

    def read_long_offset():
        if read_bit():
            return read_byte() - 256
        repeats = 256 - expand_prefix(0x7F)
        high = 0xFF
        for _ in range(repeats):
            high = ((high << 1) + read_bit() - 1) & 0xFF
        if high == 0xE1:
            high = read_byte()
        return (high << 8) + read_byte() - 65536

    # Первый литерал идёт до управляющих битов, следующие литералы перемежаются ими.
    output = bytearray((read_byte(),))
    while True:
        if read_bit():
            output.append(read_byte())
            continue
        length = 1
        while length < 16:
            group = 2 * read_bit() + read_bit()
            length += group
            if group < 3:
                break
        if length == 4:
            # Особая группа выбирает пачку литералов, точную длину либо конец потока.
            if not read_bit():
                count = 2 * (expand_prefix(0x10) + 6)
                output.extend(read_byte() for _ in range(count))
                continue
            length = read_byte()
            if length == 0:
                break
            if length < 16:
                length = (length << 8) + read_byte()
            offset = read_long_offset()
        elif length == 1:
            offset = expand_prefix(0x3F) - 256
        elif length == 2:
            offset = read_byte() - 256
        else:
            if length > 4:
                length -= 1
            offset = read_long_offset()
        assert -len(output) <= offset < 0 and len(output) + length <= output_size - 6
        for _ in range(length):
            output.append(output[offset])
    assert len(output) == output_size - 6 and position == len(stream)
    output.extend(raw[8:14])
    return bytes(output)


def check_loader(basic, dos, system):
    memory = SliceableMemory(out7ffd=0x10)
    put(memory, LOADER_ENTRY, DISK[LOADER_OFFSET:ARCHIVE_BASE])
    put(memory, 0x5C00, system)
    put(memory, 0x5CF4, track_sector_word(ARCHIVE_BASE))
    assert b'AWAKEN' in bytes(memory[0x827C:0x82D7])
    cpu = Simulator(memory, {'PC': LOADER_ENTRY, 'SP': 0x5FFF, 'IY': 0x5C3A},
                    config={'fast_ldir': False, 'fast_djnz': False})
    registers = cpu.registers
    ports = ArticlePorts(memory)
    cpu.set_tracer(ports)

    def set_rom(image):
        memory.memory[0] = image

    set_rom(basic)
    run_to(cpu, 0x8136)
    source = ARCHIVE_BASE
    members = []
    # Независимый расчёт трёх таблиц из 64 байтов длин до переноса 011B байтов.
    for lengths, table, count in DIRECTORY:
        for index in range(count):
            length = memory[lengths + index]
            expected = track_sector_word(source) if length else b'\0\0'
            address = table + index * 2
            assert bytes(memory[address:address + 2]) == expected
            if length:
                member = decode_hr21(DISK[source:source + length * 256])
                members.append((dict(directory=lengths, index=index, disk_offset=source,
                                     sector_count=length), member))
            source += length * 256
    assert source == 0xDF00 and bytes(memory[0x5CF4:0x5CF6]) == track_sector_word(source)
    assert bytes(memory[0x5D3D:0x5E58]) == bytes(memory[0x81BC:0x82D7])

    rows, decoded = [], []
    for page, count, destination, output_size, digest in STAGES:
        run_to(cpu, 0x3D13)
        assert (registers[C], registers[B], registers[H] * 256 + registers[L]) == (5, count, destination)
        assert bytes((registers[E], registers[D])) == track_sector_word(source) and memory.o7ffd == page
        end = source + count * 256
        disk_bytes = DISK[source:end]
        cursor = len(ports.attempts)
        run_with_rom(cpu, basic, dos, set_rom, 0x8169)
        expected_reads = [(index // 16, index % 16 + 1) for index in range(source // 256, end // 256)]
        assert ports.attempts[cursor:] == expected_reads
        assert bytes(memory[destination:destination + len(disk_bytes)]) == disk_bytes
        assert bytes(memory[0x5CF4:0x5CF6]) == track_sector_word(end)
        row = dict(disk_offset=source, sectors=expected_reads, port_7ffd=page, destination=destination)
        if output_size:
            assert disk_bytes[:4] == b'hr21' and int.from_bytes(disk_bytes[4:6], 'little') == output_size
            packed_size = int.from_bytes(disk_bytes[6:8], 'little')
            assert (count - 1) * 256 < packed_size + 8 <= count * 256
            run_to(cpu, 0x7F00)
            assert registers[H] * 256 + registers[L] == registers[D] * 256 + registers[E] == destination
            run_to(cpu, 0x8148)
            output = bytes(memory[destination:destination + output_size])
            assert output == decode_hr21(disk_bytes) and sha256(output).hexdigest() == digest
            decoded.append(output)
            row.update(hr2_input_bytes=packed_size, output_bytes=output_size, output_sha256=digest)
        source = end
        rows.append(row)
    run_to(cpu, 0x6164)
    assert (registers[PC], registers[SP], memory.o7ffd, source) == (0x6164, 0x5FFD, 0x10, 0xFC00)
    return rows, decoded, members, cpu, ports


def check_article_selection(cpu, ports, basic, dos, members):
    memory, registers = cpu.memory, cpu.registers
    requests = []
    halt_addresses = (0x617F, 0x6181, 0x6183, 0x6185, 0x627A)

    def set_rom(image):
        memory.memory[0] = image

    def continue_to(stop):
        for _ in range(500000):
            pc = registers[PC]
            if pc == stop:
                return
            if pc == 0x3D13:
                sp = registers[SP]
                assert int.from_bytes(memory[sp:sp + 2], 'little') == 0x79DF and registers[C] == 5
                first = registers[D] * 16 + registers[E]
                count = registers[B]
                destination = registers[H] * 256 + registers[L]
                page = memory.o7ffd
                cursor = len(ports.attempts)
                run_with_rom(cpu, basic, dos, set_rom, 0x79DF)
                set_rom(basic)
                expected = [(i // 16, i % 16 + 1) for i in range(first, first + count)]
                assert ports.attempts[cursor:] == expected
                assert bytes(memory[destination:destination + 256 * count]) == DISK[first * 256:(first + count) * 256]
                requests.append(dict(disk_offset=first * 256, count=count, destination=destination,
                                     port_7ffd=page, sectors=expected))
            elif pc in halt_addresses:
                registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
                cpu.run()
                assert cpu.accept_interrupt(registers, memory, pc)
                assert registers[PC] == 0x6161 and bytes(memory[0x6161:0x6164]) == bytes.fromhex('C3 29 79')
            else:
                cpu.run()
        raise AssertionError(('Граница архивного меню', hex(stop), hex(registers[PC])))

    set_rom(basic)
    continue_to(0x617F)
    assert memory[0x78DA] == 1 and memory[0x7834] == 7
    for selection in range(2, 6):
        # Четыре исходных пробуждения меню с нажатой клавишей A.
        ports.key = (0xFDFE, 1)
        continue_to(0x6180)
        continue_to(0x617F)
        assert memory[0x78DA] == selection and memory[0x79E5] == 1
    ports.key = (0xBFFE, 1)
    continue_to(0x627A)
    assert [(r['disk_offset'], r['count'], r['destination'], r['port_7ffd']) for r in requests] == [
        (0x5200, 13, 0x8000, 0x10), (0xDD00, 2, 0xC000, 0x11),
        (0x3A00, 6, 0xCB58, 0x14), (0xA900, 8, 0x8000, 0x10),
    ]
    article = next(output for row, output in members if row['disk_offset'] == 0xA900)
    assert article.startswith(b'\x05Awaken second breez\xFF') and len(article) == 2684
    assert bytes(memory[0x8000:0x8000 + len(article)]) == article
    before = bytes(memory[0x4000:0x5B00])
    ports.key = None
    continue_to(0x6297)
    screen = bytes(memory[0x4000:0x5B00])
    assert screen != before and any(screen[:0x1800])
    return dict(requests=requests, selected_row=5, title='Awaken second breez',
                text_sha256=sha256(article).hexdigest(), rendered_screen_sha256=sha256(screen).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    basic, dos, system = model_rom_context(args.dos_rom)
    rows, decoded, members, cpu, ports = check_loader(basic, dos, system)
    article = check_article_selection(cpu, ports, basic, dos, members)
    for row, output in [*zip(rows[1:], decoded, strict=True), *members]:
        name = f"00_Article_{row['disk_offset']:05X}.unpacked.bin"
        target = ROOT / 'Tools/Disasm/Extracted/Deleted' / name
        if target.exists():
            assert target.read_bytes() == output
        else:
            target.write_bytes(output)
        row['decoded_path'] = target.relative_to(ROOT).as_posix()
        row['output_bytes'] = len(output)
        row['output_sha256'] = sha256(output).hexdigest()
    result = dict(passed=True, loader_disk_offset=LOADER_OFFSET, model_loader_entry=LOADER_ENTRY,
                  model_archive_base=ARCHIVE_BASE, original_disk_sha256=sha256(DISK).hexdigest(),
                  dos_rom_sha256=sha256(dos).hexdigest(), directory_entries=64,
                  stages=rows, directory_members=[row for row, _ in members],
                  reached_entry=0x6164, independent_decoder_matches_ram=True,
                  expanded_code_executed=True, article_selection=article,
                  active_game_entry_proved=False, native_execution=False, assembly_executed=False)
    report = ROOT / 'Tools/Disasm/Reports/DeletedArticleLoaderVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', 'utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
