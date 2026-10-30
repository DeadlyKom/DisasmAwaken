"""Исходная обёртка строки миссии с реальным XOR, указателем и проверкой сохранённого операнда."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,SP,PC
from CheckRowHighlight import make_context,band_parameters
from CheckScreenUpdate import PortTrace,put,pointer_image
from CheckSelectionBand import xor_band


def main():
 station,_,banks=make_context();banks=[bytearray(b) for b in banks]
 memory=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=0x10);sim=Simulator(memory)
 initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xF2ED,'IY':0x5C3A,
  '^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 baseline=[(i*73+(i>>8)*19+17)&255 for i in range(8192)];cases=changed=0
 for last in (False,True):
  for previous in (0,1,255):
   for py in range(192):
    memory.banks=[b.copy() for b in banks];memory.memory=[None,memory.banks[5],memory.banks[2],None];memory.out7ffd(0x10)
    put(memory,0xF2ED,[6,10,11,4,0x26]);put(memory,0x9CA6,[0,0xE0])
    put(memory,0xE000,[0,0x70,0xC5,0x6F,1,1] if last else [0xC5,0x6F,0,0x70,1,1])
    put(memory,0x8500,[31,0]);put(memory,0x8600,bytes(768))
    for y in range(10,14):
     for x in range(6,17):memory[0x8600+32*y+x]=1
    put(memory,0x6307,[50,py]);memory[0x6306]=0x10;memory[0x6548]=0xA5;memory[0x9B16]=0x5A;memory[0x6F54]=previous
    scene=baseline.copy()
    def invert(image,row):
     params=band_parameters(6,10,11,3,row)
     if params is not None:xor_band(image,*params)
    if previous!=255:invert(scene,previous)
    put(memory,0x4000,scene);put(memory,0x7FFE,[255,63]);sim.registers[:]=initial;r=sim.registers;trace=PortTrace(sim);sim.set_tracer(trace)
    hit=83<=py<99;row=(py-83)//8 if hit else None;update=last and hit and row!=previous
    expected=scene.copy()
    if update:
     if previous!=255:invert(expected,previous)
     invert(expected,row);expected=pointer_image(expected,station,50,py)
    r[PC]=0x6F4D;recent=[]
    for _ in range(30000):
     if r[PC]==0x3FFF:break
     recent=(recent+[(hex(r[PC]),r[SP])])[-25:]
     if r[PC]<0x4000 or r[SP]>0x8000:raise AssertionError(("invalid_control_or_stack",last,previous,py,recent))
     sim.opcodes[memory[r[PC]]]()
    else:raise AssertionError(("instruction_limit",last,previous,py,hex(r[PC]),r[SP]))
    assert bytes(memory[0x4000:0x6000])==bytes(expected),(last,previous,py,update)
    assert memory[0x6F54]==(row if update else previous)
    assert memory.o7ffd==0x10 and memory[0x6306]==0x10
    assert bool(r[F]&0x40)==(not update) and r[SP]==0x8000 and r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
    if update:assert (r[A],r[F])==(row,0)
    cases+=1;changed+=update
 report=dict(passed=True,cases=cases,changed_cases=changed,
  method='original_mission_hover_wrapper_two_row_limit_real_xor_pointer_and_operand_store',
  all_pointer_y_values=True,last_handler_gate=True,bitmap_and_attributes_checked=True,
  calls_stubbed=False,irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/MissionHoverVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
