"""Выделение только четырёх проверенных разностей, без экспорта соседних обработчиков."""
import PreviewClipProductDifferenceFacts as facts
from ClassifyD3DFragments import apply


if __name__=='__main__':
 apply(facts,'PreviewClipProductDifferences','Source/Resources/06_D3D/ClipProductDifferences.bin',tuple(
  (p-0xC000,p+20-0xC000,p,'Source/D3D/'+facts.FUNCTIONS[p][0]+'.asm') for p,_,_ in facts.PAIRS),
  'PreviewClipProductDifferencesVerification')
