"""Подготовка радиуса, абсолютных смещений и двух разрядов квадранта в начале C000."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckWorldSignature import logical_flags


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 cases=called=xskip=yskip=truncated=0
 for profile,(max_x,max_y) in enumerate(((239,175),(0,0),(1,255),(255,175),(31,23))):
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=max_y,max_x;r[D]=r[E]=0;sim.run(start=0xD0C3,stop=0x3FFF)
  half_x=((max_x+1)&255)//2;half_y=(((max_y+1)&255)//2)|(128 if half_x<2 else 0)
  def check(source_word,sx,sy):
   nonlocal cases,called,xskip,yskip,truncated
   high=source_word>>8;radius=(3*(high if high else (source_word&255)//2))&255
   ax=sx if sx<32768 else 65536-sx;ay=sy if sy<32768 else 65536-sy
   pass_x=ax<radius+half_x;pass_y=pass_x and ay<radius+half_y;code=int(sx<32768)|(int(sy<32768)<<1)
   # Подготовка независимых полных координат, их упаковка сохраняет переносы между словами и байтами.
   ox,oy=0x1234,0x5678;wx=(ox+half_x+sx)&65535;wy=(oy+half_y-sy)&65535
   memory[0x6300:0x6304]=bytes([ox&255,oy&255,ox>>8,oy>>8]);memory[0x983F:0x9843]=bytes([wx>>8,wy>>8,wx&255,wy&255])
   memory[0x988E:0x9890]=source_word.to_bytes(2,'little');memory[0xDFAB:0xDFAF]=bytes([0xA7])*4
   sim.registers[:]=initial;r=sim.registers;mode=(source_word^sx^sy)&255;r[A]=mode;r[F]=mode^0x5A;r[PC]=0xC000
   # Остановка перед неизвестным диспетчером либо перед дальнейшими маркерами, вызовы не подменяются.
   for _ in range(160):
    if r[PC] in (0xDFC3,0xC0A4):break
    sim.run()
   else:raise AssertionError('prefix_instruction_limit')
   assert r[PC]==(0xDFC3 if pass_y else 0xC0A4),(profile,source_word,sx,sy,ax,ay)
   assert memory[0xDFAB:0xDFAF]==bytes([ay&255 if pass_x else 0xA7,ax&255,code if pass_y else 0xA7,radius])
   assert memory[0xDFC4]==mode and r[SP]==(0x7FFC if pass_y else 0x7FFE)
   assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
   if pass_y:
    rotated=((sx>>8)<<1 | (sx>>15))&255
    assert (r[A],r[F],r[16])==(code,logical_flags(rotated)&0xC4,ay&255)
    assert memory[0x7FFC:0x7FFE]==bytes([0xA4,0xC0]);called+=1;truncated+=ax>255 or ay>255
   elif pass_x:yskip+=1
   else:xskip+=1
   cases+=1
  if profile==0:
   # Проверка всех слов исходного радиуса и каждой 16-битной разности по обеим осям.
   for value in range(65536):
    check(value,0,0);check(0x0100,value,0);check(0x2800,0,value)
  # Проверка всех 256 радиусов с границами грубого отбрасывания, включая абсциссу 8000.
  for radius in range(256):
   high=(radius*171)&255;word=high<<8
   xs={0,32768,(radius+half_x-1)&65535,(radius+half_x)&65535,(-(radius+half_x-1))&65535}
   ys={0,32768,(radius+half_y-1)&65535,(radius+half_y)&65535,(-(radius+half_y-1))&65535}
   for sx in xs:
    for sy in ys:check(word,sx,sy)
 report=dict(passed=True,cases=cases,dispatch_prepared_cases=called,x_rejected_cases=xskip,y_rejected_cases=yskip,prepared_offsets_truncated_to_byte_cases=truncated,
  method='original_C000_prefix_until_actual_DFC3_call_or_marker_continuation_independent_word_geometry_and_radius_formula',
  setup_profiles=[[239,175],[0,0],[1,255],[255,175],[31,23]],all_source_radius_words=True,all_coordinate_difference_words_in_base_profile=True,
  radius_formula='3*(high(source) if high(source)!=0 else low(source)//2) AND 255',
  quadrant_bit_0='wrapped WorldX-OriginX-HalfX is nonnegative',quadrant_bit_1='wrapped OriginY-WorldY+HalfY is nonnegative',
  quadrant_upper_bits_cleared_by_this_writer=True,full_C000_and_DFC3_proved=False,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ArcGeometryPrefixVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
