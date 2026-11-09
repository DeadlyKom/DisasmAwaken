"""Оба физических фрагмента ускорения, настоящие освобождение, создание и 16 шагов шкалы."""
from collections import Counter
import argparse,json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC
from CheckScreenUpdate import put
from ReferenceActionBoostCommand import BoostMachine
from ActionRandomStreamLayout import STREAMS
from CheckActionPatchedVector import COEFFICIENTS


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true');args=parser.parse_args()
    flat=flat_action();baseline=[bytearray([160+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000]);baseline[0]=bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16);simulator=Simulator(memory);counts=Counter();paths=Counter();depth=0
    seed=next(p for n,_,p in STREAMS if n==8)
    def check(preferred=1,fallback=0,highs=(48,48,48),code=1,opcode=58,fast=0,slow=0,rotation=17,second=136,word=136,current=0,free=True):
        nonlocal depth
        serial=counts['cases'];memory.recording=False
        for bank,raw in zip(memory.banks,baseline):bank[:]=raw
        memory.out7ffd(16)
        put(memory,0xA100,[0,highs[0],0,highs[1],0,highs[2]]);memory[0xA112]=code
        put(memory,0xA140,[0,128 if free else 1]);memory[0xA158]=0;memory[0xA152]=23
        put(memory,0xA180,[0,1]);memory[0xA192]=20;put(memory,0xA1C0,[128,128])
        for address,value in ((0x9C10,preferred),(0x9C11,fallback),(0x6E72,opcode),(0x750D,fast),(0x7515,slow),
                              (0x752C,rotation),(0x7534,second),(0x9BD2,current),(0x6F59,serial&255)):memory[address]=value
        put(memory,0xA78F,word.to_bytes(2,'little'));put(memory,seed,(serial&65535).to_bytes(2,'little'));memory[seed+2]=(serial*73)&255
        for i,row in enumerate(COEFFICIENTS):
            for j,address in enumerate(row):memory[address]=127 if i==j else 0
        put(memory,0xBFFE,[255,63])
        initial=get_registers({'PC':0x74A3,'SP':0xBFFE,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        initial[14]=serial&255;initial[15]=serial&255;initial[26]=serial&1;initial[27]=serial%3
        model=BoostMachine(memory.banks,initial);model.boost();simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(10000):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',serial,model.path))
        memory.recording=False;compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(simulator.registers[i]==model.r[i] for i in compared),(serial,highs,code,fast,slow,model.path,[(i,simulator.registers[i],model.r[i]) for i in compared if simulator.registers[i]!=model.r[i]])
        for page,offset,_ in memory.writes:
            if page==2 and 0x3FBE<=offset<0x3FFE:depth=max(depth,0x3FFE-offset)
        model.banks[2][0x3FDE:0x3FFE]=memory.banks[2][0x3FDE:0x3FFE]
        assert memory.banks==model.banks,(serial,model.path,'RAM')
        outside=lambda rows:[r for r in rows if r[0]!=2 or not 0x3FDE<=r[1]<0x3FFE]
        assert Counter(outside(memory.writes))==Counter(outside(model.writes)),(serial,model.path,'writes')
        assert memory.o7ffd==16;paths.update(model.path);counts['cases']+=1
        if counts['cases']%16384==0:print(str(counts['cases'])+' boost cases passed',flush=True)
    # Проверка каждой ветви до полного перебора байтовых параметров, без изменения инструкций потомков.
    for preferred in (0,1,128,129,255):
        for fast,slow in ((0,0),(255,0),(255,7),(255,255)):
            for rotation,second in ((0,0),(1,0),(1,1)):
                check(preferred=preferred,fallback=1,fast=fast,slow=slow,rotation=rotation,second=second)
    for free in (False,True):check(rotation=1,second=1,free=free)
    for code in (0,16,17,18,20):
        for highs in ((0,0,0),(47,47,47),(48,0,0),(255,255,255),(128,0,0)):check(code=code,highs=highs)
    if not args.quick:
        for preferred in range(256):
            for fallback in range(256):check(preferred=preferred,fallback=fallback,rotation=0)
        for fast in range(256):
            for slow in range(8):check(fast=fast,slow=slow,rotation=0)
        for slow in range(256):check(fast=255,slow=slow,rotation=0,current=0)
        for rotation in range(256):check(rotation=rotation,second=1)
        for second in range(256):check(rotation=1,second=second)
        for code in range(256):check(code=code,highs=(0,0,0))
        for opcode in range(256):check(opcode=opcode)
        for axis in range(3):
            for high in range(256):
                values=[0,0,0];values[axis]=high;check(highs=tuple(values))
        for word in (0,1,0x0F78,0x0F80,0x0FF8,0x1000,0x7FF8,0x8000,0xFFFF):check(word=word,rotation=1,second=1)
    result=dict(passed=True,total_cases=counts['cases'],paths=dict(paths),quick_scope=args.quick,
        all_preferred_fallback_pairs=not args.quick,all_fast_counter_and_three_bit_slow_pairs=not args.quick,
        all_high_bytes_each_axis=not args.quick,all_opcode_class_rotation_bytes=not args.quick,
        real_release_search_spawn_random_transform_and_sixteen_gauge_calls_executed=True,
        all_registers_except_R_and_T_checked=True,all_ram_and_write_multiplicity_outside_32_byte_stack_checked=True,
        maximum_observed_additional_stack_bytes=depth,full_joint_input_product_exhausted=False,assembly_executed=False,native_execution=False)
    stems=('ActionBoostCommandQuickVerification',) if args.quick else ('ActionBoostCommandVerification','ActionBoostAdvanceVerification')
    for stem in stems:(ROOT/('Tools/Disasm/Reports/'+stem+'.json')).write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
