"""6417, реальный поиск, коды из сохранённого HL и все исходы изменения списка A01C."""
from collections import Counter
import argparse,json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionClass19Spawn import Class19Machine


def profiles():
    for reuse in range(256):
        for r in range(256):yield reuse,r,(reuse+r)%4,(reuse+r)%6,(reuse*73+r)&255,None,'all_reuse_and_R_bytes'
    for rate in range(256):
        for r in (0,1,31,63,127,128,254,255):
            for reuse in (1,3):
                for style in range(6):yield reuse,r,1,style,rate,None,'all_rate_bytes_and_list_styles'
    for value in range(256):
        for r in (0,1,31,63,127,128,254,255):yield 1,r,1,0,(value*73)&255,value,'all_list_head_bytes'


def prepared_profiles():
    for kind in range(256):
        for quantity in range(256):yield kind,0,1,1,quantity,None,'all_kind_quantity_pairs_H_zero'
    for high in range(256):
        for kind in (0,4,5,26,27,127,128,255):
            for quantity in (0,1,8,255):
                for free in (0,2):yield kind,high,free,(kind+quantity)%6,quantity,None,'all_H_and_kind_quantity_edges'
    for kind in (0,4,5,26,27,127,128,255):
        for quantity in (0,1,8,255):
            for high in (0,238,255):
                for style in range(6):yield kind,high,1,style,quantity,None,'caller_H_and_list_styles'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepared',action='store_true');args=parser.parse_args()
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    simulator=Simulator(memory);cases=0;paths=Counter();counts=Counter();depth=0;inserted_fe=0
    for reuse,r,free_style,list_style,rate,head,profile in (prepared_profiles() if args.prepared else profiles()):
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        for row in range(25):
            address=0xA100+64*row;memory[address],memory[address+1],memory[address+24]=0,1,0
        if free_style:
            memory[0xA101]=128
            if free_style==2:memory[0xA118],memory[0xA141]=255,128
        memory[0xA740],memory[0xA741]=128,128
        lists=((254,),(255,254),(1,255,254),(0,1,254),(254,255,254),(254,))
        items=(head,254) if head is not None else lists[list_style]
        for index,value in enumerate(items):memory[0xA01C+index]=value
        ix=0xA700;components=(0x7FFF if cases&1 else 0x1234,0x8000,0xFFFF)
        for axis,value in enumerate(components):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
        for offset,value in ((7,r),(8,reuse),(9,rate),(16,rate),(24,reuse)):memory[ix+offset]=value
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0x6417,'SP':stack,'AF':(cases*109)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':(cases*73)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,r,cases&1,cases%3
        if args.prepared:
            initial[24]=0x6441;initial[6:8]=[r,reuse];initial[0]=rate
        model=Class19Machine(memory.banks,initial);model.class19_spawn(prepared=args.prepared)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(2500):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',reuse,r,list_style))
        memory.recording=False
        assert all(model.r[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,profile,model.path,[(i,model.r[i],simulator.registers[i]) for i in (*range(25),26,27) if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(cases,'RAM')
        for bank,pos,value in memory.writes:
            if bank==2 and stack-6<=pos+0x8000<stack:depth=max(depth,stack-pos-0x8000)
            if bank==2 and 0x201C<=pos<0x2028 and value==254:inserted_fe+=1
        counts[profile]+=1;paths.update(model.path);cases+=1
        if cases%32768==0:print(str(cases)+' class19 spawn cases passed',flush=True)
    assert cases==(82496 if args.prepared else 92160) and depth==2 and inserted_fe and paths['packed_HL_differs_from_child']
    result=dict(passed=True,total_cases=cases,profiles=dict(counts),paths=dict(paths),inserted_FE_writes=inserted_fe,
        all_reuse_and_initial_R_products=not args.prepared,all_rate_and_list_head_bytes=not args.prepared,
        prepared_entry_6441_executed=args.prepared,all_kind_quantity_pairs_H_zero=args.prepared,
        generated_list_code_from_packed_HL_not_allocated_IY=True,real_search_and_both_index_conversions_executed=True,
        exact_registers_flags_r_sp=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        maximum_additional_stack_bytes=depth,complete_external_return=True,all_input_products_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/('Tools/Disasm/Reports/'+('ActionPreparedClass19Spawn' if args.prepared else 'ActionClass19Spawn')+'Verification.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='paths'},indent=2))


if __name__=='__main__':main()
