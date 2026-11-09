"""Команда 722E, настоящий E835 с проекцией, клиппингом, растеризацией и очередью."""
from collections import Counter
import json,sys
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionTextQueueCalls import Memory,Ports
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import put
from CheckMusic import Simulator,get_registers,PC
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionAntimissileCommand import AntimissileMachine
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    baseline=[bytearray([0xA0+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000]);baseline[0]=bytearray(flat[0xC000:]);baseline[1]=bytearray(base_memory()[0xC000:])
    memory=Memory(banks=[bytearray(b) for b in baseline],out7ffd=16);simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports)
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    counts=Counter();paths=Counter();depth=0
    def check(delay=0,words=(3,176,256),code=17,target=26,flags=0,prefix=0,head=0,mask=0):
        nonlocal depth
        memory.recording=False
        for bank,raw in zip(memory.banks,baseline):bank[:]=raw
        memory.out7ffd(16);serial=counts['cases'];memory[0xA85F]=delay
        # Создание разных предшественников, не подходящих по классу, цели либо признаку свободной записи.
        for i in range(prefix):
            base=0xA100+64*i
            put(memory,base,[0,128 if i%3==0 else 0]);memory[base+18]=0 if i%3==1 else 17;memory[base+15]=0
        base=0xA100+64*prefix
        put(memory,base,[0,0]);memory[base+18]=code;memory[base+15]=target;memory[base+12]=flags
        for i,value in enumerate(words):put(memory,base+26+2*i,value.to_bytes(2,'little'))
        put(memory,base+64,[128,128]);put(memory,0xBFFE,[255,63])
        for i in range(16):
            memory.banks[1][0x2C80+2*i]=128 if mask&(1<<i) else 1;memory.banks[1][0x2C81+2*i]=(i*37)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes((0,0));memory.banks[1][0x2C5D:0x2C5F]=(0xEC80+2*head).to_bytes(2,'little')
        initial=get_registers({'PC':0x722E,'SP':0xBFFE,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        initial[14]=serial&255;initial[15]=serial&255;initial[26]=serial&1;initial[27]=serial%3
        model=AntimissileMachine(memory.banks,initial);model.antimissile(ops)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;ports.events=[]
        for _ in range(30000):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',words,code,target,prefix,model.path))
        memory.recording=False;compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(simulator.registers[i]==model.r[i] for i in compared),(words,code,target,prefix,model.path,[(i,simulator.registers[i],model.r[i]) for i in compared if simulator.registers[i]!=model.r[i]])
        for page,offset,_ in memory.writes:
            if page==2 and 0x3FBE<=offset<0x3FFE:depth=max(depth,0x3FFE-offset)
        model.banks[2][0x3FDE:0x3FFE]=memory.banks[2][0x3FDE:0x3FFE]
        assert memory.banks==model.banks,(words,code,target,prefix,model.path,'RAM')
        outside=lambda rows:[r for r in rows if r[0]!=2 or not 0x3FDE<=r[1]<0x3FFE]
        assert Counter(outside(memory.writes))==Counter(outside(model.writes)),(words,code,target,prefix,model.path,'writes')
        assert ports.events==model.ports and memory.o7ffd==16
        paths.update(model.path);counts['cases']+=1
        if counts['cases']%65536==0:print(str(counts['cases'])+' antimissile cases passed',flush=True)
    # Проверка полного домена задержки, фильтров класса и цели, флагов и очереди.
    for delay in range(256):check(delay=delay)
    for code in range(256):check(code=code)
    for target in range(256):check(target=target)
    for flags in range(256):check(flags=flags)
    for prefix in range(16):check(prefix=prefix)
    for head in range(17):
        for mask in (0,65535,0xAAAA,0x5555):check(head=head,mask=mask)
    # Проверка всех слов каждого векторного среза, в том числе маркера, совместного знака и трёх переполнений.
    for axis in range(3):
        for word in range(65536):
            values=[3,176,256];values[axis]=word;check(words=tuple(values))
    result=dict(passed=True,total_cases=counts['cases'],paths=dict(paths),all_word_values_at_each_component=True,
        all_delay_class_target_flag_bytes=True,real_queue_E835_projection_clipping_renderer_executed=True,
        all_registers_except_R_and_T_checked=True,all_ram_and_write_multiplicity_outside_32_byte_stack_checked=True,
        maximum_observed_additional_stack_bytes=depth,full_joint_input_product_exhausted=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionAntimissileCommandVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
