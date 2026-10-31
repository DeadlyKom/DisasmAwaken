"""Три группы восстанавливаемых панелей, порядок списка и отсутствие немедленного рисования."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,H,L,D,E,SP
from CheckRowHighlight import make_context

GROUPS=((0x7D87,((0x6FC5,31),(0xAA4F,33),(0xAA85,32))),
        (0x7DA9,((0x7D77,35),(0x7071,34))),
        (0x7DC5,((0x6AB6,39),(0x7B40,36),(0x7B25,37),(0x7227,38))))


def main():
    _,_,banks=make_context();base=bytearray(65536);base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0]);initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    cases=0
    for entry,group in GROUPS:
        for kind in range(4):
            for disabled in (False,True):
                for height in range(256):
                    m=bytearray(base);s=Simulator(m);s.registers[:]=initial
                    m[0x5F00:0x5F04]=bytes([0x21,group[-1][1],0,0xC9]);m[0x5F08:0x5F0C]=bytes([0x21,63,0,0xC9]);m[0x9CA6:0x9CA8]=bytes([0,0xB4]);m[0x9A82]=0xA7;m[0x6ACC]=0xA7;m[0xB3FF]=0xA5;m[0xB501]=0x5A
                    original_records={};saved={};keys={0x5F00:group[-1][1],0x5F08:63}
                    for j,(pointer,index) in enumerate(group):
                        m[pointer]=0xC9 if disabled else 0x21;m[pointer+1:pointer+3]=index.to_bytes(2,'little');keys[pointer]=index
                        record=bytes([0xA0,0xB0,1,1,0x26,0,0,0,(height+index)&255,(height*3+index)&255,(height*5+index)&255,height if j==len(group)-1 else (height+j+1)&255,0,0,0,0]);address=0xF0FD+16*index;m[address:address+16]=record;original_records[index]=record;saved[index]=record[8:12]
                    entries=[] if kind==0 else ([p for p,_ in reversed(group)]+[0x5F08] if kind==1 else ([0x5F00,0x5F08] if kind==2 else [group[0][0],group[0][0],0x5F08]))
                    raw=b''.join(p.to_bytes(2,'little') for p in entries)+bytes([1,1]);m[0xB400:0xB500]=raw+bytes(256-len(raw));expected=list(entries)
                    # Независимый список удаляет первое совпадение индекса и добавляет выбранный адрес в конец.
                    for pointer,index in group:
                        found=next((i for i,p in enumerate(expected) if keys[p]==index),None)
                        selected=expected.pop(found) if found is not None else pointer;expected.append(selected)
                    m[0x7FFE:0x8000]=bytes([255,63]);screen=bytes(m[0x4000:0x6000]);s.run(start=entry,stop=0x3FFF);r=s.registers
                    expected_raw=b''.join(p.to_bytes(2,'little') for p in expected)+bytes([1,1]);assert m[0xB400:0xB400+len(expected_raw)]==expected_raw
                    for pointer,index in group:
                        address=0xF0FD+16*index;record=bytearray(original_records[index]);record[:4]=saved[index];assert m[address:address+16]==record and m[pointer]==(0xC9 if disabled else 0x21)
                    assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F])==(expected[-1],group[-1][1],height,0xA4)
                    assert bytes(m[0x4000:0x6000])==screen and m[0x9A82]==0 and m[0xB3FF]==0xA5 and m[0xB501]==0x5A and r[SP]==0x8000
                    assert m[0x6ACC]==(0 if entry==0x7DC5 else 0xA7) and r[2:4]==initial[2:4] and r[8:12]==initial[8:12] and r[16:24]==initial[16:24];cases+=1
    report=dict(passed=True,cases=cases,all_saved_height_bytes=True,empty_reversed_aliased_and_duplicate_lists=True,
                existing_same_index_handler_retained=True,disabled_opcodes_not_enabled=True,all_physical_record_fields_compared=True,
                no_immediate_screen_drawing=True,equipment_info_text_index_reset_to_zero=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/PanelOpeningVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
