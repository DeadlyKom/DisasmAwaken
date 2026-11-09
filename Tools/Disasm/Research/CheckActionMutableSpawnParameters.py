"""Реальный писатель параметров и два потребителя изменяемых полей новой записи."""
from collections import Counter
import json,os,tempfile
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckIntro import ROOT
from CheckMusic import PC,SP,Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionFoldedRandom import step


def main():
    flat=flat_action();banks=[bytearray(0x4000) for _ in range(8)]
    for bank,start in ((5,0x4000),(2,0x8000),(0,0xC000)):banks[bank][:]=bytes(flat[start:start+0x4000])
    memory=RecordedBanks(banks=banks,out7ffd=16);sim=Simulator(memory)
    trace=PortTrace(sim);sim.set_tracer(trace)
    initial=get_registers({'SP':0xBFFE,'IX':0xA100,'IY':0x5C3A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        'AF':0xA55A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0},None,False)
    seeds={}
    # Поиск реальных состояний потока 13 для каждого младшего выходного байта.
    for seed in range(65536):
        result=step(seed,0)
        seeds.setdefault(result['word']&255,(seed,result))
        if len(seeds)==256:break
    assert len(seeds)==256
    counts=Counter();branches=Counter();seen_field11=set();seen_candidates=set()
    original=bytes((i*37+11)&255 for i in range(64))
    parameters=bytes(flat[0x9BA4:0x9BB3])

    def check(profile,cap,mask,low,field11):
        memory.recording=False
        for index,byte in enumerate(parameters):memory[0x9BA4+index]=byte
        memory[0x9BB0],memory[0x9BB1],memory[0x9BB2]=mask,cap,field11
        memory[0xBFFE],memory[0xBFFF]=255,63
        sim.registers[:]=initial;sim.run(start=0xAC5D,stop=0x3FFF)
        assert (memory[0x7E07],memory[0x7E09],memory[0x7DE4])==(mask,cap,field11)
        random12=step((cap*257+mask*73+low*19)&65535,field11)
        seed12=(cap*257+mask*73+low*19)&65535
        seed13,random13=seeds[low]
        seed2=(mask*281+low*47)&65535;fold2=cap^field11;random2=step(seed2,fold2)
        stream3=((cap*211+mask*97+low)&65535).to_bytes(2,'little')
        candidate=low|mask
        value=candidate if candidate<cap else (cap-1)&255
        for name,start,stop in (('finish',0x7DD8,0x7E18),('alternate',0x7A51,0x7A99)):
            memory.recording=False
            for offset,byte in enumerate(original):memory[0xA100+offset]=byte
            for address,seed,fold in ((0xEBF0,seed12,field11),(0xEBF3,seed13,0),(0xEBEA,seed2,fold2)):
                memory[address],memory[address+1],memory[address+2]=seed&255,seed>>8,fold
            memory[0xEBDB],memory[0xEBDC],memory[0xEBDD]=*stream3,255
            expected=bytearray(original)
            expected[11],expected[12],expected[20],expected[21]=255,0,0,255
            expected[13:15]=stream3;expected[17],expected[19]=field11,value
            if name=='finish':expected[34]=(random13['word']>>8)|160
            else:expected[18]=0
            sim.registers[:]=initial;memory.writes=[];memory.recording=True;trace.writes=[]
            sim.run(start=start,stop=stop)
            context=(name,profile,cap,mask,low,field11)
            assert sim.registers[PC]==stop and sim.registers[SP]==0xBFFE,context
            assert bytes(memory[0xA100:0xA140])==expected,context
            for address,result in ((0xEBF0,random12),(0xEBF3,random13),(0xEBEA,random2)):
                expected_state=result['word'].to_bytes(2,'little')+bytes((result['fold'],))
                if address==0xEBEA and name=='finish':expected_state=seed2.to_bytes(2,'little')+bytes((fold2,))
                assert bytes(memory[address:address+3])==expected_state,context
            assert bytes(memory[0xEBDB:0xEBDE])==stream3+bytes((255,)),context
            assert memory.o7ffd==16 and not trace.writes,context
            counts[name+'_'+profile]+=1;branches['candidate' if candidate<cap else 'cap_minus_one']+=1
        seen_field11.add(field11);seen_candidates.add((cap,candidate))

    # Полный перебор cap и кандидата при маске 00, оба реальных потребителя.
    for cap in range(256):
        for low in range(256):check('all_cap_candidate_pairs',cap,0,low,(cap*73+low*17)&255)
        if cap%64==63:print('Checked spawn caps through '+str(cap),flush=True)
    # Полный перебор маски и случайного младшего байта при нескольких граничных cap и иных значениях.
    for mask in range(256):
        for low in range(256):
            cap=(0,1,255,(mask*73+low*17)&255)[low&3]
            check('all_mask_random_low_pairs',cap,mask,low,(mask*31+low*19)&255)
    assert len(seen_field11)==256 and len(seen_candidates)==65536
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),branches=dict(branches),
        actual_apply_parameter_set_executed=True,both_actual_consumers_executed=True,
        actual_random_streams_executed=True,all_cap_candidate_pairs=True,all_mask_random_low_pairs=True,
        all_field11_bytes_observed=True,whole_64_byte_record_compared=True,cap_zero_produces_ff=True,
        field11_random_masks_disjoint=True,initial_operands=[50,100,32],
        boundary='FinishSpawnRecord 7DD8..7E18 and SpawnAlternate 7A51..7A99, stop before class overrides and later fields',
        full_spawn_executed=False,all_joint_inputs_exhausted=False,exact_refresh_and_flags_proved=False,
        irq_executed=False,assembly_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/ActionMutableSpawnParametersVerification.json'
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='spawn-parameters-',suffix='.tmp',delete=False) as output:
        temporary=output.name;output.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,target);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
