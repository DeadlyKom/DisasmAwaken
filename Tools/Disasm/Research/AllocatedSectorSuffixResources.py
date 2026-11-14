"""Физические суффиксы выделенных секторов, игровая неиспользуемость не утверждается."""
RANGES=((5, 3864, 4096, 'Source/Resources/05_LANG/AfterMarketScript.bin', 3864), (6, 15978, 16128, 'Source/Resources/06_D3D/AfterDescriptionText.bin', 15978), (8, 5921, 6144, 'Source/Resources/08_HELP/SectorTail.bin', 5921), (18, 7213, 7424, 'Source/Resources/18_DATAS/SectorTail.bin', 7213), (19, 8224, 8448, 'Source/Resources/19_3DPART/SectorTail.bin', 8224), (21, 3784, 3840, 'Source/Resources/21_VOXAL/SectorTail.bin', 3784), (22, 6878, 6912, 'Source/Resources/22_CONTROL0/SectorTail.bin', 6878), (23, 6474, 6656, 'Source/Resources/23_CONTROL/SectorTail.bin', 6474), (24, 10580, 10752, 'Source/Resources/24_OBJECT3D/SectorTail.bin', 10580), (29, 19114, 19200, 'Source/Resources/29_FINALF/SectorTail.bin', 19114), (30, 18676, 18688, 'Source/Resources/30_scene1po/SectorTail.bin', 18676), (39, 3076, 3328, 'Source/Resources/39_BAR/SectorTail.bin', 3076), (40, 16268, 16384, 'Source/Resources/40_BD0/SectorTail.bin', 16268), (41, 16152, 16384, 'Source/Resources/41_BD1/SectorTail.bin', 16152), (42, 16248, 16384, 'Source/Resources/42_BD2/SectorTail.bin', 16248), (43, 12048, 12288, 'Source/Resources/43_BD3/SectorTail.bin', 12048))

MIRROR_STARTS = {
    5: 0x0D18,
    6: 0x3C6A,
    8: 0x1521,
    21: 0x0CC8,
    22: 0x18DE,
    23: 0x174A,
    24: 0x2754,
    30: 0x47F4,
}


def check_mirrors(sources):
    total = 0
    for slot, start, end, _, declared in RANGES:
        if slot not in MIRROR_STARTS:
            continue
        source = sources[slot]
        length = end - start
        matching_start = MIRROR_STARTS[slot]
        assert matching_start + length <= declared
        assert source[start:end] == source[matching_start:matching_start + length]
        total += length
    assert total == 1061
    # Исходный потребитель ищет подчёркивание, в копии LANG такого байта нет.
    assert b'_' not in sources[5][0x0F18:0x1000]
    return total
