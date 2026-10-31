"""Выделение только проверенного делителя, остаток исходной области сохраняется."""
import PreviewSlopeDivisionFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewSlopeDivision','Source/Resources/06_D3D/AfterModelPointers.bin',(
  (0x102C,0x14DF,None,'Source/Resources/06_D3D/BeforeSlopeDivision.bin'),
  (0x14DF,0x1518,0xD4DF,'Source/D3D/DividePreviewSlopeByte.asm')),
  'PreviewSlopeDivisionVerification')
