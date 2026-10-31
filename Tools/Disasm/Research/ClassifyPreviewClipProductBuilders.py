"""Выделение 124 исходных байтов четырёх производителей, соседние пересечения остаются сохранены."""
import PreviewClipProductBuilderFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipProductBuilders','Source/Resources/06_D3D/BeforeClipCorners.bin',(
  (0x2171,0x25E8,None,'Source/Resources/06_D3D/BeforeClipProductBuilders.bin'),
  *((p-0xC000,p+31-0xC000,p,'Source/D3D/'+facts.FUNCTIONS[p][0]+'.asm') for p,_,_,_ in facts.ITEMS),
  (0x2664,0x27B4,None,'Source/Resources/06_D3D/BeforeClipCorners.bin')),
  'PreviewClipProductBuildersVerification')
