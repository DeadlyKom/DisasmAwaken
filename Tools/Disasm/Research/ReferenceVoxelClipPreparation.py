"""Независимая стоимость подготовки ED06 до первого развёрнутого входа.

Документация: ../../../Docs/VoxelSpriteClipBounds.md#r-подготовки-шагов-и-полного-вызова
"""
from ReferenceVoxelSmallArithmetic import divide_value_m1, multiply_m1


def preparation_cost(x, y, width, height, source_width, source_height):
    left, top, right, bottom = max(0, x), max(0, y), min(64, x + width), min(24, y + height)
    assert right > left and bottom > top
    left_trim, top_trim = left - x, top - y
    odd_left = left & 1
    skip = 32 - ((right + 1) // 2 - left // 2)
    step_x, divide_x_m1 = divide_value_m1(source_width, width)
    step_y, divide_y_m1 = divide_value_m1(source_height, height)
    integer_y = step_y >> 8
    # Постоянные участки включают обе CALL делителя, но не их тела.
    cost = 129 + divide_x_m1 + divide_y_m1
    cost += int(left_trim != 0) + int(top_trim != 0) + 3 * odd_left
    cost += int(source_width < 17)
    if top_trim:
        cost += 6 + multiply_m1(top_trim)
        source_top = (((top_trim & 127) * step_y) & 65535) >> 8
        if source_top:
            cost += 12 + multiply_m1(source_top)
    if left_trim:
        cost += 48 + 2 * (left_trim & 127).bit_count()
    if integer_y:
        cost += 33 + (integer_y & 127).bit_count()
    if right & 1:
        cost += 4 + int(not odd_left)
    cost += 6 * odd_left + 4 * int(not (skip & 1))
    return cost
