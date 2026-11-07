"""State06, настоящий OBJECT3D, банк 3, выделение малого эффекта и возврат к State07."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckEffects import memory_image
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from CheckActionRecordIndex import add_flags
from ReferenceActionClampVectorWords import logical_flags
from ReferenceControlsPointRespawn import cp_flags,refresh


def profiles():
    for offset in range(0,256,2):
        for free in range(9):
            for ttl in (0,1,25,26,27,255):yield offset,free,ttl,offset,offset^255,None,'all_original_model_offsets'
    vectors=(0,1,255,256,32767,32768,65535,0xA55A)
    for ttl in range(256):
        for free in range(9):
            for value in vectors:yield 0,free,ttl,value,ttl,None,'all_ttl_and_vector_edges'
    for mode in range(256):
        for free in range(9):
            for flags in (0,255):yield 0,free,mode,mode*257,flags,mode,'all_forced_header_modes'
    for flags in range(256):
        for free in range(9):yield 0,free,flags,flags*257,flags,None,'all_alternate_input_flags'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[3]=bytearray(memory_image()[0xC000:]);objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();banks[4][:len(objects)]=objects
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;counts=Counter();paths=Counter();depth=0
    for offset,free,ttl,value,prime_flags,forced_mode,profile in profiles():
        memory.recording=False
        for page in range(8):memory.banks[page][:]=baseline[page]
        old=(cases%4)*8;memory.out7ffd(old);ix=0xA700;stack=0xBFFE
        vector=(value,(value*73)&65535,value^65535)
        for axis,word in enumerate(vector):memory[ix+2*axis],memory[ix+2*axis+1]=word&255,word>>8
        memory[ix+6]=offset;memory[ix+10]=6;memory[ix+17]=cases&255
        memory[0x6D39],memory[0x6D3D]=cases&255,ttl
        for row in range(8):
            for byte in range(18):memory[0xA795+18*row+byte]=(cases*37+row+byte)&255
            memory[0xA79C+18*row]=0 if row==free else 1
        memory[0xA82C]=128;memory[stack],memory[stack+1]=255,63
        pointer=memory[0x9E00+offset]+256*memory[0x9E00+((offset+1)&255)]
        if forced_mode is not None:
            assert 0xC000<=pointer<0xFFFF
            memory.banks[4][(pointer+1)&0x3FFF]=forced_mode
        def object_byte(address):
            address&=65535
            if address<0x4000:return memory.roms[1][address]
            bank=5 if address<0x8000 else 2 if address<0xC000 else 4
            return memory.banks[bank][address&0x3FFF]
        mode=object_byte(pointer+1)
        initial=get_registers({'PC':0xF6EC,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDE00|prime_flags,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        wanted=list(initial);expected=[bytearray(bank) for bank in memory.banks];writes=[]
        def put(address,byte,bank=None):
            if bank is None:bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=byte;writes.append((bank,address&0x3FFF,byte))
        def word(address,item):put(address,item&255);put(address+1,item>>8)
        # Создание эталона трёх вложенных рамок, два чтения OBJECT3D не меняют исходный BC.
        word(stack-2,0xF6F2);word(stack-4,0xAAD8);word(stack-6,0x369C)
        word(stack-4,0xAAE1);word(stack-6,0x369C)
        word(stack-2,0xF70F);word(stack-4,0x6CF6);word(stack-6,0x9ABC);word(stack-4,0x6D00)
        for address,byte in ((0xEC5A,mode),(0xEC7D,12),(0xEC79,12),(0xEC6C,13)):put(address,byte,3)
        selected=0xA795+18*free
        if free<8:
            record=[]
            for item in vector:record.extend((item&255,item>>8))
            record.extend((mode,26,0,0xD8,0,0xD8,1,13,0xC0,0,12,12))
            for index,byte in enumerate(record):put(selected+index,byte)
            wanted[16:18]=[0,0x54];effect_cost=59+7*free;path='allocated'
        else:
            wanted[16:18]=[26,prime_flags];effect_cost=17+7*8;path='full_list'
        word(stack-4,0x6D05);word(stack-6,18)
        put(0x6D39,1)
        if ttl<26:put(0x6D3D,26)
        put(ix+10,7);put(ix+17,18)
        wanted[0:8]=[max(ttl,26),cp_flags(ttl,26),0,18,0,0xC0,0xD8,0]
        for register,item in zip((22,20,18),vector):wanted[register:register+2]=[item>>8,item&255]
        wanted[10:12]=[selected>>8,selected&255]
        wanted[12],wanted[15],wanted[24]=stack+2,refresh(initial[15],83+effect_cost+2*int(ttl<26)),0x3FFF
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(1000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',offset,free,ttl))
        memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,profile,offset,free,ttl,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert memory.banks==expected and Counter(memory.writes)==Counter(writes),(cases,'RAM')
        assert trace.writes==[(0x7FFD,20),(0x7FFD,16),(0x7FFD,19),(0x7FFD,16)] and memory.o7ffd==16
        for bank,pos,_ in memory.writes:
            if bank==2 and stack-10<=pos+0x8000<stack:depth=max(depth,stack-pos-0x8000)
        counts[profile]+=1;paths[path]+=1;cases+=1
    assert cases==32256 and depth==6
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),all_original_even_model_offsets=True,
        all_256_ttl_values=True,all_256_forced_header_modes=True,all_alternate_input_flags=True,
        real_OBJECT3D_read_small_effect_bank3_and_runtime_return_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        real_four_port_writes_compared=True,maximum_additional_stack_bytes=depth,complete_external_return=True,
        bank4_unloaded_tail_fixture_fill=164,forced_header_modes_are_test_fixtures=True,
        all_input_products_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionSmallEffectStateVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
