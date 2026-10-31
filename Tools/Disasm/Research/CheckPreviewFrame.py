"""E07F, точный префикс трёх параметров, EI и реальный завершающий помощник станции."""
import json
from ProbePreviewPolygon import context,ROOT
from skoolkit.simutils import PC,IFF
from PreviewEdgeRasterOracle import arithmetic
from CheckPreviewFaceFill import QUADS,TRIANGLES
from CheckWorldSignature import logical_flags


def main():
 m,s,initial=context();prefix_cases=0
 for accumulator in range(256):
  for phase in range(256):
   old=(phase,phase*37&255,phase*53&255)
   expected=(8,(old[1]+2)&255,0) if accumulator==1 else tuple((v+d)&255 for v,d in zip(old,(1,2,3)))
   m.recording=False;m[0xCDC7:0xCDCA]=old;s.registers[:]=initial;r=s.registers;r[0]=accumulator;m.recording=True;m.writes=[]
   # Проверка всех A и всех значений каждой байтовой компоненты до вызова настоящего EC28.
   s.run(start=0xE07F,stop=0xE0AD);value,flags=arithmetic(old[1],2) if accumulator==1 else arithmetic(old[2],3)
   assert tuple(m[0xCDC7:0xCDCA])==expected and (r[0],r[1])==(value,flags)
   assert r[2:12]==initial[2:12] and r[16:24]==initial[16:24] and r[12]==initial[12]
   assert {p for p,v in m.writes}==set(range(0xCDC7,0xCDCA)) and len(m.writes)==3;prefix_cases+=1
 frame_cases=0
 for selector,count in ((0,7),(1,4)):
  for model in range(count):
   m,s,initial=context();m.recording=False;m[0xE146]=model;m[0x7FFE:0x8000]=[255,63];s.registers[:]=initial;r=s.registers;r[0]=selector;r[6]=0x8C;r[7]=0x50;r[4]=r[5]=0
   # Подготовка настоящим внешним E13C, банк и станционная таблица берутся из исходных файлов.
   s.run(start=0xE13C,stop=0x3FFF)
   for accumulator in (0,1,2,255):
    m.recording=False;m[0x7FFE:0x8000]=[255,63];s.registers[12]=0x7FFE;s.registers[0]=accumulator;s.registers[IFF]=0
    old=tuple(m[0xCDC7:0xCDCA]);wanted=(8,(old[1]+2)&255,0) if accumulator==1 else tuple((v+d)&255 for v,d in zip(old,(1,2,3)))
    # Проверка полного графического прохода до завершающего CALL, IRQ симулятор не подаёт.
    s.run(start=0xE07F,stop=0xE0B1);r=s.registers;before=tuple(r[:28]);quad=m[0xF0F0]^0x60;triangle=m[0xF2B7]^0x60
    assert r[IFF]==1 and tuple(m[0xCDC7:0xCDCA])==wanted and r[12]==0x7FFE
    s.run(stop=0x3FFF)
    assert all(m[p]==quad for p in QUADS) and all(m[p]==triangle for p in TRIANGLES)
    assert (r[0],r[1],r[12],r[IFF])==(triangle,logical_flags(triangle),0x8000,1)
    assert tuple(r[2:12])==before[2:12] and tuple(r[16:24])==before[16:24];frame_cases+=1
 report=dict(passed=True,prefix_cases=prefix_cases,full_frame_cases=frame_cases,all_256_input_a=True,all_byte_values_of_each_orientation_parameter=True,
  prefix_all_other_registers_and_exact_three_write_set=True,real_e13c_ec28_queue_render_and_6364=True,ei_changes_iff_zero_to_one=True,
  exact_final_broadcast_headers_and_af=True,real_cpu_sp_restored=True,independent_whole_frame_bitmap_oracle=False,
  irq_delivered=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewFrameVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
