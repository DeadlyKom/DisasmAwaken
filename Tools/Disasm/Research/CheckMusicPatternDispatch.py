"""Проверка фактических диапазонов кодов и отложенных целей трёх декодеров."""
from pathlib import Path
import collections,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research'))
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory


def add_flags(a,b):
 v=(a+b)&255
 return (v&0xA8)|(0x40 if not v else 0)|(0x10 if (a&15)+(b&15)>15 else 0)|(4 if (~(a^b)&(a^v)&128) else 0)|int(a+b>255)


def main():
 raw=(ROOT/'Tools/Disasm/Extracted/Active/10_MUZ1.C.bin').read_bytes();m=Memory([0]*65536);m[0xDB00:0xDB00+len(raw)]=raw;s=Simulator(m);counts=collections.Counter();table_words={}
 profiles=(('A',0xE439,0xE43C,0xDD,0xDE,(0xE41B,0xE475,0xE3E4,0xE3F8,0xE3DC,0xE479,0xE462)),('B',0xE4E6,0xE4E9,0xDD,0xFE,(0xE4C8,0xE529,0xE491,0xE4A5,0xE489,0xE52D,0xE516)),('C',0xE583,0xE586,0xDE,0x1E,(0xE564,0xE5D1,0xE53D,0xE5B2,0xE5E6,0xE5D5,0xE5BE)))
 for name,entry,read,page,anchor,targets in profiles:
  for opcode in range(256):
   # Независимая таблица диапазонов, особая шумовая команда присутствует только у B.
   thresholds=(0xF0,0xD0,0xC0,0xB0,0x50,0x40,0x10);category=None
   if name=='B' and 0x20<=opcode<0x40:category='noise';threshold=0x20;target=0xE511
   else:
    for n,threshold in enumerate(thresholds):
     if opcode>=threshold:category=('sample_ornament','sample_or_end','volume_or_release','envelope_or_delay','note','ornament','envelope_sample')[n];target=targets[n];break
   effect=category is None
   for flags in range(256):
    note=opcode^flags;m.recording=False;m[0x7000]=opcode;m[0xE2B9]=note;m[0xE6EC]=0xA5;m[0xBFFC:0xC000]=[0xA5,0xA5,255,63]
    initial=get_registers({'HL':0xDB57,'DE':0x7000,'BC':0x2468,'AF':0x9800|flags,'IX':0xABCD,'IY':0x5C3A,'^HL':0x1234,'^DE':0x0618,'^BC':0x9ABC,'^AF':0xDEF0,'SP':0xBFFE,'PC':entry},None,False);s.registers[:]=initial;m.writes=[];m.recording=True
    for n in range(40):
     pc=s.registers[PC];de=s.registers[4]*256+s.registers[5]
     if (not effect and pc==target) or (effect and pc==read and de==0x7001):break
     s.run()
    else:raise AssertionError(('dispatch_boundary',name,opcode,flags))
    m.recording=False;r=s.registers;assert r[4]*256+r[5]==0x7001 and r[2]*256+r[3]==0x1020
    assert all(r[i]==initial[i] for i in (8,9,10,11,*range(16,24)))
    if effect:
     low=(0xE0+2*opcode+anchor)&255;address=page*256+low;word=m[address]+256*m[address+1];table_words[name,str(opcode)]=(address,word)
     expected=[(0xBFFC,word&255),(0xBFFD,word>>8)]
     if name=='C':expected.append((0xE6EC,note))
     assert sorted(m.writes)==sorted(expected) and r[SP]==0xBFFC and r[6]*256+r[7]==word
     next_low=(low+1)&255;expected_f=(add_flags(0xE0+2*opcode,anchor)&1)|(next_low&0xA8)|(0x40 if not next_low else 0)|(4 if low==0x7F else 0)|(16 if low&15==15 else 0)
     assert r[0]==(note if name=='C' else word&255) and r[1]==expected_f,(name,opcode,flags,r[:8],word,expected_f)
     counts[name+'.deferred_pointer']+=1
    else:
     assert not m.writes and r[SP]==0xBFFE and r[6]*256+r[7]==0xDB57
     # Проверка F по сумме, непосредственно выбирающей диапазон исходного декодера.
     increment={0xF0:0x10,0xD0:0x20,0xC0:0x10,0xB0:0x10,0x50:0x60,0x40:0x10,0x20:0x20,0x10:0x10 if name=='B' else 0x30}[threshold]
     assert r[0]==opcode-threshold and r[1]==add_flags((opcode-threshold-increment)&255,increment)
     counts[name+'.'+category]+=1
 report={'passed':True,'cases_by_route':dict(counts),'total_cases':sum(counts.values()),'all_opcode_and_input_flag_bytes':True,
  'deferred_words':[{'channel':n,'opcode':int(op),'address':a,'target':w} for (n,op),(a,w) in sorted(table_words.items())],
  'channel_b_has_distinct_noise_range':True,'all_deferred_stack_words_checked':True,'reserved_pointer_words_not_executed':True,
  'handlers_not_executed':True,'irq_executed':False,'full_pattern_decode_proved':False,'assembly_executed':False}
 (ROOT/'Tools/Disasm/Reports/MusicPatternDispatchVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='deferred_words'},indent=2))


if __name__=='__main__':main()
