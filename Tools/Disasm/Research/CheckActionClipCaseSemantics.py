"""Реальные ACTION-случаи против условий и числовой композиции доказанных помощников."""
from collections import Counter
import inspect,json,random,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
import CheckPreviewClipCaseSemantics as reference
from ReferenceControlsPointRespawn import cp_flags
from ReferenceActionClipping import Clipping
from InspectZ80 import decoder


def main():
    full_registers='--full-registers' in sys.argv
    # Используется общая формула произведений и пути, вертикальное правило ACTION отличается от D3D.
    text=inspect.getsource(reference.expected).replace('low<192','low<128')
    namespace=dict(reference.expected.__globals__);exec(compile(text,'<action_clip_numeric_composition>','exec'),namespace)
    expected=namespace['expected'];profile=(255,95,256,96)
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    m=RecordedBanks(banks=banks,out7ffd=16);s=Simulator(m)
    operations={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    decisions=json.loads((ROOT/'Tools/Disasm/Reports/ActionClipDecisionPaths.json').read_text('utf-8'))['cases']
    cases={(c['first'],c['second']):c for c in decisions}
    initial=get_registers({'AF':0x5A5D,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
        '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFF8},None,False)
    def classify(point):
        x,y=point;return (2 if x<0 else 1 if x>255 else 0)|(8 if y<0 else 4 if y>95 else 0)
    def packed(point,code):return b''.join((v&65535).to_bytes(2,'little') for v in point)+bytes((((code^15)<<4)|code,))
    def put(address,data):
        for i,value in enumerate(data):m[address+i]=value
    counts=Counter();coverage=set();maximum=0
    def check(first,second,seen):
        nonlocal maximum
        c0,c1=classify(first),classify(second);case=cases[c0,c1]
        for block in (0,1):
            wanted,new_seen,exit,path=expected(case,first,second,seen,block,profile)
            m.recording=False
            put(0xCF0B,packed(first,c0));put(0xCF1B,packed(second,c1));m[0xCF07]=seen;m[0xCF03]=block;m[0x9BA3]=0
            put(0x8FFF,bytes([0xA7])*258);put(0xBFF8,bytes((0x93,0xC9))*3+bytes((255,63)))
            s.registers[:]=initial;s.registers[PC]=case['entry']
            oracle=None
            if full_registers:
                oracle=Clipping(m.banks,s.registers,operations,PC,SP);oracle.run()
                m.writes=[];m.recording=True
            for _ in range(1800):
                if s.registers[PC]==0x3FFF:break
                s.run()
            else:raise AssertionError(('возврат случая',first,second,case['entry']))
            m.recording=False
            if oracle is not None:
                compared=(*range(13),14,*range(16,24),PC,26,27)
                assert all(oracle.r[i]==s.registers[i] for i in compared),(first,second,seen,block,'registers',[(i,oracle.r[i],s.registers[i]) for i in compared if oracle.r[i]!=s.registers[i]])
                assert all(a==b for a,b in zip(oracle.banks,m.banks)),(first,second,seen,block,'physical RAM')
                assert Counter(oracle.writes)==Counter(m.writes),(first,second,seen,block,'write multiplicity',Counter(oracle.writes)-Counter(m.writes),Counter(m.writes)-Counter(oracle.writes))
            size=m[0x9BA3];actual=[(m[0x9000+i],m[0x9001+i]) for i in range(0,size,2)]
            assert actual==wanted and size==2*len(wanted),(first,second,seen,block,actual,wanted)
            assert m[0xCF07]==new_seen and m[0xCF03]==block
            assert bytes(m[0xCF0B+i] for i in range(5))==packed(first,c0) and bytes(m[0xCF1B+i] for i in range(5))==packed(second,c1)
            assert m[0x8FFF]==m[0x9100]==0xA7 and all(m[0x9000+i]==0xA7 for i in range(size,256))
            registers=s.registers
            assert registers[SP]==0xC000 and registers[10:12]==initial[10:12] and registers[18:24]==initial[18:24]
            if exit=='normal':assert (registers[0],registers[1],registers[4]*256+registers[5])==(size,cp_flags(size,4),0xC993)
            else:assert (registers[0],registers[1],registers[2]*256+registers[3],registers[6]*256+registers[7])==(0xC9,0x89,0xC8,0xCA5B)
            coverage.add((c0,c1,path));counts['block_'+str(block)]+=1;counts[exit]+=1;maximum=max(maximum,len(wanted))
    # Проверка сетки граничных координат и всех младших отметок углов при двух режимах запрета.
    points=[(x,y) for x in (-256,-1,0,127,254,255,256,511) for y in (-256,-1,0,47,94,95,96,351)]
    for first in points:
        for second in points:
            for seen in range(16):check(first,second,(240 if seen&1 else 0)|seen)
    # Проверка всех старших и младших разрядов прежних отметок на представителях каждой зоны.
    representatives=[(x,y) for x in (-64,7,319) for y in (-64,11,159)]
    for first in representatives:
        for second in representatives:
            for seen in range(256):check(first,second,seen)
    rng=random.Random(0xC07B)
    for _ in range(2048):check(tuple(rng.randrange(-512,768) for _ in range(2)),tuple(rng.randrange(-512,768) for _ in range(2)),rng.randrange(256))
    missing=[dict(first=c['first'],second=c['second'],path=i,conditions=p['conditions'])
        for c in decisions for i,p in enumerate(c['paths']) if (c['first'],c['second'],i) not in coverage]
    report=dict(passed=True,total_cases=counts['block_0']+counts['block_1'],paths=dict(counts),physical_pairs=81,
        semantic_paths_executed=len(coverage),all_symbolic_paths_executed=not missing,missing_paths=missing,
        maximum_output_points=maximum,all_initial_corner_bytes_tested=True,
        real_action_helpers_and_frame_returns=True,vertical_low_byte_sign_rule_preserved=True,
        independent_geometry_proof=False,decision_paths_derived_from_original_graph=True,
        all_final_registers_except_R_proved=full_registers,all_final_registers_proved=False,
        all_physical_ram_bytes_proved=full_registers,write_multiplicity_proved=full_registers,
        refresh_and_timing_independently_checked=False,assembly_executed=False,irq_executed=False,native_execution=False)
    tag='ActionClipCaseRegistersVerification' if full_registers else 'ActionClipCaseSemanticsVerification'
    (ROOT/('Tools/Disasm/Reports/'+tag+'.json')).write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps({k:v for k,v in report.items() if k!='missing_paths'},indent=2))


if __name__=='__main__':main()
