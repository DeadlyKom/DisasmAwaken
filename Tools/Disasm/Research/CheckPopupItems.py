"""Очистка группы #20 с исключением индекса и подготовка контекстного элемента 40, без рисования и IRQ."""
from pathlib import Path
from itertools import product
import hashlib
import json
import random
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==4)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=[0]*65536;memory[0x6000:]=source
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0xA5CF,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    simulator=Simulator(memory);rng=random.Random(0x9E1F);filter_cases=removed_total=0
    memory[0x9CA6:0x9CA8]=[0,0xE0]

    def key_of(pointer):return memory[pointer+1]+256*memory[pointer+2]

    def reference(data,flags,skip):
        data=data[:];removed=0;last=None;seen=set()
        while True:
            signature=bytes(data)
            if signature in seen:return data,removed,last,False
            seen.add(signature)
            position=0
            while data[position+1]!=1:
                pointer=data[position]+256*data[position+1];key=key_of(pointer)
                group=0 if key==skip else flags[key]&0xE0
                last=(pointer,key,group,group<0x20)
                if group==0x20:
                    # Расчёт фиксированного физического сдвига, ограничитель не определяет длину копирования.
                    data[position:position+128]=data[position+2:position+130]
                    removed+=1;last=(pointer,key,0,False)
                    break
                position+=2
            else:return data,removed,last,True

    def filter_case(keys,flags,skip,disabled=False):
        nonlocal filter_cases,removed_total
        for key in range(46):
            handler=0x7000+4*key
            memory[handler:handler+4]=[0xC9 if disabled else 0x21,key,0,0xC9]
            memory[0xF0FD+16*key+4]=flags[key]
        data=[(i*37+0x5A)&255 for i in range(2*len(keys)+132)]
        for i,key in enumerate(keys):data[2*i:2*i+2]=list((0x7000+4*key).to_bytes(2,'little'))
        data[2*len(keys):2*len(keys)+2]=[1,1]
        expected,removed,last,terminates=reference(data,flags,skip)
        memory[0xE000:0xE000+len(data)]=data
        memory[0x9E31:0x9E33]=list(skip.to_bytes(2,'little'));memory[0x9A82]=0x5A
        memory[0x7FFE:0x8000]=[255,63];simulator.registers[:]=initial;r=simulator.registers;r[PC]=0x9E1F
        seen=set();cycle=False
        for step in range(300000):
            if r[PC]==0x3FFF:break
            if r[PC]==0x9E1F:
                state=(bytes(memory[0xE000:0xE000+len(data)]),tuple(r[:12]),tuple(r[16:24]),r[SP],memory[0x9A82])
                if state in seen:cycle=True;break
                seen.add(state)
            simulator.run()
        else:raise AssertionError('Не обнаружен ожидаемый выход либо повтор полного состояния')
        assert cycle!=terminates
        if terminates:
            assert memory[0xE000:0xE000+len(data)]==expected
            end=next(i for i in range(0,len(expected),2) if expected[i+1]==1)
            assert r[H]*256+r[L]==0xE000+end+1 and r[B]==0
            assert r[A]==(last[2] if last else initial[A])
            assert r[C]==((last[0]+2)&255 if last else initial[C])
            assert r[D]*256+r[E]==(last[1] if last else initial[D]*256+initial[E])
            assert r[F]==0x42|int(last[3] if last else initial[F]&1)
            assert memory[0x9A82]==(0 if removed else 0x5A)
            assert r[SP]==0x8000
        assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
        for key in range(46):assert memory[0xF0FD+16*key+4]==flags[key]
        filter_cases+=1;removed_total+=removed
        return cycle

    # Проверка всех флаговых байтов при сохранении выбранного индекса и при его отсутствии.
    for value,skip,disabled in product(range(256),(0,45,0xFFF0),(False,True)):
        flags={k:0x40 for k in range(46)};flags[0]=value;flags[45]=value^1
        assert not filter_case([0,45,0,1,45],flags,skip,disabled)
    # Проверка всех длин до 64 указателей, дублей, пустого списка и разных расположений группы #20.
    for length,kind,skip in product(range(65),range(5),(0,45,0xFFF0)):
        keys=[rng.randrange(46) for i in range(length)]
        flags={k:(0x20 if kind==0 else 0x40 if kind==1 else 0x20 if kind==2 and k&1 else rng.randrange(256)) for k in range(46)}
        assert not filter_case(keys,flags,skip)
    saved_flags=initial[F];initial[F]&=~1
    assert not filter_case([],{k:0 for k in range(46)},0xFFF0)
    initial[F]=saved_flags
    # Проверка повторяющегося состояния на длинном списке, копирование 128 байтов не достигает ограничителя.
    nonterminating=int(filter_case([i%46 for i in range(65)],{k:0x20 for k in range(46)},0xFFF0))
    assert nonterminating==1
    # Проверка позиции контекстного меню на всех 65536 парах байтов координат.
    menu_cases=0
    memory[0x7584:0x7586]=[40,0]
    memory[0xF381]=source[0x9381]
    for x,y in product(range(256),repeat=2):
        mode=(x+y)%3;selected=0x7100 if mode==2 else 0x7583
        memory[0x7100:0x7104]=[0xC9,40,0,0xC9]
        memory[0x7000:0x7004]=[0x21,0,0,0xC9]
        data=[0x55]*136
        pointers=[0x7000] if mode==0 else [selected,0x7000]
        for i,pointer in enumerate(pointers):data[2*i:2*i+2]=list(pointer.to_bytes(2,'little'))
        data[2*len(pointers):2*len(pointers)+2]=[1,1]
        memory[0xE000:0xE088]=data
        record=0xF37D;memory[record:record+4]=[0xA5]*4
        memory[record+8:record+12]=[8,2,9,9]
        memory[0x6307:0x6309]=[x,y];memory[0x9A82]=0x5A
        memory[0x7FFE:0x8000]=[255,63];simulator.registers[:]=initial;r=simulator.registers
        r[A]=(x^y)&255
        simulator.run(start=0x9E4E,stop=0x3FFF)
        position=[min(23,x//8),min(15,y//8)]
        assert memory[record:record+4]==position+[9,9] and memory[record+8:record+12]==position+[9,9]
        assert memory[0x9839]==(x^y)&255 and memory[0x9A82]==0
        assert r[H]*256+r[L]==selected and r[D]*256+r[E]==40 and r[B]*256+r[C]==0x36C9
        assert r[A]==9 and r[F]==0xA4 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
        expected_pointers=[0x7000,selected,0x0101]
        assert memory[0xE000:0xE006]==[v for p in expected_pointers for v in p.to_bytes(2,'little')]
        menu_cases+=1
    report=dict(method='original_popup_group_filter_and_context_item_preparation',passed=True,
                source_sha256=hashlib.sha256(source).hexdigest(),filter_cases=filter_cases,removed_operations=removed_total,
                nonterminating_long_list_cases=nonterminating,menu_coordinate_cases=menu_cases,
                irq_executed=False,drawing_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/PopupItemsVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
