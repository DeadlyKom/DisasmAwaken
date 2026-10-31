"""Типизация двух физических записей с сохранением десятибайтового промежутка между ними."""
import PreviewLineWorkData as facts
from ClassifyPreviewSceneRecords import apply


if __name__=='__main__':
 apply(facts,'PreviewLineWorkData',(('Source/Resources/06_D3D/AfterClipCorners.bin',(
  (0x251,0x25B,'unclassified','Source/Resources/06_D3D/BeforeLineCoordinates.bin'),
  (0x25B,0x261,'typed_data',facts.TABLES[0][1]),
  (0x261,0x26B,'unclassified','Source/Resources/06_D3D/BetweenLineWords.bin'),
  (0x26B,0x26F,'typed_data',facts.TABLES[1][1]))),),'PreviewClippedFaceStreamVerification','PreviewClippedFaceStream')
