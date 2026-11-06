"""62CF, насыщенный счётчик двух совпадений, полные домены классов/кодов, ссылок и заголовков."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh,cp_flags


def profiles():
    for code in range(256):
        for state in range(256):
            target=(code*73+state)&255
            yield ((0,1,code,state,target),(1,1,3,2,target)),target,0x9C,'all_class_and_state_codes'
    for link in range(256):
        for target in range(256):
            yield ((0,1,3,2,link),(1,1,3,2,target)),target,0x9C,'all_link_target_pairs'
    for low in range(256):
        for high in range(256):
            yield ((low,high,3,2,17),(1,1,3,2,17)),17,0x9C,'all_header_pairs'
    for length in range(27):
        for style in range(3):
            rows=tuple((i+1,128 if style==0 or (style==2 and i&1) else 1,1,2,17) for i in range(length))
            yield rows,17,0x9C,'marker_positions'
    for position in range(26):
        for style in range(3):
            rows=tuple((i+1,128 if style==0 or (style==2 and i&1) else 1,1,2,17) for i in range(position))
            yield rows+((1,1,3,2,17),),17,0x9C,'one_match_positions'
    for first in range(26):
        for second in range(first+1,26):
            for style in range(3):
                rows=tuple((i+1,1 if i in (first,second) else 128 if style==0 or (style==2 and i&1) else 1,
                    3 if i in (first,second) else 1,2,17) for i in range(second+1))
                yield rows,17,0x9C,'two_match_positions'
    for c in range(256):
        for length in (0,26):yield ((1,128,3,2,17),)*length,17,c,'initial_C_without_active_rows'
    randomizer=random.Random(0x62CF)
    for _ in range(4096):
        target=randomizer.randrange(256);rows=[]
        for index in range(randomizer.randrange(27)):
            kind=randomizer.randrange(5)
            row=(index+1,128,3,2,target) if kind==0 else (index+1,1,1,2,target) if kind==1 else (
                index+1,1,3,1,target) if kind==2 else (index+1,1,3,2,target^1) if kind==3 else (index+1,1,3,2,target)
            rows.append(row)
        yield tuple(rows),target,randomizer.randrange(256),'mixed_lists'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks];simulator=Simulator(memory)
    counts=Counter();outcomes=Counter();touched=set();costs=[]
    for rows,target,initial_c,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        setup={};old=serial&63;memory.out7ffd(old);stack=0x8002 if serial&1 else 0xBFFE
        ix=0xA100+64*(serial%26)

        def put(address,value):
            bank=5 if address<0x8000 else 2;memory[address]=value;setup[bank,address&0x3FFF]=value

        for index,row in enumerate(rows):
            for offset,value in zip((0,1,18,10,11),row):put(0xA100+64*index+offset,value)
        marker=0xA100+64*len(rows);put(marker,128);put(marker+1,128)
        put(ix+13,target);put(stack,255);put(stack+1,63);touched=set(setup)
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x3600|initial_c,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':ix,'IY':(serial*73)&65535,'SP':stack,'PC':0x62CF},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        # Подсчёт по независимому списку, завершение при двух подходящих строках либо первом маркере.
        number=0;c=initial_c;m1=4
        for index,row in enumerate((*rows,(128,128,0,0,0))):
            low,high,code,state,link=row;pointer=0xA100+64*index
            if high==128:
                if low==128:m1+=8;address=pointer;reason='marker';break
                m1+=9;continue
            c=(pointer+1)&255
            if code!=3:m1+=12;continue
            if state!=2:m1+=19;continue
            if link!=target:m1+=27;continue
            number+=1;m1+=31
            if number==2:address=pointer+1;reason='two_matches';break
        else:raise AssertionError('фикстура без завершения')
        m1+=3;wanted=list(initial);wanted[0:2]=[number,cp_flags(number,2)]
        wanted[2:8]=[number,c,0,64,address>>8,address&255]
        wanted[15]=refresh(initial[15],m1);wanted[SP],wanted[PC]=stack+2,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x62CF,stop=0x3FFF);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(serial,rows,target,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert not memory.writes and memory.o7ffd==old,(serial,'RAM_or_page_write')
        counts[kind]+=1;outcomes[str(number)+'_'+reason]+=1;costs.append(m1)
    for (bank,offset),value in setup.items():baseline[bank][offset]=value
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),outcomes=dict(outcomes),
        all_class_state_pairs=True,all_link_target_pairs=True,all_two_byte_header_pairs=True,
        all_initial_C_without_active_rows=True,two_match_positions_with_three_prefix_styles=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,no_memory_or_stack_writes=True,
        marker_returns_byte0_pointer=True,two_matches_return_byte1_pointer=True,C_tracks_last_active_header_low=True,
        count_saturates_at_two=True,FF_link_is_compared_as_ordinary_byte=True,all_64_initial_paging_values_distributed=True,
        observed_m1_min=min(costs),observed_m1_max=max(costs),independent_list_predicate_oracle=True,
        full_list_product_exhausted=False,game_array_capacity_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==202350
    (ROOT/'Tools/Disasm/Reports/ActionClass3LinkCountVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
