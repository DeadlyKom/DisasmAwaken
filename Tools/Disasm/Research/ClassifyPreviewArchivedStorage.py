"""Публикует исходные резервы и выравнивания из авторской разметки D3D."""
import json

from CheckIntro import ROOT


RESERVE = 'D3D_AUTHORED_RESERVE'
ALIGNMENT = 'D3D_AUTHORED_ALIGNMENT'
SCENE_GAPS = (
    (0x0203, 0x020C, 'ScenePageAfterSeed'),
    (0x0221, 0x022B, 'ScenePageAfterAngles'),
    (0x0231, 0x023B, 'ScenePageAfterClipFirst'),
    (0x0241, 0x024B, 'ScenePageAfterClipSecond'),
    (0x0251, 0x025B, 'ScenePageAfterCorners'),
    (0x0261, 0x026B, 'ScenePageAfterLineCoords'),
    (0x0271, 0x027B, 'ScenePageAfterEdgeMode'),
    (0x027C, 0x02DC, 'ScenePageBeforeClipProducts'),
    (0x02E0, 0x02EA, 'ScenePageBetweenTopBottom'),
    (0x02F0, 0x02FA, 'ScenePageBetweenLeftRight'),
)
ROWS = (
    *((a, b, name, RESERVE, 'Исходные байты резерва L90..L91 страницы C2') for a, b, name in SCENE_GAPS),
    (0x07FC, 0x0800, 'QueuePageTail', RESERVE, 'Последние четыре байта резерва L9D за узлами очереди'),
    (0x0DCA, 0x0E00, 'PreviewObjectRecordTail', RESERVE, 'Хвост первой записи Carsb после десяти начальных байтов'),
    (0x0E02, 0x0E40, 'PreviewObjectEndTail', RESERVE, 'Хвост второй записи Carsb после маркера 8080'),
    (0x0F04, 0x1000, 'DrawStatePageAlignment', ALIGNMENT, 'Выравнивание ADRXX00 перед указателями моделей L97'),
    (0x102C, 0x1100, 'ModelPointerPageAlignment', ALIGNMENT, 'Выравнивание ADRXX00 между DATA3D и XR2'),
    (0x1110, 0x11C0, 'FillPageCodeAlignment', ALIGNMENT, 'Конец выравнивания XR2 перед рисователем по D1C0'),
)
RESOURCES = tuple((a, b, f'Source/D3D/Resources/{name}.bin', kind, note)
                  for a, b, name, kind, note in ROWS)


if __name__ == '__main__':
    from ClassifyStationWorkspaceResources import publish

    proof = json.loads((ROOT / 'Tools/Disasm/Reports/PreviewArchivedStorageVerification.json').read_bytes())
    assert proof['passed'] and proof['matched_ranges'] == [list(row[:2]) for row in ROWS]
    publish(slot=6, origin=0xC000, ranges=tuple(row[:2] for row in ROWS), resources=RESOURCES,
            tag='PreviewArchivedStorage', resource_module='ClassifyPreviewArchivedStorage',
            resource_name='PREVIEW_ARCHIVED_STORAGE', proof=dict(archive_proof='PreviewArchivedStorageVerification.json',
                                                                  actual_game_consumers_proved=False))
