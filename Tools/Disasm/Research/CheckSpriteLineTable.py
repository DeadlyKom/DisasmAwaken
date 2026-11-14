"""Три страницы адресации просмотра, все байтовые начала и независимая ULA-формула за пределами экрана."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP,PC,I,R,IFF,IM
from CheckRowHighlight import make_context
from PackedRefreshTrace import PackedRefreshTrace


def address(y):return 0x4000+(y//64)*2048+(y&7)*256+((y//8)&7)*32


def main(refresh_only=False):
 _,_,banks=make_context();m=bytearray(65536);m[0x4000:0x8000]=bytes(banks[5]);m[0x8000:0xC000]=bytes(banks[2]);m[0xC000:]=bytes(banks[0]);m[0x7FFE:0x8000]=bytes([255,63]);s=Simulator(m);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);expected=bytearray(m);cases=0
 # Проверка, что реальные входные таблицы отвечают независимой формуле адреса ULA.
 assert all(m[0x8200+y]==address(y)>>8 and m[0x8300+y]==address(y)&255 for y in range(256)) and all(m[0x8400+x]==x//8 for x in range(256))
 flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text(encoding='utf-8'))
 rows=[row for region in flow if region['name']=='Station' for row in region['instructions'] if 0x6322<=row['address']<0x6364]
 trace=PackedRefreshTrace(rows,0)
 # Подсчёт по блокам, полный обход содержит 32 восьмёрки и четыре переноса младшего адреса.
 cost=20+256*10+32*4+28*3+3+32*(1+8*3+4)+1
 assert cost==3724
 for y in range(256):
  origin=(y+16)&255;rows=[address(origin+i) for i in range(256)];expected[0xC900:0xCA00]=bytes(a>>8 for a in rows);expected[0xCA00:0xCB00]=bytes(a&255 for a in rows);end=address(origin+256)
  for x in (((y*73)&255,) if refresh_only else range(256)):
   column=((x+8)&255)//8;expected[0xCB00:0xCC00]=bytes(column+i//8 for i in range(256));s.registers[:]=initial;r=s.registers;r[D]=y;r[E]=x
   r[I]=x;r[R]=y;r[IFF]=y&1;r[IM]=y%3
   if refresh_only:
    trace.initial_r=r[R];trace.m1=trace.steps=0;trace.prefix_counts.clear();r[PC]=0x6322
    # Проверка каждой команды и шага R для всех 256 начал Y.
    for _ in range(cost):
     trace.before(m,r[PC],r[R]);s.run();trace.after(r[R])
    trace.finish(r[R]);assert trace.m1==trace.steps==cost and r[PC]==0x3FFF
   else:s.run(start=0x6322,stop=0x3FFF)
   assert r[R]==((y&128)|((y+cost)&127))
   assert (r[I],r[IFF],r[IM])==(x,y&1,y%3)
   # Итоговые флаги альтернативного AF относятся к двум INC H после последнего продвижения строки, основного AF к завершению таблицы колонок.
   alt_a=(origin&7) if origin&7 else (0 if origin%64==0 else end>>8);alt_f=0x88|int(origin%64==0)
   assert (r[H]*256+r[L],r[D]*256+r[E],r[2],r[3],r[A],r[F],r[16],r[17],r[SP])==(0xCB00,end,0,initial[3],column+32,0x42,alt_a,alt_f,0x8000),(x,y,list(r[:18]))
   assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24] and m==expected;cases+=1
 report=dict(passed=True,cases=cases,all_byte_origins=not refresh_only,all_Y_origins=True,all_X_origins=True,all_joint_X_Y_pairs=not refresh_only,independent_extended_ula_formula=True,full_memory_compared=True,all_768_table_bytes_compared=True,offscreen_addresses_preserved=True,full_main_and_alternate_flags_checked=True,full_m1_per_call=cost,independent_block_m1_formula=True,all_initial_R_values=True,every_instruction_and_R_step_checked=refresh_only,I_IM_IFF_preserved=True,irq_executed=False,native_execution=False,assembly_executed=False)
 name='SpriteLineTableRefresh' if refresh_only else 'SpriteLineTable'
 (ROOT/('Tools/Disasm/Reports/'+name+'Verification.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
