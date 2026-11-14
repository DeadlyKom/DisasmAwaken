"""Числовые результаты и M1 двух семибитовых помощников VOXAL.

Документация: ../../../Docs/VoxelSmallArithmetic.md
"""


def multiply_m1(multiplier):
    low = multiplier & 127
    return 22 + low.bit_count() + (low & 1)


def divide_value_m1(numerator, divisor):
    assert 0 <= numerator <= 255 and 1 <= divisor <= 255
    value = numerator & 127
    highest = max(0, value.bit_length() - 1)
    remainder, integer, restores = 0, 0, 0
    for bit in range(highest, -1, -1):
        trial = 2 * remainder + ((value >> bit) & 1) - divisor
        borrow = trial < 0
        restores += borrow
        remainder = trial + divisor if borrow else trial
        integer = 2 * integer + int(not borrow)
    # Восьмибитный ADD переносит старший бит удвоения в последующий SBC.
    fraction = 0
    for _ in range(8):
        doubled = 2 * remainder
        trial = (doubled & 255) - divisor - (doubled >> 8)
        borrow = trial < 0
        restores += borrow
        restored = (trial & 255) + divisor if borrow else trial
        fraction = 2 * fraction + int(restored <= 255)
        remainder = restored & 255
    return (integer << 8) | fraction, 78 + 2 * highest + restores
