"""Полный D1AC, реальные классификация, отсечение и три режима линий, независимый экранный результат."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address
from CheckMapLine import points
from CheckClipSegment import outcode,encoded
from CheckWorldSignature import logical_flags


def intersection(first,second,boundary):
 x1,y1=first;x2,y2=second;number=(y1-y2)*(x1-boundary);den=x2-x1
 assert den
 magnitude=-number-1 if number<0 else number;quotient=magnitude//abs(den)
 if (number<0)!=(den<0):quotient=quotient^65535
 coordinate=(quotient+y1)&65535;value=0 if coordinate&32768 else coordinate&255 if coordinate&255<192 else 255
 return boundary,value


def clipped(first,second):
 c1,c2=outcode(*first),outcode(*second)
 if c1&c2:return None
 if c1==c2==0:return first,second
 # Здесь проверяется подмножество с боковыми пересечениями, другие четыре внешние зоны нужны отдельно.
 assert (c1|c2)&~3==0
 if c1==0:first,second=second,first;c1,c2=c2,c1
 start=intersection(first,second,0 if c1==2 else 255)
 return start,second if not c2 else intersection(first,second,0 if c2==2 else 255)


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x993D,'DE':0x9970,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=240;sim.registers[E]=248;sim.run(start=0xC49B,stop=0x3FFF)
 baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912));rng=random.Random(0xD1AC);counts=collections.Counter();edges=rendered=pixels=0
 # Проверка реальных размеров списка 0..10, всех битов заголовка и перемешанных либо повторённых пятибайтовых индексов.
 for count in range(11):
  for style in range(4):
   for high in range(4):
    for seed in range(24):
     header=(high<<6)|(style<<4)|count
     if seed==0:coordinates=[(rng.randrange(-96,0),rng.randrange(176)) for _ in range(count)]
     elif seed==1:coordinates=[(rng.randrange(255,352),rng.randrange(176)) for _ in range(count)]
     elif seed==2:coordinates=[(rng.randrange(255),rng.randrange(-96,0)) for _ in range(count)]
     elif seed==3:coordinates=[(rng.randrange(255),rng.randrange(255,352)) for _ in range(count)]
     else:coordinates=[(rng.randrange(-96,352) if seed&1 else rng.randrange(255),rng.randrange(176)) for _ in range(count)]
     order=list(range(count));rng.shuffle(order)
     if count and seed%3==0:order=[rng.randrange(count) for _ in range(count)]
     source_points=bytearray()
     for x,y in coordinates:
      wx,wy=0x4000+x,0x4000+y;source_points.extend([wx>>8,wy>>8,wx&255,wy&255,rng.randrange(256)])
     record_bytes=bytes(source_points)+bytes([0xA7])*(50-len(source_points));order_bytes=bytes([header])+bytes(i*5 for i in order)+bytes([0xA7])*(10-count)
     memory[0x993D:0x996F]=record_bytes;memory[0x9970:0x997B]=order_bytes;memory[0x6300:0x6304]=bytes([0,0,0x40,0x40])
     memory[0xF800:0xF84C]=bytes([0xA7])*76;memory[0x4000:0x5B00]=baseline;memory[0xDE3C:0xDE3E]=bytes([0xA7,0x55]);memory[0xD306]=0x77
     expected=bytearray(baseline);aggregate=0;common=15
     for p in coordinates:aggregate|=encoded(*p);common&=outcode(*p)
     mode='clear' if style==0 else 'set' if style==1 else 'xor';mode_bytes=bytes([0xA1,0x30]) if style==0 else bytes([0xB1,0x38]) if style==1 else bytes([0xA9,0x38])
     if count>=2 and not common:
      for i in range(count-1):
       pair=clipped(coordinates[order[i]],coordinates[order[i+1]]);edges+=1
       if pair is None:continue
       rendered+=1
       for x,y in points(*pair):
        assert 0<=x<256 and 0<=y<192,(coordinates,order,pair)
        address=bitmap_address(y,x//8)-0x4000;mask=128>>(x&7)
        if mode=='clear':expected[address]&=255^mask
        elif mode=='set':expected[address]|=mask
        else:expected[address]^=mask
        pixels+=1
     sim.registers[:]=initial;r=sim.registers;sim.run(start=0xD1AC,stop=0x3FFF)
     assert memory[0x4000:0x5B00]==expected,(count,style,high,seed,coordinates,order)
     assert memory[0x993D:0x996F]==record_bytes and memory[0x9970:0x997B]==order_bytes
     assert r[SP]==0x8000 and r[10:12]==initial[10:12]
     if count<2:
      assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F])==(0x993D,0x9970,0x36C9,0,0x54 if count==0 else 0x42)
      assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and memory[0xF800:0xF84C]==bytes([0xA7])*76
      assert memory[0xDE3C:0xDE3E]==bytes([0xA7,0x55]) and memory[0xD306]==0x77;counts['count_'+str(count)+'_early']+=1
     else:
      work=b''.join((x&65535).to_bytes(2,'little')+(y&65535).to_bytes(2,'little')+bytes([encoded(x,y)]) for x,y in coordinates)
      assert memory[0xF800:0xF800+5*count]==work and memory[0xF800+5*count:0xF84C]==bytes([0xA7])*(76-5*count)
      if common:
       assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[F])==(0xF801+5*count,0x47AD,aggregate*256+outcode(*coordinates[-1]),common<<4,logical_flags(common<<4)|0x10)
       assert r[18:24]==[0x36,0x40,(0xF800+5*count)>>8,(0xF800+5*count)&255,0x99,0x70] and r[16:18]==[5*count,0x42|((5*count)&0x28)],(count,style,high,seed,list(r))
       assert memory[0xDE3C:0xDE3E]==bytes([0xA7,0x55]) and memory[0xD306]==0x77;counts['common_outside_swapped_sets']+=1
      else:
       assert (r[H]*256+r[L],r[B]*256+r[C],r[8]*256+r[9])==(0x9971+count,0x40,0xF800+order[-1]*5)
       assert r[18:24]==[aggregate,outcode(*coordinates[-1]),0x47,0xAD,0xF8,1+5*count]
       assert memory[0xDE3C:0xDE3E]==mode_bytes and memory[0xD306]==(0x28 if style==0 else 0x20);counts[mode+'_chain']+=1
 report=dict(passed=True,cases=sum(counts.values()),outcomes=dict(counts),edge_pairs=edges,accepted_pairs=rendered,pixel_operations=pixels,
  method='original_D1AC_full_stored_point_conversion_outcodes_real_side_clipping_and_line_raster_against_independent_screen_model',
  point_count_domain=[0,10],header_variants_checked=176,all_header_bit_positions_varied=True,all_256_header_values_tested=False,repeated_and_permuted_indices=True,top_bottom_common_reject_checked=True,
  individual_top_bottom_clipped_edges_tested=False,common_reject_returns_exchanged_general_sets=True,
  coordinate_origin=[0x4000,0x4000],table_builder_input_DE=0xF0F8,synthetic_alignment_fixture=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MapPointChainVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
