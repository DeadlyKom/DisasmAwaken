"""Селектор двух исходных сообщений, настоящий текстовый поток и независимая композиция глифов с переносами."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckTextStream import reference
from CheckInsetFrame import bitmap_address


def main():
 _,_,banks=make_context();m=bytearray(65536);m[0x4000:0x8000]=bytes(banks[5]);m[0x8000:0xC000]=bytes(banks[2]);m[0xC000:]=bytes(banks[0]);s=Simulator(m)
 texts=['Расшифрована система:Дзета-43/78-Д','Внимание! Расшифрован иносигнал прошлых поколений: Каждые 69 космолет зарождается жизнь нового типа.И если это не произойдет все предыдущие поколения будут уничтожены!']
 starts=[];cursor=0xE262
 for text in texts:
  assert m[cursor]==10;start=cursor+1;end=m.index(10,start);assert bytes(m[start:end]).decode('cp866')==text;starts.append((start,bytes(m[start:end+1])));cursor=end
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912));widths=m[0x8900:0x8A00];cases=accepted=clipped=0
 for selector,(start,text) in enumerate(starts):
  for width in (48,80,160,255):
   for height in (16,80,192):
    for mode in (0,1,255):
     for x,y in ((0,0),(13,8),(0,176)):
      for origin in ((0,0),(3,3),(65535,0),(0,185)):
       # Независимый текстовый договор задаёт позиции попыток глифов и точный выход, пиксели вычисляются по исходному шрифту.
       positions=[];offset,ex,ey,a,f,calls=reference(text,widths,x,y,width,height,mode,(0,17,42,100,255),origin,0x36,positions=positions)
       expected=bytearray(baseline)
       for code,gx,gy in positions:
        if gy>=height or gx+widths[code]>255 or gx+widths[code]>=width:continue
        px=(origin[0]+gx)&65535;py=(origin[1]+gy)&65535
        if px>255 or py>184:continue
        for row,bits in enumerate(m[0x8A00+8*code:0x8A08+8*code]):
         for bit in range(8):
          if px+bit<256 and bits&(128>>bit):expected[bitmap_address(py+row,(px+bit)//8)-0x4000]^=128>>((px+bit)&7)
        accepted+=1
       # Подготовка окна и обычного JP завершения строки, инструкция пиксельного ядра не подменяется.
       for address,value in ((0x6320,x),(0x6321,y),(0xAEB3,width),(0xAEAB,height),(0xBD26,mode),(0xAEBB,origin[0]&255),(0xAEBF,origin[0]>>8),(0xAEC7,origin[1]&255),(0xAECB,origin[1]>>8)):
        m[address]=value
       m[0xBD4F]=0xC3;m[0x98BF]=selector;m[0x4000:0x5B00]=baseline;m[0x7FFE:0x8000]=bytes([255,63]);s.registers[:]=initial;s.run(start=0x6E76,stop=0x3FFF);r=s.registers
       assert (r[H]*256+r[L],m[0x6320],m[0x6321],r[A],r[F])==(start+offset,ex,ey,a,f),(selector,width,height,mode,x,y,origin)
       assert m[0x4000:0x5B00]==expected and m[0x98BF]==selector
       assert r[D:E+1]==initial[D:E+1] and r[B:C+1]==initial[B:C+1] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
       cases+=1;clipped+=offset<len(text)
 report=dict(passed=True,cases=cases,independently_composed_glyphs=accepted,early_stream_stops=clipped,message_selectors=[0,1],real_text_and_glyph_code=True,all_bitmap_and_attribute_bytes_compared=True,unknown_selector_values_not_assigned_meanings=True,method='original_6E76_and_PrintAfterLF_PrintText_DrawGlyph_against_text_cursor_and_font_xor_models',irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/DecodedMessageVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
