"""Межбанковые HELP-вызовы из банка 5 и сохранение бита экранной страницы."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,payload,put
from CheckHelpLineIndex import expected as line_index
from CheckJustifiedText import reference as justified
from skoolkit.simutils import SP


def main():
 _,_,base=make_context();raw=payload(8);base[7][0x1B00:0x1B00+len(raw)]=list(raw);fixture=Fixture(base);m=fixture.memory;s=fixture.sim;initial=fixture.initial
 widths=list(m[0x8900:0x8A00]);counts=collections.Counter()
 def prepare(page,width,height):
  m.out7ffd(page);m[0x6306]=page;put(m,0x7FFE,(255,63));s.registers[:]=initial
  for a,v in ((0xAEB3,width),(0xAEAB,height),(0xAEBB,0),(0xAEBF,0),(0xAEC7,0),(0xAECB,0)):m[a]=v
  put(m,0xAED5,(0x68,0x48,0x26));fixture.trace.writes.clear()
 def after(page):
  r=s.registers;flags=(page&0xA8)|(4 if page.bit_count()%2==0 else 0)
  assert r[0]==page and r[1]==flags and m.o7ffd==m[0x6306]==page and r[SP]==0x8000
  assert r[16:24]==initial[16:24] and r[10:12]==initial[10:12] and r[14]==initial[14] and r[26:28]==initial[26:28]
  assert fixture.trace.writes==[(0x7FFD,page|7),(0x7FFD,page)],fixture.trace.writes
 # Проверка каждого реального LF-раздела, обеих страниц экрана и разных высот.
 for page in (0x10,0x18):
  for selector in range(9):
   for width in (96,168,248):
    for height in (8,13,24,192):
     prepare(page,width,height);m.banks[7][0x1B01]=selector
     text=raw[0x8E2:]+bytes([10])*1024;m.banks[7][0x23E2:0x23E2+len(text)]=list(text)
     pointers,x,y,a=line_index(list(text),selector,width,height,widths,initial[2]*256+initial[3]);n=len(pointers)
     s.run(start=0x69B8,stop=0x3FFF);r=s.registers;after(page)
     assert tuple(r[2:10])==(0,0,n>>8,n&255,0xE3,0x7B,(0xDB7C+2*n)>>8,(0xDB7C+2*n)&255)
     assert m[0xBD26]==1 and m[0x6995]+256*m[0x6996]==n and (m[0x6320],m[0x6321])==(x,y)
     expected=b''.join(p.to_bytes(2,'little') for p in pointers)+bytes(2048-2*n)
     assert bytes(m.banks[7][0x1B7C:0x237C])==expected;counts['index_and_store_count']+=1
 # Проверка нулевой и непустой записи через реальный хвост PrintJustified и оба переключения банка.
 for page in (0x10,0x18):
  for index in (0,1,511,1023):
   for text in (None,b'ONE TWO THREE FOUR\n',b'A\rB C\n'):
    for height in (8,24,192):
     prepare(page,96,height);pointer=0 if text is None else 0xE3E2;offset=0x1B7C+2*index;m.banks[7][offset:offset+2]=list(pointer.to_bytes(2,'little'));r=s.registers;r[6],r[7]=index>>8,index&255
     if text is not None:
      data=list(text)+[10]*1024;m.banks[7][0x23E2:0x23E2+len(data)]=data
      consumed,x,y,a,flags,bc,d,e,calls=justified(0xADCD,data,widths,0,8,96,height,0x0800,0xDB,0x7C)
      expected=(bc>>8,bc&255,d,e,(pointer+consumed)>>8,(pointer+consumed)&255)
     else:expected=(8,0,0xDB,0x7C,0,0)
     s.run(start=0x69CF,stop=0x3FFF);after(page);assert tuple(r[2:8])==expected and r[8:10]==initial[8:10];counts['print_banked_line']+=1
 # Проверка всех AF и всех прежних байтов Style на исходной пятибайтовой процедуре.
 prepare(0x10,96,192)
 for af in range(65536):
  put(m,0x7FFE,(255,63));s.registers[:]=initial;r=s.registers;r[0],r[1]=af>>8,af&255;m[0xBD26]=(r[0]^r[1]);s.run(start=0x6A7E,stop=0x3FFF)
  assert r[:2]==[0,0x44] and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000 and m[0xBD26]==0
  counts['disable_wrap_all_af']+=1
 report=dict(passed=True,cases_by_path=dict(counts),real_bank_switch_helpers_and_help_instructions=True,both_screen_page_bits=True,
  independent_line_index_and_print_layout=True,entire_cache_and_stored_word_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/StationHelpCallsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
