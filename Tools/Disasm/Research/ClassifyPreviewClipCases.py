"""Точечное выделение проверенных обработчиков, остальная часть E171 сохраняется бинарно."""
import PreviewClipCaseFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipCases','Source/Resources/06_D3D/BeforeClipProductBuilders.bin',(
  (0x2171,0x21EB,None,'Source/Resources/06_D3D/PreviewClipPolygonDispatcher.bin'),
  (0x21EB,0x25E8,0xE1EB,'Source/D3D/PreviewClipCases.asm')),'PreviewClipCaseSemanticsVerification')
