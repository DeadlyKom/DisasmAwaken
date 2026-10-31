"""Выделение пяти проверенных блоков цепочек, подготовка D41B остаётся исходным бинарным ресурсом."""
import PreviewPolygonEdgesFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewPolygonEdges','Source/Resources/06_D3D/AfterPolygonRows.bin',(
  (0x1282,0x1285,0xD282,'Source/D3D/SelectPreviewRightEdge.asm'),
  (0x1285,0x128C,0xD285,'Source/D3D/WrapPreviewLeftEdge.asm'),
  (0x128C,0x134B,0xD28C,'Source/D3D/UpdatePreviewLeftEdge.asm'),
  (0x134B,0x1350,0xD34B,'Source/D3D/WrapPreviewRightEdge.asm'),
  (0x1350,0x140F,0xD350,'Source/D3D/UpdatePreviewRightEdge.asm'),
  (0x140F,0x14DF,None,'Source/Resources/06_D3D/BeforeSlopeDivision.bin')),
  'PreviewPolygonEdgesVerification')
