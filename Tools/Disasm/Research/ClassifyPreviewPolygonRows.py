"""Выделение только развёрнутой строки и общего цикла, две цепочки сохраняются исходными байтами."""
import PreviewPolygonRowsFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewPolygonRows','Source/Resources/06_D3D/BeforeSlopeDivision.bin',(
  (0x102C,0x11C0,None,'Source/Resources/06_D3D/BeforePolygonSpan.bin'),
  (0x11C0,0x1207,0xD1C0,'Source/D3D/WritePreviewPolygonSpan.asm'),
  (0x1207,0x1282,0xD207,'Source/D3D/StepPreviewPolygonRow.asm'),
  (0x1282,0x14DF,None,'Source/Resources/06_D3D/AfterPolygonRows.bin')),
  'PreviewPolygonSpanVerification')
