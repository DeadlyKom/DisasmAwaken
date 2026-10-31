"""Оригинальный полный проход DD4F с настоящими ориентацией, заливкой и рёбрами, без отсечения."""
import collections,json,math,random
from ProbePreviewPolygon import context,ROOT
from PreviewFaceStreamOracle import render
from skoolkit.simutils import PC,SP


def main():
 m,s,initial=context();cases=0;events_total=collections.Counter();buffers=(bytes(6144),bytes([255]*6144),bytes((i*37+11)&255 for i in range(6144)),bytes((85,170))*3072)
 def check(records,count,initial_flag):
  nonlocal cases
  points=[(80+round(55*math.sin(-math.pi/2+2*math.pi*i/count)),96+round(55*math.cos(-math.pi/2+2*math.pi*i/count))) for i in range(count)]
  vertices=bytearray(256)
  for i,(row,column) in enumerate(points):vertices[5*i:5*i+5]=[column,0,row,0,0xF0]
  stream=bytes([v for header,indices in records for v in (header,*[5*i for i in indices])]+[0]);source=buffers[cases%4];expected=render(source,stream,vertices,initial_flag,initial)
  m.recording=False;m[0x4000:0x5800]=source;m[0x6000:0x6000+len(stream)]=stream;m[0xC600:0xC700]=vertices;m[0xC27B]=initial_flag;m[0xC23B]=0x5A;m[0xC22B]=0xF1;m[0x7FFE:0x8000]=[255,63]
  s.registers[:]=initial;r=s.registers;r[6]=0x60;r[7]=0;r[PC]=0xDD4F;m.recording=True;m.writes=[];events=[]
  for _ in range(500000):
   pc=r[PC]
   if pc==0x3FFF:break
   assert pc not in (0xE171,0xEAB6),('unexpected_clipper',records)
   # Поиск фактических вызовов исходных рисователей без подмены их процедур.
   if pc==0xD41B:
    size=m[0xC22B];contour=tuple((m[0xC801+i],m[0xC800+i]) for i in range(0,size,2));events.append(('polygon',m[0xC23B],contour))
   elif pc==0xDE1C:
    opcode,branch=m[0xC26F:0xC271];mode={0xA1:'and',0xB1:'or',0xA9:'xor'}[opcode]
    assert (branch,m[0xDE34])==((0x30,0xB8) if mode=='and' else (0x38,0xB0))
    events.append(('edge',mode,(m[0xC24C],m[0xC24B]),(m[0xC24E],m[0xC24D])))
   s.run()
  else:raise AssertionError(('instruction_limit',records))
  assert events==expected['events'],(records,initial_flag,events,expected['events'])
  assert bytes(m[0x4000:0x5800])==expected['bitmap'],(records,initial_flag)
  assert (r[0],r[1],r[6]*256+r[7],r[SP])==(0,0x54,0x6000+expected['position'],0x8000)
  # Проверка полного конечного контекста композицией договоров последней грани и каждого ребра.
  final=expected['registers']
  for key,offset in (('bc',2),('de',4),('ix',8),('iy',10),('alt_bc',18),('alt_de',20),('alt_hl',22)):
   assert r[offset]*256+r[offset+1]==final[key],(records,initial_flag,key,r[offset:offset+2],final)
  assert tuple(r[16:18])==final['alt_af'],(records,initial_flag,r[16:18],final)
  assert (m[0xC27B],m[0xC23B],m[0xC22B])==(expected['face_flag'],expected['fill_mode'],expected['contour_size'])
  assert bytes(m[0xC600:0xC700])==vertices and bytes(m[0x6000:0x6000+len(stream)])==stream
  events_total.update(event[0] for event in events);cases+=1
 # Проверка всех допустимых счётчиков положительной грани, режимов 0..4 и обоих порядков обхода.
 for count in range(3,16):
  for mode in range(5):
   for reverse in (False,True):check([(mode*16+count,list(reversed(range(count))) if reverse else list(range(count)))],count,0)
 # Проверка четырёх кодов операции линии, обеих ветвей bit6 и всех счётчиков 2..15.
 for count in range(2,16):
  for operator in range(4):
   for gated in (False,True):
    for flag in (0,1):check([(0x80+operator*16+64*gated+count,list(range(count)))],count,flag)
 # Проверка каждого байтового значения признака предыдущей грани, нуль отличается от любого ненуля.
 for flag in range(256):
  check([],3,flag)
  for operator in range(4):check([(0xC2+operator*16,[0,1])],3,flag)
 rng=random.Random(0xDD4F)
 for _ in range(64):
  count=rng.randrange(3,16);front=list(range(count));back=list(reversed(front));records=[]
  for _ in range(8):
   if rng.randrange(2):records.append((rng.randrange(5)*16+count,rng.choice((front,back))))
   else:records.append((0x80+rng.randrange(4)*16+64*rng.randrange(2)+count,front))
  check(records,count,rng.randrange(256))
 report=dict(passed=True,cases=cases,events=dict(events_total),full_original_dd4f_pass_executed=True,orientation_and_both_renderers_not_stubbed=True,independent_stream_parser_and_bitmap_composition=True,all_positive_counts_3_through_15=True,all_polyline_counts_2_through_15=True,all_four_line_operator_codes=True,all_256_previous_face_flags=True,bit6_depends_on_previous_orientation_only=True,exact_call_parameters_and_order=True,final_hl_af_sp_and_control_bytes_checked=True,projected_vertices_and_input_stream_preserved=True,all_final_registers_proved=True,clipped_dbe9_path_proved=False,convex_onscreen_zero_origin_profile=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewInsideFaceStreamVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
