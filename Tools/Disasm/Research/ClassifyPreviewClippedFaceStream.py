"""Точечное выделение полного DBE9 после композиционной проверки bitmap и состояния линии."""
import PreviewClippedFaceStreamFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClippedFaceStream','Source/Resources/06_D3D/BeforeInsideFaceStream.bin',(
  (0x1BE9,0x1D4F,0xDBE9,'Source/D3D/RenderPreviewClippedFaces.asm'),),'PreviewClippedFaceStreamVerification')
