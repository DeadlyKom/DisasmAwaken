"""Выделение только полного быстрого прохода, путь с отсечением остаётся исходным бинарным ресурсом."""
import PreviewInsideFaceStreamFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewInsideFaceStream','Source/Resources/06_D3D/BeforeFaceCodes.bin',(
  (0x1BE9,0x1D4F,None,'Source/Resources/06_D3D/BeforeInsideFaceStream.bin'),
  (0x1D4F,0x1DFD,0xDD4F,'Source/D3D/RenderPreviewInsideFaces.asm')),
  'PreviewInsideFaceStreamVerification')
