"""Типизация трёх исходных байтов без присвоения назначения оставшемуся хвосту объекта."""
import PreviewFrameData as facts
from ClassifyPreviewSceneRecords import apply


if __name__=='__main__':
 apply(facts,'PreviewFrameData',(('Source/Resources/06_D3D/AfterPixelMasks.bin',(
  (0xDC0,0xDC7,'unclassified','Source/Resources/06_D3D/BeforePrimaryAngles.bin'),
  (0xDC7,0xDCA,'typed_data',facts.TABLES[0][1]),(0xDCA,0xE40,'unclassified','Source/Resources/06_D3D/AfterPrimaryAngles.bin'))),),
  'PreviewFrameVerification','PreviewFrame')
