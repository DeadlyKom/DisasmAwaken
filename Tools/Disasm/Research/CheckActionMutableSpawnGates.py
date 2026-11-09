"""Общее поле 06, пересчёт порога планировщика и порог сохранённого слова поля 0B."""
from collections import Counter
import json,os,tempfile
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckIntro import ROOT
from CheckMusic import PC,SP,Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionFoldedRandom import step
from PreviewEdgeRasterOracle import arithmetic


def compare_flags(value,operand):
    # Расчёт CP, неофициальные разряды 5 и 3 берутся из операнда, а не из разности SUB.
    _,flags=arithmetic(value,operand,True)
    return (flags&~0x28)|(operand&0x28)


def main():
    flat=flat_action();banks=[bytearray(0x4000) for _ in range(8)]
    for bank,start in ((5,0x4000),(2,0x8000),(0,0xC000)):banks[bank][:]=bytes(flat[start:start+0x4000])
    m=RecordedBanks(banks=banks,out7ffd=16);sim=Simulator(m);trace=PortTrace(sim);sim.set_tracer(trace)
    initial=get_registers({'SP':0xBFFE,'IX':0xA100,'IY':0x5C3A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        'AF':0xA55A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0},None,False)
    parameters=bytes(flat[0x9BA4:0x9BB3]);counts=Counter();outcomes=Counter();seeds={}
    # Поиск состояний настоящего потока 0 с каждым выходным младшим байтом.
    for seed in range(65536):
        value=step(seed,0);seeds.setdefault(value['word']&255,(seed,value))
        if len(seeds)==256:break
    assert len(seeds)==256

    def apply(value):
        m.recording=False
        for index,byte in enumerate(parameters):m[0x9BA4+index]=byte
        m[0x9BAA],m[0x9BAF]=value,value
        m[0xBFFE],m[0xBFFF]=255,63
        sim.registers[:]=initial;sim.run(start=0xAC5D,stop=0x3FFF)
        assert m[0x7B6B]==m[0x6874]==m[0x79A4]==value

    def begin():
        sim.registers[:]=initial;m.writes=[];trace.writes=[];m.recording=True

    def shared():assert m.o7ffd==16 and not trace.writes

    for base in range(256):
        apply(base)
        for maximum in range(256):
            m.recording=False;m[0x7B6B]=base;begin();sim.registers[7]=maximum
            sim.run(start=0x686C,stop=0x687C)
            changed=maximum>=28;limit=min(255,maximum-27+base) if changed else base
            if changed:
                result,flags=arithmetic(maximum-27,base,False)
                expected_a=limit;expected_writes=[(5,0x3B6B,limit)]
            else:
                flags=compare_flags(maximum,28)
                expected_a=maximum;expected_writes=[]
            context=('bias',base,maximum)
            assert m[0x7B6B]==limit and m[0x6874]==base and m.writes==expected_writes,context
            assert tuple(sim.registers[:2])==(expected_a,flags),context
            assert sim.registers[SP]==0xBFFE and sim.registers[2:12]==initial[2:7]+[maximum]+initial[8:12],context
            shared();counts['all_bias_maximum_pairs']+=1
        # Восстановление непосредственно применённого порога перед полным перебором потока.
        m.recording=False;m[0x7B6B]=base
        for low,(seed,value) in seeds.items():
            m.recording=False;m[0xEBDE],m[0xEBDF],m[0xEBE0]=seed&255,seed>>8,0;begin()
            sim.registers[PC]=0x7B66
            for _ in range(100):
                if sim.registers[PC] in (0x794B,0x7B6F):break
                sim.run()
            else:raise AssertionError('schedule instruction limit')
            flags=compare_flags(low,base)
            assert sim.registers[PC]==(0x794B if low<base else 0x7B6F)
            assert tuple(sim.registers[:2])==(low,flags) and sim.registers[SP]==0xBFFE
            assert bytes(m[0xEBDE:0xEBE1])==value['word'].to_bytes(2,'little')+bytes((value['fold'],))
            shared();counts['all_scheduler_limit_random_low_pairs']+=1
        # Полный перебор порога и младшего байта при разрешённом старшем байте 23.
        for low in range(256):
            m.recording=False;m[0x799C],m[0x799D]=low,35;begin();sim.registers[PC]=0x799B
            for _ in range(12):
                if sim.registers[PC] in (0x79A6,0x3FFF):break
                sim.run()
            else:raise AssertionError('saved word instruction limit')
            flags=compare_flags(low,base);accepted=low>=base
            assert sim.registers[PC]==(0x79A6 if accepted else 0x3FFF)
            assert tuple(sim.registers[:2])==(low,flags) and sim.registers[SP]==(0xBFFE if accepted else 0xC000)
            assert not m.writes;shared();counts['all_saved_limit_low_pairs']+=1
            outcomes['saved_accepted' if accepted else 'saved_rejected']+=1
        # Проверка всех старших байтов сохранённого слова, вход в расчёт счётчика остаётся вне модели.
        for high in range(256):
            low=(base*73+high*17)&255
            m.recording=False;m[0x799C],m[0x799D]=low,high;begin();sim.registers[PC]=0x799B
            for _ in range(12):
                if sim.registers[PC] in (0x79A6,0x3FFF):break
                sim.run()
            else:raise AssertionError('saved high instruction limit')
            accepted=high==35 and low>=base
            assert sim.registers[PC]==(0x79A6 if accepted else 0x3FFF)
            assert not m.writes;shared();counts['all_saved_limit_high_pairs']+=1
        if base%64==63:print('Checked spawn gate parameters through '+str(base),flush=True)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),outcomes=dict(outcomes),
        actual_apply_parameter_set_executed=True,actual_consumers_executed=True,
        actual_stream0_executed=True,field06_duplicates_initial_limit_and_bias_base=True,
        field06_later_limit_recalculation=True,bias_saturates_at_ff=True,maximum_below_1c_preserves_limit=True,
        saved_word_requires_high_23=True,saved_low_limit_zero_accepts_all_low_bytes=True,
        all_joint_inputs_exhausted=False,full_spawn_or_body_update_executed=False,
        refresh_irq_native_execution_proved=False,assembly_executed=False)
    target=ROOT/'Tools/Disasm/Reports/ActionMutableSpawnGatesVerification.json'
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='spawn-gates-',suffix='.tmp',delete=False) as output:
        temporary=output.name;output.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,target);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
