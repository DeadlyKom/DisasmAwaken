"""7176 до перенесённого входа 4200, настоящий текст и полные исходные циклы задержки."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionTextQueueCalls import Memory,Ports
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import put
from CheckMusic import Simulator,get_registers,PC
from ReferenceControlsTextQueue import insert
import ReferenceControlsTextDisplay as text


def main():
    flat=flat_action();baseline=[bytearray([160+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000]);baseline[0]=bytearray(flat[0xC000:]);baseline[1]=bytearray(base_memory()[0xC000:])
    profiles=[]
    # Проверка обоих исходных значений длительности, DI и подмена счётчиков ожидания отсутствуют.
    for recognition in (0,255):
        banks=[bytearray(b) for b in baseline];memory=Memory(banks=banks,out7ffd=16)
        virtual=list(flat);virtual[0xC000:]=banks[1];text.initialize(virtual);virtual[text.COLUMN]=23
        banks[1][:]=bytes(virtual[0xC000:]);memory[0x9C2A]=recognition;put(memory,0xBFFE,[255,63])
        expected=[bytearray(b) for b in banks];virtual[0x4000:0xC000]=bytes(banks[5])+bytes(banks[2])
        queued=insert({a:virtual[a] for a in range(65536)},0xF37F)
        for address,value in queued['writes']:virtual[address]=value
        events=[]
        for _ in range(256):text.consume(virtual,events)
        expected[5][:]=bytes(virtual[0x4000:0x8000]);expected[2][:]=bytes(virtual[0x8000:0xC000]);expected[1][:]=bytes(virtual[0xC000:])
        expected[5][0x1800:0x1B00]=bytes(768)
        copied=bytes(flat[0x71CB:0x722E]);assert len(copied)==99
        expected[5][0x200:0x263]=copied
        initial=get_registers({'PC':0x7176,'SP':0xBFFE,'AF':0x65A5,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports);simulator.registers[:]=initial
        memory.writes=[];memory.recording=True;consumes=0;entries=0;waits=0;rotations=0;steps=0
        while simulator.registers[PC]!=0x4200:
            pc=simulator.registers[PC];consumes+=pc==0x7186;entries+=pc==0xECA2;waits+=pc==0x719F;rotations+=pc==0x719A
            simulator.run();steps+=1
            assert steps<12000000,('граница не достигнута',hex(pc))
        memory.recording=False;outer=128 if recognition==255 else 64
        assert consumes==256 and waits==outer*255*255 and rotations==outer,(consumes,waits,rotations)
        assert ports.events==[(0x7FFD,17),(0x7FFD,16),(0x7FFD,17),(0x7FFD,31)] and memory.o7ffd==31
        # Проверка всей RAM кроме обычного временного стека и двух байтов SavedSP настоящей прокрутки.
        expected[2][0x3FBE:0x3FFE]=banks[2][0x3FBE:0x3FFE]
        expected[1][0x2FC1:0x2FC3]=banks[1][0x2FC1:0x2FC3]
        assert banks==expected,[(p,next((i for i,(a,b) in enumerate(zip(banks[p],expected[p])) if a!=b),None)) for p in range(8) if banks[p]!=expected[p]]
        r=simulator.registers
        assert r[0]==31 and r[2:8]==[0,0,0x42,0x63,0x72,0x2E] and r[8:13]==initial[8:13]
        assert r[14]==initial[14] and r[26:28]==initial[26:28]
        profiles.append(dict(recognition=recognition,consumer_calls=consumes,consumer_entries_including_CR_restarts=entries,wait_outer=rotations,wait_DJNZ_executions=waits,
            text_glyphs=sum(e[0]=='glyph' for e in events),text_scrolls=sum(e[0]=='scroll' for e in events),instructions=steps))
        print('hyper preparation profile passed '+str(recognition),flush=True)
    result=dict(passed=True,total_cases=len(profiles),profiles=profiles,actual_text_queue_and_renderer_executed=True,
        all_original_delay_instructions_executed=True,no_counter_patching=True,copied_bytes=99,relay_code_bytes=90,file_key_bytes=9,
        all_eight_banks_compared_except_64_stack_bytes_and_scroll_saved_SP=True,
        final_A_HL_DE_BC_IX_IY_SP_I_IM_IFF_checked=True,full_text_registers_R_T_and_write_multiplicity_checked=False,
        stopped_before_copied_relay_entry=True,TRDOS_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionHyperJumpPreparationVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
