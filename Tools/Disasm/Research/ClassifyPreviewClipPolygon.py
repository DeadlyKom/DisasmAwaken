"""Выделение обхода с сохранением общего RET и порядка двух смежных include."""
import PreviewClipPolygonFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipPolygon','Source/Resources/06_D3D/PreviewClipPolygonDispatcher.bin',(
  (0x2171,0x21EB,0xE171,'Source/D3D/ClipPreviewPolygon.asm'),),'PreviewClipPolygonVerification')
