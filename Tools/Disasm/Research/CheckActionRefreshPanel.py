"""Принудительная перерисовка панели 6145, композиция проверенных независимых моделей детей."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionPanelGauges import reference as panel,REQUESTS
from ReferenceControlsBcdExact import evaluate as bcd
from ReferenceControlsPointRespawn import refresh

REQUEST_WRITE_ORDER=(0x669F,0x666B,0x664A,0x668E,0x667D,0x665C)


def evaluate(memory,initial,values,preferred,fallback,word,counter):
    registers=list(initial);writes=[];ports=[];shadow={};stack=initial[12]
    def emit(bank,offset,value):writes.append((bank,offset,value));shadow[bank,offset]=value
    def put(address,value):emit(5 if address<0x8000 else 2,address&0x3FFF,value)
    def push(pointer,value):put(pointer,value&255);put(pointer+1,value>>8)
    def select(page,return_address):
        push(stack-2,return_address);push(stack-4,(registers[2]<<8)|registers[3]);ports.append((0x7FFD,page));registers[0]=page
    # Выбор ACTION и создание запросов всех шкал независимо от их старого состояния.
    select(0x10,0x614A);registers[0]=1
    for address in REQUEST_WRITE_ORDER:put(address,1)
    push(stack-2,0x6161)
    registers,child_writes,child_ports,panel_m1,page=panel(registers,(1,)*6,values,preferred,fallback,word,0x10)
    assert page==0x10
    for bank,offset,value in child_writes:
        # Модель шкал использует внешний SP=BFFE, CALL обёртки добавляет ещё одно слово.
        if bank==2 and 0x3FF8<=offset<=0x3FFD:offset+=stack-0xBFFE-2
        emit(bank,offset,value)
    ports.extend(child_ports)
    # Выбор CONTROL и хвостовая передача без ещё одного адреса возврата.
    select(0x11,0x6166);e,d,l,h=counter
    registers[2],registers[4:8]=255,[d,e,h,l]
    registers[15]=refresh(initial[15],29+panel_m1)
    class View:
        def __getitem__(self,address):
            bank=1 if address>=0xC000 else 2 if address>=0x8000 else 5
            offset=address&0x3FFF
            return shadow.get((bank,offset),memory.banks[bank][offset])
    registers,digit_writes,bcd_m1=bcd(View(),registers)
    for address,value in digit_writes:put(address,value)
    return registers,writes,ports,29+panel_m1+bcd_m1


def profiles():
    # Проверка всех значений каждого прямого входа шкалы и каждой пары счётчика.
    for index in range(4):
        for value in range(256):
            fields=[0,7,46,255];fields[index]=value
            yield fields,0,0xAB,0xFF43,[0x12,0x34,0x56,0x78],'gauge_bytes'
            pairs=[0x12,0x34,0x56,0x78];pairs[index]=value
            yield [0,7,46,255],0x77,0xAB,0x8000,pairs,'counter_bytes'
    # Проверка всех исходных страниц и крайних величин шестой шкалы.
    for old in range(32):
        for word in (0,1,3,4,183,184,187,188,1023,1024,0x7FFF,0x8000,0xFC00,0xFF44,0xFFFF):
            yield [0,47,128,255],old*7,255-old,word,[old,0x12,0x34,0xFF],'signed_edges_and_pages'
    randomizer=random.Random(0x6145)
    # Проверка смешанных исходных запросов, байтов шкал, счётчика и экранных тетрад.
    for _ in range(4096):
        yield [randomizer.randrange(256) for _ in range(4)],randomizer.randrange(256),randomizer.randrange(256),randomizer.randrange(65536),[randomizer.randrange(256) for _ in range(4)],'mixed_panels'


def main():
    for name in ('ActionPanelGauges','ControlsBcdExact'):
        assert json.loads((ROOT/('Tools/Disasm/Reports/'+name+'Verification.json')).read_text())['passed']
    flat=flat_action();baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:])
    memory=RecordedBanks(banks=[bytearray(bank) for bank in baseline],out7ffd=16);simulator=Simulator(memory)
    touched=set();counts=Counter();m1_costs=set();page_set=set();request_sets=[set() for _ in REQUESTS]
    for values,preferred,fallback,word,counter,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        old=serial&31;stack=0xBFFE if serial&1 else 0x9008;memory.out7ffd(old);page_set.add(old)
        for index,address in enumerate(REQUESTS):
            request=(serial*73+index*47)&255;request_sets[index].add(request);memory[address]=request
        for address,value in zip((0xA794,0xA8BC,0x6682,0x6693),values):memory[address]=value
        for address,value in zip((0x9C10,0x9C11,0xA78F,0xA790,stack,stack+1), (preferred,fallback,word&255,word>>8,255,63)):
            memory[address]=value
        for index,value in enumerate(counter):memory[0x9BBD+index]=value
        for high in range(0x51,0x57):memory.banks[5][(high<<8)-0x4000:((high+1)<<8)-0x4000]=bytes((high*7+low*73+serial*31)&255 for low in range(256))
        initial=get_registers({'AF':(serial*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0x6145},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted,writes,ports,cost=evaluate(memory,initial,values,preferred,fallback,word,counter)
        expected=[bytearray(bank) for bank in memory.banks]
        for bank,offset,value in writes:expected[bank][offset]=value
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        visits=Counter()
        for _ in range(4000):
            pc=simulator.registers[24]
            if pc==0x3FFF:break
            if pc in (0x6649,0xE8FD,0xF142,0xF188):visits[pc]+=1
            if pc==0x6649:assert all(memory[address]==1 for address in REQUESTS)
            if pc==0xF142:assert simulator.registers[12]==stack and memory.o7ffd==0x11
            simulator.run()
        else:raise AssertionError(('no_return',serial))
        memory.recording=False
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,kind,values,word,counter,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert visits=={0x6649:1,0xE8FD:6,0xF142:1,0xF188:8},(serial,'children',visits)
        assert trace.writes==ports and len(ports)==14 and memory.o7ffd==0x11,(serial,'ports')
        assert Counter(writes)==Counter(memory.writes) and all(a==b for a,b in zip(expected,memory.banks)),(serial,'RAM_or_multiplicity')
        assert min(offset for bank,offset,_ in writes if bank==2)==(stack-8)&0x3FFF
        assert [memory[address] for address in REQUESTS]==[0,1,0,0,0,0]
        touched={(bank,offset) for bank,offset,_ in writes};counts[kind]+=1;m1_costs.add(cost)
    assert len(page_set)==32 and all(len(values)==256 for values in request_sets)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),
        method='independent_parent_and_checked_child_composition_against_original_bytes',exact_registers_including_R=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,all_32_unlocked_initial_configurations=True,
        all_old_request_bytes_each_position=True,six_real_gauge_calls=True,eight_real_digit_calls=True,
        full_request_mask_forced=True,second_request_preserved_as_one=True,other_five_requests_cleared=True,
        tail_jump_keeps_external_return_frame=True,maximum_additional_stack_bytes=8,port_writes=14,final_7ffd=17,
        locked_configuration_outside_contract=True,observed_m1_min=min(m1_costs),observed_m1_max=max(m1_costs),
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionRefreshPanelVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
