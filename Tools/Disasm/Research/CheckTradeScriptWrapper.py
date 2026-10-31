"""Банковая обёртка торгового события, настоящий интерпретатор с явно пустым входным сценарием и реальные рисователи."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put


def main():
    _,_,banks=make_context();manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==5);lang=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=list(lang)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=active_status=0
    for page in (0x10,0x18):
        for event in (0,9,10,255):
            for height in (6,12):
                for status_enabled in (False,True):
                    m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[A]=event;r[PC]=0x7044
                    # Меняется только сценарий входных данных, инструкции интерпретатора и обёртки оригинальные.
                    m.banks[6][0xA8F]=0;m[0x6306]=page;put(m,0x6307,[50,83]);m[0x6548]=1;m[0x9B16]=0
                    put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768));put(m,0x7F36,[0,0]);put(m,0xF0FD,[0,0,31,8,0,0]);m[0x7F35]=0x21 if status_enabled else 0xC9
                    put(m,0x7072,[34,0]);put(m,0xF31D,[4,9,24,height,1,5]);put(m,0x7026,[0,0]);m[0x984B]=0;put(m,0x984C,[0,0,0xD2,4,16,32])
                    for row in range(30):put(m,0x9555+2*row,[1,3]);put(m,0x9852+2*row,[2,4])
                    m[0x9555+60]=255;put(m,0x7FFE,[255,63]);calls=[];wakes=0;script_ix=None;draw_flags=None
                    for _ in range(300000):
                        pc=r[PC]
                        if pc==0x3FFF:break
                        if pc==0xC000 and m.o7ffd&7==6:calls.append('script');assert m[0x983A]==event
                        if pc==0x7054:script_ix=list(r[8:10])
                        if pc==0x7F35:calls.append('status')
                        if pc==0x7071:calls.append('trade')
                        if pc==0x705D:draw_flags=r[F]
                        if pc==0xC089:assert m[pc]==0x76;r[PC]+=1;wakes+=1
                        else:s.run()
                    else:raise AssertionError(('instruction_limit',page,event,height,status_enabled,hex(r[PC])))
                    assert calls==['script','status','trade'] and wakes==1 and r[SP]==0x8000
                    assert m[0x983A]==event and m[0x7068]==255 and m[0x7063]>0 and (r[A],r[F])==(0x10,draw_flags)
                    assert r[8:10]==script_ix and r[10:12]==initial[10:12] and m[0x6306]==0x10 and m.o7ffd==0x10 and m[0x9B16]==0
                    expected=[(0x7FFD,(page&0xF8)|0x16),(0x7FFD,(page&0xF8)|0x10),(0x7FFD,0x17),(0x7FFD,0x18),(0x7FFD,0x10)]
                    assert trace.writes==expected
                    cases+=1;active_status+=status_enabled
    report=dict(passed=True,cases=cases,active_status_draw_cases=active_status,event_codes=[0,9,10,255],real_banked_interpreter_entry_and_return=True,
                script_input_fixture='NUL at CA8F in modeled LANG bank only',original_trade_script_commands_executed=False,
                real_status_and_trade_drawers=True,actual_call_order_and_ports_checked=True,explicit_halt_wakeups=cases,
                independent_whole_screen_oracle_in_this_model=False,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/TradeScriptWrapperVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
