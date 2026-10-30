"""Исходное знаковое умножение карты, включая граничный код 8000 и три ядра."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckWorldSignature import logical_flags


def signed(value):return value if value<32768 else value-65536


def sbc16_flags(left,right,carry):
 total=left-right-carry;result=total&65535
 return ((result>>8)&0xA8)|(0x40 if result==0 else 0)|(((left^right^result)>>8)&0x10)|(((left^right)&(left^result)&0x8000)>>13)|2|(total<0)


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==7)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 memory[0x7FFE:0x8000]=bytes([255,63]);cases=defects=0;paths={'8x8':0,'8x16':0,'16x16':0}
 for fixed in (0,1,255,256,32767,32768,65535):
  for variable in range(65536):
   for left,right in ((variable,fixed),(fixed,variable)):
    x,y=signed(left),signed(right);mx,my=abs(x),abs(y);large=mx>=256 and my>=256;small=mx<256 and my<256
    # Полное ядро пропускает старший бит и при отсутствии оставшихся старших битов принудительно добавляет разряд 8.
    defect=large and right==32768;magnitude=mx*256 if defect else mx*my
    expected=(-magnitude if (left^right)&32768 else magnitude)&0xFFFFFFFF
    sim.registers[:]=initial;r=sim.registers;r[H],r[L]=left>>8,left&255;r[D],r[E]=right>>8,right&255
    sim.run(start=0xDB63,stop=0x3FFF)
    assert ((r[H]*256+r[L])<<16)|(r[D]*256+r[E])==expected,(left,right,hex(expected),list(r))
    a=(left>>8)^(right>>8);negative=a&128
    flags=sbc16_flags(0,magnitude>>16,int(bool(magnitude&65535))) if negative else logical_flags(a)
    bc=magnitude>>16 if negative else 0 if large else initial[B]*256 if not small else initial[B]*256+initial[C]
    ix=magnitude&65535 if large else 0x2468
    assert (r[A],r[F],r[B]*256+r[C],r[8]*256+r[9],r[SP])==(a,flags,bc,ix,0x8000),(left,right,list(r),flags,bc,ix)
    assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
    paths['16x16' if large else '8x8' if small else '8x16']+=1;cases+=1;defects+=defect
 report=dict(passed=True,cases=cases,paths=paths,second_operand_8000_full_kernel_cases=defects,
  method='original_signed_multiply_all_words_against_seven_boundaries_both_orders',
  extreme_operand_asymmetry_preserved=True,all_output_registers_and_flags_checked=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SignedMultiplyVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
