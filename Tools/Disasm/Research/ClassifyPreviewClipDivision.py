"""Выделение только 181 байта доказанного делителя, диспетчер отрезка сохраняется отдельно."""
import PreviewClipDivisionFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipDivision','Source/Resources/06_D3D/AfterFaceProduct.bin',(
  (0x2A01,0x2AB6,0xEA01,'Source/D3D/DividePreviewClip32To16.asm'),
  (0x2AB6,0x2B10,None,'Source/Resources/06_D3D/PreviewClipSegmentDispatcher.bin')),
  'PreviewClipDivisionVerification')
