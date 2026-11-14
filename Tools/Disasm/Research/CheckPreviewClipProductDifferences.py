"""Четыре разности полных 32-битных кэшей, возвращаемый HL и Z только старшего слова.

Документация: ../../../Docs/PreviewClipProducts.md#r-четырёх-разностей-кэшей
"""
from pathlib import Path
import json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from CheckSignedMultiply import sbc16_flags
SLOTS={'Top':(0xC2DC,0xC2DE),'Bottom':(0xC2EA,0xC2EC),'Left':(0xC2EE,0xC2FA),'Right':(0xC2FC,0xC2FE)}
ENTRIES=((0xE7E0,'Top','Left'),(0xE7F4,'Top','Right'),(0xE808,'Bottom','Left'),(0xE81C,'Bottom','Right'))


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=z_with_low=0
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 code=[i for region in flow if region['name']=='D3D' for i in region['instructions'] if 0xE7E0<=i['address']<0xE830]
 assert len(code)==32 and sum(len(bytes.fromhex(row['hex'])) for row in code)==80
 for row in code:
  instruction=bytes.fromhex(row['hex']);address=row['address'];assert bytes(m[address:address+len(instruction)])==instruction==raw[address-0xC000:address-0xC000+len(instruction)]
 for entry,_,_ in ENTRIES:assert sum(2 if bytes.fromhex(i['hex'])[0]==0xED else 1 for i in code if entry<=i['address']<entry+20)==12
 refresh_seeds={entry:set() for entry,_,_ in ENTRIES}
 def check(first,second):
  nonlocal cases,z_with_low
  low_borrow=int((first&65535)<(second&65535));result=(first-second)&0xFFFFFFFF;high=result>>16;flags=sbc16_flags(first>>16,second>>16,low_borrow)
  for entry,first_name,second_name in ENTRIES:
   m.recording=False
   for name,value in ((first_name,first),(second_name,second)):
    low,upper=SLOTS[name];m[low:low+2]=[value&255,(value>>8)&255];m[upper:upper+2]=[(value>>16)&255,value>>24]
   s.registers[:]=initial;r=s.registers;r[0]=cases&255;r[1]=(r[1]&254)|(cases&1)
   serial=cases//4;r[14]=serial&255;r[15]=(serial*73)&255;r[26]=serial&1;r[27]=serial%3
   initial_r=r[15];system=(r[14],r[26],r[27]);refresh_seeds[entry].add(initial_r)
   m.recording=True;m.writes=[];s.run(start=entry,stop=0x3FFF)
   assert tuple(r[:8])==(cases&255,flags,second>>24,(second>>16)&255,initial[4],initial[5],high>>8,high&255)
   assert r[8:12]==initial[8:12] and r[12]==0x8000 and r[16:24]==initial[16:24] and not m.writes
   assert r[15]==(initial_r&128)|((initial_r+12)&127)
   assert (r[14],r[26],r[27])==system
   z_with_low+=bool(flags&64 and result&65535);cases+=1
 # Проверка каждого младшего слова первого результата на пяти границах второго, старшие слова проходят полный диапазон.
 for low in range(65536):
  for other in (0,1,32767,32768,65535):check((((low*73+17)&65535)<<16)|low,(((other*37+low*3+29)&65535)<<16)|other)
 # Проверка границ знакового переполнения всей 32-битной разности и ненулевого младшего слова при Z=1.
 values=(0,1,65535,0xFFFF0000,0x7FFFFFFF,0x80000000,0xFFFFFFFF)
 for first in values:
  for second in values:check(first,second)
 rng=random.Random(0xE7E0)
 for _ in range(8192):check(rng.randrange(1<<32),rng.randrange(1<<32))
 assert z_with_low
 report=dict(passed=True,cases=cases,all_four_entry_pairs=True,all_65536_first_low_words=True,second_low_boundaries=[0,1,32767,32768,65535],independent_32_bit_difference_and_low_borrow=True,exact_high_sbc_flags=True,z_checks_high_word_only=True,z_with_nonzero_low_word_cases=z_with_low,exact_main_alternate_and_index_context=True,no_memory_writes=True,left_product_low_and_high_physically_separated=True,irq_executed=False,native_execution=False,assembly_executed=False)
 assert all(values==set(range(256)) for values in refresh_seeds.values())
 report.update(R_full_M1=12,all_256_R_values_per_entry=True,R_bit7_and_I_IM_IFF_preserved=True,
  all_original_80_code_bytes_checked=True,R_full_joint_input_product=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipProductDifferencesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
