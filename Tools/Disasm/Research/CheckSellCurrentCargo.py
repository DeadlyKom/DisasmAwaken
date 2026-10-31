"""Callback продажи всего текущего груза с исходным сценарием и полной перерисовкой."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put,PortTrace
from CheckOriginalTradeScript import reference


def main():
    _,_,banks=make_context();manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));entry=next(e for e in manifest['entries'] if e['slot']==5);lang=(ROOT/(entry['path']+'.sectors.bin')).read_bytes();banks[6][:len(lang)]=list(lang)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    active=0;paths={};inputs=((1,0,7,1000),(1,3,7,1000),(129,3,7,500),(1,127,255,65000),(127,1,1,65535),(1,128,7,1000),(1,255,255,65000))
    for page in (0x10,0x18):
        for index in (0,29):
            for stock,cargo,price,credits in inputs:
                m=SliceableMemory(banks=[b.copy() for b in banks],out7ffd=page);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace);s.registers[:]=initial;r=s.registers;r[PC]=0x7D63
                m[0x6306]=page;put(m,0x6307,[50,83]);m[0x6548]=1;m[0x9B16]=0;put(m,0x8500,bytes([0x80,255])*128);put(m,0x8600,bytes(768))
                put(m,0xF0FD,[0,0,31,8,0,0]);put(m,0x7F36,[0,0]);put(m,0x7072,[34,0]);put(m,0xF31D,[4,9,24,12,1,5]);put(m,0x6E8B,[10,0]);put(m,0x9CA6,[0xDE,0xF3]);put(m,0xF3DE,[0x8A,0x6E,1,1]);m[0x6E91]=0xA7
                put(m,0x7026,[0,0]);m[0x7068]=index;m[0x984A]=255;m[0x984B]=0;put(m,0x984C,[0,0]);put(m,0x984E,credits.to_bytes(2,'little'));m[0x9851]=255
                put(m,0x9852,bytes(60));put(m,0x988E,bytes(52));put(m,0x98F6,bytes(14))
                for row in range(30):put(m,0x9555+2*row,[1,3])
                m[0x9555+60]=255;m[0x9555+2*index]=stock;m[0x9556+2*index]=price;m[0x9852+2*index]=cargo;put(m,0x7FFE,[255,63]);wakes=0;events=0;render_flags=None
                for _ in range(350000):
                    pc=r[PC]
                    if pc==0x3FFF:break
                    if pc==0x7044:assert r[A]==11;events+=1
                    if pc==0x705D:render_flags=r[F]
                    if pc==0xC089:assert m[pc]==0x76;r[PC]+=1;wakes+=1
                    else:s.run()
                else:raise AssertionError(('instruction_limit',page,index,stock,cargo,price,credits,hex(r[PC])))
                es,eg,ec,messages,_=reference(11,stock,cargo,price,credits,0,255)
                assert (m[0x9555+2*index],m[0x9852+2*index],m[0x984E]+256*m[0x984F])==(es,eg,ec)
                assert m[0x7068]==0 and m[0x983A]==11 and (r[A],r[F])==(0,render_flags)
                assert m[0x6E91]==(messages[-1] if messages else 0xA7) and events==1 and wakes==1 and r[SP]==0x8000
                assert m[0x6306]==0x10 and m.o7ffd==0x10 and m[0x9B16]==0 and bytes(m.banks[6][0xA8F:len(lang)])==lang[0xA8F:]
                key='message_'+str(messages[-1]) if messages else 'success';paths[key]=paths.get(key,0)+1;active+=1
    # Проверка отсутствующей строки, включая сохранённые F и чтение соседнего байта CALL как старшего H.
    m=bytearray(65536);m[0x4000:0x8000]=bytes(banks[5]);m[0x8000:0xC000]=bytes(banks[2]);m[0xC000:]=bytes(banks[0]);s=Simulator(m)
    for flags in range(256):
        m[0x7068]=255;put(m,0x7FFE,[255,63]);before=bytes(m);s.registers[:]=initial;r=s.registers;r[F]=flags;s.run(start=0x7D63,stop=0x3FFF)
        assert bytes(m)==before and (r[H]*256+r[L],r[A],r[F],r[SP])==(0xCDFF,255,0x6A,0x8000)
        assert r[2:6]==initial[2:6] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
    report=dict(passed=True,active_cases=active,no_selection_cases=256,paths=paths,forced_row_zero_after_repaint=True,
                original_trade_event_11_script_executed=True,real_status_and_trade_drawers=True,real_banking_and_pointer=True,
                adjacent_call_opcode_high_byte_checked=True,independent_money_quantity_and_message_oracle=True,
                independent_full_bitmap_oracle_in_this_model=False,explicit_halt_wakeups=active,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/SellCurrentCargoVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
