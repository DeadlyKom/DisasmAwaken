"""Исходный рисователь C004/C026 и три слоя растровых плиток перед маршрутами BANK."""

from collections import Counter
from itertools import product
import json

from CheckBankStripArchiveConsumer import BANK_OFFSET, DISK, FIXED_OFFSET, ROOT
from CheckMusic import PC, SP, Simulator


LAYER_BASES = (0xC36F, 0xCC6F, 0xD56F)
LAYER_SIZE = 0x900
SELECTION_SIZE = 192
DESTINATIONS = (0xA42E, 0x885C, 0x6C8A)
LAYERS_END = LAYER_BASES[-1] + LAYER_SIZE


class TileMemory(bytearray):
    registers = None

    def __init__(self, image):
        super().__init__(image)
        self.reads = []
        self.writes = []

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if isinstance(address, int) and self.registers is not None and self.registers[PC] == 0xC35E:
            if address != 0xC35E:
                self.reads.append((address, value))
        return value

    def __setitem__(self, address, value):
        if isinstance(address, int) and self.registers is not None and self.registers[PC] == 0xC361:
            self.writes.append((address, value))
        super().__setitem__(address, value)


def tile_expectation(image, pixels, group, choice):
    reads, writes = [], []
    origin_x, origin_y = 5 * (3 - choice), 7 * group

    def draw(destination, coordinate_index, first_byte, mode):
        coordinate = 0xC305 + 2 * coordinate_index
        dx, dy = image[coordinate:coordinate + 2]
        x, y = origin_x + dx, origin_y + dy
        first_pixel = destination + y * 339 + (x & ~1) * 2 + (1 - (x & 1)) + 5
        for row in range(8):
            source, target = first_byte + row, first_pixel + 42 * row
            value = image[source]
            reads.append((source, value))
            if mode == 'erase':
                pixels[target] &= 255 ^ value
            elif mode == 'restore':
                pixels[target] |= value
            else:
                assert mode == 'replace'
                pixels[target] = value
            writes.append((target, pixels[target]))

    return draw, reads, writes


def mask_pointer(image, coordinate_index):
    pointer = 0xC2D5 + 2 * coordinate_index
    return int.from_bytes(image[pointer:pointer + 2], 'little')


def expected_tiles(image, pixels, group, choice, right, equal):
    draw, reads, writes = tile_expectation(image, pixels, group, choice)
    selection = group * 4 + choice

    for layer, destination in zip(LAYER_BASES, DESTINATIONS):
        tile_source = layer + SELECTION_SIZE * selection
        for index in range(20 if equal else 0, 22):
            extra = 2 if right and index >= 20 else 0
            draw(destination, index + extra, tile_source + 8 * (index + extra), 'replace')
    if equal:
        for index in range(22):
            coordinate_index = index + (2 if not right and index >= 20 else 0)
            source = mask_pointer(image, coordinate_index) + 0x60
            draw(0x885C if right else 0x6C8A, coordinate_index, source, 'erase')
    return reads, writes


def expected_rebuild(image, pixels, group, choice, right, equal):
    draw, reads, writes = tile_expectation(image, pixels, group, choice)
    first_end = 22 if right else 20
    end_pair = [first_end, first_end + 1]
    all_tiles = [*range(20), *end_pair]
    for destination in (0x6C8A, 0xA42E, 0x885C):
        for index in end_pair if equal else all_tiles:
            draw(destination, index, mask_pointer(image, index) + 0x60, 'erase')
    for index in all_tiles:
        draw(0x885C if right else 0x6C8A, index, mask_pointer(image, index), 'restore')
    return reads, writes


def probe(memory, entry, **registers):
    cpu = Simulator(memory, dict(registers, PC=entry, SP=0x5FFE))
    memory.registers = cpu.registers
    for _ in range(20000):
        if cpu.registers[PC] == 0x3FFF:
            assert cpu.registers[SP] == 0x6000
            return
        cpu.run()
    raise AssertionError((entry, 'граница возврата'))


def seed_targets(memory, targets):
    for target, _ in targets:
        memory[target] = 0xA5 ^ (target & 255)


