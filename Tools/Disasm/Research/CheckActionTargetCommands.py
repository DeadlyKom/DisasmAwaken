"""72BE и 72E2, настоящий код команд и очереди, без сборки и подмен CALL."""
from collections import Counter
import argparse,json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import put
from CheckActionTextQueueCalls import Memory,Ports
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert
from CheckSignedMultiply import sbc16_flags
from CheckActionOverlayModeCommand import comparison_flags


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tractor',action='store_true');parser.add_argument('--free-flight',action='store_true');args=parser.parse_args();assert not (args.tractor and args.free_flight)
    flat=flat_action();baseline=[bytearray([0xA0+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000])
    baseline[0]=bytearray(flat[0xC000:]);baseline[1]=bytearray(base_memory()[0xC000:])
    memory=Memory(banks=[bytearray(b) for b in baseline],out7ffd=16)
    sim=Simulator(memory);ports=Ports(memory);sim.set_tracer(ports);counts=Counter()

    def check(entry,delay,request,head=0,mask=0,old_page=16,beam=0,equipment=254,limit_word=136,motion_opcode=58):
        memory.recording=False
        for bank,original in zip(memory.banks,baseline):bank[:]=original
        memory.out7ffd(old_page);memory[0xA85F]=delay;memory[0xAA8E]=request;memory[0x7318]=beam;memory[0x9C24]=equipment;memory[0x9C28]=equipment;memory[0x6E72]=motion_opcode;put(memory,0x7693,limit_word.to_bytes(2,'little'))
        put(memory,0x9B1B,[3,128,255]);put(memory,0xBFFE,[255,63])
        for i in range(16):
            memory.banks[1][0x2C80+2*i]=128 if mask&(1<<i) else 1
            memory.banks[1][0x2C81+2*i]=(i*37)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes((0,0))
        cursor=QUEUE+2*head;memory.banks[1][0x2C5D:0x2C5F]=cursor.to_bytes(2,'little')
        expected=[bytearray(b) for b in memory.banks];wanted_ports=[]
        initial=get_registers({'AF':0xA5EF,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':entry},None,False)
        serial=counts['cases'];initial[14]=serial&255;initial[26]=serial&1;initial[27]=serial%3
        wanted=list(initial);wanted[PC]=0x3FFF;wanted[SP]=0xC000
        if delay:
            wanted[0:2]=[delay,and_flags(delay)];counts['delay_exit']+=1
        elif entry in (0x7439,0x754C) and equipment==255:
            expected[2][0x285F]=20 if entry==0x754C else 10;wanted[0:2]=[0,0x50];counts['missing_equipment']+=1
        elif entry==0x754C and limit_word!=136:
            expected[2][0x285F]=20;difference=(limit_word-136)&65535
            wanted[0:2]=[(equipment+1)&255,sbc16_flags(limit_word,136,0)]
            wanted[2:4]=[0,136];wanted[6:8]=[difference>>8,difference&255];counts['limit_exit']+=1
        else:
            expected[2][0x285F]=20 if entry==0x754C else 10 if entry==0x7439 else 7;expected[0][0x2CA9:0x2CAB]=(0xEDA8).to_bytes(2,'little')
            wanted[6:8]=[0xED,0xA8]
            if entry==0x754C:
                new_opcode=201 if motion_opcode==58 else 58;expected[5][0x2E72]=new_opcode
                wanted[0:2]=[new_opcode,comparison_flags(motion_opcode,58)];wanted[2:4]=[0,136]
                messages=(0xF1E1 if motion_opcode==58 else 0xF1F0,0xF200);counts['toggle_free_flight']+=1
            elif entry==0x72BE:
                expected[2][0x1B1B:0x1B1E]=bytes((255,255,255))
                messages=(0xF354,);wanted[0:2]=[255,0x54];counts['clear_targets']+=1
            else:
                result=request^1;expected[2][0x2A8E]=result
                messages=(0xF1E1 if result else 0xF1F0,0xF214)
                if entry==0x7439:
                    new_beam=beam^1;expected[5][0x3318]=new_beam
                    expected[2][0x1B1B:0x1B1E]=bytes((255,255,255))
                    messages=(0xF1E1 if new_beam else 0xF1F0,0xF2D9)+messages
                wanted[0:2]=[result,and_flags(result)&~16];counts['toggle_request']+=1
            virtual={a:expected[1][a-0xC000] for a in range(QUEUE,QUEUE+34)}
            virtual[PRODUCER],virtual[PRODUCER+1]=cursor&255,cursor>>8
            for message in messages:
                result=insert(virtual,message);counts['accepted' if result['accepted'] else 'dropped']+=1
                for address,value in result['writes']:
                    virtual[address]=value;expected[1][address-0xC000]=value
                wanted_ports.extend(((0x7FFD,17),(0x7FFD,16)))
        sim.registers[:]=initial;memory.writes=[];memory.recording=True;ports.events=[]
        for _ in range(1500):
            if sim.registers[PC]==0x3FFF:break
            sim.run()
        else:raise AssertionError(('нет возврата',entry,delay,request,head,mask))
        memory.recording=False
        # Проверка всех архитектурных регистров кроме R и тактов, двух банковых выходов и RAM вне временного CPU-стека.
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(sim.registers[i]==wanted[i] for i in compared),[(i,sim.registers[i],wanted[i]) for i in compared if sim.registers[i]!=wanted[i]]
        assert ports.events==wanted_ports,(ports.events,wanted_ports)
        assert memory.o7ffd==(16 if wanted_ports else old_page)
        stack=[off for bank,off,value in memory.writes if bank==2 and off>=0x3FE0]
        assert all(off>=0x3FEC for off in stack)
        # Сопоставление всех банков целиком, исключаются только уже ограниченные восемнадцать временных байтов стека.
        expected[2][0x3FEC:0x3FFE]=memory.banks[2][0x3FEC:0x3FFE]
        assert memory.banks==expected,(entry,delay,request,head,mask)
        counts['cases']+=1

    # Проверка всех задержек, полных кодов оборудования и независимого переключения двух байтовых запросов.
    if args.free_flight:
        for delay in range(256):check(0x754C,delay,0)
        for equipment in range(256):check(0x754C,0,0,equipment=equipment)
        for opcode in range(256):check(0x754C,0,0,motion_opcode=opcode)
        for limit_word in range(65536):check(0x754C,0,0,limit_word=limit_word)
        for head in range(17):
            for mask in (0,65535,0xAAAA,0x5555):
                for opcode in (0,58,201,255):check(0x754C,0,0,head,mask,8*(head&3),motion_opcode=opcode)
    elif args.tractor:
        for delay in range(256):check(0x7439,delay,0)
        for equipment in range(256):check(0x7439,0,0,equipment=equipment)
        for beam in range(256):
            for request in (0,1,2,255):check(0x7439,0,request,beam=beam)
        for request in range(256):
            for beam in (0,1,2,255):check(0x7439,0,request,beam=beam)
        for head in range(17):
            for mask in (0,65535,0xAAAA,0x5555):
                for request in (0,1,2,255):
                    for beam in (0,1,2,255):check(0x7439,0,request,head,mask,8*((head+request)&3),beam=beam)
    else:
        for entry in (0x72BE,0x72E2):
            for delay in range(256):check(entry,delay,0)
            for request in range(256):check(entry,0,request)
            for head in range(17):
                for mask in (0,65535,0xAAAA,0x5555):
                    for request in (0,1,2,255):check(entry,0,request,head,mask,8*((head+request)&3))
    result=dict(passed=True,total_cases=counts['cases'],counts=dict(counts),
        real_queue_and_banking_executed=True,all_registers_except_R_and_T_checked=True,
        all_ram_except_18_byte_temporary_stack_checked=True,maximum_stack_bytes=18,
        tested_entry_instruction_bytes_preserved=True,mutable_operands_or_gates_prepared=True,entry_bank_zero_required=True,assembly_executed=False,native_execution=False)
    (ROOT/('Tools/Disasm/Reports/'+('ActionFreeFlightCommand' if args.free_flight else 'ActionTractorModeCommand' if args.tractor else 'ActionTargetCommands')+'Verification.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
