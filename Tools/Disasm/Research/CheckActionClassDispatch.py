"""64DF, точный косвенный переход без исполнения ещё не разобранных обработчиков."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    count=0;targets={};ignored_cases=0
    assert flat[0x6524]==0xC9
    # Проверка каждого байта класса на каждой из 26 физических записей ACTION.
    for index in range(26):
        ix=0xA100+64*index
        for value in range(256):
            memory.recording=False;memory[ix+18]=value
            memory[0xBFFE],memory[0xBFFF]=255,63
            initial=get_registers({'AF':(value*256+index*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,
                'IX':ix,'IY':0x5C3A,'SP':0xBFFE,'PC':0x64DF},None,False)
            initial[14],initial[15],initial[26],initial[27]=count&255,count&255,count&1,count%3
            # Расчёт исходного оборачиваемого индекса и адреса, проверка верхней границы в коде отсутствует.
            offset=(2*value)&255;address=0x64F0+offset
            target=flat[address]+256*flat[address+1]
            flags=(offset&128)|(64 if offset==0 else 0)|(4 if offset.bit_count()%2==0 else 0)|0x20
            wanted=list(initial);wanted[0:2]=[target&255,flags];wanted[2:4]=[0x64,0xF0]
            wanted[6:8]=[target>>8,target&255];wanted[15]=refresh(initial[15],13);wanted[PC]=target
            before=[bytearray(b) for b in memory.banks]
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True
            # Исполнение ровно одиннадцати инструкций заканчивается непосредственно после JP (HL).
            for _ in range(11):simulator.run()
            memory.recording=False
            assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(index,value,target,
                [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
            assert not memory.writes and all(a==b for a,b in zip(before,memory.banks))
            if 10<=(value&127)<=25:
                # Проверка настоящего общего RET всех шестнадцати классов после косвенного диспетчера.
                assert target==0x6524
                simulator.run()
                returned=list(wanted);returned[PC],returned[SP]=0x3FFF,0xC000;returned[15]=refresh(initial[15],14)
                assert all(returned[i]==simulator.registers[i] for i in (*range(25),26,27)),(index,value,'common_RET')
                assert not memory.writes and all(a==b for a,b in zip(before,memory.banks))
                ignored_cases+=1
            targets[str(value)]=target;count+=1
    report=dict(passed=True,total_cases=count,all_256_class_codes_and_26_records=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,no_memory_or_stack_writes=True,
        numeric_dispatch_formula_proved=True,refresh_m1=13,original_table_entries=26,
        class_128_aliases_class_0=True,classes_26_through_127_read_following_code_as_addresses=True,
        execution_stopped_after_indirect_jump=True,target_handler_semantics_proved=False,
        class_domain_in_all_game_writers_proved=False,targets=targets,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    ignored=dict(passed=True,total_cases=ignored_cases,original_opcode=0xC9,common_target=0x6524,
        all_classes_10_through_25_and_high_bit_aliases=True,all_26_record_positions=True,
        actual_dispatcher_and_common_RET_executed=True,exact_registers_including_R=True,
        all_physical_ram_bytes_proved=True,no_memory_or_stack_writes=True,return_refresh_m1=1,
        full_dispatch_refresh_m1=14,assembly_executed=False,irq_executed=False,native_execution=False)
    assert ignored_cases==832
    (ROOT/'Tools/Disasm/Reports/ActionIgnoredClassesVerification.json').write_text(json.dumps(ignored,indent=2)+'\n','utf-8')
    (ROOT/'Tools/Disasm/Reports/ActionClassDispatchVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='targets'},indent=2))


if __name__=='__main__':main()
