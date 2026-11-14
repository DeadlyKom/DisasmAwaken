"""Публикует три исходных выравнивания файла KARTA."""
import json

from CheckIntro import ROOT


FORMAT = 'MAP_AUTHORED_ALIGNMENT'
RESOURCES = (
    (0x1418, 0x1420, 'Source/Map/Resources/LineMaskAlignment.bin', FORMAT,
     'Заполнение до 16-байтовой границы таблицы масок ld1l'),
    (0x1DB0, 0x1E00, 'Source/Map/Resources/ClipPageAlignment.bin', FORMAT,
     'Заполнение ADRXX00 перед младшей страницей таблицы отсечения l95'),
    (0x28BE, 0x2900, 'Source/Map/Resources/DistanceTableAlignment.bin', FORMAT,
     'Заполнение ADRXX00 перед таблицей квадратов CIRCL_TB.dat'),
)


if __name__ == '__main__':
    from ClassifyStationWorkspaceResources import publish

    ranges = tuple(row[:2] for row in RESOURCES)
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/MapArchivedAlignmentVerification.json').read_bytes())
    assert proof['passed'] and proof['published_ranges'] == [list(row) for row in ranges]
    publish(slot=7, origin=0xC000, ranges=ranges, resources=RESOURCES,
            tag='MapArchivedAlignment', resource_module='ClassifyMapArchivedAlignment',
            resource_name='MAP_ARCHIVED_ALIGNMENT', proof=dict(archive_proof='MapArchivedAlignmentVerification.json'))
