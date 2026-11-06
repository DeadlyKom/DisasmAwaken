"""Девять настоящих табличных произведений перед группой, без подмены инструкций."""
from collections import Counter
import json
import random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator, get_registers, PC
from CheckActionRenderMatrix import OUTPUT
from PreviewModelMatrixOracle import product, square
from PreviewVertexProductsOracle import general
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh

TARGETS = (0xD69D,0xD6A0,0xD6A3,0xD69C,0xD69F,0xD6A2,0xD6E2,0xD6E1,0xD6DF)


def main():
    flat=flat_action()
    assert bytes(flat[0x9800:0x9900]) == bytes(square(i) for i in range(256))
    baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory)
    counts=Counter()

    def check(coefficients,factors,profile):
        memory.recording=False
        for address in TARGETS:
            memory[address]=flat[address]
        for row in range(3):
            for column in range(3):
                memory[OUTPUT[row][column]]=coefficients[row][column]
        serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'BC':factors[0]*256+factors[1],'DE':factors[2]*256+0xA5,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xD5F9},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        words,thirds=general(coefficients,factors)
        values=tuple(w>>8 for w in words)+tuple(w&255 for w in words)+thirds
        last,index,difference_square=product(coefficients[2][1],factors[2])
        wanted=list(initial)
        wanted[0:2]=[last,sub8_flags(square(index),difference_square)]
        wanted[5],wanted[6],wanted[7]=difference_square,0x98,index
        wanted[15]=refresh(initial[15],127)
        wanted[PC]=0xD694
        expected=[bytearray(b) for b in memory.banks]
        writes=[]
        for address,value in zip(TARGETS,values):
            expected[0][address&0x3FFF]=value
            writes.append((0,address&0x3FFF,value))
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        for _ in range(110):
            if simulator.registers[PC]==0xD694:
                break
            simulator.run()
        else:
            raise AssertionError('продолжение D694')
        memory.recording=False
        compared=(*range(16),*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(coefficients,factors,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(memory.writes)==Counter(writes),'RAM'
        counts[profile]+=1
    # Проверка всех пар байтов примитива одновременно в девяти местах с разным порядком столбцов.
    for coefficient in range(256):
        for factor in range(256):
            check(((coefficient,)*3,)*3,(factor,)*3,'all_primitive_pairs')
    # Проверка независимого назначения каждого физического коэффициента и каждого входного регистра.
    for value in range(256):
        for position in range(9):
            matrix=[[0x13,0x57,0x9B],[0x24,0x68,0xAC],[0x35,0x79,0xBD]]
            matrix[position//3][position%3]=value
            check(matrix,(0x43,0x87,0xCB),'coefficient_slices')
        for position in range(3):
            factors=[0x43,0x87,0xCB]
            factors[position]=value
            check(((0x13,0x57,0x9B),(0x24,0x68,0xAC),(0x35,0x79,0xBD)),factors,'factor_slices')
    rng=random.Random(0xD5F9)
    for _ in range(4096):
        check(tuple(tuple(rng.randrange(256) for _ in range(3)) for _ in range(3)),tuple(rng.randrange(256) for _ in range(3)),'mixed')
    report=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),
        original_square_table_verified=True,all_primitive_pairs=True,all_nine_coefficient_slices=True,all_three_factor_slices=True,
        exact_registers_flags_refresh=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        stack_untouched=True,fallthrough_D694=True,whole_group_composition_executed=False,all_joint_inputs_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionVertexProductsVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
