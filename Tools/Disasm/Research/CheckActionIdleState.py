"""State00 и нулевой хвост, реальные F0F8, 6D06 и три умножителя до полного RET."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from CheckActionObjectOffsetTransfer import reference
from ReferenceActionObjectOffsetVector import evaluate as offset_vector
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();assert flat[0xF691:0xF694]==[0x21,0,0]
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter()
    def check(entry,current,limit,marker,af):
        nonlocal cases
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        ix=0xA100+64*(cases%26);stack=0xBFFE
        record={1:128 if marker else cases%128,7:cases&255,8:cases*73&255,9:cases*109&255,
            10:(0,19,20)[cases%3],15:limit,16:current,18:(0,15,16,255)[cases%4],36:cases*137&255}
        for offset,value in record.items():memory[ix+offset]=value
        for address,value in zip((0xE5B0,0xE5CF,0xE5EA),(af,af^65535,af*73&65535)):
            memory[address],memory[address+1]=value&255,value>>8
        memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':entry,'SP':stack,'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        wanted=list(initial);operations=[]
        if entry==0xF691 or current==0:
            wanted[6:8]=[0,0];m1=5 if entry==0xF691 else 9
            if entry!=0xF691:wanted[0:2]=[0,0x54]
            for address in (0xE5B0,0xE5CF,0xE5EA):operations.extend(((address,0),(address+1,0)))
            wanted[24],wanted[12],wanted[15]=0x3FFF,stack+2,refresh(initial[15],m1);path='reset_bases'
        else:
            # Расчёт исходного двойного DEC и настоящего CALL подготовителя, 1 оборачивается в FF.
            record[16]=(current-2)&255;operations.append((ix+16,record[16]));operations.extend(((stack-2,0x8D),(stack-1,0xF6)))
            child=list(initial);child[12]=stack-2;child[15]=refresh(initial[15],9)
            wanted,writes,path=reference(child,ix,record);operations.extend(writes)
            if marker:
                wanted[24],wanted[12]=0x3FFF,stack+2;wanted[15]=refresh(wanted[15],1);path='marker_return'
            else:
                # Расчёт настоящего вычислителя по прежнему DE и фазовым таблицам, затем оба внешних RET.
                offsets=(record[7],(record[8]+128)&255,record[9])
                calculated=offset_vector(memory,wanted,offsets,0xF68D)
                wanted=calculated['registers'];operations.extend(calculated['writes'])
                wanted[15]=refresh(wanted[15],1)
                wanted[12],wanted[24]=stack+2,0x3FFF;path='complete_offset_vector_return'
        expected=[bytearray(bank) for bank in memory.banks];writes=[]
        for address,value in operations:
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(1000):
            if simulator.registers[24]==wanted[24]:break
            simulator.run()
        else:raise AssertionError(('нет границы',entry,current,limit,marker))
        memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,entry,path,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert memory.banks==expected and Counter(memory.writes)==Counter(writes),(cases,'RAM',path)
        assert memory[stack]==255 and memory[stack+1]==63
        if wanted[24]==0x6D06:assert memory[stack-2]==0x8D and memory[stack-1]==0xF6
        paths[path]+=1;counts[hex(entry)]+=1;cases+=1
    # Проверка всех входных AF и всего домена каждого прежнего базового слова на отдельном нулевом хвосте.
    for af in range(65536):check(0xF691,0,0,False,af)
    # Проверка всех пар исходного байта 10 и ограничителя 0F при обоих путях доступности записи.
    for current in range(256):
        for limit in range(256):
            for marker in (False,True):check(0xF67F,current,limit,marker,(current<<8)|limit)
    assert cases==196608
    result=dict(passed=True,total_cases=cases,cases_by_entry=dict(counts),paths=dict(paths),
        all_input_AF_for_reset=True,all_counter_limit_and_marker_products=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        actual_offset_prepare_child_executed=True,offset_calculator_and_multiply_children_executed=True,
        preserved_child_return_word=0xF68D,maximum_additional_stack_bytes=8,
        original_zero_immediate_required=True,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionIdleStateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
