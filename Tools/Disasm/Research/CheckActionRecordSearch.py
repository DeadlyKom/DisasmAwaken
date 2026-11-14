"""E9A1, поиск записи с пропуском FF в поле 18 и явным маркером конца."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def inc_flags(value,carry):
    result=(value+1)&255
    return (result&0xA8)|(64 if not result else 0)|(16 if value&15==15 else 0)|(4 if value==127 else 0)|carry


def main():
    original=flat_action();memory=Memory(original);simulator=Simulator(memory);counts=Counter();touched=set();skip_total=0
    costs=[];found_A80_cases=0
    def check(position,first,tag,marker,pattern,kind):
        nonlocal touched,skip_total,found_A80_cases
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=original[address]
        # Создание занятых строк и пропускаемых строк перед выбранной границей поиска.
        rows=[]
        for i in range(position):rows.append((17,128,255) if pattern and i%2==0 else (45,1,73))
        rows.append((128,128,tag) if marker else (first,128,tag))
        # Создание достижимого завершения для выбранной строки с тегом FF.
        if not marker and first!=128 and tag==255:rows.append((0,128,0))
        for i,row in enumerate(rows):
            base=0xA100+i*64;memory[base],memory[base+1],memory[base+24]=row
        memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xE9A1},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);writes=[];m1=3
        # Поиск первой принятой строки или маркера по независимому списку записей.
        for i,(header,state,skip) in enumerate(rows):
            m1+=6
            if state!=128:continue
            m1+=4
            if header==128:
                wanted[0:2]=[128,0x42];result='end_marker';break
            base=0xA100+i*64;writes.append((base+24,0));expected[base+24]=0;m1+=6
            if skip==255:skip_total+=1;continue
            wanted[0:2]=[(skip+1)&255,inc_flags(skip,int(header<128))];m1+=1;result='found';break
        else:raise AssertionError('эталон без достижимого завершения')
        wanted[4:6]=[0,64];wanted[10:12]=[base>>8,base&255] if result=='found' else [(0xA100+i*64)>>8,(0xA100+i*64)&255]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        measured_m1=0
        for _ in range(4000):
            if simulator.registers[PC]==0x3FFF:break
            old_r=simulator.registers[15]
            simulator.run()
            increment=(simulator.registers[15]-old_r)&127
            assert increment in (1,2),(serial,'неожиданное изменение R',increment)
            measured_m1+=increment
        else:raise AssertionError(('возврат',position,first,tag,marker,pattern))
        assert measured_m1==m1,(serial,'M1',measured_m1,m1)
        costs.append(m1)
        # Проверка ненулевого результата 80, совпадение A с маркером не означает отказа по Z.
        if result=='found' and skip==127:
            assert simulator.registers[0]==128 and not simulator.registers[1]&64
            found_A80_cases+=1
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(position,first,tag,marker,pattern,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==writes,(position,first,tag,marker,pattern)
        touched={0xA100+i*64+j for i in range(len(rows)) for j in (0,1,24)};counts[kind]+=1
    # Проверка каждой позиции до 255 с занятым и смешанным префиксом и обоими видами завершения.
    for position in range(256):
        for pattern in (0,1):
            for marker in (False,True):check(position,0,0,marker,pattern,'all_positions')
    print('All 256 positions and termination profiles passed',flush=True)
    # Проверка каждой пары первого байта и тега на двух префиксах, включая переполнение тега FF.
    for first in range(256):
        for tag in range(256):
            for pattern in (0,1):check(3,first,tag,False,pattern,'all_header_and_tag_pairs')
    assert counts.total()==132096 and found_A80_cases
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),cleared_skip_records=skip_total,
        method='independent_record_list_search_against_original_instructions',
        all_header_tag_pairs=True,all_positions_within_256_records=True,explicit_end_marker_and_skip_ff=True,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,no_cpu_stack_writes=True,
        full_M1_count_compared_not_only_R_modulo_128=True,observed_M1_min=min(costs),observed_M1_max=max(costs),
        found_A80_with_Z_clear_cases=found_A80_cases,
        maximum_records_is_not_a_proved_game_limit=True,termination_requires_reachable_match_or_marker=True,
        all_joint_inputs_exhausted=False,record_field_game_meanings_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordSearchVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
