"""Выделение последнего обнаруженного внешнего входа D3D без запуска сборки."""
import PreviewFrameFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewFrame','Source/Resources/06_D3D/BeforePreviewThird.bin',(
  (0x207F,0x20B5,0xE07F,'Source/D3D/RenderPreviewFrame.asm'),),'PreviewFrameVerification')
