"""Выделение всех четырёх проверенных пересечений, без замены настроенных операндов значениями модели."""
import PreviewClipIntersectionFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipIntersections','Source/Resources/06_D3D/BeforeClipCorners.bin',tuple(
  (p-0xC000,end-0xC000,p,'Source/D3D/'+facts.FUNCTIONS[p][0]+'.asm') for p,_,end in facts.ITEMS),
  'PreviewClipIntersectionsVerification')
