"""Выделение EAB6..EB0F после проверки настоящего префикса и полного сегмента."""
import PreviewClipDispatchFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipDispatch','Source/Resources/06_D3D/PreviewClipSegmentDispatcher.bin',(
  (0x2AB6,0x2B10,0xEAB6,'Source/D3D/DispatchPreviewClipSegment.asm'),),'PreviewClipDispatchVerification')
