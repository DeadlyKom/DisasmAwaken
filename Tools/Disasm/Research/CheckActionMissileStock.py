"""70ED выбирает байт остатка ракет и его адрес, сообщения подтверждаются в Controls банка 1."""
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags
from ReferenceControlsPointRespawn import refresh


def main():
    memory=Memory(flat_action());simulator=Simulator(memory)
    memory[0xBFFE:0xC000]=[0xFF,0x3F]
    counts={'preferred':0,'fallback':0}
    for preferred in range(256):
        for fallback in range(256):
            memory.recording=False;memory[0x9C12:0x9C14]=[fallback,preferred]
            initial=get_registers({'AF':(preferred<<8)|fallback,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
                'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x70ED},None,False)
            initial[14],initial[15],initial[26],initial[27]=preferred,fallback,preferred&1,fallback%3
            wanted=list(initial)
            wanted[0:2]=[preferred if preferred else fallback,and_flags(preferred)]
            wanted[6:8]=[0x9C,0x13 if preferred else 0x12]
            wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],4 if preferred else 7)
            before=list(memory);simulator.registers[:]=initial;memory.writes=[];memory.recording=True
            for _ in range(9):
                if simulator.registers[PC]==0x3FFF:break
                simulator.run()
            else:raise AssertionError(('возврат',preferred,fallback))
            memory.recording=False
            compared=(*range(13),14,15,*range(16,24),PC,26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(preferred,fallback)
            assert memory==before and memory.writes==[]
            counts['preferred' if preferred else 'fallback']+=1
    # Проверка текстовых свидетельств в банке Controls, верхний банк ACTION здесь не используется.
    controls=base_memory();texts={}
    for address,expected in ((0xF26D,'Осталось '),(0xF277,' ракет.\r'),(0xF280,'Ракеты исчерпаны.\r'),(0xF2E9,'Ракета ушла.\r')):
        raw=bytes(controls[address:]).split(b'\x0A',1)[0]
        assert raw.decode('cp866')==expected,(hex(address),raw)
        texts[format(address,'04X')]=dict(bank=1,encoding='cp866',text=expected,hex=raw.hex())
    report=dict(passed=True,total_cases=sum(counts.values()),cases_by_path=counts,
        all_input_byte_pairs=True,exact_registers_flags_refresh_sp=True,
        every_ram_byte_checked=True,no_memory_or_stack_writes=True,
        physical_field_order=['Fallback','Preferred'],returned_pointer_selects_source=True,
        flags_describe_preferred_not_fallback=True,stock_role_source='calls at 70AC and 70DE, decrement at 70C6, queued fragments in bank 1',
        text_evidence=texts,subtype_meaning_of_two_counters_proved=False,
        caller_handlers_executed=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileStockVerification.json').write_bytes(
        (json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({k:v for k,v in report.items() if k!='text_evidence'},indent=2))


if __name__=='__main__':main()
