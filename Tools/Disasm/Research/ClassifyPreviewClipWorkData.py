"""Типизация 12 существующих байтов отсечения, без новых структур и новых областей памяти."""
import PreviewClipWorkData as facts
from ClassifyPreviewSceneRecords import apply


if __name__=='__main__':
 def typed(t):return t[2],t[3],'typed_data',t[1]
 apply(facts,'PreviewClipWorkData',(
  ('Source/Resources/06_D3D/BetweenContourSizeMode.bin',(
   typed(facts.TABLES[0]),(0x231,0x23B,'unclassified','Source/Resources/06_D3D/AfterClipFirst.bin'))),
  ('Source/Resources/06_D3D/AfterFillMode.bin',(
   typed(facts.TABLES[1]),(0x241,0x24B,'unclassified','Source/Resources/06_D3D/AfterClipSecond.bin'))),
  ('Source/Resources/06_D3D/BetweenEdgeEndpointsMode.bin',(
   typed(facts.TABLES[2]),(0x251,0x26F,'unclassified','Source/Resources/06_D3D/AfterClipCorners.bin')))),
  'PreviewClipSegmentVerification','PreviewClipSegment')
