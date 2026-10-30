"""Исходный C677, шесть курсоров, мигание и трёхстрочные фазы против независимой модели bitmap."""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address
from CheckSignedMultiply import sbc16_flags

CURSORS=(0xC6CA,0xC6E7,0xC704,0xC721,0xC73E,0xC75B)
RESOURCES=(0xC6C1,0xC6DE,0xC6FB,0xC718,0xC735,0xC752)
STARTS=(0xCACF,0xCA7E,0xCA45,0xCB38,0xCBB9,0xCC52)


def dec_flags(old,carry):
 value=(old-1)&255
 return (value&0xA8)|(0x40 if value==0 else 0)|(0x10 if old&15==0 else 0)|(4 if old==128 else 0)|2|carry


def add_flags(left,right):
 total=left+right;value=total&255
 return (value&0xA8)|(0x40 if value==0 else 0)|(0x10 if (left&15)+(right&15)>15 else 0)|(4 if (~(left^right)&(left^value)&128) else 0)|int(total>255)


def draw(expected,source,resource,x,y):
 phase=6*(x&7);column=x//8
 for row in range(3):
  for side in range(2):expected[bitmap_address(y+row,column+side)-0x4000]^=source[resource-0xC000+phase+2*row+side]


def reference_cluster(source,base,count,ox,oy,assigned,cursors,pattern,paths):
 expected=bytearray(base);xbase,ybase=8*(ox+4),8*(oy+4);cx,cy=xbase+3,ybase+6
 for row,mask in enumerate((0x1C,0x3E,0x3E,0x3E,0x1C)):expected[bitmap_address(ybase+4+row,xbase//8)-0x4000]^=mask
 new_cursors=list(cursors);remaining=count;wraps=0
 for index,resource in enumerate(assigned):
  if resource==0xCD93:
   before=pattern;pattern=((pattern>>1)|(pattern<<7))&255
   if not before&1:resource=0xCD03
  pointer=new_cursors[index];start,end=paths[index]
  if pointer==end:pointer=start;wraps+=1
  raw_x,raw_y=source[pointer-0xC000:pointer-0xC000+2];new_cursors[index]=pointer+2;last_resource=resource
  previous=remaining;remaining=(remaining-1)&255
  if remaining&128:break
  draw(expected,source,resource,(raw_x+cx)&255,(raw_y+cy)&255)
 return expected,new_cursors,pattern,last_resource,pointer,raw_x,raw_y,previous,remaining,wraps


def main():
 _,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0xB200,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 rng=random.Random(0xC677);baseline=bytes((i*73+(i>>5)*19+17)&255 for i in range(6912));single=whole=blink=drawn=skipped=wrapped=0
 # Проверка каждого байта альтернативного счётчика, всех восьми фаз и пересечений строковых границ.
 for count in range(256):
  for phase in range(8):
   for resource in (0xCD03,0xCD33,0xCD63,0xCD93):
    x=8*(phase*3)+phase;y=(0,5,6,7,8,62,63,189)[phase];base_x,base_y=rng.randrange(256),rng.randrange(256)
    raw_x,raw_y=(x-base_x)&255,(y-base_y)&255;carry=phase&1
    memory[0x4000:0x5B00]=baseline;expected=bytearray(baseline);memory[0xB200:0xB202]=bytes([raw_x,raw_y]);memory[0xC845:0xC847]=resource.to_bytes(2,'little')
    memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[A]=raw_x;r[B],r[C]=base_y,base_x;r[16],r[17]=count,0x5C|carry
    sim.run(start=0xC827,stop=0x3FFF);remaining=(count-1)&255
    if remaining&128:
     assert (r[A],r[F],r[16],r[17],r[D]*256+r[E])==(remaining,dec_flags(count,carry),raw_y,add_flags(raw_x,base_x),(0x24<<8)|x)
     skipped+=1
    else:
     draw(expected,source,resource,x,y);drawn+=1
     assert (r[A],r[F],r[16],r[17],r[D]*256+r[E])==(0,0x44,remaining,dec_flags(count,carry),resource+6*phase+5)
    assert memory[0x4000:0x5B00]==expected and r[H]*256+r[L]==0xB202 and (r[B],r[C])==(base_y,base_x)
    assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24];single+=1
 # Проверка всех состояний циклической маски мигания на выбранном и остальных ресурсах.
 for pattern in range(256):
  for resource in (0,0xCD03,0xCD33,0xCD63,0xCD93,0xFFFF):
   memory[0xC777]=pattern;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[H],r[L]=resource>>8,resource&255
   sim.run(start=0xC76E,stop=0x3FFF)
   changed=resource==0xCD93;rotated=((pattern>>1)|(pattern<<7))&255
   assert r[H]*256+r[L]==(resource if not changed or pattern&1 else 0xCD03) and memory[0xC777]==(rotated if changed else pattern)
   difference=(resource-0xCD93)&65535;total=difference+0xCD93
   flags=(sbc16_flags(resource,0xCD93,0)&0xC4)|((resource>>8)&0x28)|(0x10 if (difference&0xFFF)+0xD93>0xFFF else 0)|int(total>65535)
   if changed:flags=(flags&0xC4)|(rotated&0x28)|(pattern&1)
   assert (r[A],r[F])==((rotated,flags) if changed else (initial[A],flags)),(pattern,resource,list(r),flags)
   assert r[D]*256+r[E]==0xCD93 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000;blink+=1
 paths=[]
 for start in STARTS:
  end=start
  while source[end-0xC000]!=0x80:end+=2
  paths.append((start,end))
 # Проверка полной композиции C677 с настоящими вызовами и переходом между шестью обёртками после RET M.
 for count in range(256):
  for origin_index,(ox,oy) in enumerate(((0,0),(3,3),(10,7),(23,15))):
   for old in (0,1):
    base=bytes(6912) if old==0 else baseline;memory[0x4000:0x5B00]=base;expected=bytearray(base)
    xbase,ybase=8*(ox+4),8*(oy+4)
    cx,cy=xbase+3,ybase+6;pattern=(count*73+origin_index*19+old)&255;memory[0xC777]=pattern;remaining=count
    assigned=tuple((0xCD03,0xCD33,0xCD63,0xCD93)[(count+i+origin_index)&3] for i in range(6));new_cursors=[]
    for index,(operand,(start,end)) in enumerate(zip(CURSORS,paths)):
     pointer=end if (count+index+old)%7==0 else start+2*((count*3+index*5+old)%((end-start)//2))
     memory[operand:operand+2]=pointer.to_bytes(2,'little');new_cursors.append(pointer)
    for operand,resource in zip(RESOURCES,assigned):memory[operand:operand+2]=resource.to_bytes(2,'little')
    # Расчёт композиции общим независимым oracle, используемым также моделью станционного callback.
    expected,new_cursors,pattern,last_resource,pointer,raw_x,raw_y,previous,remaining,wrap_count=reference_cluster(source,base,count,ox,oy,assigned,new_cursors,pattern,paths)
    wrapped+=wrap_count
    memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[A]=count;r[D],r[E]=oy,ox;r[F]=0x5C|old
    sim.run(start=0xC677,stop=0x3FFF)
    assert memory[0x4000:0x5B00]==expected,(count,origin_index,old)
    assert memory[0xC777]==pattern and memory[0xC7B6]==count and int.from_bytes(memory[0xC845:0xC847],'little')==last_resource
    assert tuple(int.from_bytes(memory[a:a+2],'little') for a in CURSORS)==tuple(new_cursors)
    assert r[H]*256+r[L]==pointer+2 and (r[B],r[C])==(cy,cx)
    if remaining&128:
     assert (r[A],r[F],r[16],r[17],r[D]*256+r[E])==(remaining,dec_flags(previous,old),raw_y,add_flags(raw_x,cx),0xCD00|((raw_x+cx)&255))
    else:
     assert (r[A],r[F],r[16],r[17],r[D]*256+r[E])==(0,0x44,remaining,dec_flags(previous,old),last_resource+6*((raw_x+cx)&7)+5)
    assert r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24];whole+=1
 report=dict(passed=True,single_sprite_cases=single,blink_cases=blink,whole_cluster_cases=whole,
  sprites_drawn_in_single_cases=drawn,sprites_skipped_in_single_cases=skipped,stream_wraps=wrapped,
  all_counter_bytes_tested=True,all_blink_mask_bytes_tested=True,all_eight_phases=True,
  method='original_entire_C677_and_helpers_against_independent_spectrum_bitmap_and_byte_counter_model',
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False,full_game_loop_proved=False)
 (ROOT/'Tools/Disasm/Reports/AnimatedVariantsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
