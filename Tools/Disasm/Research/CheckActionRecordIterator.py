"""Итератор E6D1 и фильтр E98D, реальный CALL, включая найденный код FF с Z=1."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh


def cp(left,right):return (sub8_flags(left,right)&~0x28)|(right&0x28)


def main():
    original=flat_action();memory=Memory(original);simulator=Simulator(memory);counts=Counter();touched=set();ff_found=0
    def check(entry,rows,step=64,start=0xA0C0,code=0,kind='iterator'):
        nonlocal touched,ff_found
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=original[address]
        addresses=[]
        for n,row in enumerate(rows):
            base=(start+(n+1)*step)&65535
            for offset,value in zip((0,1,18),row):memory[base+offset]=value;addresses.append(base+offset)
        memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':code*256+0x68,
            'BC':step,'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':start,'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);writes=[];m1=3 if entry==0xE98D else 0;cursor=0
        # Поиск последовательных результатов итератора с последующей независимой фильтрацией кода.
        while True:
            child=0
            while True:
                header,state,record_code=rows[cursor];base=(start+(cursor+1)*step)&65535;cursor+=1
                child+=6
                if state!=128:a,f,marker=state,cp(state,128),False;break
                child+=4
                if header==128:a,f,marker=128,0x42,True;child+=1;break
            m1+=child
            if entry==0xE6D1:break
            # Создание эталона настоящей записи возврата CALL, отдельно от контракта ребёнка.
            writes.extend([(0xBFFC,0x97),(0xBFFD,0xE9)]);expected[0xBFFC:0xBFFE]=[0x97,0xE9]
            m1+=2
            if marker:break
            m1+=4
            if record_code!=code:continue
            a=(code+1)&255;f=(a&0xA8)|(64 if not a else 0)|(16 if code&15==15 else 0)|(4 if code==127 else 0)
            m1+=2;ff_found+=int(code==255);break
        wanted[0:2]=[a,f];wanted[10:12]=[base>>8,base&255]
        if entry==0xE98D:wanted[2:4]=[0,64]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(5000):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',entry,len(rows),step,start,code))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(entry,rows[-2:],step,code,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes)
        touched=set(addresses)|{address for address,_ in writes};counts[kind]+=1
    # Проверка каждого шага BC при непосредственном выходе на A100, включая нулевой шаг.
    for step in range(65536):
        for row in ((0,1,0),(128,128,0)):check(0xE6D1,[row],step,(0xA100-step)&65535,kind='all_steps')
    print('All 65536 BC steps passed',flush=True)
    # Проверка каждого сочетания байтов заголовка, пропускаемая запись завершается следующей активной.
    for header in range(256):
        for state in range(256):check(0xE6D1,[(header,state,0),(0,1,0)],kind='all_header_states')
    # Проверка всех пар требуемого и фактического кодов с настоящими вложенными вызовами.
    for code in range(256):
        for actual in range(256):check(0xE98D,[(0,1,actual),(0,1,code)],code=code,kind='all_code_pairs')
    # Проверка всех 256 позиций маркера и совпадения после пропущенных доступных записей.
    for count in range(256):
        for code in (0,127,128,255):
            for end in ((128,128,code),(0,1,code)):
                check(0xE98D,[(0,128,0)]*count+[end],code=code,kind='all_positions_and_markers')
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),found_ff_with_zero_result=ff_found,
        method='independent_record_iterator_and_filter_with_original_child_executed',
        all_step_words=True,all_header_state_pairs=True,all_requested_actual_code_pairs=True,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
        iterator_writes_no_memory=True,filter_writes_only_cpu_stack=True,maximum_additional_stack_bytes=2,
        found_ff_returns_z_set=True,termination_requires_reachable_result_or_marker=True,
        game_array_limit_proved=False,all_joint_inputs_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordIteratorVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
