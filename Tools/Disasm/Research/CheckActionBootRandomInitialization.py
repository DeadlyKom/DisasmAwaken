"""Полная инициализация потоков ACTION с независимой числовой рекурсией.

Документация: ../../../Docs/ActionRandomInitialization.md
"""
from collections import Counter
from hashlib import sha256
import json

from CheckActionParameterActivation import flat_action
from CheckMapRaster import ObservedMemory
from CheckStationFlightCycle import ROOT, DISK, ENTRIES, payload
from ReferenceActionFoldedRandom import step
from ReferenceControlsPointRespawn import refresh
from ActionRandomStreamLayout import STREAMS
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, PC, SP, R, I, IM, IFF


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(DISK).hexdigest()==manifest['sha256']
    baseline=flat_action()
    baseline[0x4200:0x43FA]=payload(17)[0x43:0x23D]
    assert bytes(baseline[0x4306:0x4355])==payload(17)[0x149:0x198]
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    code={}
    for group in flow:
        for row in group['instructions']:
            pc=row['address']
            if row['slot']==17 and ((group['name']=='ActionBoot' and 0x4306<=pc<0x4355)
                    or (group['name']=='Action' and (0xEB72<=pc<0xEB79 or 0xEC08<=pc<0xEC54))):
                raw=bytes.fromhex(row['hex'])
                start=ENTRIES[17]['offset']+row['offset']
                assert DISK[start:start+len(raw)]==raw==bytes(baseline[pc:pc+len(raw)])
                assert pc not in code
                code[pc]=raw
    last_call=max(pc for pc,raw in code.items() if 0x4306<=pc<0x4355 and raw[0]==0xCD)
    destinations=(0xEBDB,0xEBFF,0xEC02,0xEC05,0xEBE1,0xEBE4,0xEBE7,0xEBEA)
    profiles=[]
    for variant in (0,1):
        for initial_r in range(256):
            memory=ObservedMemory(baseline)
            # Подготовка исходных состояний либо отдельного ненулевого профиля для проверки сохранённых FoldByte.
            if variant:
                for index,_,address in STREAMS:
                    memory[address:address+3]=[(index*37+11)&255,(index*53+19)&255,(index*29+0xA5)&255]
            stack=0xBFFE
            memory[stack:stack+2]=[255,63]
            initial=get_registers(dict(PC=0x4306,SP=stack,HL=0x1357,DE=0x2468,BC=0x369C,
                AF=0x5A5D,IX=0xABCD,IY=0x5C3A,I=initial_r,IM=initial_r%3,IFF=initial_r&1,R=initial_r,
                **{'^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210}),None,False)
            expected=list(memory)
            writes=Counter()
            def put(address,value):
                expected[address]=value
                writes[address]+=1
            def word(address,value):
                put(address,value&255)
                put(address+1,value>>8)
            # Расчёт выборки R после двух загрузок и префиксной LD A,R.
            sampled=refresh(initial_r,4)
            warm=(sampled&3)+1
            seed=0xC900+sampled
            state=dict(word=seed,fold=memory[0xEBE0])
            word(0x5CC2,0xC9F1)
            word(0xEBDE,seed)
            for _ in range(warm):
                state=step(state['word'],state['fold'])
                word(0xEBDE,state['word']);put(0xEBE0,state['fold'])
            warm_word=state['word']
            word(destinations[0],state['word'])
            for target in destinations[1:]:
                state=step(state['word'],state['fold'])
                word(0xEBDE,state['word']);put(0xEBE0,state['fold'])
                word(target,state['word'])
            put(0xAA9A,1);put(0xA8BC,0x2E)
            # Расчёт конечных слов временного стека, последние CALL и передача DE перекрывают более ранние слова.
            for address,value in ((stack-6,warm_word),(stack-4,state['word']),(stack-2,last_call+3)):
                expected[address]=value&255;expected[address+1]=value>>8
            for offset,count in ((2,warm+7),(4,warm+14),(6,2*warm)):
                writes[stack-offset]+=count;writes[stack-offset+1]+=count
            cpu=Simulator(memory)
            cpu.registers[:]=initial
            memory.writes=[];memory.recording=True
            m1=0;minimum=stack
            for _ in range(1200):
                pc=cpu.registers[PC]
                if pc==0x3FFF:
                    break
                assert pc in code and bytes(memory[pc:pc+len(code[pc])])==code[pc]
                opcode=memory[pc]
                assert opcode not in (0xDD,0xFD,0xCB)
                assert bytes(memory[pc:pc+2])!=bytes.fromhex('ed4f')
                m1+=2 if opcode==0xED else 1
                cpu.opcodes[opcode]()
                assert cpu.registers[R]==refresh(initial_r,m1)
                minimum=min(minimum,cpu.registers[SP])
            else:
                raise AssertionError(('instruction_limit',initial_r,variant))
            memory.recording=False
            r=cpu.registers
            wanted=list(initial)
            wanted[0:2]=[0x2E,state['flags']]
            wanted[2:4]=[0,initial[3]]
            wanted[6:8]=[state['word']>>8,state['word']&255]
            wanted[18:24]=[0,state['mixed_low']&255,state['word']>>8,state['word']&255,0xEB,0xDE]
            wanted[R]=refresh(initial_r,491+70*warm)
            wanted[SP],wanted[PC]=stack+2,0x3FFF
            assert all(r[i]==wanted[i] for i in (*range(25),26,27)),(initial_r,variant,[(i,r[i],wanted[i]) for i in range(28) if i!=25 and r[i]!=wanted[i]])
            assert m1==491+70*warm and minimum==stack-6
            assert list(memory)==expected,(initial_r,variant,'RAM')
            assert Counter(address for address,value in memory.writes)==writes,(initial_r,variant,'writes')
            profiles.append(dict(variant=variant,initial_R=initial_r,sampled_R=sampled,warm_calls=warm,
                total_stream0_calls=warm+7,M1=m1,final_R=r[R],final_HL=state['word'],final_F=r[1],
                minimum_SP=minimum,stream0_fold=state['fold']))
    result=dict(passed=True,original_disk_sha256=manifest['sha256'],cases=len(profiles),
        all_initial_R_bytes=True,initial_fold_profiles=['original_states','prepared_nonzero_states'],
        seed_high_byte=0xC9,R_sample_M1=4,warm_call_counts=[1,2,3,4],
        exact_M1_formula='491+70*warm_calls',M1_values=sorted({p['M1'] for p in profiles}),
        complete_register_contract_checked=True,R_checked_after_every_instruction=True,
        all_65536_memory_bytes_and_write_multiplicity_checked=True,temporary_stack_bytes=6,
        copied_low_word_destinations=list(destinations),other_stream_fold_bytes_preserved=True,
        all_24_bit_initial_states_proved=False,IRQ_executed=False,native_execution=False,assembly_executed=False,
        profiles=profiles)
    path=ROOT/'Tools/Disasm/Reports/ActionBootRandomInitializationVerification.json'
    if path.exists():
        assert json.loads(path.read_bytes())==result
    else:
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='profiles'},ensure_ascii=False))


if __name__=='__main__':
    main()
