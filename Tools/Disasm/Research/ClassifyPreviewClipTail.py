"""Выделение восьми проверенных помощников, разности кэшированных произведений остаются исходными байтами."""
import PreviewClipTailFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipTail','Source/Resources/06_D3D/BeforeClipUnwind.bin',(
  (0x2171,0x27B4,None,'Source/Resources/06_D3D/BeforeClipCorners.bin'),
  (0x27B4,0x27BF,0xE7B4,'Source/D3D/AppendPreviewClipTopLeft.asm'),
  (0x27BF,0x27CA,0xE7BF,'Source/D3D/AppendPreviewClipTopRight.asm'),
  (0x27CA,0x27D5,0xE7CA,'Source/D3D/AppendPreviewClipBottomLeft.asm'),
  (0x27D5,0x27E0,0xE7D5,'Source/D3D/AppendPreviewClipBottomRight.asm'),
  (0x27E0,0x2830,None,'Source/Resources/06_D3D/ClipProductDifferences.bin'),
  (0x2830,0x283B,0xE830,'Source/D3D/SubtractPreviewClipColumns.asm'),
  (0x283B,0x2846,0xE83B,'Source/D3D/SubtractPreviewClipRows.asm'),
  (0x2846,0x284E,0xE846,'Source/D3D/AppendPreviewClipSecond.asm'),
  (0x284E,0x285D,0xE84E,'Source/D3D/AppendPreviewClipPoint.asm')),
  'PreviewClipTailVerification')
