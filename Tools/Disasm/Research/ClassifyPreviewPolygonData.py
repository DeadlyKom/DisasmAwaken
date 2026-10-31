"""Типизация только 18 исходных байтов трёх физических записей заливки."""
import PreviewPolygonData as facts
from ClassifyPreviewSceneRecords import apply


if __name__=='__main__':
 def typed(t):return t[2],t[3],'typed_data',t[1]
 apply(facts,'PreviewPolygonData',(
  ('Source/Resources/06_D3D/BeforeEdgeEndpoints.bin',(
   (0x21E,0x22B,'unclassified','Source/Resources/06_D3D/BeforeContourSize.bin'),typed(facts.TABLES[0]),
   (0x22C,0x23B,'unclassified','Source/Resources/06_D3D/BetweenContourSizeMode.bin'),typed(facts.TABLES[1]),
   (0x23C,0x24B,'unclassified','Source/Resources/06_D3D/AfterFillMode.bin'))),
  ('Source/Resources/06_D3D/BeforePolygonSpan.bin',(
   (0x102C,0x1100,'unclassified','Source/Resources/06_D3D/BeforeFillPatterns.bin'),typed(facts.TABLES[2]),
   (0x1110,0x11C0,'unclassified','Source/Resources/06_D3D/AfterFillPatterns.bin')))),
  'PreviewPolygonVerification','PreviewPolygonFill')