def main():
    image = bytearray(65536)
    image[0x6000:0xC000] = DISK[FIXED_OFFSET:BANK_OFFSET]
    image[0xC000:] = DISK[BANK_OFFSET:BANK_OFFSET + 0x4000]
    assert LAYERS_END == 0xDE6F
    traces = Counter()
    mask_traces = Counter()
    rebuild_writes = 0
    cases = 0
    for equal, (right, entry) in product((False, True), ((False, 0xC026), (True, 0xC004))):
        for selection in range(12):
            group, choice = divmod(selection, 4)
            other_group, other_choice = divmod(selection if equal else (selection + 1) % 12, 4)
            memory = TileMemory(image)
            memory[0x62F7] = int(right)
            if right:
                memory[0x664B:0x664F] = bytes((other_choice, other_group, choice, group))
            else:
                memory[0x664B:0x664F] = bytes((choice, group, other_choice, other_group))
            memory[0x5FFE:0x6000] = b'\xFF\x3F'
            # Ненулевые операнды отличают прямую запись от OR даже на исходно пустом слое.
            _, targets = expected_tiles(image, memory.copy(), group, choice, right, equal)
            seed_targets(memory, targets)
            expected = memory.copy()
            reads, writes = expected_tiles(image, expected, group, choice, right, equal)
            probe(memory, entry)
            assert memory.reads == reads, (
                entry, selection, len(memory.reads), len(reads),
                next(((index, actual, wanted) for index, (actual, wanted) in
                      enumerate(zip(memory.reads, reads)) if actual != wanted), None))
            assert memory.writes == writes, (entry, selection)
            assert all(memory[target] == expected[target] for target, _ in writes)
            traces.update(address for address, _ in reads)

            mask_memory = TileMemory(image)
            mask_memory[0x5FFE:0x6000] = b'\xFF\x3F'
            mask_memory[0x664B:0x664F] = memory[0x664B:0x664F]
            mask_memory[0xC000:0xC002] = bytes((5 * (3 - choice), 7 * group))
            mask_memory[0xC2A7] = 4 * right
            _, targets = expected_rebuild(image, mask_memory.copy(), group, choice, right, equal)
            seed_targets(mask_memory, targets)
            expected = mask_memory.copy()
            reads, writes = expected_rebuild(image, expected, group, choice, right, equal)
            probe(mask_memory, 0xC1FF, HL=0x885C if right else 0x6C8A)
            assert mask_memory.reads == reads and mask_memory.writes == writes, (entry, selection, equal)
            assert all(mask_memory[target] == expected[target] for target, _ in writes)
            mask_traces.update(address for address, _ in reads)
            rebuild_writes += len(writes)
            cases += 1
    assert all(traces[address] for address in range(LAYER_BASES[0], LAYERS_END))
    assert max(traces) == LAYERS_END - 1
    mask_addresses = sorted(address for address in traces if address < LAYER_BASES[0])
    assert len(mask_addresses) == 96
    assert sorted(mask_traces) == list(range(0x6665, 0x6725))
    report = dict(passed=True, total_cases=cases, source_file='Tools/Disasm/Disk/original.trd',
                  layer_cpu_addresses=list(LAYER_BASES), layer_bytes=LAYER_SIZE,
                  selections_per_layer=12, bytes_per_selection=SELECTION_SIZE,
                  layer_disk_ranges=[[BANK_OFFSET + address - 0xC000,
                                      BANK_OFFSET + address - 0xC000 + LAYER_SIZE] for address in LAYER_BASES],
                  layer_bytes_read=LAYERS_END - LAYER_BASES[0], source_reads=sum(traces.values()),
                  first_source_address=min(traces), last_source_address=max(traces),
                  route_bytes_also_read=sum(address >= LAYERS_END for address in traces),
                  exact_source_addresses_values_and_pixel_writes=True,
                  replacement_distinguished_from_or=True,
                  unequal_selections_executed=True, equal_selections_executed=True,
                  erase_mask_source_bytes_read=len(mask_addresses), erase_mask_addresses=mask_addresses,
                  rebuild_cases=cases, rebuild_mask_source_bytes_read=len(mask_traces),
                  rebuild_writes=rebuild_writes,
                  game_entry_proved=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/BankArchiveTileLayersVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
