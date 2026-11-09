"""Исходный загрузчик, разбиение и растровый цикл scene1po из свободных секторов."""
import hashlib
import json

from CheckBankStripArchiveConsumer import ArchivePorts, ExtendedMemory
from CheckInsetFrame import bitmap_address
from CheckStationFlightCycle import DISK, ENTRIES, payload, put, run_to
from TraceFlight import A, C, H, L, PC, SP, ROOT, Simulator
from skoolkit.simutils import get_registers


FIXED_OFFSET = 0x8B100
SLOT = 30
RETURN_SENTINEL = 0x3FFF
ROW_BYTES = 92
HEIGHT = 203
INPUT = 0x7700


def start_call(cpu, address, **pairs):
    cpu.registers[:] = get_registers(dict(pairs, PC=address, SP=0x5BFC), None, False)
    put(cpu.memory, 0x5BFC, RETURN_SENTINEL.to_bytes(2, 'little'))


def exercise(include_sector_tail):
    raw = payload(SLOT)
    entry = ENTRIES[SLOT]
    assert len(raw) == ROW_BYTES * HEIGHT and entry['length'] == len(raw)
    sectors = DISK[entry['offset']:entry['offset'] + 0x4900]
    data = sectors if include_sector_tail else raw
    memory = ExtendedMemory()
    put(memory, 0x4000, DISK[FIXED_OFFSET:FIXED_OFFSET + 0x1100])
    assert int.from_bytes(memory[0x4A4B:0x4A4D], 'little') == ROW_BYTES
    assert int.from_bytes(memory[0x4A51:0x4A53], 'little') == HEIGHT
    assert bytes(memory[0x5018:0x501A]) == bytes.fromhex('B8 4F')
    put(memory, 0x4FB6, memory[0x5018:0x501A])
    cpu = Simulator(memory)
    ports = ArchivePorts(memory)
    cpu.set_tracer(ports)
    start_call(cpu, 0x4916)
    run_to(cpu, 0x3D13)
    key = bytes(memory[0x5CDD:0x5CE6])
    assert key == DISK[16 * SLOT:16 * SLOT + 9] == b'scene1pos'
    registers = cpu.registers
    assert (registers[A], registers[C], registers[H], registers[L]) == (255, 0x0E, 0x77, 0)
    put(memory, INPUT, data)
    stack = registers[SP]
    registers[PC] = int.from_bytes(memory[stack:stack + 2], 'little')
    registers[SP] += 2
    assert registers[PC] == 0x492B
    run_to(cpu, RETURN_SENTINEL)

    extra_fixed = bytes(memory[INPUT + len(raw):0xC000])
    old_page14 = bytes((index * 17 + 53) & 255 for index in range(0x4000))
    memory.banks[14][:] = old_page14
    start_call(cpu, 0x492D)
    run_to(cpu, RETURN_SENTINEL)
    assert ports.pages == [0x5D, 0x5E] and registers[SP] == 0x5BFE
    first = 178 * ROW_BYTES
    assert bytes(memory.banks[13][:first]) == raw[:first]
    assert not any(memory.banks[13][first:])
    second_start = 0x54
    second = raw[first:] + extra_fixed + old_page14[:80]
    wanted = bytearray(old_page14)
    wanted[second_start:second_start + len(second)] = second
    assert memory.banks[14] == wanted
    assert len(raw[first:]) == 25 * ROW_BYTES and len(second) == 26 * ROW_BYTES
    assert int.from_bytes(memory[0x4A44:0x4A46], 'little') == ROW_BYTES - 32
    assert int.from_bytes(memory[0x4A57:0x4A59], 'little') == INPUT + (90 - 32) // 2

    # Сверка окон, включая обе физические страницы и первую и последнюю строки.
    window_bytes = 0
    for row, count, column in ((0, 8, 29), (170, 8, 60), (178, 8, 0), (195, 8, 29)):
        page = 13 if row < 178 else 14
        source = 0xC000 + (row * ROW_BYTES if page == 13 else second_start + (row - 178) * ROW_BYTES) + column
        memory.out7ffd(0x50 + page - 8)
        screen = bytearray(memory[0x4000:0x5B00])
        # Окно не пересекает код, который исполняется по 4A00.
        dest = bitmap_address(95)
        for index in range(count):
            destination = bitmap_address(95 - index) - 0x4000
            begin = (row + index) * ROW_BYTES + column
            screen[destination:destination + 32] = raw[begin:begin + 32]
        start_call(cpu, 0x4A00, AF=count << 8, HL=source, DE=dest)
        run_to(cpu, RETURN_SENTINEL)
        assert bytes(memory[0x4000:0x5B00]) == screen, (row, count, column)
        window_bytes += count * 32

    return dict(file_key=key.decode('ascii'), sector_tail_supplied=include_sector_tail,
                loaded_bytes=len(data), initial_destination=INPUT, width_bytes=ROW_BYTES, height=HEIGHT,
                first_page=13, first_page_rows=178, second_page=14, second_page_start=second_start,
                second_page_rows=25, extra_fixed_bytes=len(extra_fixed), extra_bank_bytes=80,
                window_bytes_compared=window_bytes)


def main():
    cases = [exercise(False), exercise(True)]
    result = dict(passed=True, original_sha256=hashlib.sha256(DISK).hexdigest(), total_cases=len(cases),
                  archived_loader_disk_offset=FIXED_OFFSET, profiles=cases, trdos_substituted=True,
                  machine_paging_model=True, active_game_entry_proved=False,
                  native_execution=False, assembly_executed=False)
    report = ROOT / 'Tools/Disasm/Reports/Scene1ArchiveConsumerVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('2 профиля scene1po, 203 строки в двух страницах, по 1024 байта вывода')


if __name__ == '__main__':
    main()
