"""Типизация 16 исходных байтов четырёх произведений, оба десятибайтовых промежутка сохранены."""
import PreviewClipProductData as facts
from ClassifyPreviewSceneRecords import apply


if __name__=='__main__':
 def typed(t):return t[2],t[3],'typed_data',t[1]
 apply(facts,'PreviewClipProductData',(
  ('Source/Resources/06_D3D/AfterFaceGateState.bin',(
   (0x27C,0x2DC,'unclassified','Source/Resources/06_D3D/BeforeClipProducts.bin'),typed(facts.TABLES[0]),
   (0x2E0,0x2EA,'unclassified','Source/Resources/06_D3D/BetweenClipTopBottom.bin'),typed(facts.TABLES[1]),typed(facts.TABLES[2]),
   (0x2F0,0x2FA,'unclassified','Source/Resources/06_D3D/BetweenClipLeftWords.bin'),typed(facts.TABLES[3]),typed(facts.TABLES[4]))),),
  'PreviewClipProductDifferencesVerification','PreviewClipProducts')
