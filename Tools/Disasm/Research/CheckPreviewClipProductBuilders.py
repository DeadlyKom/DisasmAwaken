"""Четыре производителя, два внутренних входа и настоящий E869 с точным порядком аргументов.

Документация: ../../../Docs/PreviewClipProducts.md#r-производителей-и-настоящего-умножителя
"""
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
from PackedRefreshTrace import PackedRefreshTrace
ENTRIES=((0xE5E8,'Top',False,0xE5F4,0xC2DC,0xC2DE,0xE5FF),(0xE5F3,'Top',True,0xE5F4,0xC2DC,0xC2DE,0xE5FF),(0xE607,'Bottom',False,0xE613,0xC2EA,0xC2EC,0xE61E),(0xE612,'Bottom',True,0xE613,0xC2EA,0xC2EC,0xE61E),(0xE626,'Left',False,0xE627,0xC2EE,0xC2FA,0xE63D),(0xE645,'Right',False,0xE646,0xC2FC,0xC2FE,0xE65C))


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=extremes=0;entries=collections.Counter()
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 code=[i for region in flow if region['name']=='D3D' for i in region['instructions'] if 0xE5E8<=i['address']<0xE664 or 0xE869<=i['address']<0xEA01]
 for row in code:
  instruction=bytes.fromhex(row['hex']);address=row['address'];assert raw[address-0xC000:address-0xC000+len(instruction)]==instruction
 child_rows=[i for i in code if i['address']>=0xE869]
 parent_code={i['address']:bytes.fromhex(i['hex']) for i in code if i['address']<0xE664}
 trace=PackedRefreshTrace(child_rows,0);seeds={};m1_bounds={}
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
   expected=product(a,b,initial_bc=initial_bc,initial_ix=ix)
   serial=entries[hex(entry)];r[14]=serial&255;r[15]=(serial*73)&255;r[26]=serial&1;r[27]=serial%3
   initial_r=r[15];system=(r[14],r[26],r[27]);seeds.setdefault(entry,set()).add(initial_r)
   trace.m1=trace.steps=0;trace.prefix_counts.clear();child_done=False;own_m1=0
   m.recording=True;m.writes=[];r[24]=entry
   for _ in range(1024):
    pc=r[24]
    if pc==0x3FFF:break
    if pc>=0xE869:
     if pc==0xE869:trace.initial_r=r[15]
     trace.before(m,pc,r[15]);s.run();trace.after(r[15])
     if r[24]==continuation:trace.finish(r[15]);child_done=True
    else:
     instruction=parent_code[pc]
     # Проверка родительских команд, четыре нижних байта границ меняются E011.
     for offset,value in enumerate(instruction):
      if pc+offset not in (0xE5F4,0xE613,0xE627,0xE646):assert m[pc+offset]==value
     cost=2 if instruction[0] in (0xCB,0xDD,0xED,0xFD) else 1;before_r=r[15]
     s.run();own_m1+=cost;assert r[15]==(before_r&128)|((before_r+cost)&127)
   else:raise AssertionError(('product builder instruction limit',entry,a,b))
   assert child_done and own_m1==(10 if cached else 17)
   assert r[15]==(initial_r&128)|((initial_r+own_m1+trace.m1)&127)
   assert (r[14],r[26],r[27])==system
   bounds=m1_bounds.setdefault(hex(entry),[own_m1+trace.m1,own_m1+trace.m1])
   bounds[0]=min(bounds[0],own_m1+trace.m1);bounds[1]=max(bounds[1],own_m1+trace.m1)
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
 assert all(values==set(range(256)) for values in seeds.values())
 report.update(R_overhead_full_entry=17,R_overhead_FromDelta=10,real_child_full_M1_and_each_R_step_checked=True,
  all_256_R_values_per_entry=True,R_bit7_and_I_IM_IFF_preserved=True,full_m1_bounds_by_entry=m1_bounds,
  independent_whole_multiply_M1_oracle=False,R_full_joint_input_product=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClipProductBuildersVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
