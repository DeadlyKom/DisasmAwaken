"""F36B, полный перебор передачи каждого слова и композиция с настоящей геометрией и шагом."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionHalfDeltaCodes import evaluate as geometry
from ReferenceActionRecordCodeStep import apply_codes


class NoWrites(list):
    recording=False
    def __setitem__(self,index,value):
        assert not self.recording,('неожиданная запись параметрического участка',index)
        super().__setitem__(index,value)


def arguments(registers,current,target):
    result=list(registers)
    for index,value in ((6,target[0]),(4,current[0]),(2,current[1]),
                        (22,target[1]),(20,target[2]),(18,current[2])):
        result[index:index+2]=[value>>8,value&255]
    result[15]=refresh(result[15],27);result[PC]=0x6265
    return result


def main():
    flat=flat_action();memory=NoWrites(flat);simulator=Simulator(memory);stage_cases=0
    standard=(0x1111,0x2222,0x3333,0x4444,0x5555,0x6666)
    # Проверка всех 65536 значений каждого из шести прочитанных слов до входа StepRecordTargetCodes.
    for position in range(6):
        for word in range(65536):
            values=list(standard);values[position]=word;current,target=values[:3],values[3:]
            for start,words in ((0xA100,current),(0xA140,target)):
                for axis,value in enumerate(words):memory[start+2*axis:start+2*axis+2]=[value&255,value>>8]
            initial=get_registers({'PC':0xF36B,'SP':0xBFFE,'AF':word,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':0xABCD,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0xA140},None,False)
            initial[14],initial[15],initial[26],initial[27]=word&255,(word*17)&255,word&1,word%3
            wanted=arguments(initial,current,target)
            memory.recording=True;simulator.registers[:]=initial
            for _ in range(20):
                if simulator.registers[PC]==0x6265:break
                simulator.run()
            else:raise AssertionError('не достигнут вход геометрии')
            memory.recording=False
            assert all(wanted[index]==simulator.registers[index] for index in (*range(25),26,27))
            stage_cases+=1
    # Подготовка восьми физических банков и исходных таблиц числовых дочерних процедур.
    flat=flat_action();flat[0x9100:0x9200]=[value&255 for value in LOG]
    flat[0x9200:0x9300]=[value>>8 for value in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in banks]
    ratio_table=bytes(flat[0x9A00:0x9B00]);root_table=bytes(banks[1][:768])
    simulator=Simulator(memory);paths=Counter();composed=0
    for serial in range(512):
        memory.recording=False
        for bank in range(8):memory.banks[bank][:]=baseline[bank]
        old=(serial%4)*8;memory.out7ffd(old);stack=0xBFFE
        current=tuple(((serial+1)*(index*7919+32767))&65535 for index in range(3))
        target=tuple(((serial+37)*(index*12347+257))&65535 for index in range(3))
        columns=((serial*73)&255,(serial*109)&255);rate=(0,1,2,3,127,128,255)[serial%7]
        for start,words in ((0xA100,current),(0xA140,target)):
            for axis,value in enumerate(words):memory[start+2*axis],memory[start+2*axis+1]=value&255,value>>8
        memory[0xA108],memory[0xA109],memory[0xA125]=*columns,rate
        memory[stack],memory[stack+1]=255,63
        expected=[bytearray(bank) for bank in memory.banks]
        initial=get_registers({'PC':0xF36B,'SP':stack,'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':(serial*109)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0xA140},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,(serial*17)&255,serial&1,serial%3
        child=arguments(initial,current,target);child[SP]-=2;child[PC]=0xAD5A
        calculated=geometry(child,ratio_table,root_table,return_address=0x6268)
        local=apply_codes(calculated['registers'],*columns,rate)
        operations=[(stack-2,0x68),(stack-1,0x62)]+calculated['writes']+local['writes']
        writes=[]
        for address,value in operations:
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True
        simulator.run(start=0xF36B,stop=0x3FFF)
        memory.recording=False
        wanted=local['registers']
        assert all(wanted[index]==simulator.registers[index] for index in (*range(15),*range(16,25),26,27))
        assert memory.banks==expected and Counter(memory.writes)==Counter(writes)
        assert trace.writes==calculated['ports'] and memory.o7ffd==16
        paths['first_written' if local['first_written'] else 'first_skipped']+=1
        paths['second_written' if local['second_written'] else 'second_skipped']+=1
        composed+=1
    result=dict(passed=True,total_cases=stage_cases+composed,parameter_cases=stage_cases,composed_cases=composed,
        all_65536_values_each_of_six_input_words_at_boundary=True,parameter_registers_flags_r_exact=True,
        parameter_ram_writes_rejected=True,parameter_m1=27,actual_geometry_root_ratio_and_step_executed=True,
        independent_existing_child_models_composed=True,composed_registers_except_r_exact=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,paths=dict(paths),
        full_composed_r_proved=False,complete_six_word_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionSelectedRecordStepVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
