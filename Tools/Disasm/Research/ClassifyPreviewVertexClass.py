"""Точечное выделение классификатора, соседняя геометрия остаётся без изменений."""
import PreviewVertexClassFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewVertexClass','Source/Resources/06_D3D/AfterProjectionScale.bin',(
  (0x1BE9,0x1F46,None,'Source/Resources/06_D3D/BeforeVertexClass.bin'),
  (0x1F46,0x1FA6,0xDF46,'Source/D3D/ClassifyPreviewVertices.asm'),
  (0x1FA6,0x2011,None,'Source/Resources/06_D3D/AfterVertexClass.bin')),
  'PreviewVertexClassVerification')
