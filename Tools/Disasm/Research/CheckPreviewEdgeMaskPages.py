"""Формулы пяти режимов и буквальное поведение всех исходных пар C0/C1."""
import json

from ProbePreviewPolygon import ROOT, context, execute
from PreviewEdgeRasterOracle import address
from PreviewPolygonOracle import PATTERNS


def main():
    memory, simulator, initial = context()
    raw = (ROOT / 'Tools/Disasm/Extracted/Active/06_D3D.C.bin').read_bytes()[:512]
    assert bytes(memory[0xC000:0xC200]) == raw

    def mask(parity, column, mode, right):
        offset = parity * 256 + (column & 7) * 32 + mode * 2 + 16 * right
        return tuple(raw[offset:offset + 2])

    for parity in range(2):
        for mode, (first, delta) in enumerate(PATTERNS[:5]):
            pattern = first ^ (delta if parity else 0)
            for column in range(8):
                assert mask(parity, column, mode, False) == (
                    (255 << (8 - column)) & 255, pattern & (255 >> column))
                assert mask(parity, column, mode, True) == (
                    255 >> column, pattern & ((255 << (8 - column)) & 255))

    cases = 0
    effects_outside_span = 0
    for mode, (first, delta) in enumerate(PATTERNS):
        for left_phase in range(8):
            for right_phase in range(8):
                for same in (False, True):
                    if same and right_phase < left_phase:
                        continue
                    left = 16 + left_phase
                    right = (16 if same else 40) + right_phase
                    vertices = ((3, left), (3, right), (5, right), (5, left))
                    for pattern_seed in (0, 255, 85):
                        before = bytes((pattern_seed,)) * 6144
                        expected = bytearray(before)
                        for parity in range(2):
                            y = 3 + parity
                            low = address(y, left) - 0x4000
                            high = address(y, right) - 0x4000
                            left_keep, left_set = mask(parity, left, mode, False)
                            right_keep, right_set = mask(parity, right, mode, True)
                            pattern = first ^ (delta if parity else 0)
                            if same:
                                keep = left_keep | right_keep
                                expected[low] = (before[low] & keep) | (right_set & ~keep)
                            else:
                                expected[low] = (before[low] & left_keep) | left_set
                                expected[low + 1:high] = bytes((pattern,)) * (high - low - 1)
                                expected[high] = (before[high] & right_keep) | right_set
                            for column in range((left // 8) * 8, (right // 8 + 1) * 8):
                                if left <= column < right:
                                    continue
                                pointer = address(y, column) - 0x4000
                                if (before[pointer] ^ expected[pointer]) & (128 >> (column & 7)):
                                    assert mode >= 5
                                    effects_outside_span += 1
                        memory.recording = False
                        memory[0x4000:0x5800] = before
                        execute(memory, simulator, initial, vertices, mode)
                        assert bytes(memory[0x4000:0x5800]) == expected, (mode, left, right, pattern_seed)
                        cases += 1
    assert cases == 2400 and effects_outside_span > 0
    report = dict(passed=True, cases=cases, literal_pairs=256, regular_pairs=160, irregular_pairs=96,
                  all_mode_indices_and_edge_pixel_phases=True, both_mask_pages_per_contour=True,
                  same_byte_and_separate_edges=True, changed_bits_outside_span=effects_outside_span,
                  original_bitmap_and_literal_masks_agree=True, normal_game_use_of_modes_5_to_7_proved=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/PreviewEdgeMaskPagesVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
