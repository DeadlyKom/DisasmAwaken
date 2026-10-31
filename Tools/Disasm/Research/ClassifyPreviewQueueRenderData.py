"""Типизация только трёх существующих параметров, хвост перед ByteCount остаётся исходным."""
import PreviewQueueRenderData as facts
from ClassifyPreviewSceneRecords import apply


if __name__=='__main__':
 apply(facts,'PreviewQueueRenderData',(('Source/Resources/06_D3D/BeforeContourSize.bin',(
  (0x21E,0x221,'typed_data',facts.TABLES[0][1]),(0x221,0x22B,'unclassified','Source/Resources/06_D3D/BeforeContourSizeAfterAngles.bin'))),),
  'PreviewQueueRenderVerification','PreviewQueueRender')
