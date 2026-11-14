"""Независимая стоимость пар и строк RasterizeSprite, буфер и восстановление SP.

Документация: ../../../Docs/VoxelSpriteClipBounds.md#r-развёрнутого-рисователя
"""
from collections import Counter
from hashlib import sha256
from itertools import chain, product
import json

from CheckVoxelEffectProjection import projection_memory
from CheckVoxelSpriteSampleRaster import divide_step, raster
from CheckVoxelSpriteClipBounds import clip_refresh
from ReferenceVoxelClipPreparation import preparation_cost
from CheckMusicGateTicks import Memory
from CheckStationFlightCycle import DISK, ENTRIES, ROOT
from ReferenceControlsPointRespawn import refresh
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, R, I, IM, IFF


def reference_cost(resource, x, y, width, height, source_width, source_height):
    """Стоимость по выбранным кодам ресурса и числовым переносам между строками."""
    left, top, right, bottom = max(0, x), max(0, y), min(64, x + width), min(24, y + height)
    assert right > left and bottom > top
    step_x, step_y = divide_step(source_width, width), divide_step(source_height, height)
    stride = 16 if source_width <= 16 else 32
    source_left = ((left - x) & 127) * step_x // 256
    source_top = ((top - y) & 127) * step_y // 256
    columns = (right + 1) // 2 - left // 2
    skip = 32 - columns
    pairs, tails, events = 0, 0, Counter()
    for row in range(bottom - top):
        source_row = source_top + row * step_y // 256
        for column in range(columns):
            codes = []
            for parity in (0, 1):
                pixel = 2 * (left // 2 + column) + parity
                if left <= pixel < right:
                    sample = source_left + (pixel - left) * step_x // 256
                    byte = resource[stride * source_row + sample]
                    codes.append(byte & 15 if parity else byte >> 4)
                else:
                    codes.append(0)
            if not any(codes):
                kind, cost = 'transparent', 22
            elif all(codes):
                kind, cost = 'opaque', 36
            else:
                kind, cost = 'partial', 43
                events['left_only' if codes[0] else 'right_only'] += 1
            events['pair_' + kind] += 1
            # Последняя группа не выполняет общий двухинструкционный переход Advance.
            if column == columns - 1:
                cost -= 2
            if not column and left & 1:
                cost -= 3
                events['odd_left_entry'] += 1
            pairs += cost
        destination = 0x8000 + (top + row) * 128 + left // 2
        destination_carry = int((destination & 255) + 128 >= 256)
        fraction_carry = int((row * step_y & 255) + (step_y & 255) >= 256)
        source_base = 0xD800 + source_left + stride * source_row
        stride_carry = int(fraction_carry and (source_base & 255) + stride >= 256)
        events['destination_carry'] += destination_carry
        events['fraction_carry'] += fraction_carry
        events['stride_carry'] += stride_carry
        # Четыре M1 продолжения ClipSprite.NextRow либо восемь M1 окончательного выхода.
        tails += 26 + destination_carry + 2 * fraction_carry + 2 * stride_carry
        tails += 8 if row == bottom - top - 1 else 4
    return pairs + tails, dict(events), skip


def main():
    baseline = projection_memory()
    offset = ENTRIES[21]['offset'] + 0xEE7A - 0xEC00
    original = bytes(baseline[0xEE7A:0xF931])
    assert original == DISK[offset:offset + len(original)]
    continuation_offset = ENTRIES[21]['offset'] + 0xEE73 - 0xEC00
    continuation = bytes(baseline[0xEE73:0xEE7A])
    assert continuation == DISK[continuation_offset:continuation_offset + 7]
    clip_offset = ENTRIES[21]['offset'] + 0x7F
    original_clip = bytes(baseline[0xEC7F:0xEE7A])
    assert original_clip == DISK[clip_offset:clip_offset + len(original_clip)]
    background = [(i * 53 + (i >> 8) * 11 + 17) & 255 for i in range(3072)]
    regular = ((x, 0, width, height, source_width, 19, pattern)
               for x, width, height, source_width, pattern in product(
                   (0, 1), range(1, 65), (1, 3), (16, 17), range(5)))
    clipped = ((x, y, width, height, source_width, source_height, pattern)
               for (x, y, width, height), (source_width, source_height), pattern in product(
                   ((-5, -3, 17, 12), (-1, -1, 64, 24), (60, 21, 17, 12), (1, 0, 17, 24)),
                   ((6, 6), (17, 19)), range(5)))
    entries, aggregate, r_codes, total = set(), Counter(), set(), 0
    costs = []
    preparation_costs = []
    full_call_costs = []
    for case, (x, y, width, height, source_width, source_height, pattern) in enumerate(chain(regular, clipped)):
        memory = Memory(baseline)
        if pattern < 4:
            resource = [(0, 0x11, 0x10, 0x01)[pattern]] * 1024
        else:
            resource = [(i * 73 + (i >> 3) * 19 + case) & 255 for i in range(1024)]
        memory[0xD800:0xDC00] = resource
        memory[0x8000:0x8C00] = background
        cpu = Simulator(memory, dict(PC=0xEC7F, SP=0xBFFE, I=0x3C, R=case & 255,
            HL=x & 65535, DE=y & 65535, BC=height * 256 + width,
            **{'^HL':source_height * 256 + source_width, '^DE':0xD800}), {'im':2, 'iff':0})
        expected_m1, events, skip = reference_cost(resource, x, y, width, height, source_width, source_height)
        first = 0xEE7A + 84 * skip + (3 if max(0, x) & 1 else 0)
        initial_r = case & 255
        prefix_m1, prefix_route = clip_refresh(x, y, width, height)
        assert prefix_route == 'visible'
        expected_preparation = preparation_cost(x, y, width, height, source_width, source_height)
        before_raster_m1 = 0
        at_steps_m1 = None
        # Подготовка контекста проверяется отдельно от стоимости развёрнутого прохода.
        for _ in range(2000):
            if cpu.registers[PC] == first:
                break
            if cpu.registers[PC] == 0xED06:
                at_steps_m1 = before_raster_m1
            opcode = memory[cpu.registers[PC]]
            before_raster_m1 += 2 if opcode in (0xCB, 0xDD, 0xED, 0xFD) else 1
            cpu.run()
            assert cpu.registers[R] == refresh(initial_r, before_raster_m1)
        else:
            raise AssertionError(('first_raster_entry', case, first, cpu.registers[PC]))
        entries.add(skip)
        assert at_steps_m1 == prefix_m1
        assert before_raster_m1 - prefix_m1 == expected_preparation, (
            x, y, width, height, source_width, source_height, before_raster_m1 - prefix_m1, expected_preparation)
        preparation_costs.append(expected_preparation)
        r_codes.add(initial_r)
        memory.writes = []
        memory.recording = True
        measured_m1 = 0
        for _ in range(150000):
            pc = cpu.registers[PC]
            if pc == 0x3FFF:
                break
            assert 0xEE73 <= pc < 0xF931, (case, hex(pc))
            opcode = memory[pc]
            assert opcode != 0xED
            measured_m1 += 2 if opcode in (0xCB, 0xDD, 0xFD) else 1
            cpu.run()
            assert cpu.registers[R] == refresh(initial_r, before_raster_m1 + measured_m1)
        else:
            raise AssertionError(('raster_instruction_limit', case))
        memory.recording = False
        context = (x, y, width, height, source_width, source_height, pattern)
        assert measured_m1 == expected_m1, (context, measured_m1, expected_m1, events)
        assert cpu.registers[SP] == 0xC000
        assert (cpu.registers[I], cpu.registers[IM], cpu.registers[IFF]) == (0x3C, 2, 0)
        touched = set()
        expected = raster(background, baseline, resource, x, y, width, height,
                          source_width, source_height, touched=touched)
        assert memory[0x8000:0x8C00] == expected, context
        writes = Counter(address for address, _ in memory.writes if 0x8000 <= address < 0x8C00)
        assert writes == Counter(dict.fromkeys(touched, 1)), context
        other = [(address, value) for address, value in memory.writes if not 0x8000 <= address < 0x8C00]
        assert other == [(0xEE7A + 84 * skip + 4, 0xF0)], (context, other)
        aggregate.update(events)
        costs.append(expected_m1)
        full_call_costs.append(before_raster_m1 + expected_m1)
        total += 1
    assert entries == set(range(32)) and r_codes == set(range(256))
    assert all(aggregate[key] for key in ('pair_transparent', 'pair_partial', 'pair_opaque', 'left_only', 'right_only',
                                        'destination_carry', 'fraction_carry', 'stride_carry'))
    report = dict(passed=True, total_cases=total, original_raster_code_sha256=sha256(original).hexdigest(),
                  original_clip_continuation_sha256=sha256(continuation).hexdigest(),
                  original_clip_code_sha256=sha256(original_clip).hexdigest(),
                  all_32_raster_entries=True, independent_pair_and_row_M1_formulas=True,
                  includes_clip_next_row_continuations=True, starts_after_clip_preparation=True,
                  r_checked_after_every_instruction=True, all_3072_buffer_bytes_compared=True,
                  all_buffer_write_counts_compared=True, only_other_write_restores_first_mask=True,
                  final_SP=0xC000, event_counts=dict(aggregate), observed_M1_min=min(costs), observed_M1_max=max(costs),
                  I_IM_IFF_preserved=True,
                  initial_I=0x3C, initial_IM=2, initial_IFF=0,
                  initial_r_codes_sampled_across_cases=sorted(r_codes),
                  all_initial_r_codes_crossed_with_all_inputs=False,
                  full_clip_preparation_R_proved=True, full_visible_clip_M1_composition_checked=True,
                  r_seeded_at_clip_entry=True, IRQ_executed=False,
                  observed_preparation_M1_min=min(preparation_costs), observed_preparation_M1_max=max(preparation_costs),
                  observed_full_call_M1_min=min(full_call_costs), observed_full_call_M1_max=max(full_call_costs),
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/VoxelRasterRefreshVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены M1 пар и строк, все 32 входа, R, буфер и восстановление SP рисователя VOXAL.')


if __name__ == '__main__':
    main()
