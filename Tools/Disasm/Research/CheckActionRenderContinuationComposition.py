"""Стыки E4DB, реальные подготовители в эталоне, независимая маршрутизация и числовые рисователи."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from CheckActionRenderMatrix import SCENE
from ReferenceActionPacketRenderer import PacketRenderer
from CheckActionVertexCodes import logic_flags
from InspectZ80 import decoder


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();base[4][:len(objects)]=objects
    ops={i.address:dict(operation=i.operation,hex=i.bytes.hex()) for i in decoder(flat).disassemble(0xC07A,0xC477,'h')}
    actual=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);sim=Simulator(actual)
    counts=Counter();events=Counter()

    def check(index,mode,phases,bases):
        for bank in range(8):actual.banks[bank][:]=base[bank]
        actual.recording=False;actual.out7ffd(16)
        actual[0x9B8D],actual[0x9B8E]=mode,index
        for i,value in enumerate(phases):actual[0x9B12+i]=value
        for row in range(3):
            for column in range(3):actual[SCENE[row][column]]=127 if row==column else 0
        for address,value in zip((0xD7A2,0xD7C4,0xD9B6),bases):
            actual[address],actual[address+1]=value&255,(value>>8)&255
        actual[0x8F00]=1 if counts.total()&1 else 14
        actual[0xBFFC],actual[0xBFFD]=0,0x8F
        actual[0xBFFE],actual[0xBFFF]=255,63
        initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFC,'PC':0xE4DB},None,False)
        expected=RecordedBanks(banks=[bytearray(b) for b in actual.banks],out7ffd=16)
        reference=Simulator(expected);reference.registers[:]=initial
        expected_trace=PortTrace(reference);reference.set_tracer(expected_trace)
        expected.writes=[];expected.recording=True
        # Композиция проверенных подготовителей, каждый вызывается с настоящим внешним словом возврата.
        for entry,return_pc in ((0xC99B,0xE4DE),(0xCB23,0xE4E1),(0xD5C9,0xE4E4),(0xDEF3,0xE4E7)):
            reference.registers[SP]-=2;stack=reference.registers[SP]
            expected[stack],expected[stack+1]=return_pc&255,return_pc>>8
            reference.registers[PC]=entry
            for _ in range(200000):
                if reference.registers[PC]==return_pc:break
                reference.run()
            else:raise AssertionError(('подготовитель',index,hex(entry)))
        expected.recording=False;r=list(reference.registers);banks=expected.banks;writes=list(expected.writes)
        # Проверка трёх отказов/выборов по точному выходу ClassifyProjectedVertices.
        if r[1]&64:
            path='projection_reject'
        else:
            r[2]=r[0];upper=(~r[0])&240;r[0:2]=[upper,logic_flags(upper)|16]
            if upper:
                path='common_outside'
            else:
                lower=r[2]&15;r[0:2]=[lower,logic_flags(lower)|16]
                path='clipped' if lower else 'inside'
                renderer=PacketRenderer(banks,r,ops,PC,SP)
                renderer.push(0xE4FD if lower else 0xE4F7);renderer.render(clipped=bool(lower))
                r,banks=renderer.r,renderer.banks;writes+=renderer.writes;events.update(renderer.events)
        # Восстановление сохранённого узла и чтение его фактического Next, включая возможные изменения RAM детьми.
        stack=r[SP];pointer=banks[2][stack&0x3FFF]+256*banks[2][(stack+1)&0x3FFF]
        r[6:8]=[pointer>>8,pointer&255];r[SP]+=2
        r[0]=banks[2][pointer&0x3FFF];r[PC]=0xE4FF
        sim.registers[:]=initial;trace=PortTrace(sim);sim.set_tracer(trace)
        actual.writes=[];actual.recording=True
        for _ in range(500000):
            if sim.registers[PC]==0xE4FF:break
            sim.run()
        else:raise AssertionError(('продолжение',index,mode,phases,bases))
        actual.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(r[i]==sim.registers[i] for i in compared),(index,mode,phases,bases,path,[(i,r[i],sim.registers[i]) for i in compared if r[i]!=sim.registers[i]])
        assert all(a==b for a,b in zip(banks,actual.banks)),(index,mode,phases,bases,path,'RAM')
        assert Counter(writes)==Counter(actual.writes),(index,path,'writes',Counter(writes)-Counter(actual.writes),Counter(actual.writes)-Counter(writes))
        assert trace.writes==expected_trace.writes==[(0x7FFD,20),(0x7FFD,16)] and actual.o7ffd==16
        counts[path]+=1

    for index in range(0,256,2):
        for mode,phases in ((1,(0,0,0)),(1,(0,64,0)),(0,(13,37,91))):
            for bases in ((4096,0,0),(0,0,0),(1024,1024,0),(4096,2048,0),(4096,0,1024)):
                check(index,mode,phases,bases)
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),renderer_child_calls=dict(events),
        all_128_original_even_model_indices=True,original_OBJECT3D_bank4_used=True,
        four_preparatory_children_execute_in_expected_model=True,independent_preparation_math=False,
        numeric_renderer_oracles=True,independent_dispatch_flags_stack_and_Next=True,
        all_physical_ram_bytes_and_write_multiplicity_checked=True,exact_registers_flags_except_R=True,
        real_paging_two_out_values_checked=True,stop=0xE4FF,
        subsequent_queue_selection_executed=False,all_scene_matrices_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRenderContinuationCompositionVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
