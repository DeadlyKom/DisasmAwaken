"""Точечное выделение накопления кодов, оба соседних графических прохода сохранены."""
import PreviewFaceCodesFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewFaceCodes','Source/Resources/06_D3D/BeforeVertexClass.bin',(
  (0x1BE9,0x1DFD,None,'Source/Resources/06_D3D/BeforeFaceCodes.bin'),
  (0x1DFD,0x1E1C,0xDDFD,'Source/D3D/CollectPreviewFaceCodes.asm'),
  (0x1E1C,0x1F46,None,'Source/Resources/06_D3D/BeforeVertexClass.bin')),
  'PreviewFaceCodesVerification')
