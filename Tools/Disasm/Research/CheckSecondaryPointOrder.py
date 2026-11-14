"""Исходная нормализация указателя второго списка, подсчёт и байтовые смещения порядка."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckMatrixKey import add_flags


class BackwardReadMemory(bytearray):
    def __getitem__(self, address):
        if isinstance(address, int) and self.registers[PC] == 0xCA01 and address < 0xC000:
            self.reads.append(address)
        return super().__getitem__(address)


def check_empty_route(station, source, initial):
    memory = BackwardReadMemory(65536)
    memory[0x6000:0x6000 + len(station)] = station
    memory[0xC000:0xC000 + len(source)] = source
    memory[0x7FFE:0x8000] = b'\xFF\x3F'
    memory[0x6309:0x630B] = b'\x3D\x99'
    assert memory[0x9970:0x997B] == b'\x22' + bytes(10)
    original_prefix = list(range(0x993D, 0x9905, -5))
    extended_prefix = [0x9901, 0x98FC, 0x98F7, 0x98F2]
    assert bytes(station[address - 0x6000] for address in original_prefix) == bytes((0xFF,)) * 11 + b'\x64'
    assert bytes(station[address - 0x6000] for address in extended_prefix) == b'\xFF\xFF\xFF\x00'
    sim = Simulator(memory)
    memory.registers = sim.registers
    for counter in range(256):
        memory[0x9906] = counter
        memory[0x9970] = 0x22
        memory.reads = []
        sim.registers[:] = initial
        sim.run(start=0xC9FB, stop=0x3FFF)
        assert memory.reads == original_prefix + (extended_prefix if counter >= 0x7F else [])
        assert memory[0x6309:0x630B] == b'\x3D\x99' and memory[0x9970:0x997B] == b'\x20' + bytes(10)
    return dict(cases=256, read_pc=0xCA01, original_counter=0x64,
                addresses_through_transition_counter=original_prefix,
                additional_addresses_for_counter_7F_through_FF=extended_prefix,
                resulting_cursor=0x993D, resulting_layout=0x20, resulting_count=0)


def main():
 station,source,banks=make_context();memory=bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 cases=0
 fixtures=[]
 # Проверка каждого первого байта во всех десяти позициях и трёх положениях исходного курсора.
 for marker in range(256):
  for position in range(10):
   values=[255]*10;values[position]=marker
   for cursor in sorted({0,position,10}):fixtures.append((values,cursor,0xA5))
 # Проверка всех исходных служебных байтов и каждого количества 0..10.
 for layout in range(256):
  for count in range(11):fixtures.append(([0x38]*count+[255]*(10-count),10,layout))
 for values,cursor,layout in fixtures:
  table=bytearray([255]*50+[128])
  for i,value in enumerate(values):table[i*5]=value
  memory[0x9938:0x993D]=bytes(5);memory[0x993D:0x9970]=table
  memory[0x6309:0x630B]=(0x993D+cursor*5).to_bytes(2,'little');memory[0x9970]=layout;memory[0x9971:0x997B]=bytes([0xA7])*10
  expected_cursor=0x993D+cursor*5
  while not 0<=memory[expected_cursor]<127:expected_cursor-=5
  expected_cursor=max(expected_cursor,0x993D)
  count=0;end=0
  for i,value in enumerate(values+[128]):
   if 127<=value<255:end=i;break
   if value!=255:count+=1
  memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;r=sim.registers;sim.run(start=0xC9FB,stop=0x3FFF)
  assert int.from_bytes(memory[0x6309:0x630B],'little')==expected_cursor and memory[0x9970]==((layout&240)|count)
  assert memory[0x9971:0x997B]==bytes([5*i for i in range(count)]+[0xA7]*(10-count))
  assert (r[D]*256+r[E],r[B],r[C],r[SP])==(5,0,0xFB,0x8000)
  assert (r[H]*256+r[L],r[A],r[F])==((0x9971+count,count*5,add_flags((count-1)*5,5)) if count else (0x993D+(end+1)*5,0,0x54)),(values,cursor,layout,count,end,r[H]*256+r[L],r[A],r[F])
  assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];cases+=1
 report=dict(passed=True,cases=cases,method='original_secondary_point_cursor_count_and_order_all_markers_slots_layout_bytes',
  marker_7F_terminates_count_and_is_skipped_backward=True,empty_FF_skipped=True,
  order_is_dense_multiples_of_five_not_compacted_slot_offsets=True,
  backward_search_guard_explicit=True,empty_original_route=check_empty_route(station,source,initial),
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/SecondaryPointOrderVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
