"""Оба обновления ребра, все 511 наклонов при каждой допустимой экранной высоте."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from Analyze import payload
from CheckPreviewCoordinateMultiply import Memory
from PreviewEdgeRasterOracle import arithmetic


def main():
 raw=payload(6);m=Memory([0]*65536);m[0xC000:0xC000+len(raw)]=raw;s=Simulator(m)
 initial=get_registers({'SP':0xFFE0,'HL':0xC03A,'DE':0xD169,'BC':0x50B3,'AF':0x005D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False);cases=0;branches={}
 for height in range(1,192):
  for delta in range(-255,256):
   start=max(0,-delta);end=start+delta;m.recording=False;m[0xC800:0xC804]=[start,0,end,height];m[0xD35F]=3
   for right in (False,True):
    pointer=0xD358 if right else 0xD290;m.recording=False;m[pointer:pointer+2]=[1,0xC8]
    s.registers[:]=initial;r=s.registers;m.recording=True;m.writes=[];s.run(start=0xD350 if right else 0xD28C,stop=0xD24A if right else 0xD242)
    magnitude=abs(delta);quotient,remainder=divmod(magnitude,height);wide=magnitude>=height
    # Расчёт целого упакованного шага и вычитаемой дробной части независимо от сдвигов кода.
    step=-((-delta)//height) if delta else 1;packed=(0x2000+32*step)&65535
    subtract=(0 if remainder==0 and wide else height-remainder) if delta>=0 else remainder
    encoded=(quotient^255)>>(1 if right and delta<0 else 0)
    expected_e=encoded if wide else start
    if not right:af=tuple(initial[:2])
    elif wide:
     high=packed>>8;af=(high,arithmetic((high-0x20)&255,0x20)[1])
    elif delta>=0:af=arithmetic(0,(delta-height)&255,True)
    else:
     _,flags=arithmetic(magnitude,height,True);af=(magnitude,(flags&~0x28)|(height&0x28))
    assert tuple(r[:8])==(*af,initial[2],initial[3],0xD1,expected_e,0xC0,0xD1),(height,delta,right,r[:8],af,packed)
    assert r[8:13]==initial[8:13] and r[16:18]==initial[16:18]
    assert r[22:24]==([height//2,initial[23]] if right else [initial[22],height//2])
    pair=(r[20]*256+r[21]) if right else (r[18]*256+r[19]);assert pair==packed
    assert r[18:20]==initial[18:20] if right else r[20:22]==initial[20:22]
    haddr=0xD233 if right else 0xD227;saddr=0xD22F if right else 0xD223;endaddr=0xD243 if right else 0xD23F
    assert (m[haddr],m[saddr],m[endaddr],m[pointer],m[pointer+1])==(height,subtract,height,3,0xC8)
    allowed={haddr,saddr,endaddr,pointer,pointer+1,*range(0xFFDA,0xFFE0)}
    if right:allowed.add(0xD239);assert m[0xD239]==1
    assert all(p in allowed for p,v in m.writes)
    key=('right' if right else 'left')+('_negative' if delta<0 else '_positive')+('_wide' if wide else '_short')
    branches[key]=branches.get(key,0)+1;cases+=1
 wrappers=0
 # Проверка обеих обёрток кольца и прямого JP к правой цепочке на всех входных F.
 for flags in range(256):
  for entry,stop in ((0xD282,0xD350),(0xD285,0xD29A),(0xD34B,0xD364)):
   for index in (range(1,256,2) if entry==0xD285 else range(256) if entry==0xD34B else (1,)):
    m.recording=False;m[0xD35F]=index;s.registers[:]=initial;r=s.registers;r[1]=flags;r[6]=0xC8;r[7]=index;saved=r[:]
    if entry==0xD285:saved[0]=index;saved[7]=index
    elif entry==0xD34B:saved[7]=1
    m.recording=True;m.writes=[];s.run(start=entry,stop=stop)
    assert r[:13]==saved[:13] and r[16:24]==saved[16:24] and not m.writes;wrappers+=1
 report=dict(passed=True,cases=cases,wrapper_cases=wrappers,branches=branches,all_191_heights_and_511_signed_slopes=True,exact_full_main_alternate_and_index_context=True,left_af_preserved=True,right_short_and_wide_af_checked=True,negative_right_half_quotient_preserved=True,exact_operand_targets_and_values=True,wrapped_left_chain_checked=True,both_wrap_helpers_and_right_selector_all_flags_checked=True,temporary_stack_writes_bounded=True,cpu_return_executed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/PreviewPolygonEdgesVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
