"""Выделение восстановления SP и прохода очереди после двух независимых проверок."""
import json
from pathlib import Path
import PreviewQueueRenderFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 root=Path(__file__).resolve().parents[3]
 assert json.loads((root/'Tools/Disasm/Reports/PreviewStackRestoreVerification.json').read_text('utf-8'))['passed']
 apply(facts,'PreviewQueueRender','Source/Resources/06_D3D/BeforeModelMatrix.bin',(
  (0x2EEE,0x2EF1,0xEEEE,'Source/D3D/RestorePreviewStack.asm'),(0x2EF1,0x2F5E,0xEEF1,'Source/D3D/RenderPreviewQueue.asm')),'PreviewQueueRenderVerification')
