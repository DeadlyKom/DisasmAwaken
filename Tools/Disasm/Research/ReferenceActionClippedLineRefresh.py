"""Итоговые M1 фиксированного XOR-пакета с отсечением.

Документация: ../../../Docs/ActionOverlayPair.md#счёт-r-фиксированной-линии-с-отсечением
"""
from functools import lru_cache
from CheckActionParameterActivation import flat_action
from ReferenceActionClipRefresh import instruction_cost as cost

RANGES = ((0xDBBD, 0xDBC3), (0xDC21, 0xDC28), (0xDC2E, 0xDC41), (0xDC4E, 0xDD23))


@lru_cache(maxsize=1)
def original_blocks():
    flat = flat_action()
    return tuple((start, bytes(flat[start:end])) for start, end in RANGES)


def eligible(read, pointer):
    return (bytes(read(pointer + i) for i in range(4)) == bytes((0xB2, 0, 5, 0))
        and all(bytes(read(start + i) for i in range(len(block))) == block for start, block in original_blocks())
        and read(0xC94B) in (0x20,0x18) and read(0xC94C) == 0x27)


def refresh_cost(first_code, second_code, clip_m1, accepted, raster_m1):
    # Пакет содержит ровно одну пару, окончание восстанавливает BC/HL и читает терминатор.
    total = (cost(0xDBBD, 0xDBC3) + cost(0xDC21, 0xDC28) + cost(0xDC2E, 0xDC41)
        + cost(0xDC4E, 0xDCAC) + cost(0xDCD6, 0xDCDD) + cost(0xDBBD, 0xDBC0))
    if not first_code:
        return total
    total += cost(0xDCAC, 0xDCAF)
    if not second_code:
        return total
    total += cost(0xDCAF, 0xDCB6)
    aggregate = first_code | second_code
    if (~aggregate) & 240:
        return total
    total += cost(0xDCB6, 0xDCBB)
    if not aggregate & 15:
        return total + cost(0xDCBB, 0xDCD6) + raster_m1
    total += cost(0xDCDD, 0xDD06) + clip_m1 + cost(0xDD06, 0xDD0A)
    if not accepted:
        return total
    return total + cost(0xDD0A, 0xDD23) + cost(0xDCD3, 0xDCD6) + raster_m1
