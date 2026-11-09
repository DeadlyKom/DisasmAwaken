"""Страница отсечённого контура и три генерируемые страницы предпросмотра."""
import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x07FC, 0x0800, 'Source/Resources/06_D3D/Unclassified07FC_0800.bin', None,
     'Unknown, четыре исходных байта между рабочей очередью и контуром'),
    (0x0800, 0x0900, 'Source/D3D/Resources/InitialPreviewContour.bin', 'INITIAL_PREVIEW_CONTOUR',
     'исходная страница C8 до копирования и отсечения контуров'),
    (0x0900, 0x0A00, 'Source/D3D/Resources/InitialPreviewRowHigh.bin', 'INITIAL_PREVIEW_ROW_HIGH',
     'исходная страница C9 до построения старших байтов адресов строк'),
    (0x0A00, 0x0B00, 'Source/D3D/Resources/InitialPreviewRowLow.bin', 'INITIAL_PREVIEW_ROW_LOW',
     'исходная страница CA до построения младших байтов адресов строк'),
    (0x0B00, 0x0C00, 'Source/D3D/Resources/InitialPreviewColumn.bin', 'INITIAL_PREVIEW_COLUMN',
     'исходная страница CB до построения байтовых столбцов'),
    (0x0C00, 0x0DB0, 'Source/Resources/06_D3D/Unclassified0C00_0DB0.bin', None,
     'Unknown, диапазон до исходных масок пикселей сохранён буквально'),
)


if __name__ == '__main__':
    reports = ROOT / 'Tools/Disasm/Reports'
    setup = json.loads((reports / 'PreviewSetupVerification.json').read_bytes())
    clip = json.loads((reports / 'PreviewClipIntersectionsVerification.json').read_bytes())
    assert setup['passed'] and setup['real_clip_and_table_callees']
    assert setup['independent_full_memory_and_register_oracle']
    assert clip['passed'] and clip['entire_output_page_and_guard_bytes_checked']
    publish(slot=6, origin=0xC000, ranges=((0x07FC, 0x0DB0),), resources=RESOURCES,
            tag='PreviewRenderWorkspace', resource_module='ClassifyPreviewRenderWorkspace',
            resource_name='PREVIEW_RENDER_INITIAL_STORAGE',
            proof=dict(bank=4, contour_page_bytes=256, generated_address_table_bytes=768,
                       unknown_neighbor_bytes=436))
