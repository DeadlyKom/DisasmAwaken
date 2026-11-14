"""Публикует исходный хвост HIPERJMP и выравнивание перед CSTB."""
import json

from CheckIntro import ROOT


RESOURCES = (
    (0x21C0, 0x2500, 'Source/Voxel/Resources/TeleportResourceTail.bin', 'VOXEL_TELEPORT_RESOURCE_TAIL',
     'Исходный хвост HIPERJMP.van после 13 кадров телепорта'),
    (0x2965, 0x2A00, 'Source/Voxel/Resources/CosineTableAlignment.bin', 'VOXEL_COSINE_TABLE_ALIGNMENT',
     'Заполнение ADRXX00 перед исходной таблицей CSTB.dat'),
)


if __name__ == '__main__':
    from ClassifyStationWorkspaceResources import publish

    proof = json.loads((ROOT / 'Tools/Disasm/Reports/VoxelArchivedLayoutVerification.json').read_bytes())
    assert proof['passed'] and proof['full_file_match_bytes'] == 0x2C00
    assert (proof['teleport']['tail_offset'], proof['teleport']['tail_bytes']) == (0x21C0, 0x340)
    assert (proof['alignment']['offset'], proof['alignment']['bytes']) == (0x2965, 155)
    publish(slot=20, origin=0xC000, ranges=((0x21C0, 0x2500), (0x2965, 0x2A00)),
            resources=RESOURCES, tag='VoxelArchivedLayout', resource_module='ClassifyVoxelArchivedLayout',
            resource_name='VOXEL_ARCHIVED_LAYOUT', proof=dict(archive_proof='VoxelArchivedLayoutVerification.json',
                                                              actual_game_consumers_proved=False))
