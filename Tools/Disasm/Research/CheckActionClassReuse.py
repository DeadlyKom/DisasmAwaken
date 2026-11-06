"""Хвост E65F, настоящий итератор списка, пометка IY и условный восстановитель смещений."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionOffsetRestore import cp_flags
from ReferenceControlsPointRespawn import refresh


def profiles():
    mixed=tuple(i%3 for i in range(26))
    # Проверка полного кода класса, только 12 запускает проход списка, 14 восстанавливает операнды.
    for code in range(256):yield code,mixed,code
    # Проверка пустого, полного несовпадающего и полного совпадающего списка.
    for kind in range(3):yield 0x12,(kind,)*26,kind
    # Проверка каждого положения в каждом из трёх состояний, остальные записи неактивны.
    for position in range(26):
        for kind in range(3):yield 0x12,tuple(kind if i==position else 0 for i in range(26)),position*3+kind
    # Создание воспроизводимых смешанных списков, полное пространство 3^26 не перебирается.
    for seed in range(1024):
        value=seed+1;row=[]
        for _ in range(26):value=(1664525*value+1013904223)&0xFFFFFFFF;row.append((value>>16)%3)
        yield 0x12,tuple(row),seed&255
    # Проверка всех входных F на трёх крайних состояниях списка.
    for flags in range(256):
        for kind in range(3):yield 0x12,(kind,)*26,flags


def main(entry=0xE65F,report_tag='ActionClassReuse'):
    assert entry in (0xE65F,0xE658)
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    counts=Counter();cases=0
    for code,kinds,flags in profiles():
        kinds=list(kinds)
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        # Создание независимой входной записи для хвоста либо реальной записи массива для полного отказа E658.
        memory[0x9012]=code;memory[0xBFFE],memory[0xBFFF]=255,63
        memory[0x9B82],memory[0x9B83]=flags,(flags*73)&255
        for i,kind in enumerate(kinds):
            pointer=0xA100+64*i
            memory[pointer],memory[pointer+1]=i+1,128 if kind==0 else 1+i%7
            memory[pointer+0x12],memory[pointer+0x18]=0x12 if kind==2 else 0x34,i+17
        memory[0xA780],memory[0xA781]=128,128
        pointer=0xA100+64*(cases%26) if entry==0xE658 else 0x9000
        memory[pointer+0x12]=code
        if entry==0xE658:
            memory[0xE605],memory[0xE606]=0xFE,0xBF
        originals=(0x8001^flags,0x7FFF-flags,0xA55A^flags)
        for address,value in zip((0xE68C,0xE692,0xE698),originals):memory[address],memory[address+1]=value&255,value>>8
        initial=get_registers({'AF':((flags*109)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':pointer,'IY':0x5C3A,
            'SP':pointer+2*(cases%3) if entry==0xE658 else 0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=flags,flags,flags&1,flags%3
        expected=[bytearray(b) for b in memory.banks];writes=[];wanted=list(initial)

        def put(address,value):
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))

        def word(address,value):put(address,value&255);put(address+1,value>>8)

        if entry==0xE658:
            # Создание эталона восстановления SP и настоящего CALL пометки входной записи IX.
            word(0xBFFC,0xE65F);put(pointer+1,128);put(pointer,0);put(pointer+0x18,255)
            kinds[cases%26]=0
        if code!=0x12:
            wanted[0:2]=[code,cp_flags(code)];m1=15 if code==0x14 else 8
            if code==0x14:
                for address,value in zip((0xE5B3,0xE5D2,0xE5ED),originals):word(address,value)
                wanted[6:8]=[originals[2]>>8,originals[2]&255]
            counts['tail_restore' if code==0x14 else 'tail_without_restore']+=1
        else:
            put(0x9B83,0);put(0x9B82,0)
            # Расчёт M1 и следа записей по числовому списку без исполнения дочерних процедур в эталоне.
            m1=10;position=0
            while True:
                word(0xBFFC,0xE677);m1+=1
                while position<26 and kinds[position]==0:position+=1;m1+=10
                if position==26:m1+=12;break
                m1+=11
                if kinds[position]==2:
                    pointer=0xA100+64*position;word(0xBFFC,0xE682)
                    put(pointer+1,128);put(pointer,0);put(pointer+0x18,255);m1+=9
                position+=1
            wanted[0:2]=[128,0x42];wanted[2:4]=[0,64];wanted[10:12]=[0xA7,128]
            counts['list_scan']+=1
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],m1+(10 if entry==0xE658 else 0)),0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(cases,code,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(cases,code,'RAM')
        assert Counter(memory.writes)==Counter(writes),(cases,code,'writes',memory.writes,writes)
        cases+=1
    report=dict(passed=True,total_cases=cases,cases_by_kind=dict(counts),entry=entry,
        restored_CPU_SP_before_first_CALL_proved=entry==0xE658,all_256_class_codes=True,all_256_initial_flags=True,
        list_records=26,marker_address=0xA780,all_record_positions_and_three_states=True,random_list_patterns=1024,
        all_list_combinations_exhausted=False,real_iterator_setter_and_restorer_executed=True,
        independent_numeric_oracle=True,exact_registers_including_R=True,all_physical_ram_bytes_proved=True,
        write_multiplicity_proved=True,hardware_bus_write_order_proved=False,
        class12_maximum_additional_stack_bytes=2,other_classes_cpu_stack_not_written=entry!=0xE658,
        marker_ret_bypasses_restorer=True,irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/('Tools/Disasm/Reports/'+report_tag+'Verification.json')).write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
