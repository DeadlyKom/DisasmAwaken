"""Компоненты, частичный отказ, поиск класса 12 и настоящий межбанковый запрос предупреждения."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from ReferenceActionRecordUpdate import RecordUpdate


def fixtures():
    # Проверка всех слов каждой компоненты при нулевой поправке, остальные компоненты равны нулю.
    for field in range(3):
        for word in range(65536):
            components=[0,0,0];components[field]=word
            yield dict(kind='all_component_words',components=components,flags=word&255)
    # Проверка границ знакового сложения и переноса вычитания на каждой позиции.
    edges=(0,1,127,128,255,256,0x70FF,0x7100,0x7FFF,0x8000,0x8001,0xFEFF,0xFF00,0xFFFF)
    for field in range(3):
        for component in edges:
            for difference in edges:
                components=[0,0,0];components[field]=component
                bases=[0,0,0];offsets=[0,0,0]
                offsets[field]=0xF001;bases[field]=(difference+0xF001)&65535
                yield dict(kind='arithmetic_edges',components=components,bases=bases,offsets=offsets)
    # Проверка каждого входного HL при четырёх удвоениях, исходные младшие биты не отбрасываются заранее.
    for word in range(65536):yield dict(kind='all_scale_words',hl=word,components=(1,2,3))
    # Проверка пяти настоящих точек входа и сохранённых оригиналов для каждого полного кода класса.
    for entry in range(0xE5A0,0xE5A5):
        for code in range(256):yield dict(kind='entry_and_class',entry=entry,code=code,components=(1,2,3),flags=code)
    # Проверка отказа на каждой позиции для класса 12, помечаются и другие активные записи этого класса.
    for field in range(3):
        for value in (0x7100,0x7FFF,0x8001,0x8EFF):
            components=[1,2,3];components[field]=value
            yield dict(kind='class12_reject',code=0x12,components=components,state=1,target=True)
    # Проверка результата поиска, вооружения предупреждения и всех курсоров очереди при разных масках занятости.
    for entry in range(0xE5A0,0xE5A5):
        for code in (0,0x12,0x14,255):
            for target in (False,True):
                for far in (False,True):
                    for alarm in (0,24,128,255):
                        yield dict(kind='post_update_routes',entry=entry,code=code,state=1,target=target,far=far,alarm=alarm)
    masks=(0,65535,*(1<<i for i in range(16)),*(65535^(1<<i) for i in range(16)))
    for head in range(17):
        for mask in masks:yield dict(kind='queue_cursor_and_mask',state=1,target=True,alarm=128,head=head,mask=mask)
    # Проверка всех физических IX, включая совпадение искомого класса с обновляемой записью.
    for position in range(26):
        for code in (0x12,0x14):
            for state in (0,1):yield dict(kind='physical_record_positions',position=position,code=code,state=state,target=True,alarm=128)


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    base[1]=bytearray(base_memory()[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    counts=Counter();paths=Counter();queue_results=Counter();cases=0
    for fixture in fixtures():
        memory.recording=False
        for page in (0,1,2,5):memory.banks[page][:]=base[page]
        memory.out7ffd(16)
        def word(address,value):memory[address],memory[address+1]=value&255,value>>8
        # Создание исходного массива, отдельная цель класса 12 появляется только в соответствующих сценариях.
        for position in range(26):
            pointer=0xA100+64*position
            memory[pointer],memory[pointer+1],memory[pointer+18],memory[pointer+24]=position+1,128,0x34,position+17
        memory[0xA780],memory[0xA781]=128,128
        record=0xA100+64*fixture.get('position',0)
        for field,value in enumerate(fixture.get('components',(1,2,3))):word(record+2*field,value)
        memory[record+18]=fixture.get('code',0)
        if fixture.get('target',False):
            target=0xA100+64*((fixture.get('position',0)+1)%26)
            for delta,value in ((0,1),(2,2),(4,0x0800 if fixture.get('far',False) else 3)):word(target+delta,value)
            memory[target+18]=0x12
        for address,value in zip((0xE5B0,0xE5CF,0xE5EA),fixture.get('bases',(0,0,0))):word(address,value)
        for address,value in zip((0xE5B3,0xE5D2,0xE5ED),fixture.get('offsets',(0,0,0))):word(address,value)
        for address,value in zip((0xE68C,0xE692,0xE698),(0x8001,0x7FFF,0xA55A)):word(address,value)
        word(0xE605,0xBFFE);word(0xBFFE,0x3FFF)
        memory[0x9B82],memory[0x9B83],memory[0xE644]=fixture.get('state',0),0xA5,fixture.get('alarm',0)
        mask=fixture.get('mask',0)
        for index in range(16):
            memory.banks[1][0x2C80+2*index]=0x80 if mask&(1<<index) else 1
            memory.banks[1][0x2C81+2*index]=(index*73+cases)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes((0,0))
        cursor=0xEC80+2*fixture.get('head',0);memory.banks[1][0x2C5D:0x2C5F]=bytes((cursor&255,cursor>>8))
        entry=fixture.get('entry',0xE5A0);flags=fixture.get('flags',cases&255)
        initial=get_registers({'AF':((cases*73)&255)*256+flags,'HL':fixture.get('hl',200),'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':record,'IY':0x5C3A,'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,cases&255,cases&1,cases%3
        expected=RecordUpdate(memory.banks,initial).run(entry)
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True;simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        compared=(*range(15),*range(16,25),26,27)
        assert all(expected.r[i]==simulator.registers[i] for i in compared),(cases,fixture,expected.path,
            [(i,expected.r[i],simulator.registers[i]) for i in compared if expected.r[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected.banks,memory.banks)),(cases,fixture,expected.path,'RAM')
        assert Counter(memory.writes)==Counter(expected.writes),(cases,fixture,expected.path,'writes',memory.writes,expected.writes)
        assert trace.writes==expected.ports and memory.o7ffd==16,(cases,fixture,'ports')
        counts[fixture['kind']]+=1;paths.update(expected.path)
        if expected.queue_result is not None:queue_results['accepted' if expected.queue_result['accepted'] else 'dropped']+=1
        cases+=1
        if cases%65536==0:print(str(cases)+' cases passed',flush=True)
    report=dict(passed=True,total_cases=cases,cases_by_kind=dict(counts),routes=dict(paths),queue_results=dict(queue_results),
        all_words_in_each_component=True,all_scale_HL_words_at_E5A0=True,all_256_class_codes_at_five_entries=True,
        all_five_original_dispatch_entries=True,independent_numeric_oracle=True,exact_registers_except_R=True,
        all_26_physical_record_positions=True,
        refresh_R_proved=False,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        actual_children_and_banked_queue_executed=True,partial_component_updates_preserved_on_rejection=True,
        all_queue_cursors=True,queue_masks_checked=34,full_component_product_exhausted=False,
        all_possible_base_offset_pairs_exhausted=False,irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordUpdateVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
