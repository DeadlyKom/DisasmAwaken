"""Четыре точные знаковые границы EDB0, табличные размеры и продолжение в реальную очередь."""
from pathlib import Path
import json,sys,random,collections,struct
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,PC,SP
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory,signed
from CheckPreviewTransform import adc16
from CheckPreviewLookupProducts import table


def sub16(a,b):
 value=(a-b)&65535
 flags=((value>>8)&0xA8)|(0x40 if value==0 else 0)|(0x10 if (a&4095)<(b&4095) else 0)|(4 if ((a^b)&(a^value)&32768) else 0)|2|int(a<b)
 return value,flags


def half(word):return (signed(word,16)//2)&65535


def span(seed,size,exponent):
 difference=(seed//2-signed(size,8)//2)&255;summed=(difference+size)&255;delta=(table(summed)-table(difference))&255
 return delta,delta<<(exponent-1)


def reference(depth,first,second,size,exponent):
 delta,extent=span(72,size,exponent);value=(half(depth)+first)&65535;value,flags=adc16(half(value),extent,0)
 if flags&128:return 'first_plus',value,flags,first,extent,delta
 value,flags=sub16(value,first)
 if flags&128:return 'first_minus',value,flags,first,extent,delta
 delta,extent=span(66,size,exponent);value=(half(half(depth))+second)&65535;value,flags=adc16(half(value),extent,0)
 if flags&128:return 'second_plus',value,flags,second,extent,delta
 value,flags=sub16(value,second)
 if flags&128:return 'second_minus',value,flags,second,extent,delta
 return 'accepted',value,flags,second,extent,delta


def main():
 m=Memory([0]*65536);raw=payload(6);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);outcomes=collections.Counter();cases=0
 def check(depth,first,second,size,exponent):
  nonlocal cases
  m.recording=False
  for ptr,value in ((0xDA16,depth),(0xDAF6,first),(0xDA38,second)):m[ptr]=value&255;m[ptr+1]=value>>8
  m[0xEDC4]=6-exponent;m[0xEDFD]=6-exponent;s.registers[:]=initial;r=s.registers;r[PC]=0xEDB0;r[3]=size;r[9]=size;m.writes=[];m.recording=True
  for _ in range(100):
   if r[PC] in (0xEE24,0xECAE):break
   s.run()
  else:raise AssertionError('Не завершена проверка границ')
  outcome,value,flags,bc,de,a=reference(depth,first,second,size,exponent)
  assert r[PC]==(0xEE24 if outcome=='accepted' else 0xECAE)
  assert (r[H]*256+r[L],r[D]*256+r[E],r[2]*256+r[3],r[A],r[F],r[SP])==(value,de,bc,a,flags,0x7FFE),(depth,first,second,size,exponent,outcome)
  assert r[8:12]==[initial[8],size,*initial[10:12]] and r[16:24]==initial[16:24] and m.writes==[]
  outcomes[outcome]+=1;cases+=1
 # Проверка каждого слова глубины с разными размерами, масштабами и обёрнутыми координатами.
 for depth in range(65536):check(depth,(depth*53+19)&65535,(depth*83+31)&65535,(depth*73)&255,depth%6+1)
 rng=random.Random(0xEDB0)
 for _ in range(8192):check(rng.randrange(65536),rng.randrange(65536),rng.randrange(65536),rng.randrange(256),rng.randrange(1,7))
 assert all(outcomes[key] for key in ('accepted','first_plus','first_minus','second_plus','second_minus'))
 # Проверка настоящего последовательного продолжения в InsertPreviewQueue на принятом пустом списке.
 integration=0
 for flags in (0,1,127,128,129,255):
  for size in (1,20,63,127):
   check(128,0,0,size,3)
   assert reference(128,0,0,size,3)[0]=='accepted'
   m.recording=False;m[0xCF02]=1;m[0xCF03]=0;m[0xCEFA]=flags;m[0xCEFB]=7;m[0xC21E]=11;m[0xC21F]=22;m[0xC220]=33;m[0xEB8D]=44;m[0xEB8E]=0;m.recording=True
   # Продолжение с текущего EE24, без подмены кода очереди и без нового входа CALL.
   for _ in range(100):
    if s.registers[PC]==0xECAE:break
    s.run()
   else:raise AssertionError('Не завершена композиция границ с очередью')
   assert bytes(m[0xC700:0xC70E])==struct.pack('<6B4H',1,flags,7,11,22,33,0,0,128,44)
   assert m[0xCF02]==0 and m[0xCF03]==14 and s.registers[SP]==0xC701
   integration+=1
 report=dict(passed=True,cases=cases,outcomes=dict(outcomes),all_depth_words=True,all_four_rejection_paths=True,independent_folded_table_and_wrapped_halfword_geometry=True,exact_register_flags_and_no_local_memory_writes=True,real_queue_fallthrough_cases=integration,prepared_jr_displacements='6-exponent for exponent 1..6',irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewBoundsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
