"""Независимый счёт M1 арифметических помощников отсечения ACTION.

Документация: ../../../Docs/ActionClipProducts.md#точный-счёт-m1-числителей
"""
from functools import lru_cache
from CheckActionParameterActivation import flat_action
from CheckSignedMultiply import refresh_cost as multiply_cost


@lru_cache(maxsize=None)
def instruction_cost(start, end):
    from InspectZ80 import decoder
    return sum(2 if instruction.bytes[0] in (0xCB, 0xED, 0xDD, 0xFD) else 1
               for instruction in decoder(flat_action()).disassemble(start, end, 'h'))


def product_cost(entry, left, right):
    assert entry in (0xC477, 0xC496, 0xC4B5, 0xC4D4)
    # Помощник включает CALL и конечный RET, числовая стоимость ребёнка добавляется один раз.
    return instruction_cost(entry, entry + 31) + multiply_cost(left, right)


def intersection_cost(entry, numerator, divisor, translated):
    from CheckSignedDivision import refresh_cost as divide_cost
    # Префикс включает CALL деления, каждое выбранное окончание включает RET писателя.
    total = instruction_cost(entry, entry + 24) + divide_cost(numerator, divisor)
    if entry in (0xC4F6, 0xC540):
        header_end, conditional_end, negative_end, normal, end = {
            0xC4F6: (0xC517, 0xC51A, 0xC52A, 0xC52C, 0xC53D),
            0xC540: (0xC561, 0xC564, 0xC575, 0xC577, 0xC588),
        }[entry]
        total += instruction_cost(entry + 24, header_end)
        if translated >> 8 == 0:
            return total + instruction_cost(normal, end)
        total += instruction_cost(header_end, conditional_end)
        if translated & 0x8000:
            return total + instruction_cost(conditional_end, negative_end)
        return total + instruction_cost(negative_end, normal) + instruction_cost(normal, end)
    header_end, low_end, negative, normal, end = {
        0xC58B: (0xC5AD, 0xC5B2, 0xC5C3, 0xC5D3, 0xC5E4),
        0xC5E7: (0xC609, 0xC60E, 0xC61F, 0xC630, 0xC641),
    }[entry]
    total += instruction_cost(entry + 24, header_end)
    if translated & 0x8000:
        return total + instruction_cost(negative, normal)
    total += instruction_cost(header_end, low_end)
    return total + instruction_cost(low_end, negative) if translated & 128 else total + instruction_cost(normal, end)
