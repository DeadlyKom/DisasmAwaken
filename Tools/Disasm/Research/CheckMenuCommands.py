"""Сохранение геометрии, фильтр закрытия списка и пять HALT исходных команд меню."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put
from CheckStationExpandedDrawTail import draw_list, word
from ProbeShipPreviewCallbacks import Fixture
from ReferenceControlsPointRespawn import refresh


class MenuChainMemory(SliceableMemory):
    def __init__(self, **options):
        super().__init__(**options)
        self.read_addresses = set()
        self.write_addresses = set()

    def __getitem__(self, address):
        if isinstance(address, int) and address >= 0xF3DE and self.o7ffd & 7 == 0:
            self.read_addresses.add(address)
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if getattr(self,'recording',False):self.events.append((address,value))
        if address >= 0xF3DE and self.o7ffd & 7 == 0:
            self.write_addresses.add(address)
        super().__setitem__(address, value)


def check_close_menu_chain(base):
    menu, removable = 40, 28
    panel = 0xF0FD + 16 * menu
    menu_action = 0x753C
    result = []
    for active in (False, True):
        fixture = Fixture(base, memory_type=MenuChainMemory)
        memory, cpu = fixture.memory, fixture.sim
        registers = cpu.registers
        handlers = {index: word(memory, 0xF0FD + 16 * index + 12) for index in (0, removable, menu)}
        for index, handler in handlers.items():
            put(memory, handler + 1, index.to_bytes(2, 'little'))
        assert memory[0xF101 + 16 * removable] == 0x70 and memory[panel + 4] == 0x26
        put(memory, 0xF3DE, b''.join(address.to_bytes(2, 'little') for address in (*handlers.values(), 0x0101)))
        put(memory, panel, (2, 2, 9, 9))
        memory[0x9E78] = 0xFF if active else 0
        put(memory, 0x9E7E, removable.to_bytes(2, 'little'))
        put(memory, 0x9A89, b'\xEA\x68')
        assert word(memory, 0x9E8B) == 0x9A58

        def invoke(entry, *, event=False):
            registers[:] = fixture.initial
            put(memory, 0x7FFE, b'\xFF\x3F')
            registers[8:10] = divmod(panel, 256)
            if event:
                registers[A], registers[D], registers[E] = 1, 0, menu
                registers[H], registers[L] = divmod(menu_action, 256)
            visited = set()
            fixture.run(entry, lambda _, pc: visited.add(pc))
            return visited

        def keys():
            return [index for _, _, index in draw_list(memory)]

        def hover_close():
            put(memory, 0x6307, (32, 27))
            invoke(0x7539)
            assert memory[0x757A] == 1, (active, memory[0x6307:0x6309], memory[panel:panel + 4], keys())

        memory.read_addresses.clear()
        memory.write_addresses.clear()
        invoke(handlers[menu])
        hover_close()
        first = invoke(menu_action, event=True)
        assert memory[0x9E78] == 0
        assert 0x9E77 in first
        assert (0xA781 in first) == (not active)
        if active:
            assert keys() == [0, removable, menu] and memory[0x757A] == 0xFF
            hover_close()
            second = invoke(menu_action, event=True)
            assert 0xA781 in second
        assert keys() == [0] and word(memory, 0x9A89) == 0x9A58 and memory[0x9A82] == 0
        assert max(memory.read_addresses) == 0xF463 and max(memory.write_addresses) == 0xF461
        assert bytes(memory.banks[0][0x34DE:]) == bytes(base[0][0x34DE:])
        result.append(dict(prepared_active_item=removable if active else None,
                           close_executed_on_click=2 if active else 1,
                           final_draw_indices=keys(), real_im2_wakeups=fixture.wakes,
                           last_draw_list_read=0xF463, last_draw_list_write=0xF461))
    return result


def main():
    _,_,base=make_context()
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    saves=closes=hides=0;close_m1=set()
    def fixture():
        memory=MenuChainMemory(banks=[bank.copy() for bank in base],out7ffd=0x10)
        simulator=Simulator(memory);simulator.registers[:]=initial
        put(memory,0x7FFE,[255,63]);return memory,simulator,simulator.registers
    # Проверка всех физических точек окончания таблицы и байтов текущей геометрии, SavedX допускает #80.
    for length,seed in product(range(47),range(16)):
        memory,simulator,r=fixture();data=[]
        for index in range(length):
            record=[(index*71+seed*19+j*37)&255 for j in range(16)]
            if record[0]==128:record[0]=129
            data.extend(record)
        data.extend([128]+[0xCC]*15);put(memory,0xF0FD,data)
        expected=data.copy()
        for index in range(length):expected[index*16+8:index*16+12]=data[index*16:index*16+4]
        simulator.run(start=0xA7B7,stop=0x3FFF)
        assert memory[0xF0FD:0xF0FD+len(data)]==expected
        assert (r[A],r[F],r[D],r[E],r[SP])==(128,0x42,0,16,0x8000)
        assert r[8]*256+r[9]==0xF0FD+16*length
        for reg in (*range(2,4),*range(6,8),*range(10,12),*range(16,24)):assert r[reg]==initial[reg]
        saves+=1
    # Проверка каждого флагового байта и смешанных списков, удаление исполняет реальный фиксированный LDIR.
    patterns=[(flag,) for flag in range(256)]
    patterns += [tuple(((i*step+seed)&255) for i in range(n))
                 for n,step,seed in product((0,2,7,46),(1,13,71),(0,0x20,0x60,0xC0))]
    for case,flags in enumerate(patterns):
        memory,simulator,r=fixture();pointers=[0x7000+8*i for i in range(len(flags))]
        for i,(pointer,flag) in enumerate(zip(pointers,flags)):
            put(memory,pointer,[0x21,i,0]);memory[0xF0FD+16*i+4]=flag
        raw=[b for p in pointers for b in (p&255,p>>8)]+[1,1]+[0xA5]*256
        put(memory,0xF3DE,raw);put(memory,0x9CA6,[0xDE,0xF3]);memory[0x9A82]=0x5A
        expected=[p for p,flag in zip(pointers,flags) if flag&0xC0 and flag&0x60!=0x60]
        r[A]=case&255;r[F]=(case*73)&255;r[14]=case&255;r[15]=(case^0xA5)&255;r[27]=case%3
        before=r.copy();memory.events=[];memory.recording=True;r[PC]=0xA781;m1=0
        # Проверка полного исходного фильтра, включая поиск и все 128 итераций LDIR каждого удаления.
        for _ in range(60000):
            if r[PC]==0x3FFF:break
            old_r=r[15];simulator.run();delta=(r[15]-old_r)&127
            assert delta in (1,2);m1+=delta
        else:raise AssertionError('Фильтр закрытия не завершился')
        memory.recording=False
        # Расчёт независимой последовательности сдвигов физического хвоста для уникальных индексов стенда.
        buffer=raw.copy();list_writes=[];kept=removed=0;expected_m1=8
        for flag in flags:
            if flag&0xC0 and flag&0x60!=0x60:
                kept+=1;expected_m1+=42
            else:
                expected_m1+=(349 if flag&0xC0==0 else 353)+21*kept
                offset=2*kept;copied=buffer[offset+2:offset+130]
                list_writes.extend((0xF3DE+offset+j,value) for j,value in enumerate(copied))
                buffer[offset:offset+128]=copied;removed+=1
        assert m1==expected_m1,(flags,m1,expected_m1)
        assert r[15]==refresh(before[15],m1) and all(r[i]==before[i] for i in (14,26,27))
        assert memory[0xF3DE:0xF3DE+len(raw)]==buffer
        assert [(a,v) for a,v in memory.events if a>=0xF3DE]==list_writes
        assert [(a,v) for a,v in memory.events if a in (0x9A89,0x9A8A)]==[(0x9A89,0x58),(0x9A8A,0x9A)]
        assert [(a,v) for a,v in memory.events if a==0x9A82]==[(0x9A82,0)]*removed
        assert all(a in (0x9A89,0x9A8A,0x9A82) or a>=0xF3DE or 0x7FEE<=a<0x7FFE for a,v in memory.events)
        if flags:
            expected_a=(~flags[-1])&0x60 if flags[-1]&0xC0 and flags[-1]&0x60!=0x60 else 0
            assert (r[H],r[L],r[D]*256+r[E],r[A],r[F])==(0,(0xF101+16*(len(flags)-1))&255,len(flags)-1,expected_a,0x42)
        else:
            assert (r[H],r[L],r[D]*256+r[E],r[A],r[F])==(0,0x58,0x247A,before[A],0x42|(before[F]&1))
        close_m1.add(m1)
        actual=[];pos=0xF3DE
        while memory[pos+1]!=1:
            actual.append(memory[pos]+256*memory[pos+1]);pos+=2;assert len(actual)<=len(flags)
        assert actual==expected
        assert memory[0x9A89:0x9A8B]==[0x58,0x9A]
        assert memory[0x9A82]==(0 if len(expected)!=len(flags) else 0x5A)
        assert r[SP]==0x8000 and r[8]*256+r[9]==0xF3DE+2*len(expected)
        for reg in (*range(2,4),*range(10,12),*range(16,24)):assert r[reg]==initial[reg]
        closes+=1
    # Проверка пяти исходных HALT с явным пробуждением, без подмены команды RET.
    for flags in range(256):
        memory,simulator,r=fixture();r[F]=flags;r[PC]=0xA770;wakes=0
        while r[PC]!=0x3FFF:
            if 0xA77B<=r[PC]<=0xA77F:
                assert memory[r[PC]]==0x76;r[PC]+=1;wakes+=1
            else:simulator.run()
        assert wakes==5 and memory[0x9A89:0x9A8B]==[0x58,0x9A] and memory[0x9CAA]==1
        assert (r[A],r[F],r[H],r[L],r[SP])==(1,flags,0x9A,0x58,0x8000)
        for reg in (*range(2,6),*range(8,12),*range(16,24)):assert r[reg]==initial[reg]
        hides+=1
    report=dict(passed=True,method='original_menu_commands_geometry_copy_close_filter_and_explicit_halt_wakeups',
                save_geometry_cases=saves,close_filter_cases=closes,hide_cases=hides,
                close_menu_chain=check_close_menu_chain(base),
                close_full_m1_values=sorted(close_m1),close_exact_hl_de_af_refresh=True,
                close_all_128_shift_writes_and_tail_checked=True,close_only_declared_memory_writes=True,
                close_i_im_iff_preserved=True,close_iff_fixture=0,
                all_flag_bytes=True,actual_remove_code_executed=True,halt_wakeup_is_fixture=True,
                irq_executed=True,irq_executed_in_isolated_cases=False,
                native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MenuCommandsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
