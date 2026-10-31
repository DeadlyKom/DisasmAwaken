"""Выделение последней подготовки и двух верхних переходников, без изменения раскладки."""
import PreviewPolygonPreparationFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewPolygonPreparation','Source/Resources/06_D3D/BeforeSlopeDivision.bin',(
  (0x140F,0x1416,0xD40F,'Source/D3D/WrapPreviewTopLeft.asm'),
  (0x1416,0x141B,0xD416,'Source/D3D/WrapPreviewTopRight.asm'),
  (0x141B,0x14DF,0xD41B,'Source/D3D/FillPreviewPolygon.asm')),
  'PreviewPolygonPreparationVerification')
