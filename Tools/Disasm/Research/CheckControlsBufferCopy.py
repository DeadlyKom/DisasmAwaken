"""C870/C882, перенос линейных 96 строк в исходную экранную раскладку Spectrum."""
from pathlib import Path
import collections
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsTextDisplay import pixel_address
from ControlsBufferCopyRegisters import expected_registers, check_registers


def main():
    base = base_memory()
    memory = Memory(base)
    simulator = Simulator(memory)
    cases = 0
    for profile in range(512):
        memory.recording = False
        memory[:] = base
        # Создание независимого фона и исходного растра со всеми байтами пикселей и флагов POP AF.
        for address in range(0x4000, 0x5B00):
            memory[address] = (address * 73 + profile * 31) & 255
        for offset in range(3072):
            memory[0x8000 + offset] = (profile & 255) if profile < 256 else (offset * 73 + (offset >> 5) * 31 + profile) & 255
        memory[0xBFFE:0xC000] = [255, 63]
        expected = list(memory)
        # Преобразование координат растра в экранный адрес, без повторения стекового алгоритма.
        for y in range(96):
            address = pixel_address(y, 0)
            expected[address:address + 32] = memory[0x8000 + 32 * y:0x8020 + 32 * y]
        initial = get_registers({'AF': profile * 73 & 65535, 'HL': 0x1357, 'DE': 0x2468,
            'BC': 0x369C, '^AF': 0xDEF0, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC,
            'IX': 0xABCD, 'IY': 0x5C3A, 'PC': 0xC870, 'SP': 0xBFFE}, None, False)
        initial[14], initial[26], initial[27] = profile & 255, profile & 1, profile % 3
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(10000):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат', profile, hex(simulator.registers[PC])))
        memory.recording = False
        # Проверка всех байтов, кроме двух исходных операндов и единственного CALL на CPU-стеке.
        excluded = {0xCA84, 0xCA8A, 0xCA8B, 0xBFFC, 0xBFFD}
        differences = [a for a in range(65536) if a not in excluded and memory[a] != expected[a]]
        assert not differences, (profile, [(hex(a), memory[a], expected[a]) for a in differences[:8]])
        pixels = [(a, v) for a, v in memory.writes if 0x4000 <= a < 0x5800]
        assert len(pixels) == 3072 and len({a for a, _ in pixels}) == 3072
        assert len(memory.writes) == 3090, (profile, len(memory.writes))
        assert memory[0xCA84] == 1 and memory[0xCA8A:0xCA8C] == [254, 191]
        registers = simulator.registers
        assert registers[SP] == 0xC000
        assert registers[6:8] == [0x8C, 0] and registers[22:24] == [0x48, 0x8F]
        assert all(registers[i] == initial[i] for i in (14, 26, 27))
        check_registers(registers, expected_registers(initial, expected, 0x8800, 0x480F, 4))
        cases += 1
    report = dict(passed=True, original_calls=cases, pixel_bytes_per_call=3072,
        viewport_width_pixels=256, viewport_height_pixels=96,
        screen_coordinates_independently_checked=True, all_uniform_byte_patterns=True,
        source_pixels_as_flags_executed=True, every_other_ram_byte_checked=True,
        exact_pixel_write_set=True, all_calls_executed_without_stubs=True,
        saved_sp_and_loop_operands_checked=True, exact_main_and_alternate_flags_checked=True,
        all_documented_register_outputs_checked=True, standalone_c882_arbitrary_inputs_proved=False,
        irq_executed=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsBufferCopyVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
