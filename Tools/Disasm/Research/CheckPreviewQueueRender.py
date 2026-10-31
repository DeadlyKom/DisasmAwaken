"""EEF1 как обход неизменяемых узлов, реальные матрицы, проекция, классификация и рисование."""
import collections,json,random,struct
from ProbePreviewPolygon import context,ROOT
from skoolkit.simutils import PC
from CheckGlyphRenderer import compare_flags


def main():
 m,s,initial=context();rng=random.Random(0xEEF1);counts=collections.Counter();cases=nodes=0
 # Настройка настоящих пределов, станционная таблица строк подготовлена context.
 m.recording=False;m[0x7FFE:0x8000]=[255,63];s.registers[:]=initial;r=s.registers;r[6]=95;r[7]=127;r[4]=r[5]=0;s.run(start=0xE011,stop=0x3FFF)
 for length in (0,1,2,4,9,18):
  for variant in range(24):
   indices=list(range(18));rng.shuffle(indices);offsets=[i*14 for i in indices[:length]];pool=bytearray((i*37+variant)&255 for i in range(256));items={}
   for number,offset in enumerate(offsets):
    values=(offsets[number+1] if number+1<length else 1,(0,1,128,129)[variant%4],4*((variant+number)%11),0 if variant&1 else number*13&255,variant*7&255,0 if variant&1 else number*29&255,
     ((5000 if 6<=variant<12 else -5000 if 12<=variant<18 else -200+variant*17)&65535),(-120+number*19)&65535,0 if variant>=20 else 800+number*43,(-70+variant*11)&65535)
    encoded=struct.pack('<6B4H',*values);pool[offset:offset+14]=encoded;items[0xC700+offset]=values
   m.recording=False;m[0xC700:0xC800]=pool;m[0xCF02]=offsets[0] if offsets else 1;m[0x4000:0x5800]=[0]*6144;m[0x7FFE:0x8000]=[255,63]
   s.registers[:]=initial;r=s.registers;r[PC]=0xEEF1;m.recording=True;m.writes=[];order=[];calls=[];current=None;renderer=None;seen_renderer=False
   for _ in range(2000000):
    pc=r[PC]
    if pc==0x3FFF:break
    # Проверка чтения каждого следующего узла именно по его Next, без замены узла линейным номером.
    if pc==0xEEF9:
     current=r[6]*256+r[7];assert current==0xC700+offsets[len(order)];order.append(current);calls=[];renderer=None;seen_renderer=False
    elif pc==0xEF5E:
     value=items[current];calls.append('model');assert r[6]*256+r[7]==0xCEFA
     assert tuple(m[0xCEFA:0xCEFC])==value[1:3] and tuple(m[0xC21E:0xC221])==value[3:6]
     actual=tuple(int.from_bytes(bytes(m[a:a+2]),'little') for a in (0xDAF6,0xDA38,0xDA16,0xEB8D));assert actual==value[6:10]
    elif pc in (0xD54C,0xD896,0xDF46):calls.append({0xD54C:'compose',0xD896:'project',0xDF46:'classify'}[pc])
    elif pc==0xEF3F:
     # Расчёт выбора рисователя из фактического результата отдельно проверенного классификатора.
     mask=r[0];renderer=None if r[1]&64 or (mask^255)&0xF0 else (0xDBE9 if mask&15 else 0xDD4F)
     counts['zero_classifier_result']+=bool(r[1]&64);counts['common_outside_classifier_result']+=not bool(r[1]&64) and bool((mask^255)&0xF0)
    elif pc in (0xEF4C,0xEF52):
     assert not seen_renderer and renderer==({0xEF4C:0xDD4F,0xEF52:0xDBE9}[pc]);seen_renderer=True;counts['inside_renderer' if pc==0xEF4C else 'clipped_renderer']+=1
    elif pc==0xEF55:
     assert calls==['model','compose','project','classify'] and seen_renderer==(renderer is not None),(variant,length,calls,renderer,seen_renderer)
     assert r[12]==0x7FFC;counts['rejected_without_renderer']+=renderer is None
    s.run()
   else:raise AssertionError(('instruction_limit',length,variant,r[PC]))
   assert order==[0xC700+o for o in offsets] and bytes(m[0xC700:0xC800])==pool and m[0xCF02]==(offsets[0] if offsets else 1)
   expected_hl=0xC700+offsets[-1] if offsets else 0xC700+initial[7]
   assert (r[0],r[1],r[6]*256+r[7],r[12])==(1,compare_flags(1,1),expected_hl,0x8000)
   assert m[0x7FFE:0x8000]==[255,63];cases+=1;nodes+=length
 report=dict(passed=True,cases=cases,nodes_checked=nodes,cases_by_renderer=dict(counts),queue_lengths=[0,1,2,4,9,18],all_11_model_offsets=True,
  noncontiguous_shuffled_queue_order=True,exact_all_ten_loaded_fields=True,real_matrix_projection_classifier_and_renderers=True,
  synthetic_queue_fields_for_rejection_paths=True,classifier_result_used_as_composition_boundary=True,independent_full_frame_bitmap_oracle=False,queue_and_head_preserved=True,
  final_hl_af_sp_and_cpu_return_checked=True,all_final_registers_proved=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewQueueRenderVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
