"""Все пары выбранного запаса и стоимости, затем пять позиций различия контекстов, граница 7176."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC
from CheckScreenUpdate import put
from ReferenceActionHyperJump import HyperJumpMachine


def main():
    flat=flat_action();baseline=[bytearray([160+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000]);baseline[0]=bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16);simulator=Simulator(memory);counts=Counter();paths=Counter()
    def check(preferred=255,fallback=255,cost=1,delay=0,equipment=0,context=b'ABCDE',destination=b'abcde'):
        memory.recording=False
        for bank,raw in zip(memory.banks,baseline):bank[:]=raw
        for address,value in ((0x9C10,preferred),(0x9C11,fallback),(0x9C8A,cost),(0xA85F,delay),(0x9C26,equipment)):memory[address]=value
        put(memory,0x9BC1,context);put(memory,0x9BC6,destination);put(memory,0xBFFE,[255,63])
        serial=counts['cases'];initial=get_registers({'PC':0x70F6,'SP':0xBFFE,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        initial[14]=serial&255;initial[15]=serial&255;initial[26]=serial&1;initial[27]=serial%3
        model=HyperJumpMachine(memory.banks,initial);model.request();simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(100):
            if simulator.registers[PC] in (0x7176,0x3FFF):break
            simulator.run()
        else:raise AssertionError(('граница не достигнута',serial))
        memory.recording=False;compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(simulator.registers[i]==model.r[i] for i in compared),(serial,preferred,fallback,cost,model.path,[(i,simulator.registers[i],model.r[i]) for i in compared if simulator.registers[i]!=model.r[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,model.path,'RAM')
        counts['cases']+=1;paths.update(model.path)
        if counts['cases']%65536==0:print(str(counts['cases'])+' hyper prefix cases passed',flush=True)
    # Проверка двойной стоимости Preferred и одинарной стоимости Fallback по всем байтовым парам.
    for value in range(256):
        for cost in range(256):
            check(preferred=value,cost=cost);check(preferred=0,fallback=value,cost=cost)
    for delay in range(256):check(delay=delay)
    for equipment in range(256):check(equipment=equipment)
    # Проверка каждой позиции пятибайтового контекста и расхода при полностью одинаковых контекстах.
    for position in range(5):
        for value in range(256):
            target=bytearray(b'ABCDE');target[position]=value;check(destination=target)
    result=dict(passed=True,total_cases=counts['cases'],paths=dict(paths),all_byte_stock_cost_pairs_both_routes=True,
        all_delay_equipment_bytes=True,each_context_byte_domain=True,original_compare_operand_7104=0,
        all_registers_except_R_and_T_checked=True,all_ram_and_write_multiplicity_checked=True,
        accepted_path_stops_before_message_at_7176=True,accepted_continuation_executed=False,
        original_charge_before_equal_context_return_preserved=True,full_joint_input_product_exhausted=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionHyperJumpVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
