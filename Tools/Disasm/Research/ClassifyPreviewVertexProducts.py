"""Выделение двух проверенных поставщиков, без экспорта остального проекта."""
import PreviewVertexProductsFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewVertexProducts','Source/Resources/06_D3D/BeforeVertexGroup.bin',(
  (0x1819,0x185E,None,'Source/Resources/06_D3D/BeforePlanarProducts.bin'),
  (0x185E,0x1896,0xD85E,'Source/D3D/ProjectPlanarVertexGroup.asm'),
  (0x1896,0x18BE,None,'Source/Resources/06_D3D/BeforeVertexProducts.bin'),
  (0x18BE,0x1908,0xD8BE,'Source/D3D/PreparePreviewVertexProducts.asm')),
  'PreviewVertexProductsVerification')
