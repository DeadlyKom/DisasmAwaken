"""ACEA, настоящие обмены слов, AF43 и восстановление SP на AD07, без подмен."""
from collections import Counter
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from CheckActionPatchedVector import INPUTS,COEFFICIENTS,OUTPUTS
from CheckActionPatchSwap import PAIRS
from ReferenceActionPatchedVector import evaluate


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter();paths=Counter();touched=set()
    def check(vector,matrix,kind):
        nonlocal touched
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=baseline[address]
        for addresses,values in zip(COEFFICIENTS,matrix):
            for address,value in zip(addresses,values):memory[address]=value
        # Создание различных старших байтов обмениваемых слов, в этом вызове потребитель префиксов не исполняется.
        for i,pair in enumerate(PAIRS):
            for side,address in enumerate(pair):memory[address+1]=(serial+i*73+side*31)&255
        old_outputs=[0x5342,0x6453,0x7564]
        for address,value in zip(OUTPUTS,old_outputs):memory[address:address+2]=[value&255,value>>8]
        stack=0xBFFE if serial&1 else 0x7FFE;memory[stack:stack+2]=[255,63]
        initial=get_registers({'AF':(serial*73)&65535,'HL':vector[0],'DE':vector[1],'BC':vector[2],
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0xACEA},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        expected=list(memory);writes=[];wanted=list(initial)
        def word(address,value):
            writes.extend([(address,value&255),(address+1,value>>8)]);expected[address:address+2]=[value&255,value>>8]
        word(stack-2,0xABCD);word(stack-4,0x5C3A)
        for address,value in zip(INPUTS,vector):word(address,value)
        word(stack-6,0xACFC)
        # Расчёт первой перестановки полных слов, низкие байты транспонируют матрицу.
        for left,right in PAIRS:
            a=expected[left]+256*expected[left+1];b=expected[right]+256*expected[right+1];word(right,a);word(left,b)
        word(0xAD08,stack-4);word(0xAFF1,0xABCD)
        result=evaluate(vector,list(map(list,zip(*matrix))),old_outputs)
        for row in result['performed']:word(OUTPUTS[row],result['outputs'][row])
        word(stack-6,0xAD0D)
        # Расчёт второй перестановки, восстанавливающей все исходные слова и старшие байты.
        for left,right in PAIRS:
            a=expected[left]+256*expected[left+1];b=expected[right]+256*expected[right+1];word(right,a);word(left,b)
        for position,value in zip((6,4,2),result['outputs']):wanted[position:position+2]=[value>>8,value&255]
        wanted[0:2]=result['af'];wanted[16:18]=result['alternate_af'];wanted[SP],wanted[PC]=stack+2,0x3FFF
        wanted[15]=refresh(initial[15],result['refresh_m1']+65)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(0xACEA,0x3FFF);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(vector,matrix,stack,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(vector,matrix,stack)
        assert min(address for address,_ in memory.writes if stack-8<=address<stack)==stack-6
        touched={address for address,_ in writes};counts[kind]+=1;paths['overflow' if result['overflow'] else 'complete']+=1
    # Проверка каждого значения третьей входной компоненты, передаваемой в BC и содержащей сохраняемый ребёнком B.
    for value in range(65536):check((0,0,value),((127,0,0),(0,127,0),(0,0,127)),'all_bc_words')
    print('All BC input words complete',flush=True)
    # Проверка каждого коэффициента каждой позиции и граничных векторов с настоящим транспонированием.
    for row in range(3):
        for column in range(3):
            for coefficient in range(256):
                matrix=[[0]*3 for _ in range(3)];matrix[row][column]=coefficient
                for word in (0,1,32767,32768,65535):check((word,word,word),matrix,'all_matrix_byte_positions')
    # Проверка смешанных векторов и матриц, включая частично изменённые выходы при переполнениях.
    generator=random.Random(0xACEA)
    for _ in range(4096):check([generator.randrange(65536) for _ in range(3)],
        [[generator.randrange(256) for _ in range(3)] for _ in range(3)],'mixed_vectors_and_matrices')
    assert paths['overflow'] and paths['complete']
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        method='wrapper_reference_with_transposed_matrix_and_checked_real_children',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        matrix_transposed_before_compute_and_restored_after=True,full_patch_words_and_prefix_bytes_restored=True,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
        sp_restored_before_second_call=True,ix_iy_restored=True,partial_outputs_returned_on_overflow=True,
        maximum_additional_stack_bytes=6,wrapper_refresh_m1=65,two_stack_fixtures=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionVectorWrapperVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
