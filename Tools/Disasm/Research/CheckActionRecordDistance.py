"""EAE9..EB40, независимые модули обёрнутых разностей, максимум, флаги, R и стек."""
from itertools import product
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import cp_flags,refresh


class Recorded(list):
    recording=False
    def __setitem__(self,index,value):
        if self.recording:
            assert isinstance(index,int)
            self.writes.append((index,value))
        super().__setitem__(index,value)


def main():
    memory=Recorded(flat_action());simulator=Simulator(memory)
    memory[0xBFFE:0xC000]=[255,63]
    cases=0;paths=set()
    def check(differences):
        nonlocal cases
        # Расчёт трёх исходных слов и разностей второй записи с первой по модулю 65536.
        left=(0x1234,0x7FFF,0xA5A5)
        right=tuple((value+delta)&65535 for value,delta in zip(left,differences))
        for start,values in ((0xA100,left),(0xA140,right)):
            for axis,value in enumerate(values):memory[start+2*axis:start+2*axis+2]=[value&255,value>>8]
        magnitudes=tuple(((-delta)&65535) if delta&0x8000 else delta for delta in differences)
        a,b,c=(value>>8 for value in magnitudes)
        maximum_yz=max(b,c)
        result=max(a,b,c)
        negative=tuple(bool(delta&0x8000) for delta in differences)
        m1=45+7*sum(negative)+int(c<b)+2*int(maximum_yz<a)
        initial=get_registers({'PC':0xEAE9,'SP':0xBFFE,'AF':((cases*73)&255)*256+(cases&255),
            'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xA100,'IY':0xA140,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
        wanted=list(initial)
        wanted[0],wanted[1]=result,cp_flags(maximum_yz,a)
        wanted[4],wanted[5]=magnitudes[0]>>8,magnitudes[0]&255
        wanted[6],wanted[7]=magnitudes[2]>>8,magnitudes[2]&255
        wanted[15]=refresh(initial[15],m1);wanted[PC],wanted[SP]=0x3FFF,0xC000
        memory.writes=[];memory.recording=True;simulator.registers[:]=initial
        for _ in range(90):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',differences))
        memory.recording=False
        compared=(*range(24),PC,26,27)
        assert all(wanted[index]==simulator.registers[index] for index in compared),(differences,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        # Проверка всех записей модели, это четыре остаточных байта двух сохранённых модулей.
        expected_writes=[(0xBFFC,magnitudes[0]&255),(0xBFFD,magnitudes[0]>>8),
                         (0xBFFA,magnitudes[1]&255),(0xBFFB,magnitudes[1]>>8)]
        assert memory.writes==expected_writes
        assert all(memory[address]==value for address,value in expected_writes)
        assert memory[0xBFFE:0xC000]==[255,63]
        paths.add((negative,c<b,maximum_yz<a))
        cases+=1
    # Проверка полного диапазона каждой разности при двух фиксированных соседних разностях.
    others=((0,0x12FF,0xF0FF),(0x7FFF,0,0x8000),(0x0100,0x0200,0))
    for axis in range(3):
        for delta in range(65536):
            values=list(others[axis]);values[axis]=delta;check(values)
    # Проверка совместных знаков, случая 8000, границ старшего байта и равенств максимумов.
    boundaries=(0,1,255,256,0x7FFF,0x8000,0xFF00,0xFFFF,0xFE01)
    for differences in product(boundaries,repeat=3):check(differences)
    result=dict(passed=True,total_cases=cases,all_65536_differences_for_each_axis=True,
        combined_boundary_cases=729,branch_profiles=len(paths),exact_registers_flags_r_sp=True,
        all_memory_writes_compared=True,stack_bytes=4,stack_values_proved=True,
        native_memory_bus_order_proved=False,all_six_input_words_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordDistanceVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
