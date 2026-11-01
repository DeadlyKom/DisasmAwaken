"""Исходные HELP-обёртки, независимые указатели, раскладка и счётчик строк в AF'."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckJustifiedText import reference as justified
from CheckTextStream import reference as stream
from skoolkit.simutils import PC,SP


def main():
 _,_,base=make_context();raw=payload(8);base[7][0x1B00:0x1B00+len(raw)]=list(raw);f=Fixture(base);m=f.memory;s=f.sim;initial=f.initial
 widths=list(m[0x8900:0x8A00]);counts=collections.Counter();columns=(2,4,8,16,32)
 def prepare(width,height,mode):
  m.out7ffd(0x17);m[0x6306]=0x17;put(m,0x4000,bytes(6912));put(m,0x7FFE,(255,63));s.registers[:]=initial
  for address,value in ((0xAEAB,height),(0xAEB3,width),(0xAEBB,0),(0xAEBF,0),(0xAEC7,0),(0xAECB,0),(0xBD26,mode),(0xBD4F,0xC3)):m[address]=value
  for address,value in zip((0xBD73,0xBD7E,0xBD89,0xBD94,0xBD9F),columns):m[address]=value
  put(m,0xAED5,(0x68,0x48,0x26));put(m,0x6320,(0xA5,0xA7))
 def execute(start):
  r=s.registers;r[PC]=start;calls=[]
  for _ in range(500000):
   pc=r[PC]
   if pc==0x3FFF:break
   if pc==0xAE8D:calls.append(r[0])
   s.run()
  else:raise AssertionError(('instruction_limit',hex(start),hex(r[PC])))
  assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and r[14]==initial[14] and r[26:28]==initial[26:28] and m.o7ffd==0x17
  return r,calls
 def line(index,text,width=96,height=192):
  prepare(width,height,1);pointer=0 if text is None else 0xE3E2
  put(m,0xDB7C+index*2,pointer.to_bytes(2,'little'));cache=bytes(m[0xDB7C:0xE37C]);r=s.registers;r[6],r[7]=index>>8,index&255
  if text is not None:
   text=list(text)+[10]*1024;put(m,pointer,text);expected=justified(0xADCD,text,widths,0,8,width,height,0x0800,0xDB,0x7C)
  r,calls=execute(0xDB42)
  if text is None:
   assert tuple(r[:8])==(0,0x44,8,0,0xDB,0x7C,0,0) and not calls and (m[0x6320],m[0x6321])==(0,8);counts['null_pointer']+=1
  else:
   consumed,x,y,a,flags,bc,d,e,glyphs=expected
   assert tuple(r[:8])==(a,flags,bc>>8,bc&255,d,e,(pointer+consumed)>>8,(pointer+consumed)&255),(index,r[:8],expected)
   assert (m[0x6320],m[0x6321])==(x,y) and calls==glyphs;counts['indexed_output']+=1
  assert bytes(m[0xDB7C:0xE37C])==cache and r[16:18]==initial[16:18]
 def record(selector,text,width=96,height=192,mode=1,high=0,original=False):
  prepare(width,height,mode);prefix=bytes([13])*(selector+1);data=list(raw[0x87C:0x8E2] if original else prefix+text)+[10]*1024;put(m,0xE37C,data)
  # Независимый выбор CR-записи и обычный поток, исходный код использует только младший байт HL.
  offset=0
  for _ in range(selector+1):offset=data.index(13,offset)+1
  expected=stream(data[offset:],widths,0,8,width,height,mode,columns,(0,0),initial[2]);consumed,x,y,a,flags,glyphs=expected
  r=s.registers;r[6],r[7]=high,selector;r,calls=execute(0xDB5B)
  delta=(y-8)&255;rows=(delta>>3)+1;rowflags=(rows&0x28)|(16 if (delta>>3)&15==15 else 0)|((delta>>2)&1)
  pointer=0xE37C+offset+consumed
  assert tuple(r[:8])==(8,initial[17],initial[2],initial[3],high,selector,pointer>>8,pointer&255),(selector,r[:8],expected)
  assert list(r[16:18])==[rows,rowflags] and (m[0x6320],m[0x6321])==(x,8) and calls==glyphs
  assert m[0xA397]==10;counts['cr_record_output']+=1
  if original:counts['original_cr_titles']+=1
 # Проверка всех физических индексов и нулевого указателя без входа в печататель.
 for index in range(1024):line(index,None);line(index,b'ONE TWO THREE FOUR\n')
 # Проверка переносов, раннего отказа и управляющих кодов на реальных печатающих процедурах.
 for text in (b'\n',b'A B C D E\n',b'A\rB\rC\n',b'A  B   C\n',b'A'*60+b' B C\n'):
  for width in (8,24,96,248):
   for height in (8,13,16,24,192):line(0,text,width,height)
 for selector in range(256):
  for high in (0,255):record(selector,b'ONE TWO\rTHREE FOUR\n',high=high)
 # Проверка исходных восьми заголовков с их фактическими смещениями и общим завершающим LF.
 for selector in range(8):record(selector,b'',original=True)
 # Проверка числа строк на границе полупереноса INC и восстановления основного F из AF'.
 for height in (128,136,192):record(0,b'A\r'*24+b'\n',height=height)
 for text in (b'\n',b'\x01',b'\x00ABC\n',b'\x02A\x03B\n',b'A\rB\rC\n',b'A'*50+b'\n'):
  for mode in (0,1,255):
   for width in (8,24,96):
    for height in (8,13,16,24,192):record(0,text,width,height,mode)
 report=dict(passed=True,cases_by_path=dict(counts),all_1024_cache_indices=True,all_256_cr_selectors=True,
  exact_main_alternate_index_context=True,independent_line_selection_layout_and_row_count=True,original_glyph_renderer_executed=True,
  independent_whole_bitmap_oracle=False,cache_not_modified_by_indexed_output=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/HelpTextOutputVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
