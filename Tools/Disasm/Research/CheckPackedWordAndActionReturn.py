"""Двухбайтовое пополнение битов и стековый возврат AF после непрямого рисователя."""
import collections,json
from ProbeShipPreviewCallbacks import Fixture,ROOT,make_context,put
from CheckScreenUpdate import pointer_image
from skoolkit.simutils import PC,SP


def main():
 station,_,base=make_context();f=Fixture(base);m=f.memory;s=f.sim;initial=f.initial;counts=collections.Counter();before=[bytes(b) for b in m.banks]
 assert bytes(m[0x7F30:0x7F33])==bytes.fromhex('cdd863') and bytes(m[0x7F33:0x7F35])==bytes.fromhex('f1c9')
 def refill(ix,c,flags):
  word=m[ix]+256*m[(ix+1)&65535];s.registers[:]=initial;r=s.registers;r[8:10]=[ix>>8,ix&255];r[3]=c;r[1]=flags;s.run(start=0xA014,stop=0x3FFF)
  assert tuple(r[:8])==(initial[0],flags,c,c,initial[4],initial[5],word>>8,word&255)
  assert r[8]*256+r[9]==(ix+2)&65535 and r[10:12]==initial[10:12] and r[16:24]==initial[16:24] and r[SP]==0x8000 and r[14]==initial[14] and r[26:28]==initial[26:28]
 # Проверка всех 65536 слов и всех сочетаний исходного C с полным F.
 for word in range(65536):put(m,0x9000,word.to_bytes(2,'little'));refill(0x9000,16,0x5D);counts['all_refill_words']+=1
 for cf in range(65536):refill(0x9000,cf>>8,cf&255);counts['all_counter_and_flags_pairs']+=1
 # Проверка каждого исходного IX, включая переход FFFF в ноль и чтение из стека либо самого кода.
 for ix in range(65536):refill(ix,16,0x5D);counts['all_stream_pointers']+=1
 # Проверка всех сохранённых AF, стек содержит SavedAF и внешний ReturnAddress.
 for af in range(65536):
  put(m,0x7FFC,af.to_bytes(2,'little'));s.registers[:]=initial;r=s.registers;r[SP]=0x7FFC;s.run(start=0x7F33,stop=0x3FFF)
  assert r[:2]==[af>>8,af&255] and r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[SP]==0x8000;counts['all_saved_af_words']+=1
 # Проверка каждого SP за ровно POP AF и RET, произвольная извлечённая цель не исполняется.
 for sp in range(65536):
  flags,a=m[sp],m[(sp+1)&65535];target=m[(sp+2)&65535]+256*m[(sp+3)&65535];s.registers[:]=initial;r=s.registers;r[SP]=sp;r[PC]=0x7F33;s.run();s.run()
  assert r[:2]==[a,flags] and r[PC]==target and r[SP]==(sp+4)&65535 and r[2:12]==initial[2:12] and r[16:24]==initial[16:24];counts['all_return_stack_pointers_two_steps_only']+=1
 # Проверка отсутствия записей инструкциями двух примитивов, исключены только входы, подготовленные самой моделью.
 allowed={(2,0x1000),(2,0x1001),(5,0x3FFC),(5,0x3FFD)}
 for bank,(old,new) in enumerate(zip(before,m.banks)):
  assert all(a==b or (bank,index) in allowed for index,(a,b) in enumerate(zip(old,new)))
 # Проверка ранее не выделенного CALL ResumePointer и общего хвоста с независимым рисунком указателя.
 for page in (0x10,0x18):
  for x in (0,7,248,255):
   for y in (0,1,7,120,184,191):
    f=Fixture(base,page=page);m=f.memory;s=f.sim;r=s.registers;put(m,0x4000,bytes([0x96])*6912);put(m,0x6307,(x,y));af=((x+y)&255)*256+((x*73+y)^0xA5)&65535;put(m,0x7FFC,af.to_bytes(2,'little'));r[SP]=0x7FFC;frame=list(m[0x4000:0x6000]);expected=pointer_image(frame,station,x,y)
    s.run(start=0x7F30,stop=0x3FFF)
    assert r[:2]==[af>>8,af&255] and r[2:12]==f.initial[2:12] and r[18:24]==f.initial[18:24] and r[SP]==0x8000
    assert bytes(m[0x4000:0x6000])==bytes(expected) and m[0x9B16]==0 and m.o7ffd==m[0x6306]==page;counts['real_pointer_resume_and_saved_af_return']+=1
 report=dict(passed=True,cases_by_path=dict(counts),stream_word_little_endian=True,flags_including_carry_preserved=True,
  stream_and_stack_wrap_checked=True,primitives_do_not_write_memory=True,new_return_continuation_bytes='CD D8 63',
  synthetic_return_from_handle_item_00=True,independent_pointer_bitmap=True,saved_af_frame_bytes=4,return_sp_delta=4,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PackedWordAndActionReturnVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
