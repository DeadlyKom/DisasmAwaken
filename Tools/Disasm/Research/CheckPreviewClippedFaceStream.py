"""Реальный полный DBE9, вызовы заливки и ребра, bitmap и состояние управляющего потока."""
import collections,json,math,random
from ProbePreviewPolygon import context,ROOT
from PreviewClippedFaceOracle import render
from CheckClipGeometry import classify
from skoolkit.simutils import PC,SP


def main():
 m,s,initial=context();cases=0;totals=collections.Counter();profile=(127,95,128,96)
 decisions={(c['first'],c['second']):c for c in json.loads((ROOT/'Tools/Disasm/Reports/PreviewClipDecisionPaths.json').read_text('utf-8'))['cases']}
 m[0x7FFE:0x8000]=[255,63];s.registers[:]=initial;r=s.registers;r[6]=95;r[7]=127;r[4]=r[5]=0;s.run(start=0xE011,stop=0x3FFF)
 buffers=(bytes(6144),bytes([255]*6144),bytes((i*37+11)&255 for i in range(6144)),bytes((85,170))*3072)
 def check(records,points,initial_flag,zero_code=None):
  nonlocal cases
  vertices=bytearray(256);point_map={}
  for i,(row,col) in enumerate(points):
   code=classify((col,row),profile);vertices[5*i:5*i+5]=(col&65535).to_bytes(2,'little')+(row&65535).to_bytes(2,'little')+bytes((0 if i==zero_code else ((~code&15)<<4)|code,));point_map[i*5]=(col,row)
  stream=bytes([v for header,indices in records for v in (header,*[5*i for i in indices])]+[0]);source=buffers[cases%4];wanted=render(source,stream,vertices,point_map,initial_flag,profile,decisions)
  m.recording=False;m[0x4000:0x5800]=source;m[0x6000:0x6000+len(stream)]=stream;m[0xC600:0xC700]=vertices
  m[0xC27B]=initial_flag;m[0xC23B]=0x5A;m[0xC22B]=0xF1;m[0xC24F]=0xA7;m[0xC250]=0x5A;m[0x7FFE:0x8000]=[255,63]
  s.registers[:]=initial;r=s.registers;r[6]=0x60;r[7]=0;r[PC]=0xDBE9;events=[];m.recording=True;m.writes=[]
  for _ in range(500000):
   pc=r[PC]
   if pc==0x3FFF:break
   # Поиск фактических входов обоих растровых алгоритмов, их тело исполняется полностью.
   if pc==0xD41B:
    size=m[0xC22B];events.append(('polygon',m[0xC23B],tuple((m[0xC801+i],m[0xC800+i]) for i in range(0,size,2))))
   elif pc==0xDE1C:
    opcode,branch=m[0xC26F:0xC271];mode={0xA1:'and',0xB1:'or',0xA9:'xor'}[opcode]
    assert (branch,m[0xDE34])==((0x30,0xB8) if mode=='and' else (0x38,0xB0))
    events.append(('edge',mode,(m[0xC24C],m[0xC24B]),(m[0xC24E],m[0xC24D])))
   s.run()
  else:raise AssertionError(('instruction_limit',records,points))
  assert events==wanted['events'],(records,points,initial_flag,events,wanted['events'])
  assert bytes(m[0x4000:0x5800])==wanted['bitmap'],(records,points,initial_flag)
  assert (r[0],r[1],r[6]*256+r[7],r[SP])==(0,0x54,0x6000+wanted['position'],0x8000)
  assert (m[0xC27B],m[0xC23B],m[0xC22B],m[0xC24F],m[0xC250])==(wanted['face_flag'],wanted['fill_mode'],wanted['contour_size'],wanted['seen'],wanted['block'])
  # Проверка десяти физических байтов разнесённого состояния последнего сегмента, включая его коды сторон.
  if wanted['line_state']:
   first,second,c0,c1=wanted['line_state'];words=tuple(int.from_bytes(bytes(m[a:a+2]),'little') for a in (0xC25B,0xC25D,0xC25F,0xC26B))
   assert words==tuple(v&65535 for v in (*first,*second)) and (m[0xC26D],m[0xC26E])==(c0,c1)
  assert bytes(m[0xC600:0xC700])==vertices and bytes(m[0x6000:0x6000+len(stream)])==stream
  totals.update(e[0] for e in events);totals['clipped_polygons']+=wanted['clipped_polygons'];totals['clipped_segments']+=wanted['clipped_segments'];cases+=1
 # Проверка всех счётчиков граней, режимов 0..4, обеих ориентаций и пяти положений относительно окна.
 for count in range(3,16):
  for center_col,center_row in ((64,48),(0,0),(127,95),(-80,48),(207,48)):
   points=[(center_row+round(38*math.sin(-math.pi/2+2*math.pi*i/count)),center_col+round(52*math.cos(-math.pi/2+2*math.pi*i/count))) for i in range(count)]
   for mode in range(5):
    for reverse in (False,True):check([(mode*16+count,list(reversed(range(count))) if reverse else list(range(count)))],points,0)
 # Проверка полилиний во всех режимах, три положения и обе ветви предшествующей ориентации.
 rng=random.Random(0xDBE9)
 for count in range(2,16):
  points=[(rng.randrange(-64,160),rng.randrange(-80,208)) for _ in range(count)]
  for operator in range(4):
   for gated in (False,True):
    for flag in (0,1):check([(0x80+operator*16+64*gated+count,list(range(count)))],points,flag)
 for flag in range(256):check([(0xC2,[0,1])],[(32,-1),(64,128)],flag)
 # Проверка раннего нулевого кода и смешанных потоков без подмены промежуточных обработчиков.
 square=[(16,-10),(16,90),(75,90),(75,-10)]
 for zero in range(4):
  for reverse in (False,True):check([(4,list(reversed(range(4))) if reverse else list(range(4))),(0x94,[0,1,2,3])],square,0,zero)
 for _ in range(32):
  points=[(20,20),(20,90),(75,90),(75,20)];records=[]
  for _ in range(8):
   records.append((rng.randrange(5)*16+4,list(rng.choice(((0,1,2,3),(3,2,1,0)))))) if rng.randrange(2) else records.append((0x84+rng.randrange(4)*16+64*rng.randrange(2),[0,1,2,3]))
  check(records,points,rng.randrange(256))
 report=dict(passed=True,cases=cases,events=dict(totals),full_original_dbe9_executed=True,real_orientation_clippers_fill_and_edge=True,independent_bitmap_composition=True,
  clipping_decisions_derived_from_original_graph=True,all_positive_counts_3_through_15=True,all_line_counts_2_through_15=True,fill_modes=[0,1,2,3,4],all_four_line_operators=True,
  all_256_initial_face_gate_values=True,zero_vertex_code_early_rejection_checked=True,exact_call_order_and_parameters=True,final_hl_af_sp_and_control_bytes_checked=True,
  exact_split_line_workspace_words_and_codes=True,all_final_registers_proved=False,profile=list(profile),nonzero_minima_checked=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewClippedFaceStreamVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
