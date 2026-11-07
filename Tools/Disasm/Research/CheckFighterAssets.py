"""Точные связи 36 указателей BAR, 204 записей и 56 маскированных изображений."""
import json

from FighterAssetData import ROOT, original, decode, render, parse


def main():
    bar, banks = original()
    pointers, groups, sprites, ends = decode(bar, banks)
    assert len(pointers) == 36 and len(groups) == 37 and len(sprites) == 56
    assert sum(group['count'] for group in groups) == 204
    assert ends == {0: 16268, 1: 16152, 2: 15528, 3: 12048}
    assert parse(render(bar, pointers, groups))[0] == bar
    result = dict(passed=True, total_cases=204, pointer_count=36, group_count=37, sprite_count=56,
                  bar_logical_bytes=len(bar), sprite_bytes=sum(ends.values()),
                  unreferenced_groups=sorted(set(group['offset'] for group in groups) - set(pointers)),
                  mask_pixel_intersections=0, banks=[dict(bank=bank, covered=ends[bank],
                      logical_length=len(data), unclassified_suffix=len(data) - ends[bank])
                      for bank, data in enumerate(banks)],
                  runtime_consumer_proved=False, unknown_step_bytes=list(range(9)),
                  header_bit14_meaning_proved=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/FighterAssetsVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
