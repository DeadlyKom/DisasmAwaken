"""Глиф либо четыре символа клавиши, независимые статусы и XOR всего экрана."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckGlyphRenderer import and_flags,compare_flags
from CheckInsetFrame import bitmap_address
from skoolkit.simutils import PC,SP


def glyph(memory,code,x,y,width,height,origin,screen=None):
 """Порядок отказов исходного DrawGlyph, без исполнения его инструкций."""
 if y>=height:return x,2,and_flags(y)
 total=x+memory[0x8900+code]
 if total>255 or total>=width:return x,3,and_flags(total&255)
 px,py=(origin[0]+x)&65535,(origin[1]+y)&65535;x=total&255
 if px&0x8000:return x,0,0x45
 if px>>8:return x,0,0x44
 if py&0x8000:return x,0,0x45
 if py>>8:return x,1,0
 if py>=185:return x,1,compare_flags(py,185)
 if screen is not None:
  for row,bits in enumerate(memory[0x8A00+8*code:0x8A08+8*code]):
   for bit in range(8):
    if px+bit<256 and bits&(128>>bit):screen[bitmap_address(py+row,(px+bit)//8)-0x4000]^=128>>((px+bit)&7)
 return x,0,0x45


def reference(memory,code,x,y,width,height,origin,screen=None):
 codes=[code] if code>=33 else list(memory[0xBE1B+(((code-30)*4)&255):0xBE1F+(((code-30)*4)&255)])
 for char in codes:x,a,f=glyph(memory,char,x,y,width,height,origin,screen)
 return x,a,f,codes


def main():
 _,_,base=make_context();fixture=Fixture(base);m=fixture.memory;s=fixture.sim;initial=fixture.initial;counts=collections.Counter()
 geometries=((0,8,188,192,(3,3)),(0,8,0,192,(3,3)),(0,8,8,192,(3,3)),(250,8,255,192,(0,0)),
  (0,8,188,8,(3,3)),(0,8,188,192,(250,176)),(0,8,188,192,(256,0)),(0,8,188,192,(0,256)),
  (0,8,188,192,(-1,0)),(0,8,188,192,(0,-9)))
 for code in range(256):
  for x,y,width,height,origin in geometries:
   put(m,0x4000,bytes([0x96])*6912);put(m,0x7FFE,(255,63));s.registers[:]=initial;r=s.registers;r[0]=code
   for a,v in ((0x6320,x),(0x6321,y),(0xAEB3,width),(0xAEAB,height),(0xAEBB,origin[0]&255),(0xAEBF,(origin[0]>>8)&255),(0xAEC7,origin[1]&255),(0xAECB,(origin[1]>>8)&255)):m[a]=v
   put(m,0xAED5,(0x68,0x48,0x26));screen=bytearray(m[0x4000:0x5B00]);rx,ra,rf,codes=reference(m,code,x,y,width,height,origin,screen);calls=[];r[PC]=0xBDF0
   for _ in range(10000):
    if r[PC]==0x3FFF:break
    if r[PC]==0xAE8D:calls.append(r[0])
    s.run()
   else:raise AssertionError('key_label_not_returned')
   assert (r[0],r[1],m[0x6320],m[0x6321])==(ra,rf,rx,y),(code,origin,r[:2],(ra,rf))
   assert calls==codes and bytes(m[0x4000:0x5B00])==bytes(screen) and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
   counts['direct_glyph' if code>=33 else 'four_glyph_lookup']+=1
 report=dict(passed=True,cases_by_path=dict(counts),all_256_input_codes=True,all_four_calls_even_after_failure=True,
  wrapped_byte_index_below_1e_checked=True,three_original_labels=['ENT ','SS  ','SP  '],independent_glyph_status_and_entire_bitmap=True,
  exact_preserved_context=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/KeyLabelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
