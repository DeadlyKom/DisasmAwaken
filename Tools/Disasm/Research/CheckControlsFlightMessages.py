"""Все 29 строк через действительную очередь и потребитель, колонки и курсоры кольца."""
import json
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory,payload
from CheckActionTextQueueCalls import Memory
from CheckMusic import Simulator,get_registers,PC
from CheckScreenUpdate import put
from ReferenceControlsTextQueue import insert
import ReferenceControlsTextDisplay as text
import ControlsFlightMessages as facts


def main():
    source=payload(23);assert len(source)==facts.END
    rows=facts.records(source);baseline=[bytearray([160+i]*16384) for i in range(8)]
    baseline[1]=bytearray(base_memory()[0xC000:]);memory=Memory(banks=[bytearray(b) for b in baseline],out7ffd=17);simulator=Simulator(memory)
    cases=0;glyphs=scrolls=0
    # Проверка каждого текста на трёх границах колонки и всех семнадцати возможных положениях курсора записи.
    for row in rows:
        for column in (0,23,255):
            for head in range(17):
                memory.recording=False
                for bank,raw in zip(memory.banks,baseline):bank[:]=raw
                virtual=[0]*65536;virtual[0x4000:0x8000]=memory.banks[5];virtual[0x8000:0xC000]=memory.banks[2];virtual[0xC000:]=memory.banks[1]
                text.initialize(virtual);virtual[text.COLUMN]=column;text.put_word(virtual,0xEC5D,0xEC80+2*head)
                queued=insert(virtual,row['address']);assert queued['accepted']
                for address,value in queued['writes']:virtual[address]=value
                text.put_word(virtual,text.READER,queued['writes'][0][0]-2)
                memory.banks[1][:]=bytes(virtual[0xC000:]);expected=list(virtual);events=[];calls=0
                while True:
                    text.consume(expected,events);calls+=1
                    put(memory,0xBFFE,[255,63]);initial=get_registers({'PC':0xECA2,'SP':0xBFFE,'AF':cases&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A},None,False)
                    simulator.registers[:]=initial
                    for _ in range(30000):
                        if simulator.registers[PC]==0x3FFF:break
                        simulator.run()
                    else:raise AssertionError((row['name'],'нет возврата'))
                    assert simulator.registers[8:12]==initial[8:12]
                    if text.word(expected,text.ACTIVE)==0:break
                    assert calls<128
                expected_banks=[bytearray(b) for b in baseline];expected_banks[5][:]=bytes(expected[0x4000:0x8000]);expected_banks[2][:]=bytes(expected[0x8000:0xC000]);expected_banks[1][:]=bytes(expected[0xC000:])
                expected_banks[2][0x3FBE:]=memory.banks[2][0x3FBE:];expected_banks[1][0x2FC1:0x2FC3]=memory.banks[1][0x2FC1:0x2FC3]
                assert memory.banks==expected_banks,(row['name'],column,head)
                rendered=sum(e[0]=='glyph' for e in events)
                assert rendered==sum(value not in (10,13) for value in row['raw']),(row['name'],head,'текст не прочитан полностью')
                cases+=1;glyphs+=rendered;scrolls+=sum(e[0]=='scroll' for e in events)
    result=dict(passed=True,total_cases=cases,strings=29,classified_logical_bytes=facts.END-facts.START,
        all_write_cursor_positions=True,column_boundaries=[0,23,255],real_consumer_glyphs_scroll_executed=True,
        glyph_events=glyphs,scroll_events=scrolls,all_eight_banks_except_stack_66_and_scroll_saved_SP_compared=True,
        IX_IY_preserved=True,exact_registers_R_T_and_write_multiplicity_proved=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsFlightMessagesVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
