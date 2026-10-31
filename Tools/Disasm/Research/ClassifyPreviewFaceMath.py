"""Выделение двух арифметических фрагментов, соседние отсечения и деления не изменяются."""
import json
import PreviewFaceMathFacts as facts
from ClassifyD3DFragments import ROOT,apply


if __name__=='__main__':
 reports=ROOT/'Tools/Disasm/Reports'
 product=json.loads((reports/'PreviewFaceProductVerification.json').read_text('utf-8'));orientation=json.loads((reports/'PreviewFaceOrientationVerification.json').read_text('utf-8'))
 assert product['passed'] and orientation['passed']
 (reports/'PreviewFaceMathVerification.json').write_text(json.dumps(dict(passed=True,product_cases=product['cases'],orientation_cases=orientation['cases'],real_nested_multipliers=True,assembly_executed=False),indent=2)+'\n','utf-8')
 apply(facts,'PreviewFaceMath',(
  ('Source/Resources/06_D3D/BeforeCoordinateMultiply.bin',(
   (0x2171,0x2869,None,'Source/Resources/06_D3D/BeforeFaceProduct.bin'),
   (0x2869,0x2A01,0xE869,'Source/D3D/MultiplyPreviewSignedWords.asm'),
   (0x2A01,0x2B10,None,'Source/Resources/06_D3D/AfterFaceProduct.bin'))),
  ('Source/Resources/06_D3D/AfterVertexClass.bin',((0x1FA6,0x2011,0xDFA6,'Source/D3D/ComputePreviewFaceOrientation.asm'),))),
  None,'PreviewFaceMathVerification')
