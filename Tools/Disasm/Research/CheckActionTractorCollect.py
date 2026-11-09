"""7317 до полного RET, настоящий стек в записи объекта, прицельный ребёнок и очередь."""
from collections import Counter
import argparse,json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionTextQueueCalls import Memory,Ports
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import put
from CheckMusic import Simulator,get_registers,PC
from ReferenceActionTractorCollect import TractorCollectMachine


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true');args=parser.parse_args()
    flat=flat_action();baseline=[bytearray([0xA0+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000])
    baseline[0]=bytearray(flat[0xC000:]);baseline[1]=bytearray(base_memory()[0xC000:])
    memory=Memory(banks=[bytearray(b) for b in baseline],out7ffd=16);simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports)
    counts=Counter();paths=Counter();record_stack_seen=False
    def check(mode=1,target=0,words=(0,0,0),state=4,class_code=19,kind=0,amount=1,stored=0,current=0,limit=255,
              control=None,reuse=0,head=0,mask=0,initial_r=0,phase=0,step=0):
        nonlocal record_stack_seen
        memory.recording=False
        for bank,raw in zip(memory.banks,baseline):bank[:]=raw
        memory.out7ffd(16);serial=counts['cases'];memory[0x7318]=mode;memory[0x9B1B]=target
        put(memory,0x73A4,[0x34,0x12]);put(memory,0x9BD2,[current,limit]);memory[0x9BD4+kind]=stored
        if control is not None:
            assert kind<28;memory[0x741D+kind]=control
        base=0xA100+64*target
        if target<128:
            for i,value in enumerate(words):put(memory,base+2*i,value.to_bytes(2,'little'))
            for field,value in ((10,state),(16,77),(17,amount),(18,class_code),(24,reuse),(35,kind)):memory[base+field]=value
        memory[0x63B7]=phase;memory[0x63B9]=step;memory[0xA8BC]=255;put(memory,0x9B19,[119,43]);put(memory,0xBFFE,[255,63])
        for i in range(16):
            memory.banks[1][0x2C80+2*i]=128 if mask&(1<<i) else 1;memory.banks[1][0x2C81+2*i]=(i*37)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes((0,0));memory.banks[1][0x2C5D:0x2C5F]=(0xEC80+2*head).to_bytes(2,'little')
        initial=get_registers({'PC':0x7317,'SP':0xBFFE,'AF':0xA5EF,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        initial[14]=serial&255;initial[15]=initial_r;initial[26]=serial&1;initial[27]=serial%3
        model=TractorCollectMachine(memory.banks,initial);model.collect_or_aim()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;ports.events=[]
        for _ in range(7000):
            if simulator.registers[PC]==0x3FFF:break
            if target<128 and base<=simulator.registers[12]<=base+6:record_stack_seen=True
            simulator.run()
        else:raise AssertionError(('нет возврата',mode,target,words,class_code,kind))
        memory.recording=False;compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(simulator.registers[i]==model.r[i] for i in compared),(mode,target,words,class_code,kind,amount,initial_r,model.path,[(i,simulator.registers[i],model.r[i]) for i in compared if simulator.registers[i]!=model.r[i]])
        model.banks[2][0x3FEC:0x3FFE]=memory.banks[2][0x3FEC:0x3FFE];assert memory.banks==model.banks,(mode,target,words,class_code,kind,model.path)
        outside=lambda rows:[r for r in rows if r[0]!=2 or not 0x3FEC<=r[1]<0x3FFE]
        assert Counter(outside(memory.writes))==Counter(outside(model.writes)),(mode,target,words,class_code,kind,model.path,'writes')
        assert ports.events==model.ports and memory.o7ffd==16
        paths.update(model.path);counts['cases']+=1
        if counts['cases']%65536==0:print(str(counts['cases'])+' tractor cases passed',flush=True)
    # Проверка каждой ветви перед полными доменами, включая реальные обращения к двум кодовым байтам правил 28 и 29.
    for mode in (0,1,2,255):
        for target in (0,24,127,128,255):check(mode=mode,target=target)
    for phase,step in ((0,1),(255,1),(127,128),(128,128)):
        for initial_r in (0,255):check(mode=0,phase=phase,step=step,initial_r=initial_r)
    for words in ((0x8000,0,0),(256,0,0),(0,65535,0),(0,0,0xFEFF),(0xFF00,255,0xFFFF)):
        for class_code in (0,16,19):check(words=words,class_code=class_code)
    for kind in (0,17,23,27,28,29,127,255):
        for class_code in (0,16,19):
            for reuse in (0,16,40,255):check(kind=kind,class_code=class_code,reuse=reuse,initial_r=127)
    for state in (0,3,4,255):check(state=state)
    for current,limit,amount,stored in ((0,0,1,0),(255,0,1,0),(0,255,201,0),(0,255,255,1),(17,16,0,200)):
        for control in (0,64,128,192):check(current=current,limit=limit,amount=amount,stored=stored,control=control)
    if not args.quick:
        for axis in range(3):
            for word in range(65536):
                values=[0,0,0];values[axis]=word;check(words=tuple(values))
        for stored in range(256):
            for amount in range(256):check(stored=stored,amount=amount)
        for mode in range(256):check(mode=mode)
        for target in range(256):check(target=target)
        for control in range(256):check(control=control,current=255,limit=0)
        for class_code in range(256):
            for initial_r in (0,1,127,128,255):check(class_code=class_code,initial_r=initial_r)
        for kind in range(256):check(kind=kind)
        for head in range(17):
            for mask in (0,65535,0xAAAA,0x5555):check(head=head,mask=mask,reuse=16)
    result=dict(passed=True,total_cases=counts['cases'],paths=dict(paths),quick_scope=args.quick,
        all_word_values_at_each_component=not args.quick,all_inventory_byte_amount_pairs=not args.quick,
        real_aim_child_and_queue_executed=True,delegated_aim_drawing_cases=paths['two_aim_lines'],actual_SP_in_record_observed=record_stack_seen,
        all_registers_except_R_and_T_checked=True,all_ram_and_write_multiplicity_outside_18_byte_stack_checked=True,
        R_derived_amount_checked_against_prefix_M1=True,full_joint_input_product_exhausted=False,
        assembly_executed=False,native_execution=False)
    stem='ActionTractorCollectQuickVerification' if args.quick else 'ActionTractorCollectVerification'
    (ROOT/('Tools/Disasm/Reports/'+stem+'.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='paths'},indent=2))


if __name__=='__main__':main()
