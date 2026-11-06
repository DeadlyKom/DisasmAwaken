"""B044 и 6D06, табличные разности и три настоящих масштабированных умножения."""
from collections import Counter
from functools import lru_cache
import json
import random
import sys

from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionScaledMultiply import signed
from CheckControlsCircleSpan import add_flags
from CheckControlsSixRowGauge import inc_flags
from CheckMusic import Simulator, get_registers
from CheckMusicGateTicks import Memory, xor_flags
from ReferenceControlsBufferPoints import sub8_flags, sub16_flags
from ReferenceControlsPointRespawn import refresh

sys.path.insert(0, str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder

COEFFICIENT_OPERANDS = (0x6D0E, 0x6D1C, 0x6D2A)
RESULT_WORDS = (0xE5B0, 0xE5CF, 0xE5EA)


@lru_cache(maxsize=None)
def cost(start, end):
    instructions = decoder(flat_action()).disassemble(start, end, 'h')
    return sum(2 if instruction.bytes[0] in (0xCB, 0xED, 0xDD, 0xFD) else 1 for instruction in instructions)


def multiply(registers, coefficient, value):
    factor = abs(signed(coefficient, 8)) & 127
    magnitude = abs(signed(value, 16))
    product = factor * magnitude
    sign = coefficient ^ (value >> 8)
    negative = bool(sign & 128)
    result = (-1 if negative else 1) * (product // 128) & 65535
    de = product // 128 if negative else magnitude
    flags = sub16_flags(0, product // 128) if negative else xor_flags(sign)
    upper = product >> 15
    flags_prime = (upper & 0x28) | (64 if not upper else 0) | (16 if ((product >> 16) & 15) * 2 + (upper & 1) > 15 else 0)
    registers[:8] = [sign, flags, registers[2], 0, de >> 8, de & 255, result >> 8, result & 255]
    registers[16:18] = [upper, flags_prime]
    m1 = (35 + factor.bit_length() - 1 + 2 * factor.bit_count() if factor else 32)
    m1 += 7 * bool(value & 0x8000) + 2 * bool(coefficient & 128) + 4 * negative
    return result, m1


def table_reference(memory, initial, offsets):
    r = list(initial)
    table = memory[0x9800:0x9900]
    waves = memory[0x9900:0x9A00]
    x0, y0, z0 = offsets
    b, c = waves[x0], waves[(x0 + 64) & 255]
    ixl, iyl = waves[y0], waves[(y0 + 64) & 255]
    d, e = waves[z0], waves[(z0 + 64) & 255]

    def half(value):
        return signed(value, 8) // 2

    def difference(first, second):
        minus = (half(first) - half(second)) & 255
        plus = (minus + second) & 255
        return (table[plus] - table[minus]) & 255, table[minus], plus

    def finish(value, flags):
        m1 = 0
        overflow = bool(flags & 4)
        if overflow:
            flags = sub8_flags(0, value)
            value = (-value) & 255
            m1 = 3
            if flags & 4:
                assert value == 128
                value = 127
                flags = 0x3F
                m1 += 1
        return value, flags, m1, overflow

    first = difference(ixl, e)[0]
    cross0 = difference(iyl, b)[0]
    difference0 = difference(difference(ixl, c)[0], d)[0]
    second, _, extra0, overflow0 = finish((difference0 - cross0) & 255, sub8_flags(difference0, cross0))
    cross1 = difference(iyl, c)[0]
    difference1, e, low = difference(difference(ixl, b)[0], d)
    third, flags, extra1, overflow1 = finish((difference1 + cross1) & 255, add_flags(difference1, cross1))
    r[:10] = [third, flags, b, c, d, e, 0x98, low, cross1, ixl]
    r[11] = iyl
    m1 = cost(0xB044, 0xB0A7) + cost(0xB0AD, 0xB0DF) + cost(0xB0E5, 0xB0E9) + extra0 + extra1
    return r, (first, second, third), m1, (overflow0, overflow1)


def profiles():
    for value in range(65536):
        yield 0x6D06, (value & 255, (value * 73) & 255, value >> 8), value, False
    generator = random.Random(0xB044)
    for _ in range(8192):
        offsets = tuple(generator.randrange(256) for _ in range(3))
        yield 0xB044, offsets, generator.randrange(65536), True
        yield 0x6D06, offsets, generator.randrange(65536), True


def main():
    original = flat_action()
    memory = Memory(original)
    simulator = Simulator(memory)
    counts, overflows = Counter(), Counter()
    touched = set()
    for entry, offsets, value, synthetic in profiles():
        serial = counts.total()
        stack = (0x9008, 0xBFFE)[serial & 1]
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        if synthetic:
            memory[0x9900:0x9A00] = [(index * 73 + serial * 109) & 255 for index in range(256)]
        memory[0xB045], memory[0xB04F], memory[0xB05C] = offsets
        memory[stack], memory[stack + 1] = 255, 63
        initial = get_registers({'AF': serial & 65535, 'HL': 0x1357, 'DE': value, 'BC': 0x369C,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC, '^AF': 0xDEF0, 'IX': 0xABCD, 'IY': 0x5C3A,
            'SP': stack, 'PC': entry}, None, False)
        initial[14], initial[15], initial[26], initial[27] = serial & 255, (serial * 73) & 255, serial & 1, serial % 3
        wanted, coefficients, m1, overflow = table_reference(memory, initial, offsets)
        writes = list(zip(COEFFICIENT_OPERANDS, coefficients))

        def word(address, item):
            writes.extend(((address, item & 255), (address + 1, item >> 8)))

        if entry == 0x6D06:
            word(stack - 2, 0xABCD)
            word(stack - 4, value)
            word(stack - 6, 0x6D0C)
            word(stack - 4, value)
            word(stack - 4, value)
            for address, coefficient in zip(RESULT_WORDS, coefficients):
                result, local_m1 = multiply(wanted, coefficient, value)
                word(address, result)
                m1 += local_m1
            wanted[8:10] = initial[8:10]
            m1 += cost(0x6D06, 0x6D38)
        wanted[12], wanted[15], wanted[24] = stack + 2, refresh(initial[15], m1), 0x3FFF
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        simulator.run(start=entry, stop=0x3FFF)
        memory.recording = False
        compared = (*range(25), 26, 27)
        assert all(wanted[reg] == simulator.registers[reg] for reg in compared), (serial, hex(entry), offsets, value, coefficients, overflow,
            [(reg, wanted[reg], simulator.registers[reg]) for reg in compared if wanted[reg] != simulator.registers[reg]])
        assert Counter(writes) == Counter(memory.writes), (serial, Counter(writes) - Counter(memory.writes), Counter(memory.writes) - Counter(writes))
        assert all(memory[address] == item for address, item in dict(writes).items())
        touched = {address for address, _ in writes}
        counts[f'{entry:04X}'] += 1
        overflows[str(overflow)] += 1
    report = dict(passed=True, total_cases=counts.total(), cases_by_entry=dict(counts), overflow_paths=dict(overflows),
        exact_registers_including_R=True, all_DE_words_for_wrapper=True, exact_operand_and_stack_writes=True,
        real_scaled_multiplication_children=True, original_IX_restored=True, actual_wrapper_stack_bytes=6,
        assembly_executed=False, irq_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionObjectOffsetVectorVerification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
