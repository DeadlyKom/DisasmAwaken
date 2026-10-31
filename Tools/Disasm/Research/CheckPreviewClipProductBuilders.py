"""Четыре производителя, два внутренних входа и настоящий E869 с точным порядком аргументов."""
from pathlib import Path
import collections,json,random,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewFaceProductOracle import product
from PreviewEdgeRasterOracle import logical
ENTRIES=((0xE5E8,'Top',False,0xE5F4,0xC2DC,0xC2DE,0xE5FF),(0xE5F3,'Top',True,0xE5F4,0xC2DC,0xC2DE,0xE5FF),(0xE607,'Bottom',False,0xE613,0xC2EA,0xC2EC,0xE61E),(0xE612,'Bottom',True,0xE613,0xC2EA,0xC2EC,0xE61E),(0xE626,'Left',False,0xE627,0xC2EE,0xC2FA,0xE63D),(0xE645,'Right',False,0xE646,0xC2FC,0xC2FE,0xE65C))


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=extremes=0;entries=collections.Counter()
 def check(a,b):
  nonlocal cases,extremes
  for entry,name,cached,operand,low,high,continuation in ENTRIES:
   boundary=m[operand]+256*m[operand+1];other_row=(a*37+11)&65535
   if name in ('Top','Bottom'):
    col=(b+313)&65535 if cached else b;other_col=71 if cached else 0;row=(a+boundary)&65535;initial_bc=boundary
   else:
    col=(b+boundary)&65535;other_col=(b*17+23)&65535;row=(a+other_row)&65535;initial_bc=other_row
   first=col.to_bytes(2,'little')+row.to_bytes(2,'little')+b'\xF0';second=other_col.to_bytes(2,'little')+other_row.to_bytes(2,'little')+b'\xF0'
   m.recording=False;m[0xC22C:0xC231]=first;m[0xC23C:0xC241]=second;s.registers[:]=initial;r=s.registers;ix=(cases*101+0x2468)&65535;r[8]=ix>>8;r[9]=ix&255
   if cached:r[4]=b>>8;r[5]=b&255
   expected=product(a,b,initial_bc=initial_bc,initial_ix=ix);m.recording=True;m.writes=[];s.run(start=entry,stop=0x3FFF)
   assert tuple(r[:8])==(*expected['af'],expected['bc']>>8,expected['bc']&255,expected['de']>>8,expected['de']&255,expected['hl']>>8,expected['hl']&255),(entry,a,b,r[:8],expected)
   assert r[8]*256+r[9]==expected['ix'] and r[10:12]==initial[10:12] and r[12]==0x8000 and r[16:24]==initial[16:24]
   sign=(a>>8)^(b>>8);writes={0x7FFC:continuation&255,0x7FFD:continuation>>8,0x7FFA:logical(sign),0x7FFB:sign,low:expected['de']&255,low+1:expected['de']>>8,high:expected['hl']&255,high+1:expected['hl']>>8}
   assert dict(m.writes)==writes and len(m.writes)==8
   assert bytes(m[0xC22C:0xC231])==first and bytes(m[0xC23C:0xC241])==second
   entries[hex(entry)]+=1;cases+=1;extremes+=expected['extreme_multiplier_lost']
 # Проверка каждого слова в обеих ролях, включая особый второй множитель 8000.
 for value in range(65536):check(value,0x8000);check(0x1234,value)
 # Настройка всех байтов границ настоящим E011, с независимыми входными координатами и оборачиваемыми разностями.
 factors=(0,1,255,256,32767,32768,65535)
 for index in range(256):
  m.recording=False;s.registers[:]=initial;r=s.registers;r[6]=index;r[7]=(index*73+19)&255;r[4]=index^255;r[5]=(index*37+11)&255;s.run(start=0xE011,stop=0x3FFF)
  for n in range(6):check(factors[n],factors[(n+index)%7])
 rng=random.Random(0xE5E8)
 for _ in range(4096):check(rng.randrange(65536),rng.randrange(65536))
 report=dict(passed=True,cases=cases,entries=dict(entries),extreme_second_8000_cases=extremes,full_and_both_cached_entries=True,all_word_values_in_both_factor_roles=True,real_multiply_not_stubbed=True,ordered_hl_de_arguments_preserved=True,all_256_configured_boundary_bytes=True,cached_de_independent_of_point_column_difference=True,exact_main_alternate_and_index_context=True,exact_four_stack_and_four_data_bytes=True,input_points_preserved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipProductBuildersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
