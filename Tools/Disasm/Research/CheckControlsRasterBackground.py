"""Исходные байты E291, накопитель фазы и фон до E4B7, без объектного прохода."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from CheckControlsCircleSpan import add_flags
from ReferenceControlsPointRespawn import refresh


def pixel_address(x, y):
    return 0x4000 | ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | (x >> 3)


def accumulator(word, fraction):
    signed = word if word < 0x8000 else word - 0x10000
    shifted = (signed >> 2) & 0xFFFF
    velocity = shifted & 255
    negative = bool(velocity & 128)
    magnitude = 256 - velocity if negative else velocity
    total = magnitude + fraction
    carry = total > 255
    step = 255 if negative else 1
    return shifted, negative, magnitude, total & 255, carry, step


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()
    compared = (*range(13), 14, *range(16, 24), PC, 26, 27)

    def check(word, fraction, phase, complete, serial):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        memory[0xA78F:0xA791] = [word & 255, word >> 8]
        memory[0xE2B0], memory[0xE2BC] = fraction, phase
        initial = get_registers({'AF': 0xA55A, 'HL': 0x1357, 'DE': 0x2468,
            'BC': 0x369C, '^AF': (serial * 37) & 65535, '^HL': 0x1234,
            '^DE': 0x5678, '^BC': 0x9ABC, 'IX': 0xABCD, 'IY': 0x5C3A,
            'SP': 0xBFFE, 'PC': 0xE291}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, serial & 255, serial & 1, serial % 3
        shifted, negative, magnitude, new_fraction, carry, step = accumulator(word, fraction)
        correction = step if carry else 0
        wanted = list(initial)
        writes = [(0xE48F, 0xFE), (0xE490, 0xBF), (0xE2B0, new_fraction)]
        wanted[0:8] = [new_fraction, add_flags(magnitude, fraction), step, correction,
            0x24, 0x68, shifted >> 8, fraction]
        wanted[8:10] = [0xA0, 0xC0]
        wanted[PC] = 0xE2BB
        prefix_m1 = 23 + 3 * negative + carry
        wanted[15] = refresh(initial[15], prefix_m1)
        if complete:
            index = (phase - correction) & 15
            writes += [(0xE2BC, index), (0xE471, index)]
            # Построение ожидаемых 80 строк по фазовым номерам, без копирования Z80-цикла.
            rows = list(range(index, 16)) + list(range(16)) * 4
            if index:
                rows += list(range(16 - index, 16))
            assert len(rows) == 80
            for y, row in enumerate(rows, 104):
                address = pixel_address(64, y)
                values = [0x55] * 10 if row == 15 else [0x80 if row % 2 == 0 else 0, 0] * 5
                writes.extend((address + i, value) for i, value in enumerate(values))
            if index:
                writes.append((0xE471, 0))
            # Нанесение центрального квадрата содержит две записи в правый байт каждой строки.
            provisional = dict(writes)
            for y in (143, 144, 145):
                for x in (103, 104, 105):
                    address = pixel_address(x, y)
                    value = provisional.get(address, memory[address]) | (128 >> (x & 7))
                    provisional[address] = value
                    writes.append((address, value))
            wanted[0:8] = [0, 8, 0, 0x80, 0x55, 0x55, 0x51, 0x4D]
            wanted[16:24] = [0x50, 2, step, correction, 0x24, 0x68, shifted >> 8, fraction]
            wanted[PC] = 0xE4B7
            # Расчёт M1, 80 строк, десять границ знакоместа, пять или шесть концов периода.
            wanted[15] = refresh(initial[15], prefix_m1 + (1031 if index else 1011))
        expected = list(memory)
        for address, value in writes:
            expected[address] = value
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(2400 if complete else 40):
            if simulator.registers[PC] == wanted[PC]:
                break
            simulator.run()
        else:
            raise AssertionError(('граница', word, fraction, phase, complete, simulator.registers[PC]))
        memory.recording = False
        indices = (*compared, 15)
        assert all(wanted[i] == simulator.registers[i] for i in indices), (word, fraction, phase, complete,
            [(i, wanted[i], simulator.registers[i]) for i in indices if wanted[i] != simulator.registers[i]])
        assert memory == expected, ('RAM', word, fraction, phase)
        assert Counter(memory.writes) == Counter(writes), ('записи', word, fraction, phase,
            Counter(memory.writes) - Counter(writes), Counter(writes) - Counter(memory.writes))
        touched = {address for address, _ in writes}
        counts['background' if complete else 'accumulator'] += 1

    # Проверка всех входных слов охватывает знаковое расширение и отброшенные младшие разряды.
    for word in range(65536):
        check(word, (word * 73) & 255, word & 15, False, word)
    # Проверка каждой пары младшего байта после сдвига и старого дробного остатка.
    for velocity in range(256):
        for fraction in range(256):
            check((velocity << 2) | (fraction & 3), fraction, 0, False, velocity * 256 + fraction)
    # Проверка всех фаз на обоих знаках скорости, переносе и отсутствии переноса.
    for phase in range(16):
        for word in (0, 4, 0x1FC, 0x200, 0x3FC, 0x8000, 0xFFFF, 0x7FFF):
            for fraction in (0, 1, 128, 255):
                check(word, fraction, phase, True, counts.total())
    report = dict(passed=True, total_cases=counts.total(), cases=dict(counts),
        all_input_words_checked=True, all_shifted_low_byte_fraction_pairs=True,
        background_cases=512, background_size_pixels=[80, 80], background_origin=[64, 104],
        center_mark_pixels=[103, 143, 3, 3], every_ram_byte_and_write_checked=True,
        exact_registers_flags_sp=True, accumulator_refresh_proved=True, background_refresh_proved=True,
        stopped_before_object_pass=True, full_e291_proved=False,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsRasterBackgroundVerification.json').write_bytes(
        (json.dumps(report, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
