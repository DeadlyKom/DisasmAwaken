"""Постоянное состояние одной физической клавиши, настоящий первый обработчик и перекрытое 27-е слово."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC
from CheckScreenUpdate import put
from ActionControlKeyLayout import ENTRIES
from ReferenceActionControlKeys import evaluate
from CheckControlsEvenSpan import and_flags


class StationaryKey:
    def __init__(self):self.reads=[];self.outs=[]
    def read_port(self,registers,port,offset=0):
        # Одна замкнутая клавиша в строке FD, бит 1, все прочие переключатели отпущены.
        value=253 if not ((port>>8)&2) else 255
        self.reads.append((port,value));return value
    def write_port(self,registers,port,value,offset):self.outs.append((port,value))


def main():
    flat=flat_action();baseline=[bytearray([160+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000]);baseline[0]=bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[b.copy() for b in baseline],out7ffd=16);simulator=Simulator(memory);ports=StationaryKey();simulator.set_tracer(ports)
    layout=next(r for r in ENTRIES if r[0]==0x7753);own,opposite,latch,value_address=layout[7:11]
    rows=[tuple(flat[0x9D4C+2*i:0x9D4E+2*i]) for i in range(27)]
    assert rows[0]==rows[-1]==(253,2)
    assert [i for i,(row,mask) in enumerate(rows) if not ((253 if not row&2 else 255)&mask)]==[0,26]
    assert flat[0x704B:0x704D]==[201,192] and bytes(flat[0xC0C9:0xC0CC])==bytes.fromhex('cd77c4')
    counts=Counter()
    # Проверка полного домена накопителя и Y при неизменном состоянии матрицы, без подмены первого обработчика.
    for counter in range(256):
        for value in range(256):
            memory.recording=False
            for bank,raw in zip(memory.banks,baseline):bank[:]=raw
            serial=counter*256+value;mode=(serial*73)&255
            for address,byte in ((own,counter),(opposite,17),(latch,0),(value_address,value),(0xA85F,mode)):memory[address]=byte
            put(memory,0xBFFE,[255,63]);expected=[bytearray(b) for b in memory.banks];writes=[]
            initial=get_registers({'PC':0x6F1D,'SP':0xBFFE,'AF':serial,'HL':((serial&255)<<8)|0x57,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
            initial[14]=serial&255;initial[15]=serial&255;initial[26]=serial&1;initial[27]=serial%3
            child=evaluate(initial,layout,counter,value)
            for address,byte in child['writes']:
                page=5 if address<0x8000 else 2;expected[page][address&0x3FFF]=byte;writes.append((page,address&0x3FFF,byte))
            h=initial[6]
            for words in (((h<<8)|27,0x7017,0xFDFE,0x9D4E,0x6F4E),((h<<8)|1,0x704B,0xFDFE,0x9D82,0x6F4E)):
                for index,word in enumerate(words):
                    for address,byte in ((0xBFFD-2*index,word>>8),(0xBFFC-2*index,word&255)):
                        expected[2][address&0x3FFF]=byte;writes.append((2,address&0x3FFF,byte))
            wanted=list(initial);wanted[:8]=[mode,and_flags(mode),253,254,0x6F,0x4E,0xC0,0xC9]
            wanted[8:10]=[0x9D,0x82];wanted[12]=0xBFF4;wanted[PC]=0xC0C9
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True;ports.reads=[];ports.outs=[];first_calls=0
            for _ in range(1000):
                if simulator.registers[PC]==0xC0C9:break
                first_calls+=simulator.registers[PC]==0x7753;simulator.run()
            else:raise AssertionError(('перекрытая цель не достигнута',counter,value))
            memory.recording=False;compared=(*range(13),14,*range(16,25),26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(counter,value,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert memory.banks==expected and Counter(memory.writes)==Counter(writes),(counter,value,'RAM')
            assert first_calls==1 and len(ports.reads)==27 and not ports.outs and memory.o7ffd==16
            assert ports.reads==[((row<<8)|254,253 if not row&2 else 255) for row,mask in rows]
            counts['original_bank0_dispatch_to_clip_entry']+=1
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),stationary_row_select=253,stationary_mask=2,
        all_Y_accumulator_value_pairs=True,real_first_handler_and_restore_frame_executed=True,all_256_mode_bytes_distributed=True,
        original_27th_word=0xC0C9,actual_bank=0,actual_target='Action.ClipInsideToTopLeft.Entry',
        physical_pointer_word_overlaps_code=True,separate_pointer_record_added=False,
        all_registers_except_R_T_and_all_eight_banks_write_multiplicity_checked=True,
        stopped_before_clip_handler=True,clip_calling_frame_preconditions_not_proved=True,
        author_intent_not_proved=True,all_keyboard_state_products_exhausted=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionOverlappingKeyDispatchVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
