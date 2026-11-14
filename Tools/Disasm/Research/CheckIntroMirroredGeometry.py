"""Центральный блок 32x32 из 64x38, четыре отражения и целобайтовое вычитание.

Документация: ../../../Docs/IntroMirroredTexture.md#центральный-блок-и-четыре-отражения
"""
from hashlib import sha256
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import original_memory, ROOT
from CheckScreenUpdate import PortTrace
from CheckStationFlightCycle import DISK, ENTRIES
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP


def geometric_texture(source):
    return bytes((source[64 * (3 + min(y, 63 - y)) + 16 + min(x, 63 - x)] - 0x89) & 255
                 for y in range(64) for x in range(64))


def main():
    flat = original_memory()
    code = bytes(flat[0x6DB6:0x6E31])
    offset = ENTRIES[3]['offset'] + 0xAB6
    assert code == DISK[offset:offset + len(code)]
    crop = [64 * row + column for row in range(3, 35) for column in range(16, 48)]
    assert len(crop) == len(set(crop)) == 1024 and max(crop) < 2432
    base = [bytearray([bank] * 16384) for bank in range(8)]
    base[5][:] = bytes(flat[0x4000:0x8000])
    base[2][0x3FFE:] = bytes((255, 63))

    def execute(source):
        memory = RecordedBanks(banks=[bank.copy() for bank in base], out7ffd=17)
        memory.banks[2][:4096] = source
        cpu = Simulator(memory, dict(PC=0x6DE6, SP=0xBFFE))
        ports = PortTrace(cpu)
        cpu.set_tracer(ports)
        cpu.run(0x6DE6, 0x3FFF)
        expected = geometric_texture(source)
        assert bytes(memory.banks[2][:4096]) == expected == bytes(memory.banks[4][:4096])
        assert cpu.registers[SP] == 0xC000
        assert ports.writes == [(0x7FFD, 20), (0x7FFD, 17)]
        return expected

    # Контроль невыбранных байтов, постороннее ненулевое заполнение не попадает в результат.
    source = bytearray([0xF3] * 4096)
    for address in crop:
        source[address] = 0x89
    assert execute(source) == bytes(4096)
    # Проверка каждой выбранной точки, одна единица обязана дать четыре симметричные позиции.
    for row in range(32):
        for column in range(32):
            address = 64 * (row + 3) + column + 16
            source[address] = 0x8A
            result = execute(source)
            positions = {64 * y + x for y in (row, 63 - row) for x in (column, 63 - column)}
            assert {i for i, value in enumerate(result) if value} == positions
            assert all(result[i] == 1 for i in positions)
            source[address] = 0x89
    # Проверка всей байтовой операции, включая заём из старшего полубайта.
    for value in range(256):
        for address in crop:
            source[address] = value
        assert execute(source) == bytes([(value - 0x89) & 255] * 4096)
    report = dict(passed=True, original_code_sha256=sha256(code).hexdigest(),
                  total_cases=1281, source_grid=[64, 38], crop_columns_inclusive=[16, 47],
                  crop_rows_inclusive=[3, 34], destination_grid=[64, 64],
                  selected_source_bytes=1024, every_selected_point_executed=True,
                  four_symmetric_outputs_per_source_point=True, all_byte_values_checked=True,
                  whole_byte_subtraction_with_borrow=True, unselected_source_bytes_excluded_by_control=True,
                  both_4096_byte_physical_destinations_compared=True,
                  source_renderer_executed=False, IRQ_executed=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroMirroredGeometryVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены 1024 точки центрального блока, четыре отражения и все 256 байтовых значений.')


if __name__ == '__main__':
    main()
