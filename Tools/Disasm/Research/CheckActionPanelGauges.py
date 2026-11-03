"""Исходный 6649, запросы перерисовки, шесть шкал, реальные страницы и физические записи."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh
from ReferenceActionPanelGauges import reference,REQUESTS


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    for tag in ('ControlsSixRowGauge','ActionGaugeWrapper','ActionPreferredByte'):
        assert read(tag+'Verification')['passed']
    flat=flat_action();baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:])
    memory=RecordedBanks(banks=[bytearray(bank) for bank in baseline],out7ffd=0x10)
    simulator=Simulator(memory);touched=set();counts=Counter()

    def check(mask,values,preferred,fallback,word,old=0x10,on=1,kind='profile'):
        nonlocal touched
        serial=counts.total();memory.recording=False
        for bank,index in touched:memory.banks[bank][index]=baseline[bank][index]
        memory.out7ffd(old)
        requests=[on if mask&(1<<i) else 0 for i in range(6)]
        for address,value in zip(REQUESTS,requests):memory[address]=value
        for address,value in zip((0xA794,0xA8BC,0x6682,0x6693),values):memory[address]=value
        put(memory,0x9C10,[preferred,fallback]);put(memory,0xA78F,[word&255,word>>8]);put(memory,0xBFFE,[0xFF,0x3F])
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6649},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted,writes,ports,cost,page=reference(initial,requests,values,preferred,fallback,word,old)
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],cost)
        expected=[bytearray(bank) for bank in memory.banks]
        for bank,index,value in writes:expected[bank][index]=value
        simulator.registers[:]=initial
        trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True
        for _ in range(1900):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',mask,values,preferred,fallback,word,old))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(mask,values,preferred,fallback,word,old,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert trace.writes==ports and memory.o7ffd==page
        assert all(a==b for a,b in zip(memory.banks,expected)) and Counter(memory.writes)==Counter(writes),('RAM',mask,word)
        touched={(bank,index) for bank,index,_ in writes}
        stack=[index for bank,index,_ in memory.writes if bank==2 and index>=0x3FF0]
        assert (min(stack)==0x3FF8) if mask else not stack
        counts[kind]+=1

    # Проверка всех сочетаний запросов и четырёх разных ненулевых кодов запроса.
    for on in (1,2,128,255):
        for mask in range(64):check(mask,[0,6,47,255],0,20,0xFF43,on=on,kind='requests')
    # Проверка каждого значения четырёх входов при одновременном обновлении шести шкал.
    for field in range(4):
        for value in range(256):
            values=[0,6,47,255];values[field]=value
            check(63,values,0,20,0xFF43,kind='values')
    print('Requests and four value inputs complete',flush=True)
    # Проверка всех пар источника второй шкалы через настоящий читатель и оба банковых переключения.
    for preferred in range(256):
        for fallback in range(256):check(2,[0,0,0,0],preferred,fallback,0,kind='preferred')
    print('Preferred/fallback full sweep complete',flush=True)
    # Проверка каждого знакового слова шестой шкалы, включая 8000 и обе границы насыщения.
    for word in range(65536):check(32,[0,0,0,0],0,0,word,kind='signed_word')
    print('Signed source full sweep complete',flush=True)
    # Проверка всех незаблокированных конфигураций порта при каждом сочетании запросов.
    for old in range(32):
        for mask in range(64):check(mask,[48,62,63,255],20,255,0x8000,old=old,kind='pages')
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),
        method='composition_of_checked_children_and_independent_parent_control_reference',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        all_request_combinations=True,nonzero_request_codes=[1,2,128,255],
        every_byte_of_four_value_inputs=True,all_preferred_fallback_pairs=True,all_signed_source_words=True,
        all_unlocked_pages_and_request_combinations=True,exact_registers_flags_refresh_sp=True,
        every_physical_ram_byte_and_write_checked=True,real_out_and_physical_eight_banks=True,
        maximum_additional_stack_bytes=6,second_request_preserved=True,other_five_requests_cleared=True,
        source_word_and_preferred_pair_unchanged=True,sixth_gauge_range=[0,46],
        all_joint_inputs_exhausted=False,game_meaning_of_source_fields_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionPanelGaugesVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
