"""Полный исходный путь присваивания семи полей до входа NextCommand, все одиннадцать операторов."""
from pathlib import Path
from itertools import product
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckMultiplyBranches import reference as multiply


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
 sources={e['slot']:(ROOT/(e['path']+'.sectors.bin')).read_bytes() for e in manifest['entries'] if e['slot'] in (4,5)}
 original=bytearray(65536);original[0x6000:]=sources[4];original[0xC000:0xC000+len(sources[5])]=sources[5]
 memory=original.copy();sim=Simulator(memory)
 initial=get_registers({'SP':0x7FF0,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 ops={'=':(0xC3D5,lambda x,y:int(x==y)),'*':(0xC3DF,lambda x,y:multiply(x,y)[0]),
 '+':(0xC488,lambda x,y:min(x+y,65535)),'-':(0xC491,lambda x,y:max(x-y,0)),
 '<':(0xC49C,lambda x,y:int(x<y)),'>':(0xC4A6,lambda x,y:int(x>y)),
 '[':(0xC4B1,lambda x,y:int(x<=y)),']':(0xC4BC,lambda x,y:int(x>=y)),
 '&':(0xC4C6,lambda x,y:x&y),'!':(0xC4CD,lambda x,y:x|y),':':(0xC4D4,lambda x,y:y)}
 fields={'c':(0x984E,0xC648,0xC652,'word'),'u':(0x984B,0xC65D,0xC669,'byte'),
 'J':(0x9851,0xC674,0xC680,'byte'),'g':(0x9852,0xC695,0xC6A5,'cargo'),
 'G':(0x9555,0xC695,0xC6A5,'market'),'o':(0x988E,0xC6CB,0xC6DB,'weight'),'i':(0x98F6,0xC6CB,0xC6DB,'weight')}
 count=0
 for key,(field,invoke,store,kind) in fields.items():
  for old,right,(symbol,(operator,formula)) in product((0,1,127,128,255,256,32767,65535),(0,1,127,255,256,32767,65535),ops.items()):
   memory[:]=original
   for address in (0x7068,0x7026,0x7217,0x71B9,0x73D8,0x737D):memory[address]=0
   raw=old if kind=='word' else old&255
   if kind=='word':memory[field:field+2]=raw.to_bytes(2,'little')
   else:memory[field]=raw
   text=(key+symbol+str(right)).encode()+b'\x00';memory[0xB000:0xB000+len(text)]=text;memory[0x7FF0:0x7FF2]=bytes([255,63])
   left=raw if kind in ('word','byte','cargo') else raw&127 if kind=='market' else raw if raw<128 else raw^255
   sim.registers[:]=initial;r=sim.registers;sim.run(start=0xC09F,stop=operator)
   indexed=kind in ('cargo','market','weight');operator_sp=0x7FE8 if indexed else 0x7FEA
   assert (r[D]*256+r[E],r[B]*256+r[C],r[H]*256+r[L],r[SP],r[22]*256+r[23])==(left,right,operator,operator_sp,0xCA7B),(key,symbol,old,right,list(r))
   assert memory[operator_sp:operator_sp+2]==store.to_bytes(2,'little')
   if indexed:assert memory[operator_sp+2:operator_sp+4]==field.to_bytes(2,'little')
   post=operator_sp+(4 if indexed else 2)
   assert memory[post:post+2]==bytes([0xCF,0xC0]) and memory[post+2:post+4]==bytes([0,0xB8])
   assert memory[0xCA7B:0xCA81]==invoke.to_bytes(2,'little')+operator.to_bytes(2,'little')+right.to_bytes(2,'little')
   result=formula(left,right);stored=result if kind=='word' else result&255 if kind=='byte' else ((raw&128)|(127 if result>>8 else result&127)) if kind in ('cargo','market') else (result&255)^(255 if raw&128 else 0)
   sim.run(start=operator,stop=0xC00C)
   assert int.from_bytes(memory[field:field+(2 if kind=='word' else 1)],'little')==stored,(key,symbol,old,right,result,stored)
   assert r[22]*256+r[23]==0xB800 and r[SP]==0x7FF0 and r[20]*256+r[21]==0xFFFB
   assert r[8]*256+r[9]==0xB000+len(text)-1 and r[10:12]==initial[10:12] and r[16:18]==initial[16:18] and r[19]==initial[19] and r[18]==({'g':1,'G':3,'o':2,'i':2}.get(key,initial[18])), (key,symbol,old,right,list(r),list(initial))
   assert memory[0x7FF0:0x7FF2]==bytes([255,63])
   count+=1
 report=dict(passed=True,cases=count,method='complete_original_assignment_until_next_command',all_seven_writers=True,all_eleven_operators=True,
  calls_stubbed=False,operator_frame_checked=True,original_expression_top_restored=True,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/AssignPipelineVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
