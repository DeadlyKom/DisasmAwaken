"""Все разности слова, три базы, точные регистры, флаги и R процедуры 6311."""
import json
from hashlib import sha256
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator, get_registers, PC, SP


class ReadOnlyFixture(list):
    def __setitem__(self,index,value):
        raise AssertionError(('процедура неожиданно пишет память',index,value))


def inspect_callers():
    """Статическая связь State08, отдельно от исполнения модельной фикстуры."""
    paths = (
        'Source/Action/ApproachTargetRecordAndResolve.asm',
        'Source/Action/CreateLinkedMissileRecord.asm',
        'Source/Action/DispatchObjectState.asm',
        'Source/Action/Data/ObjectStateHandlers.asm',
    )
    source = [(ROOT / path).read_text(encoding='utf-8') for path in paths]
    # Проверка трёх прямых вызовов, комментарии не считаются инструкциями.
    instructions = [line.split(';', 1)[0].strip() for line in source[0].splitlines()]
    assert instructions.count('CALL @Action.ApproachWordAndAccumulate.Entry') == 3
    # Проверка состояния и класса, записываемых создателем связанной ракеты.
    creator = [line.split(';', 1)[0].strip() for line in source[1].splitlines()]
    assert 'LD (IY + @FActionRecord.StateCode), #08' in creator
    assert 'LD (IY + @FActionRecord.ClassCode), #11' in creator
    # Проверка сохранения состояния класса 11 на входе Entry диспетчера.
    dispatch = source[2].split('Entry:', 1)[1].split('StoreRemainder:', 1)[0]
    assert dispatch.index('CP #12') < dispatch.index('CP #10')
    assert 'JP Z, @Action.SetClass18ObjectState.Entry' in dispatch
    assert 'JR NC, @Action.DispatchObjectState.CallHandler' in dispatch
    # Проверка физической записи обработчика State08 в таблице.
    state = source[3].split('State08:', 1)[1].split('}', 1)[0]
    assert '@Action.ApproachTargetRecordAndResolve.Entry' in state
    return dict(method='static_source_relationship_not_native_execution',
                direct_helper_calls=3, created_state=8, created_class=17,
                class_17_preserves_state_at_dispatch_entry=True,
                source_sha256={path: sha256((ROOT / path).read_bytes()).hexdigest()
                               for path in paths},
                native_creation_to_dispatch_execution_proved=False)


def main():
    callers=inspect_callers()
    flat=flat_action()
    flat[0xBFFE:0xC000]=[255,63]
    memory=ReadOnlyFixture(flat)
    simulator=Simulator(memory)
    counts={'small_positive':0,'small_negative':0,'large_positive':0,'large_negative':0}
    cases=0
    for base in (0,0x7FFF,0xFFFF):
        for delta in range(65536):
            negative=bool(delta&0x8000)
            magnitude=(-delta)&65535 if negative else delta
            small=magnitude<256
            step=magnitude//8 if small else 180
            signed_step=step if negative else (-step)&65535
            residual=(delta+signed_step)&65535
            high=residual>>8
            folded=high^255 if high&128 else high
            aggregate=(delta*73+(base>>8))&255
            result=folded|aggregate
            flags=(result&0xA8)|(0x40 if result==0 else 0)|(4 if result.bit_count()%2==0 else 0)
            # Расчёт R по двум ветвям нормализации, малому шагу и инверсии старшего байта остатка.
            m1=25+7*negative+9*small+7*(not negative)+(1 if high&128 else 0)
            value=(base+delta)&65535
            initial=get_registers({'PC':0x6311,'SP':0xBFFE,'AF':((delta*13)&255)*256+(delta&255),
                'HL':value,'BC':base,'DE':0xA55A,'IX':0xABCD,'IY':0x5C3A,
                '^AF':0x1234,'^HL':0x5678,'^DE':0x9ABC,'^BC':0xDE00|aggregate},None,False)
            initial[14],initial[15],initial[26],initial[27]=delta&255,(delta*17)&255,delta&1,delta%3
            wanted=list(initial)
            wanted[0],wanted[1]=result,flags
            wanted[4],wanted[5]=signed_step>>8,signed_step&255
            output=(value+signed_step)&65535
            wanted[6],wanted[7]=output>>8,output&255
            wanted[19]=result
            wanted[15]=(initial[15]&128)|((initial[15]+m1)&127)
            wanted[PC],wanted[SP]=0x3FFF,0xC000
            simulator.registers[:]=initial
            for _ in range(60):
                if simulator.registers[PC]==0x3FFF:break
                simulator.run()
            else:raise AssertionError(('нет возврата',base,delta))
            compared=(*range(24),PC,26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(base,delta,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            counts[('small_' if small else 'large_')+('negative' if negative else 'positive')]+=1
            cases+=1
    assert memory==flat
    result=dict(passed=True,total_cases=cases,cases_by_path=counts,
        all_65536_differences_for_each_base=True,bases=[0,0x7FFF,0xFFFF],
        exact_registers_flags_r_sp_and_all_ram=True,any_memory_write_rejected=True,
        all_input_words_product_exhausted=False,source_caller_relationship=callers,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionApproachWordVerification.json').write_text(
        json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
