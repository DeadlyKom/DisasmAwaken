"""Публикует 67 нулей ADRXX00 за границей переноса состояния ACTION."""
import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x3DBD, 0x3E00, 'Source/Action/Resources/ObjectTablePageAlignment.bin', 'ACTION_OBJECT_TABLE_ALIGNMENT',
     'Остаток нулевого выравнивания ADRXX00 перед страницей указателей OBJECT3D'),
)


if __name__ == '__main__':
    report = json.loads((ROOT / 'Tools/Disasm/Reports/ActionArchivedObjectTableVerification.json').read_bytes())
    ranges = tuple(item[:2] for item in RESOURCES)
    assert report['passed'] and report['published_ranges'] == [list(row) for row in ranges]
    publish(slot=17, origin=0x6000, ranges=ranges, resources=RESOURCES, tag='ActionObjectTableAlignment',
            resource_module='ClassifyActionObjectTableAlignment', resource_name='ACTION_OBJECT_TABLE_ALIGNMENT',
            proof=dict(archive_proof='ActionArchivedObjectTableVerification.json'))
