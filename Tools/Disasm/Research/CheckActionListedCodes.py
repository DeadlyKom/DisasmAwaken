"""DDD1..DDEF, настоящий обход индексов кодов с отдельным расчётом числа M1."""
from collections import Counter
import json
import random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionVertexCodes import logic_flags
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action()
    baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory)
    counts=Counter()

    def check(indices,table,count):
        memory.recording=False
        for i,value in enumerate([0xA5]+list(indices)):memory[0x9000+i]=value
        for i,value in enumerate(table):memory[0x8E00+i]=value
        memory[0xBFFE],memory[0xBFFF]=255,63
        serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':0x9000,'DE':0x2468,'BC':count*256+0x9C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xDDD1},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        aggregate=0;aborted=False
        for consumed,index in enumerate(indices[:count or 256],1):
            value=table[(index+4)&255]
            if value==0:aborted=True;break
            aggregate|=value
        wanted=list(initial)
        wanted[0:2]=[0,0x45] if aborted else [aggregate,logic_flags(aggregate)]
        wanted[3]=aggregate
        end=0x9001+consumed;wanted[4:6]=[end>>8,end&255]
        wanted[9]=count
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        wanted[15]=refresh(initial[15],19+10*(consumed-1) if aborted else 11+10*consumed)
        expected=[bytearray(b) for b in memory.banks]
        expected[2][0x3FFC:0x3FFE]=bytes((0,0x90))
        writes=[(2,0x3FFC,0),(2,0x3FFD,0x90)]
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(2700):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError('возврат списка кодов')
        memory.recording=False
        compared=(*range(16),*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(count,consumed,aborted,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(writes)==Counter(memory.writes),'RAM'
        counts['zero_abort' if aborted else 'complete']+=1
    # Проверка всех значений счётчика, включая B=0 как 256 элементов, и каждой позиции раннего нуля.
    for count in range(256):
        indices=list(range(256))
        check(indices,[0xF0]*256,count)
        for stop in range(count or 256):
            table=[0xF0]*256;table[(stop+4)&255]=0
            check(indices,table,count)
    # Проверка всех байтов индекса и кода, включая оборачивание index+4 внутри страницы.
    for index in range(256):
        for value in range(256):
            table=[0xA5]*256;table[(index+4)&255]=value
            check([index]+[0]*255,table,1)
    rng=random.Random(0xDDD1)
    for _ in range(1024):
        check([rng.randrange(256) for _ in range(256)],[rng.randrange(256) for _ in range(256)],rng.randrange(256))
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),all_count_bytes=True,
        all_zero_positions=True,all_index_and_code_byte_pairs=True,index_plus_four_wraps_within_page=True,
        exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        nonzero_end_reject_code_not_hidden=True,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionListedCodesVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
