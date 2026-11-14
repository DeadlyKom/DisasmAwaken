"""Исходный XOR семистрочного маркера точки, все байтовые смещения и независимый экранный оракул.

Документация: ../../../Docs/MapPointMarker.md
Документация: ../../../Docs/MapMarkerSprites.md
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckInsetFrame import bitmap_address
from CheckWorldSignature import logical_flags
from CheckGlyphRenderer import compare_flags


class ResourceReadMemory(bytearray):
 recording=False
 def __getitem__(self,key):
  if self.recording:
   indices=(key,) if isinstance(key,int) else range(*key.indices(len(self)))
   self.resource_reads.extend(address for address in indices if 0xD800<=address<0xD880)
  return super().__getitem__(key)


def main(record_resource_reads=False):
 _,source,banks=make_context();memory=ResourceReadMemory(65536) if record_resource_reads else bytearray(65536);memory[0x4000:0x8000]=bytes(banks[5]);memory[0x8000:0xC000]=bytes(banks[2]);memory[0xC000:0xC000+len(source)]=source
 if record_resource_reads:
  # Проверка всех загруженных секторов KARTA и положительной CPU-пробы байта и слова в хвосте.
  from hashlib import sha256
  manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
  disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
  entry=next(row for row in manifest['entries'] if row['slot']==7)
  assert sha256(disk).hexdigest()==manifest['sha256']
  assert bytes(source)==disk[entry['offset']:entry['offset']+entry['allocated_length']]
  memory[0x3000:0x3006]=bytes.fromhex('3A0ED82A0FD8')
  probe=Simulator(memory);memory.resource_reads=[];memory.recording=True
  probe.run(start=0x3000,stop=0x3006);memory.recording=False
  assert memory.resource_reads==[0xD80E,0xD80F,0xD810]
  memory.resource_reads=[];memory.recording=True;memory[0xD80E:0xD810];memory.recording=False
  assert memory.resource_reads==[0xD80E,0xD80F]
 sim=Simulator(memory);initial=get_registers({'SP':0x7FFE,'HL':0xD800,'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 # Создание настоящих адресных таблиц с внутренним началом X=8,Y=16.
 memory[0x7FFE:0x8000]=bytes([255,63]);sim.registers[:]=initial;sim.registers[D]=sim.registers[E]=0;sim.run(start=0xC49B,stop=0x3FFF)
 origin_x,origin_y=0x1234,0x5678;memory[0x6300:0x6306]=bytes([origin_x&255,origin_y&255,origin_x>>8,origin_y>>8,128,96])
 sprite=bytes((i*73+19)&255 for i in range(128));memory[0xD800:0xD880]=sprite
 if record_resource_reads:assert all(sprite[phase*16+offset] for phase in range(8) for offset in (14,15))
 baseline=bytes((i*53+(i>>8)*11+17)&255 for i in range(6912));drawn=cases=0
 coords=[(x,y) for x in range(256) for y in range(256)]+[(x,y) for x,y in ((-1,0),(0,-1),(256,0),(0,256),(-32768,0),(0,-32768))]
 # Проверка отсечения, всех восьми фаз и точных четырнадцати экранных XOR на допустимом пути.
 for dx,dy in coords:
  px,py=(origin_x+dx+3)&65535,(origin_y+dy+3)&65535
  first=((py>>8)<<8)|(px>>8);second=((py&255)<<8)|(px&255)
  sim.registers[:]=initial;r=sim.registers;r[D],r[E]=first>>8,first&255;r[B],r[C]=second>>8,second&255
  memory[0x4000:0x5B00]=baseline;memory[0x7FFE:0x8000]=bytes([255,63]);expected=bytearray(baseline)
  valid=0<=dx<120 and 0<=dy<89
  if valid:
   phase=(dx&7)*16
   for row in range(7):
    address=bitmap_address(16+dy+row,1+dx//8)-0x4000
    expected[address]^=sprite[phase+2*row];expected[address+1]^=sprite[phase+2*row+1]
  if record_resource_reads:memory.resource_reads=[];memory.recording=True
  sim.run(start=0xC231,stop=0x3FFF)
  if record_resource_reads:
   memory.recording=False
   assert memory.resource_reads==(list(range(0xD800+phase,0xD800+phase+14)) if valid else []),(dx,dy,memory.resource_reads)
  assert memory[0x4000:0x5B00]==expected,(dx,dy,valid)
  assert r[B]*256+r[C]==0xD800 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
  if valid:
   last=bitmap_address(16+dy+6,1+dx//8)+1
   assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F])==(0xD800+phase+13,last,expected[last-0x4000],logical_flags(expected[last-0x4000]))
  elif (dx&65535)>>8 or (dy&65535)>>8:
   high=((dx&65535)>>8)|((dy&65535)>>8);assert (r[A],r[F])==(high,logical_flags(high))
  elif dx>=120:assert (r[A],r[F])==(120,compare_flags(120,dx))
  else:assert (r[A],r[F])==(89,compare_flags(89,dy))
  drawn+=valid;cases+=1
 report=dict(passed=True,cases=cases,drawn=drawn,method='original_map_point_marker_full_bitmap_all_byte_offsets_and_word_rejections',
  rows=7,bytes_per_row=2,phase_stride=16,phases=8,attributes_preserved=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 if record_resource_reads:
  report.update(method='original_point_marker_exact_resource_reads_and_bitmap_all_byte_offsets',
   original_disk_sha256=manifest['sha256'],original_KARTA_sectors_matched=True,
   exact_resource_read_sequence_checked=True,resource_read_count=drawn*14,
   rejected_cases_without_resource_reads=cases-drawn,
   input_sprite_has_nonzero_phase_tails=True,CPU_byte_and_word_probe_passed=True,memory_slice_probe_passed=True,
   every_accepted_case_reads_offsets_0_through_13_only=True,
   all_initial_byte_offsets_for_one_original_viewport=True,
   all_word_offsets_or_viewports_proved=False,other_resource_consumers_excluded=False,
   global_tail_purpose_proved=False)
 target='MapPointMarkerResourceReadsVerification.json' if record_resource_reads else 'MapPointMarkerVerification.json'
 (ROOT/'Tools/Disasm/Reports'/target).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--resource-reads',action='store_true')
 main(parser.parse_args().resource_reads)
