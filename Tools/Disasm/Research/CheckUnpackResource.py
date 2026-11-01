"""Все исходные HR-ресурсы, независимый декодер и четыре профиля перекрытия входа с выходом."""
import collections,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from Analyze import payload
from PackedResourceCodec import decode
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,PC,SP,I,IFF,IM


def main():
 structure=(ROOT/'Includes/Structs/Include.inc').read_text('utf-8').split('struct FUnpackTailFrame',1)[1].split('                ends',1)[0]
 assert re.findall(r'(?m)^(\w+)\s+dw #0000\s*;',structure)==['FinalWord0','FinalWord1','FinalWord2','ReturnAddress']
 records=json.loads((ROOT/'Tools/Disasm/Reports/Screens.json').read_text('utf-8'));previous=json.loads((ROOT/'Tools/Disasm/Reports/DecodedScreens.json').read_text('utf-8'));hashes={(r['slot'],r['index']):r['sha256'] for r in previous}
 station=payload(4);original=[0]*65536;original[0x6000:]=station;initial=get_registers({'SP':0x5FFE,'AF':0x5A5D,'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,'I':0xA7,'IM':2,'IFF':1,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 counts=collections.Counter();packets=collections.Counter();outputs=[];lookaheads=[]
 for record in records:
  raw=payload(record['slot'])[record['offset']:record['offset']+record['packed_size']];size=record['unpacked_size'];packed=len(raw)
  for source,dest in ((0xC000,0x4000),(0xB000,0xC000),(0xD000,0xC000),(0x6000,0x4000)):
   m=original.copy();m[source:source+packed]=raw;m[0x5FFE:0x6000]=[255,63];base=max(source,dest+size-packed)
   assert max(source,0x9EFF)>=min(source+packed,0xA020) and max(dest,0x9EFF)>=min(dest+size,0xA020)
   expected=decode(raw,bytes(m[base+packed:base+packed+2]));assert hashlib.sha256(expected['data']).hexdigest()==hashes[record['slot'],record['index']]
   before=m.copy();s=Simulator(m);r=s.registers;r[:]=initial;r[6:8]=[source>>8,source&255];r[4:6]=[dest>>8,dest&255];r[PC]=0x9EFF;native=collections.Counter();tail=0;frame=False
   for steps in range(600000):
    pc=r[PC]
    if pc==0x3FFF:break
    if pc==0x9F35 and not frame:
     assert r[SP]==0x5FF8 and bytes(m[0x5FF8:0x6000])==raw[6:12]+bytes((255,63));frame=True
    if pc in (0x9F35,0xA009):native['literal_bytes']+=1
    if pc==0x9F9A:native['matches']+=1
    if pc==0x9FB0:native['reference_literal_reference']+=1
    if pc==0x9FA0:native['window_rotations']+=1
    if pc==0x9FD4:native['word_lengths']+=1
    if pc==0x9FE6:
     assert tail<3 and r[SP]==0x5FF8+2*tail and bytes(m[r[SP]:r[SP]+2])==raw[6+2*tail:8+2*tail];tail+=1
    s.run()
   else:raise AssertionError(('instruction_limit',record['slot'],record['index'],hex(source),hex(dest),hex(r[PC])))
   assert bytes(m[dest:dest+size])==expected['data'] and frame and tail==3
   assert r[:8]==[15,0x4A,expected['remaining_bits'],16,expected['window_mask'],4,expected['bit_word']>>8,expected['bit_word']&255],(record['slot'],record['index'],r[:8],expected)
   assert r[8]*256+r[9]==base+expected['stream_position'] and r[10:12]==initial[10:12] and r[16:18]==initial[16:18]
   assert r[18:24]==[0,expected['final_output_count_low'],expected['final_tail_word']>>8,expected['final_tail_word']&255,0x27,0x58]
   assert r[SP]==0x6000 and r[I]==initial[I] and r[IFF]==initial[IFF] and r[IM]==initial[IM]
   for name,value in native.items():assert value==expected['counts'].get(name,0),(record['slot'],record['index'],name,value,expected['counts'])
   assert all(a==b or dest<=address<dest+size or base+1<=address<base+packed or 0x5FF6<=address<0x6000 for address,(a,b) in enumerate(zip(before,m)))
   counts['complete_original_calls']+=1;counts['relocated_inputs']+=base!=source;counts['all_output_bytes']+=size;counts['stack_frame_checks']+=4
   if expected['lookahead_bytes_read']:lookaheads.append(dict(slot=record['slot'],index=record['index'],source=source,dest=dest,bytes=expected['lookahead_bytes_read']))
   if source==0xC000:packets.update(expected['counts'])
   outputs.append(dict(slot=record['slot'],index=record['index'],source=source,dest=dest,relocated_base=base,instructions=steps,stream_position=expected['stream_position'],sha256=hashlib.sha256(expected['data']).hexdigest()))
 report=dict(passed=True,cases_by_path=dict(counts),resources=len(records),independent_packet_counts=dict(packets),profiles=outputs,lookahead_cases=lookaheads,
  independent_dictionary_bitstream_and_output=True,all_main_and_alternate_general_registers_checked=True,all_writes_limited_to_declared_ranges=True,
  six_saved_tail_bytes_restored=True,physical_three_tail_words_and_return_checked=True,overread_word_on_final_refill_documented=True,
  existing_screen_hashes_match=True,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/UnpackResourceVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ('profiles','lookahead_cases')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
