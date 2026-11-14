"""Сумма квадрата 2x2 на замкнутой текстуре, сохранённая строка и точные записи.

Документация: ../../../Docs/IntroGeneratedEffects.md#сохранённая-строка-и-сумма-на-месте
"""
from collections import Counter
from hashlib import sha256
from random import Random
import json

from CheckIntro import original_memory, ROOT
from CheckStationFlightCycle import DISK, ENTRIES
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP


class KernelMemory(list):
    recording = False

    def __getitem__(self, address):
        if self.recording and isinstance(address, int) and 0xC000 <= address < 0xC100:
            self.guard_reads.append(address)
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.recording:
            assert isinstance(address, int)
            self.writes.append((address, value))
        super().__setitem__(address, value)


def expected_texture(texture):
    rows = []
    for y in range(64):
        row = bytes((texture[y * 64 + x] + texture[y * 64 + (x + 1) % 64]
                     + texture[((y + 1) % 64) * 64 + x]
                     + texture[((y + 1) % 64) * 64 + (x + 1) % 64] + 0x40) & 255
                    for x in range(64))
        rows.append(row * 4)
    return b''.join(rows)


def main():
    flat = original_memory()
    code = bytes(flat[0x6B1B:0x6B47])
    offset = ENTRIES[3]['offset'] + 0x81B
    assert code == DISK[offset:offset + len(code)]
    rng = Random(0x6B28)
    textures = []
    for y, x in ((0, 0), (0, 63), (63, 0), (63, 63)):
        texture = bytearray(4096)
        texture[y * 64 + x] = 1
        textures.append(('corner', (y, x), texture))
    textures.extend(('constant', value, bytes([value] * 4096)) for value in range(256))
    textures.extend(('random', index, rng.randbytes(4096)) for index in range(8))
    memory = KernelMemory(flat)
    cpu = Simulator(memory)
    corners = []
    for kind, parameter, texture in textures:
        memory.recording = False
        memory[:] = flat
        expanded = b''.join(bytes(texture[y * 64:(y + 1) * 64]) * 4 for y in range(64))
        memory[0x8000:0xC000] = expanded
        memory[0xC000:0xC100] = [0xF3] * 256
        cpu = Simulator(memory, dict(PC=0x6B1B, SP=0x5FFE))
        expected = list(memory)
        buffer = expected_texture(texture)
        expected[0x8000:0xC000] = buffer
        expected[0xC000:0xC100] = expanded[:256]
        expected[0x5FFC:0x5FFE] = [0, 0x80]
        memory.writes, memory.guard_reads = [], []
        memory.recording = True
        cpu.run(0x6B1B, 0x6B47)
        memory.recording = False
        assert list(memory) == expected, (kind, parameter)
        assert cpu.registers[SP] == 0x5FFE and cpu.registers[PC] == 0x6B47
        writes = Counter(address for address, _ in memory.writes)
        assert writes == Counter({**dict.fromkeys(range(0x8000, 0xC100), 1), 0x5FFC:1, 0x5FFD:1})
        reads = Counter(memory.guard_reads)
        assert reads == Counter({address:1 if address in (0xC000, 0xC040) else 2
                                 for address in range(0xC000, 0xC041)})
        if kind == 'corner':
            y, x = parameter
            cells = {(y, x), ((y - 1) % 64, x), (y, (x - 1) % 64),
                     ((y - 1) % 64, (x - 1) % 64)}
            positions = {row * 256 + column + repeat * 64 for row, column in cells for repeat in range(4)}
            assert {i for i, value in enumerate(buffer) if value != 0x40} == positions
            assert all(buffer[i] == 0x41 for i in positions)
            corners.append(dict(source_cell=[y, x], output_cells=sorted(cells), physical_changed_bytes=len(positions)))
    report = dict(passed=True, total_cases=len(textures), original_kernel_sha256=sha256(code).hexdigest(),
                  corner_impulses=corners, all_constant_input_bytes_checked=True, random_profiles=8,
                  full_65536_byte_memory_compared=True, exact_write_counts=True,
                  expanded_texture_bytes=16384, original_guard_row_bytes_written=256,
                  guard_read_addresses_inclusive=[0xC000, 0xC040], guard_read_count_per_case=128,
                  guard_row_not_replaced_with_transformed_first_row=True,
                  kernel_stack=0x5FFE, kernel_temporary_stack_bytes=2,
                  later_attribute_matrix_writes_executed=False, texture_expander_executed=False,
                  bank_1_at_C000_assumed=True, IRQ_executed=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroColumnTextureKernelVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены 268 суммирующих проходов, оба заворачивания, 65 адресов сохранённой строки и вся RAM.')


if __name__ == '__main__':
    main()
