"""Настройка исходных границ D3D, все байтовые размеры и полное сравнение банка.

Документация: ../../../Docs/PreviewClipBounds.md#полные-записи-r-и-активная-рамка-возврата
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from Analyze import payload
from D3DClipFacts import PATCHES,PATCH_FORMS
from CheckPreviewCoordinateMultiply import Memory
from collections import Counter


def reference_patch(max_x,max_y,min_x,min_y):
 result={}
 def byte(address,value):result[address]=value
 def word(address,value):result[address]=value&255;result[address+1]=value>>8
 byte(0xDAE7,((max_x+1)&255)//2);byte(0xDBA5,((max_y+1)&255)//2)
 for a,x,y in ((0xE7DB,max_x,max_y),(0xE7BA,min_x,min_y),(0xE7D0,max_x,min_y),(0xE7C5,min_x,max_y)):word(a,256*x+y)
 for addresses,value in (((0xE613,0xE6E0,0xE6F3,0xE72E,0xE78B),max_x),((0xDF7F,),(max_x+1)&255),((0xE5F4,0xE695,0xE6A8,0xE73F,0xE79C),min_x),((0xE646,0xE69D,0xE6E8,0xE788,0xE799,0xE7AB),max_y),((0xDF64,),(max_y+1)&255),((0xE627,0xE692,0xE6DD,0xE72B,0xE73C,0xE74E),min_y)):
  for address in addresses:byte(address,value)
 return result


def main():
 raw=payload(6);forms={}
 for address,(opcode,kind,size) in PATCH_FORMS.items():
  assert raw[address-0xC001]==opcode,(hex(address),kind)
  forms[PATCHES[address]]=dict(address=address,instruction=kind,bytes_written=size)
 m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;m[0x7FFE:0x8000]=[255,63];expected=bytearray(m[0xC000:]);s=Simulator(m)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
 codes=[i for region in flow if region['name']=='D3D' for i in region['instructions'] if 0xE011<=i['address']<0xE07F]
 assert len(codes)==46 and sum(len(bytes.fromhex(i['hex'])) for i in codes)==110
 assert sum(2 if bytes.fromhex(i['hex'])[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in codes)==50
 for row in codes:
  code=bytes.fromhex(row['hex']);address=row['address'];assert bytes(m[address:address+len(code)])==code==raw[address-0xC000:address-0xC000+len(code)]
 refresh_seeds=set()
 for max_x in range(256):
  for max_y in range(256):
   for min_x,min_y in ((0,0),((max_y*73+19)&255,(max_x*47+31)&255)):
    s.registers[:]=initial;r=s.registers;r[H]=max_x;r[L]=max_y;r[D]=min_x;r[E]=min_y
    r[14]=cases&255;r[15]=(cases*73)&255;r[26]=cases&1;r[27]=cases%3
    initial_r=r[15];system=(r[14],r[26],r[27]);refresh_seeds.add(initial_r)
    # Независимая геометрия задаёт четыре угла и повторённые байтовые пределы.
    patch=reference_patch(max_x,max_y,min_x,min_y)
    assert len(patch)==34
    for address,value in patch.items():expected[address-0xC000]=value
    m.recording=True;m.writes=[]
    s.run(start=0xE011,stop=0x3FFF)
    # Флаги принадлежат последнему INC верхнего Y, Carry остаётся от его раннего деления на два.
    value=(max_y+1)&255;flags=(value&0xA8)|(0x40 if value==0 else 0)|(0x10 if max_y&15==15 else 0)|(4 if max_y==127 else 0)|(value&1)
    assert (r[H],r[L],r[D],r[E],r[A],r[F],r[SP])==(max_x,min_y,min_x,max_y,min_y,flags,0x8000)
    assert r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    assert bytes(m[0xC000:])==expected,(max_x,max_y,min_x,min_y)
    assert Counter(m.writes)==Counter(patch.items())
    assert r[15]==(initial_r&128)|((initial_r+50)&127)
    assert (r[14],r[26],r[27])==system
    cases+=1
 # Ограниченная проверка перекрытия активного возврата словом настраиваемого MinCorner.
 probe=Memory(list(m));probe.recording=False;probe[0xE7BA:0xE7BC]=[255,63]
 cpu=Simulator(probe);cpu.registers[:]=initial;r=cpu.registers;r[H:L+1]=[0x77,0x88];r[D:E+1]=[0x11,0x22]
 r[SP]=0xE7BA;r[24]=0xE011;r[15]=0xFE;probe.recording=True;probe.writes=[]
 for _ in range(46):cpu.run()
 assert r[24]==0x1122 and r[SP]==0xE7BC and r[15]==0xB0
 assert Counter(probe.writes)==Counter(reference_patch(0x77,0x88,0x11,0x22).items())
 report=dict(passed=True,cases=cases,original_patch_instruction_forms=forms,all_byte_width_height_pairs=True,nonzero_and_inverted_lower_bounds=True,full_bank_compared=True,byte_overflow_preserved=True,full_register_and_flags_checked=True,irq_executed=False,native_execution=False,assembly_executed=False)
 assert refresh_seeds==set(range(256))
 report.update(original_code_instructions=46,original_code_bytes=110,R_full_M1=50,
  all_256_R_values=True,R_bit7_and_I_IM_IFF_preserved=True,all_34_CPU_writes_values_and_multiplicity_checked=True,
  hardware_bus_write_order_proved=False,R_full_joint_input_product=False,
  return_frame_alias_probe=dict(input_SP=0xE7BA,initial_return=0x3FFF,actual_return=0x1122,
   bounded_instructions=46,target_executed=False,overwriting_field='D3DClipState.MinCorner'))
 (ROOT/'Tools/Disasm/Reports/PreviewClipBoundsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
