"""Физические пары маски и пикселей после последнего индексируемого кадра BD2."""
from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x3CA8, 0x3F78, 'Source/Resources/42_BD2/UnindexedMaskPixelPairs.bin',
     'BD_MASK_PIXEL_PAIRS_WITHOUT_GEOMETRY',
     '360 пар маска, пиксели после последнего кадра BAR, размеры не установлены'),
)


if __name__ == '__main__':
    data = (ROOT / 'Tools/Disasm/Extracted/Active/42_BD2.C.bin').read_bytes()
    start, end, *_ = RESOURCES[0]
    assert end == len(data)
    tail = data[start:end]
    pairs = tuple(zip(tail[::2], tail[1::2]))
    assert len(pairs) == 360 and all(mask & pixels == 0 for mask, pixels in pairs)
    assert (255, 0) in pairs and any(pixels for _, pixels in pairs)
    assert any(mask & pixels for mask, pixels in zip(tail[1::2], tail[2::2]))
    publish(slot=42, origin=0xC000, ranges=((start, end),), resources=RESOURCES,
            tag='FighterMaskTail', resource_module='ClassifyFighterMaskTail',
            resource_name='FIGHTER_MASK_TAIL',
            proof=dict(mask_pixel_pairs=len(pairs), pair_alignment_checked=True,
                       dimensions_or_game_consumer_proved=False))
