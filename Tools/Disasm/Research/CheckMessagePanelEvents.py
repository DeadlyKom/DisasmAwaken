"""Исходные действия двух панелей, реальные список, перерисовка и фильтр строки."""
from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'), str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put, PortTrace


def main():
    _, _, banks = make_context()
    initial = get_registers({'SP':0x7FFE, 'HL':0x1357, 'DE':0x247A, 'BC':0x36C9,
                             'AF':0x5A5D, 'IX':0x2468, 'IY':0x5C3A, '^HL':0x369C,
                             '^DE':0x47AD, '^BC':0x58BE, '^AF':0x69CF}, None, False)
    cases = removed = redrawn = early = wakes = hover = 0
    observed = set()
    for index, entry, draw, y, flags, caption in ((24,0x6DC5,0x6DD4,3,1,2), (10,0x6E82,0x6E8A,5,0x21,20)):
        for last in (True, False):
            for selector in (range(256) if last else (0,1,2,127,128,255)):
                for same_row in (False, True):
                    m = SliceableMemory(banks=[b.copy() for b in banks], out7ffd=0x10)
                    s = Simulator(m); trace = PortTrace(s); s.set_tracer(trace)
                    # Подготовка настоящих операндов обёрток и геометрии обеих панелей.
                    put(m, draw+1, index.to_bytes(2,'little'))
                    put(m, 0xF0FD+16*index, [8,y,16,16,flags,caption,0,0,8,y,16,16,0,0,0,0])
                    put(m, 0x5F00, [0x21,63,0,0xC9])
                    put(m, 0x9CA6, [0,0xB4])
                    entries = [0x5F00,draw] if last else [draw,0x5F00]
                    raw = b''.join(p.to_bytes(2,'little') for p in entries)+bytes([1,1])
                    put(m, 0xB400, raw+bytes(128)); m[0xB3FF]=0xA5; m[0xB486]=0x5A
                    put(m, 0x8500, bytes([0x80,255])*128); put(m, 0x8600, bytes(768))
                    m[0x9E78]=0; m[0xCA20]=6; m[0x9A82]=0xA7; m[0x6306]=0x10
                    m[0x6307]=0; m[0x6308]=y*8+3 if same_row else 80
                    m[0xAEC7]=y*8+3; m[0xAECB]=0; m[0x6548]=1
                    put(m, 0x9A90, [0x58,0x9A]); put(m, 0x9A8D, [255,255]); m[0x9B16]=0
                    put(m, 0x983F, bytes([0x38,0x4B,0,0])); m[0x98BF]=0; m[0x6E91]=0
                    put(m, 0x7FFE, [255,63]); s.registers[:]=initial; r=s.registers
                    r[H],r[L]=draw>>8,draw&255; r[D],r[E]=0,index; r[A]=selector; r[PC]=entry
                    call_wakes=0; saw_draw=False
                    for _ in range(180000):
                        pc=r[PC]
                        if pc==0x3FFF:break
                        if pc in (0x6DC5,0x6DC8,0x6DC9,0x6DCA,0x6DCD,0x6DD0,0x6DD1,0x6DD2,0x6E82,0x6E85,0x6E86):observed.add(pc)
                        if pc==draw:saw_draw=True
                        if pc==0xC089:
                            assert m[pc]==0x76; r[PC]+=1; call_wakes+=1
                        else:s.run()
                    else:raise AssertionError(('instruction_limit',index,last,selector,same_row,hex(r[PC])))
                    # Проверка закрытия по независимой формуле, а не по факту посещения DropItemDraw.
                    expected_remove = last and selector<128 and (index==10 or (selector!=1 and same_row))
                    expected_draw = not last and selector<128
                    expected_entries = ([0x5F00] if expected_remove else ([0x5F00,draw] if selector<128 else entries))
                    expected_raw=b''.join(p.to_bytes(2,'little') for p in expected_entries)+bytes([1,1])
                    assert m[0xB400:0xB400+len(expected_raw)]==list(expected_raw),(index,last,selector,same_row,'list')
                    assert m[0x9A82]==(0 if expected_remove else 0xA7),(index,last,selector,same_row,'event',m[0x9A82])
                    assert saw_draw==expected_draw and call_wakes==int(expected_draw)
                    assert r[SP]==0x8000 and r[D]*256+r[E]==index and r[8:10]==initial[8:10]
                    assert m[0xCC17]==0x37 and m[0xB3FF]==0xA5 and m[0xB486]==0x5A
                    assert m[0x6306]==0x10
                    if not expected_draw:assert not trace.writes
                    if selector&128:
                        assert (r[A],r[F])==(selector,(selector&0xA8)|1)
                        assert r[B:C+1]==initial[B:C+1] and r[8:12]==initial[8:12]; early+=1
                    if expected_remove:assert (r[A],r[F])==(0,0x44)
                    if last and selector==1 and index==24:assert (r[A],r[F])==(0,0x42)
                    cases+=1; removed+=expected_remove; redrawn+=expected_draw; wakes+=call_wakes
        # Проверка обоих прямых RET и входящих JP без подмены инструкций.
        for address in ((0x6DC2,0x6DD3) if index==24 else (0x6E7F,0x6E89)):
            for flags_byte in range(256):
                m=bytearray(65536); m[0x4000:0x8000]=bytes(banks[5]); m[0x8000:0xC000]=bytes(banks[2]); m[0xC000:]=bytes(banks[0])
                m[0x7FFE:0x8000]=bytes([255,63]); s=Simulator(m); s.registers[:]=initial; r=s.registers; r[F]=flags_byte
                expected=list(r[:24]); s.run(start=address,stop=0x3FFF)
                assert list(r[:12])==expected[:12] and list(r[16:24])==expected[16:24] and r[SP]==0x8000
                hover+=1
    report=dict(passed=True,event_cases=cases,removed_cases=removed,redrawn_cases=redrawn,bit7_early_cases=early,
                hover_cases=hover,explicit_halt_wakeups=wakes,visited_event_instructions=sorted(observed),
                all_selector_bytes_without_redraw=True,real_repaint_and_list_helpers=True,
                geometry_action_disabled_in_fixture=True,active_callback_disabled_in_fixture=True,
                independent_full_bitmap_oracle=False,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MessagePanelEventsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
