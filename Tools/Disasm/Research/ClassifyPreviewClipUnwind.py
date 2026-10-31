"""Выделение только проверенного десятибайтового специального выхода."""
import PreviewClipUnwindFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipUnwind','Source/Resources/06_D3D/BeforeFaceProduct.bin',(
  (0x2171,0x285D,None,'Source/Resources/06_D3D/BeforeClipUnwind.bin'),
  (0x285D,0x2867,0xE85D,'Source/D3D/UnwindPreviewClipFrame.asm'),
  (0x2867,0x2869,None,'Source/Resources/06_D3D/BeforeFaceProduct.bin')),
  'PreviewClipUnwindVerification')
