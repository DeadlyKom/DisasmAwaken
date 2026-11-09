"""Исходные байты областей очереди граней и результата отсечения ACTION."""
import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x2EC8, 0x2F00, 'Source/Resources/17_ACTION/Unclassified2EC8_2F00.bin', None,
     'Unknown, хвост перед страницей рабочих узлов'),
    (0x2F00, 0x2FFC, 'Source/Action/Resources/InitialRenderQueuePool.bin', 'INITIAL_ACTION_RENDER_QUEUE',
     'исходные 252 байта области восемнадцати рабочих узлов'),
    (0x2FFC, 0x3000, 'Source/Resources/17_ACTION/Unclassified2FFC_3000.bin', None,
     'Unknown, при FreeOffset=FC вставка не создаёт узел'),
    (0x3000, 0x3100, 'Source/Action/Resources/InitialClipOutputPage.bin', 'INITIAL_ACTION_CLIP_OUTPUT',
     'исходные 256 байтов рабочей страницы упакованных пар'),
)


if __name__ == '__main__':
    reports = ROOT / 'Tools/Disasm/Reports'
    queue = json.loads((reports / 'ActionRenderQueueInsertVerification.json').read_bytes())
    clip = json.loads((reports / 'ActionClipIntersectionsVerification.json').read_bytes())
    assert queue['passed'] and queue['node_stride'] == 14 and queue['tested_node_counts'] == list(range(19))
    assert clip['passed'] and clip['all_output_offsets'] and clip['every_physical_ram_byte_and_write_multiplicity_checked']
    publish(slot=17, origin=0x6000, ranges=((0x2EC8, 0x3100),), resources=RESOURCES,
            tag='ActionRenderWorkspace', resource_module='ClassifyActionRenderWorkspace',
            resource_name='ACTION_RENDER_INITIAL_STORAGE',
            proof=dict(runtime_queue_nodes=18, runtime_node_stride=14, clip_output_page_bytes=256,
                       unknown_neighbor_bytes=60))
