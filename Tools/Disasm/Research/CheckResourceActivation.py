"""Оригинальный поиск текстового заголовка CF18 и установка байта записи FF/FE."""
from pathlib import Path
from itertools import product
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckMarketAccess import add16_flags


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();original=bytearray(65536);original[0xC000:0xC000+len(source)]=source
 memory=original.copy();sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69A5},None,False)
 active=skipped=0
 for group,record,offset,mode in product((0,1,255),(0,1,255),(0,1,2,255,256,65535),(0,1,2,255)):
  memory[:]=original;text=str(offset).encode()+b'!';memory[0xB000:0xB000+len(text)]=text;memory[0x9A1C]=group;memory[0x9A1D]=record
  n=group or 256;k=record or 256;payload=bytes([0x31,255])*n+bytes([0x32,254])*k
  memory[0x9A49:0x9A49+len(payload)]=payload;marker=0x9A49+len(payload)-1;target=(marker+offset)&65535
  if offset!=0:memory[target]=0xAA
  prior=memory[target]
  header=lambda g,r,i:('_X'+str(g)+'?'+str(r)+'!'+str(i)+' payload\r').encode()
  headers=header((group+1)&255,record,offset&255)+header(group,(record+1)&255,offset&255)+header(group,record,(offset+1)&255)+header(group,record,offset&255)
  memory[0xCF18:0xCF18+len(headers)]=headers;memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;r[16]=mode
  sim.run(start=0xC10E,stop=0x3FFF)
  if mode:
   assert (memory[target],r[A],r[F],r[H]*256+r[L],r[D]*256+r[E],r[B],r[C],r[SP])==(1,254,add16_flags(marker,offset,0x44),0xCF18+len(headers),offset,0,group,0x8000)
   assert r[8]*256+r[9]==0xB000+len(text)-1;active+=1
  else:
   assert memory[target]==prior and (r[A],r[F],r[SP])==(0,0x44,0x8000)
   assert r[2:12]==initial[2:12];skipped+=1
  assert r[16:18]==initial[0:2] and r[18:24]==initial[18:24] and r[10:12]==initial[10:12]
 report=dict(passed=True,method='original_resource_activation_with_three_header_mismatch_paths',active_cases=active,skipped_cases=skipped,
  header_index_compared_as_byte_but_target_offset_is_word=True,zero_counts_mean_256=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ResourceActivationVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
