"""Типизация одного сохранённого байта ориентации, без изменения соседнего состояния."""
import PreviewFaceGateData as facts
from ClassifyPreviewSceneRecords import apply


if __name__=='__main__':
 apply(facts,'PreviewFaceGateData',(
  ('Source/Resources/06_D3D/AfterEdgeMode.bin',(
   (0x271,0x27B,'unclassified','Source/Resources/06_D3D/BeforeFaceGateState.bin'),
   (0x27B,0x27C,'typed_data',facts.TABLES[0][1]),
   (0x27C,0x300,'unclassified','Source/Resources/06_D3D/AfterFaceGateState.bin'))),),
  'PreviewInsideFaceStreamVerification','PreviewFaceStream')
