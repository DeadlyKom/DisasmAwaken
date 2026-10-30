"""Три строки признаков системы, оригинальные печататели и независимый XOR по байтам шрифта."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address


def main():
 _,_,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:]=bytes(banks[0]);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'DE':0xA503,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 names=['Демократия','Диктатура','Анархия','Необитаемая','Неизвестный'];economies=['агрокультурная','культурная','технологическая','общая'];baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912));cases=glyphs=0
 for major in range(5):
  for minor in range(4):
   for level in range(1,17):
    for y in (0,64,152):
     expected=bytearray(baseline);rows=[(25,y,names[major]),(16 if major>=3 else 18,y+8,'-' if major>=3 else economies[minor]),(34,y+16,'-' if major>=3 else str(level))]
     for x,row,text in rows:
      for code in text.encode('cp866'):
       for line,bits in enumerate(memory[0x8A00+8*code:0x8A08+8*code]):
        for bit in range(8):
         if bits&(128>>bit):expected[bitmap_address(row+line,(x+bit)//8)-0x4000]^=128>>((x+bit)&7)
       x+=memory[0x8900+code];glyphs+=1
     last_x=x
     # Подготовка обычного текстового окна, прямой шрифт и три полностью помещающиеся строки без изменения исходных инструкций.
     for address,value in ((0x6320,25),(0x6321,y),(0xAEAB,192),(0xAEB3,255),(0xAEBB,0),(0xAEBF,0),(0xAEC7,0),(0xAECB,0),(0xBD26,0)):
      memory[address]=value
     memory[0x4000:0x5B00]=baseline;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[H]=major;r[L]=level;r[E]=minor
     sim.run(start=0xA3A1,stop=0x3FFF)
     assert memory[0x4000:0x5B00]==expected,(major,minor,level,y)
     assert r[H]*256+r[L]==((y+16)<<8)|34 and r[D]==0xA5 and r[E]==minor and (r[A],r[F])==(0,0x45),(major,minor,level,y,list(r))
     assert r[B]*256+r[C]==(0x36C9 if major>=3 else 10) and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
     assert memory[0x6320:0x6322]==bytes([last_x,y+16]);cases+=1
 report=dict(passed=True,cases=cases,independently_composed_glyphs=glyphs,major_codes=list(range(5)),minor_codes=list(range(4)),levels=list(range(1,17)),cursor_rows=[0,64,152],method='original_trait_formatter_real_text_and_number_printers_independent_font_xor_bitmap',successful_text_window_only=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SystemTraitsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
