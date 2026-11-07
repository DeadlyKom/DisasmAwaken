"""Все 65535 допустимых геометрических квадратов, независимые bit_length/bit_count и точный R."""
import json
from collections import Counter
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionSquareRefresh import refresh_cost
from ReferenceControlsPointRespawn import refresh


def main():
    memory=flat_action();memory[0xBFFE:0xC000]=[255,63];simulator=Simulator(memory);cases=0;costs=Counter()
    for value in range(65536):
        if value==0x8000:continue
        initial=get_registers({'PC':0xC6F4,'SP':0xBFFE,'HL':value,'DE':value,'BC':0x369C,'IX':0xABCD,
            'AF':cases&65535,'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IY':0x5C3A},None,False)
        initial[15]=(value*73)&255;simulator.registers[:]=initial
        simulator.run(start=0xC6F4,stop=0x3FFF)
        cost=refresh_cost(value)
        assert simulator.registers[15]==refresh(initial[15],cost),(value,cost,initial[15],simulator.registers[15])
        assert simulator.registers[12]==0xC000 and simulator.registers[24]==0x3FFF
        costs[cost]+=1;cases+=1
    assert cases==65535
    result=dict(passed=True,total_cases=cases,all_square_arguments_except_8000=True,independent_bit_length_and_popcount_formula=True,
        exact_R_with_bit7_preserved=True,external_return_verified=True,minimum_m1=min(costs),maximum_m1=max(costs),
        arbitrary_signed_multiply_R_proved=False,argument_8000_covered=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionSquareRefreshVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
