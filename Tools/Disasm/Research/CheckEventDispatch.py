"""Диспетчер события с исходными поиском владельца, очисткой всплывающих элементов и подготовкой меню."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import put


def dec_flags(value,carry):
    result=(value-1)&255
    return (carry&1)|2|(result&0xA8)|(0x40 if result==0 else 0)|(0x10 if value&15==0 else 0)|(4 if value==128 else 0)


def main():
    _,_,base=make_context();base=[bytearray(bank) for bank in base]
    memory=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=0x10);simulator=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=transfers=suppressed=opened=background=cleanup=0
    scenarios=list(product(range(256),(False,True),('none','invalid','valid'),(0,1),(0,1),(False,)))
    scenarios += list(product((1,2,3,129),(False,True),('none','invalid','valid'),(0,1),(0,1),(True,)))
    for code,held,owner_kind,enabled,hidden,popups in scenarios:
        memory.banks=[bank.copy() for bank in base];memory.memory=[None,memory.banks[5],memory.banks[2],None]
        memory.out7ffd(0x10);simulator.registers[:]=initial;r=simulator.registers
        keys=[5,10,40,43] if popups else [5,6]
        wrappers={key:0x7000+8*key for key in keys}
        flags={key:(0x20 if key in (10,40,43) else 0x40) for key in keys}
        for key in keys:
            put(memory,wrappers[key],[0x21,key,0,0xC9]);memory[0xF0FD+16*key+4]=flags[key]
        handler=0x7400;event_target=handler+3
        put(memory,0xF0FD+16*5+6,[handler&255,handler>>8])
        memory[0xF0FD+16*5+4]=0x43;flags[5]=0x43
        # Создание фактического загрузочного операнда меню и его сохранённого размера.
        memory[0x7584]=40;put(memory,0xF37D+8,[0,0,9,9])
        raw=[b for key in keys for b in (wrappers[key]&255,wrappers[key]>>8)]+[1,1]+[0xA5]*256
        put(memory,0xE000,raw);put(memory,0x9CA6,[0,0xE0]);put(memory,0x7FFE,[255,63])
        put(memory,0x6307,[231,183]);put(memory,0x8600,[0]*768)
        memory[0x8600+32*(183//8)+231//8]=0 if owner_kind=='none' else 1
        put(memory,0x8500,[5,255 if owner_kind=='invalid' else 0])
        memory[0x9A82]=enabled;memory[0x9CAA]=hidden;memory[0x9839]=0xA5;memory[0xCA20]=0x5A
        entry_flags=((code*73+0x81)&0xBF)|(0x40 if held else 0)
        encoded_code=code|0x80 if held else code
        saved_flags=((encoded_code&0xA8)|(4 if not encoded_code.bit_count()%2 else 0)) if held else entry_flags
        r[A],r[F],r[PC]=code,entry_flags,0x9DBA
        for _ in range(10000):
            if r[PC] in (0x3FFF,event_target):break
            if r[PC]==0x9E1F and owner_kind=='valid':
                sp=r[SP]
                assert memory[sp:sp+10]==[0xE4,0x9D,5,0,5,0,saved_flags,encoded_code,255,63]
            simulator.run()
        else:raise AssertionError('Диспетчер не завершился')
        selected=5 if owner_kind=='valid' else None
        expected_keys=keys.copy()
        can_dispatch=owner_kind=='valid' and enabled and not popups
        if owner_kind=='valid':
            expected_keys=[key for key in keys if key==selected or flags[key]&0xE0!=0x20]
            assert memory[0x9E31:0x9E33]==[5,0]
            assert memory[0x9CAA]==hidden
            if can_dispatch:
                assert r[PC]==event_target and r[H]*256+r[L]==event_target
                assert r[D]*256+r[E]==5 and r[8]*256+r[9]==0xF0FD+16*5
                assert (r[A],r[F],memory[0x9839],memory[0xCA20])==(
                    (encoded_code-1)&255,dec_flags(encoded_code,saved_flags), (encoded_code-1)&255,0x43)
                transfers+=1
            else:
                assert r[PC]==0x3FFF and (r[A],r[F])==(encoded_code,saved_flags)
                assert memory[0x9839]==0xA5 and memory[0xCA20]==0x5A
                assert r[8:12]==initial[8:12];suppressed+=1
        else:
            assert memory[0x9E31:0x9E33]==[0xF0,255] and memory[0x9CAA]==0
            if encoded_code==1:
                expected_keys=[key for key in keys if key!=40]+[40]
                assert memory[0xF37D:0xF37D+4]==[23,15,9,9]
                assert (r[A],r[F],memory[0x9839],memory[0x9A82])==(9,0xA4,0,0);opened+=1
            elif encoded_code==2:
                expected_keys=[key for key in keys if flags[key]&0xE0!=0x20];cleanup+=1
            else:
                assert (r[A],r[F])==((encoded_code-2)&255,dec_flags((encoded_code-1)&255,saved_flags))
                assert memory[0x9839]==0xA5;background+=1
        actual=[];pos=0xE000
        while memory[pos+1]!=1:
            pointer=memory[pos]+256*memory[pos+1];actual.append(memory[pointer+1]+256*memory[pointer+2]);pos+=2
            assert len(actual)<20
        assert actual==expected_keys
        assert r[SP]==(0x7FFE if can_dispatch else 0x8000)
        assert r[10:12]==initial[10:12] and r[16:24]==initial[16:24]
        cases+=1
    report=dict(passed=True,method='original_event_dispatch_owner_popup_cleanup_and_menu_preparation',
                cases=cases,event_transfers=transfers,suppressed_valid_owner=suppressed,
                menu_openings=opened,background_returns=background,popup_cleanups=cleanup,
                all_input_codes=True,equal_input_high_bit_checked=True,
                handler_plus_three_verified=True,event_handler_body_executed=False,
                selected_cleanup_frame_verified=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/EventDispatchVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
