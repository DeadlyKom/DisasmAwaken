"""Настоящий ApplyParameterSet и выбор изменяемых порогов F798/F79C без исполнения эффекта."""
from collections import Counter
import json,os,tempfile
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckIntro import ROOT
from CheckMusic import PC,SP,Simulator,get_registers
from CheckScreenUpdate import PortTrace
from PreviewEdgeRasterOracle import arithmetic


def main():
    flat=flat_action();banks=[bytearray(0x4000) for _ in range(8)]
    for bank,start in ((5,0x4000),(2,0x8000),(0,0xC000)):banks[bank][:]=bytes(flat[start:start+0x4000])
    m=RecordedBanks(banks=banks,out7ffd=16);s=Simulator(m);trace=PortTrace(s);s.set_tracer(trace)
    initial=get_registers({'SP':0xBFFE,'IX':0xA100,'IY':0x5C3A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        'AF':0xA55A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0},None,False)
    parameters=bytes(flat[0x9BA4:0x9BB3]);counts=Counter();outcomes=Counter();flags_seen=set();links_seen=set();refresh_seeds=set();m1_paths=Counter()
    def check(profile,other_limit,link_limit,linked,flags,first,second,value):
        m.recording=False
        for i,byte in enumerate(parameters):m[0x9BA4+i]=byte
        # Поле 00 меняет F79C, поле 02 меняет F798, более поздние PS1/PS2 не затрагиваются.
        m[0x9BA4],m[0x9BA6]=link_limit,other_limit
        m[0xA10B],m[0xA10C],m[0xA113]=linked,flags,value
        m[0x9C1A],m[0x9C1B]=first,second;m[0xBFFE],m[0xBFFF]=255,63
        s.registers[:]=initial;m.writes=[];m.recording=True;trace.writes=[]
        s.run(start=0xAC5D,stop=0x3FFF)
        assert s.registers[SP]==0xC000 and len(m.writes)==15
        assert m[0xF798]==other_limit and m[0xF79C]==link_limit
        assert m[0xF7A8]==30 and m[0xF7B0]==60 and m[0xF7B4]==20
        if linked!=26:limit=other_limit
        elif not flags&8:limit=link_limit
        else:limit=30 if first!=255 else 60 if second!=255 else 20
        result,expected_f=arithmetic(value,limit,True)
        s.registers[:]=initial;s.registers[PC]=0xF792;m.writes=[]
        initial_r=(value^limit^flags^linked)&255;s.registers[15]=initial_r;refresh_seeds.add(initial_r)
        # Расчёт M1 пяти путей до развилки, CALL эффекта добавляет одну выборку.
        if linked!=26:prefix_m1=9
        elif not flags&8:prefix_m1=13
        elif first!=255:prefix_m1=17
        elif second!=255:prefix_m1=21
        else:prefix_m1=22
        effect=value<limit;expected_m1=prefix_m1+int(effect);measured_m1=0
        for _ in range(32):
            if s.registers[PC] in (0xEA29,0xF7E6):break
            # Проверка выборок каждого шага, DD CB d op даёт два M1, не три.
            pc=s.registers[PC];cost=2 if m[pc] in (0xCB,0xDD,0xED,0xFD) else 1
            before_r=s.registers[15]
            s.run()
            assert s.registers[15]==(before_r&128)|((before_r+cost)&127)
            measured_m1+=cost
        else:raise AssertionError(('instruction_limit',hex(s.registers[PC])))
        r=s.registers;effect=value<limit
        context=(profile,other_limit,link_limit,linked,flags,first,second,value,limit)
        assert r[PC]==(0xEA29 if effect else 0xF7E6),context
        assert tuple(r[:2])==(result,expected_f) and r[3]==limit and r[2]==initial[2],context
        assert r[4:12]==initial[4:12] and r[16:24]==initial[16:24]
        assert r[14]==initial[14] and r[26:28]==initial[26:28]
        assert measured_m1==expected_m1,context
        assert r[15]==(initial_r&128)|((initial_r+expected_m1)&127),context
        m1_paths[str(prefix_m1)]+=1
        assert r[SP]==(0xBFFC if effect else 0xBFFE)
        if effect:
            assert bytes(m[0xBFFC:0xBFFE])==bytes([0xBF,0xF7]) and len(m.writes)==2
            assert Counter(m.writes)==Counter(((2,0x3FFC,0xBF),(2,0x3FFD,0xF7)))
        else:assert not m.writes
        assert not trace.writes and m.o7ffd==16
        m.recording=False;counts[profile]+=1;outcomes['call_effect' if effect else 'dispatch']+=1
        flags_seen.add(flags);links_seen.add(linked)
    # Независимый полный перебор порога и проверяемого байта каждого изменяемого пути.
    for limit in range(256):
        for value in range(256):
            linked=(limit+value)&255
            if linked==26:linked=27
            check('other_link_all_limit_value_pairs',limit,(limit*37+91)&255,linked,(limit*73+value*17)&255,
                  (limit*3+value)&255,(limit+value*5)&255,value)
            check('link_1a_clear_bit3_all_limit_value_pairs',(limit*73+11)&255,limit,26,((limit+value*11)&255)&247,
                  (limit+value*3)&255,(limit*5+value)&255,value)
        if limit%64==63:print('Checked mutable thresholds through '+str(limit),flush=True)
    # Проверка обхода обоих изменяемых порогов при установленном бите 3 и приоритета PS1.
    for other,base in ((0,0),(255,255),(0,255),(255,0),(17,93)):
        for first,second in ((0,0),(0,255),(255,0),(255,255)):
            for value in range(256):
                check('equipment_override',other,base,26,((other+value*7)&255)|8,first,second,value)
    assert len(flags_seen)==len(links_seen)==256
    assert refresh_seeds==set(range(256)) and set(m1_paths)=={'9','13','17','21','22'}
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),outcomes=dict(outcomes),
        all_limit_value_pairs_for_each_mutable_branch=True,all_link_and_flag_bytes_observed=True,
        actual_apply_parameter_set_executed=True,actual_consumer_gate_executed=True,
        field_00_operand=0xF79C,field_02_operand=0xF798,ps1_ps2_and_fallback_unchanged=[30,60,20],
        exact_sub_af_selected_c_registers_and_stack_checked=True,consumer_stack_write_addresses_and_values_checked=True,effect_body_executed=False,
        all_joint_inputs_exhausted=False,refresh_and_timing_proved=False,
        consumer_refresh_proved=True,consumer_m1_paths=dict(m1_paths),consumer_R_initial_values=256,
        consumer_R_bit7_preserved=True,effect_call_included_in_consumer_m1=True,
        apply_parameter_set_refresh_proved=False,effect_body_refresh_proved=False,irq_executed=False,
        assembly_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/ActionMutableEffectLimitsVerification.json'
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='effect-limits-',suffix='.tmp',delete=False) as output:
        temporary=output.name;output.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,target);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
