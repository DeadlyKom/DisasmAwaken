"""Точечное выделение двух доказанных обходов из двух оставшихся бинарных участков."""
import PreviewModelWalkFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewModelWalk',(
  ('Source/Resources/06_D3D/BeforePlanarProducts.bin',((0x1819,0x185E,0xD819,'Source/D3D/ProjectPlanarModelGroups.asm'),)),
  ('Source/Resources/06_D3D/BeforeVertexProducts.bin',((0x1896,0x18BE,0xD896,'Source/D3D/ProjectPreviewModelGroups.asm'),))),
  None,'PreviewModelWalkVerification')
