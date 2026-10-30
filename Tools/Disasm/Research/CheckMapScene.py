"""Весь C000, исходные дуга, шесть маркеров, внутренняя цепочка и 512 секторных слов."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP,PC
from CheckRowHighlight import make_context
from CheckArcDispatcher import reference as arc_reference
from CheckVisibleMapPoints import visible_points
from CheckMapLine import points as line_points
from CheckInsetFrame import bitmap_address


def key(x,y):return bytes([x>>8,y>>8,x&255,y&255])


def marker(screen,source,address,x,y,ox,oy,width,height):
 dx=(x-ox-3)&65535;dy=(y-oy-3)&65535
 if dx>=((width-8)&255) or dy>=((height-7)&255):return False
 phase=(dx&7)*16;resource=source[address-0xC000:address-0xC000+128]
 for row in range(7):
  target=bitmap_address(16+dy+row,1+dx//8)-0x4000
  screen[target]^=resource[phase+2*row];screen[target+1]^=resource[phase+2*row+1]
 return True


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 rng=random.Random(0xC000);cases=arcs=markers=stars=chains=shared_snapshot_cases=0
 original_shared_codes=bytes(banks[2][0x19A3:0x19AE])+bytes([0x81])
 for width,height in ((128,96),(208,112)):
  sim.registers[:]=initial;r=sim.registers;r[H],r[L]=height-1,width-1;r[D]=r[E]=0;sim.run(start=0xD0C3,stop=0x3FFF)
  for seed in range(512):
   ox,oy=((0x1234,0x5678),(0x12C8,0x56C8),(0x12FF,0x56FF),(0x1200,0x5600))[seed&3]
   w=(0,1,2,6,0x0100,0x0300,0x2800,0x5500,0xAA55,0xFFFF)[seed%10];rbyte=(3*((w>>8) if w>>8 else (w&255)//2))&255
   mode_parameter=(seed*37)&255;mode=0x38 if mode_parameter&1 else 0x30
   def coordinate():return (ox+rng.randrange(-96,width+96))&65535,(oy+rng.randrange(-96,height+96))&65535
   primary=(ox+(seed*17)%(width+192)-96,oy+(seed*23)%(height+192)-96);primary=tuple(v&65535 for v in primary)
   selected=coordinate();cursor=coordinate();cursor_missing=bool(seed&4)
   count_a=seed%11;count_b=(seed//3)%6;count_aux=(seed//7)%11
   records_a=[];table_a=bytearray([255]*51)
   for index in range(count_a):
    if (seed+index)%4==0:continue
    point=coordinate();records_a.append(point);table_a[5*index:5*index+5]=key(*point)+bytes([index])
   table_a[5*count_a]=0x80 if seed&1 else 0xFE
   local_b=[(rng.randrange(width),rng.randrange(height)) for _ in range(count_b)]
   records_b=[((ox+x)&65535,(oy+y)&65535) for x,y in local_b]
   table_b=bytearray([255]*51)
   for index,point in enumerate(records_b):table_b[5*index:5*index+5]=key(*point)+bytes([index])
   table_b[5*count_b]=255 if seed&8 else 128
   auxiliary=[coordinate() for _ in range(10)];codes=bytes(0 if (seed+i)%3==0 else 1+(seed+i)%127 for i in range(count_aux))+bytes([0x80+(seed&127)])
   if seed%16==0:codes=original_shared_codes;count_aux=11;shared_snapshot_cases+=1
   chain_count=min(count_b,(seed//5)%6);style=seed&3;order=list(range(chain_count));rng.shuffle(order)
   if chain_count and seed&16:order=[0]*chain_count
   order_data=bytes([((seed>>4)&3)*64+style*16+chain_count])+bytes(5*i for i in order)+bytes(10-chain_count)
   tables=bytearray(rng.randrange(256) for _ in range(1024))
   if seed&32 and (ox&255)+width>256 and (oy&255)+height>256:tables[-2:]=bytes(2)
   else:tables[-2:]=bytes([ox&255,oy&255])
   baseline=bytes((i*53+(i>>8)*11+seed)&255 for i in range(0x1B00));expected=bytearray(baseline)
   sx=(primary[0]-ox-width//2)&65535;sy=(oy-primary[1]+height//2)&65535
   ax=sx if sx<32768 else 65536-sx;ay=sy if sy<32768 else 65536-sy;pass_x=ax<rbyte+width//2;draw_arc=pass_x and ay<rbyte+height//2
   quadrant=int(sx<32768)|(int(sy<32768)<<1)
   if draw_arc:expected,_,_=arc_reference(expected,rbyte,ax&255,ay&255,quadrant,mode,width,height);arcs+=1
   # Воспроизведение фактического порядка ресурсов маркеров до изменения линии и секторных пикселей.
   for address,point in [(0xCFC3,primary),(0xCDC3,selected),*([(0xCF43,cursor)] if not cursor_missing else []),
                         *((0xD043,p) for p in records_a),*((0xCEC3,auxiliary[i]) for i in range(count_aux) if codes[i]),
                         *((0xCE43,p) for p in records_b)]:markers+=marker(expected,source,address,*point,ox,oy,width,height)
   if count_b and chain_count>=2:
    for first,second in zip(order,order[1:]):
     for x,y in line_points(local_b[first],local_b[second]):
      address=bitmap_address(16+y,(8+x)//8)-0x4000;mask=128>>(x&7)
      if style==0:expected[address]&=255^mask
      elif style==1:expected[address]|=mask
      else:expected[address]^=mask
    chains+=1
   accepted=list(visible_points(tables,ox&255,oy&255,width,height))
   for _,x,y in accepted:expected[bitmap_address(16+y,(8+x)//8)-0x4000]^=128>>(x&7)
   stars+=len(accepted)
   # Подготовка согласованного снимка входных списков и координат, исходные ресурсы остаются в банке.
   memory[0x4000:0x5B00]=baseline;memory[0x6300:0x6306]=bytes([ox&255,oy&255,ox>>8,oy>>8,width,height]);memory[0x6309:0x630B]=(0xB400).to_bytes(2,'little')
   memory[0x983F:0x9843]=key(*primary);memory[0x9844:0x9848]=key(*selected);memory[0x988E:0x9890]=w.to_bytes(2,'little')
   memory[0x990A:0x993D]=table_a;memory[0x993D:0x9970]=table_b;memory[0x9970:0x997B]=order_data
   memory[0x997B:0x99A3]=b''.join(key(*point) for point in auxiliary);memory[0x99A3:0x99A3+len(codes)]=codes
   memory[0xB400:0xB405]=bytes([255])*5 if cursor_missing else key(*cursor)+bytes([0])
   memory[0xF200:0xF600]=tables;memory[0xDFAB:0xDFAF]=bytes([0xA7])*4
   for address in (0xE426,0xE438,0xE44F,0xE460):memory[address]=0x38
   sim.registers[:]=initial;r=sim.registers;r[A]=mode_parameter
   sim.run(start=0xC000,stop=0xC14B);before_tail=list(r);assert memory[0xC14B]==0x76
   # Явное пробуждение HALT, без исполнения ISR или аппаратной синхронизации.
   r[PC]=0xC14C;sim.run(stop=0x3FFF)
   assert memory[0x4000:0x5B00]==expected,(width,height,seed,draw_arc,[(hex(i+0x4000),a,b) for i,(a,b) in enumerate(zip(memory[0x4000:0x5B00],expected)) if a!=b][:12])
   assert memory[0xF200:0xF600]==tables and memory[0x990A:0x993D]==table_a and memory[0x993D:0x9970]==table_b and memory[0x9970:0x997B]==order_data
   assert memory[0xDFAB:0xDFAF]==bytes([ay&255 if pass_x else 0xA7,ax&255,quadrant if draw_arc else 0xA7,rbyte])
   assert memory[0xDFC4]==mode_parameter and all(memory[a]==(mode if draw_arc else 0x38) for a in (0xE426,0xE438,0xE44F,0xE460))
   assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[SP])==(tables[-1]*256+tables[-2],(oy&255)*256+(ox&255),(1-height)&255,0x8000)
   assert r[F]&1==int(not accepted or accepted[-1][0]!=511) and r[10:12]==initial[10:12] and r[8:10]==before_tail[8:10]
   assert r[19]==before_tail[C]
   if accepted:
    _,x,y=accepted[-1];assert (r[22]*256+r[23],r[20]*256+r[21],r[18])==(0xF100+x,bitmap_address(16+y,(8+x)//8),x)
   assert memory[0xC22E:0xC230]==bytes([254,127])
   cases+=1
 report=dict(passed=True,cases=cases,arc_dispatch_calls=arcs,visible_marker_calls=markers,sector_pixel_xors=stars,nontrivial_chains=chains,
  method='entire_original_C000_arc_all_six_original_marker_resources_inside_point_chains_and_sector_pixels_against_composed_independent_bitmap_model',
  viewport_profiles=[[128,96],[208,112]],wrapped_sector_origins=True,all_chain_styles=True,empty_and_holey_lists=True,
  original_shared_code_snapshot_cases=shared_snapshot_cases,negative_guard_from_adjacent_interface_data_checked=True,
  general_register_sets_return_exchanged=True,final_carry_describes_last_sector_word=True,
  halt_wakeup_fixture=True,irq_executed=False,native_execution=False,assembly_executed=False,calls_stubbed=False,
  individually_clipped_chain_edges_tested=False,full_game_loop_proved=False)
 (ROOT/'Tools/Disasm/Reports/MapSceneVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
