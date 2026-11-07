"""617D, реальные дочерние процедуры без сборки, полные банки и кратность записей."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionClass20Spawn import Class20Machine
from ActionRandomStreamLayout import STREAMS
from CheckActionPatchedVector import COEFFICIENTS
from ReferenceActionFoldedRandom import step


def main():
    flat=flat_action();banks=[bytearray([160+i]*16384) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks]
    simulator=Simulator(memory);paths=Counter();total=0;maximum_stack=0
    seed_pointer=next(p for n,_,p in STREAMS if n==8)
    # Проверка всех слов состояния потока с разными свёртками, режимами и местами выделения.
    for serial in range(66560):
        memory.recording=False
        for b in range(8):memory.banks[b][:]=baseline[b]
        slot=serial%26
        for index in range(25):
            address=0xA100+64*index
            memory[address],memory[address+1],memory[address+24]=index,1,serial&255
        if slot<25:
            address=0xA100+64*slot
            memory[address],memory[address+1],memory[address+24]=0,128,0
        memory[0xA740],memory[0xA741]=128,128
        seed=serial&65535
        memory[seed_pointer],memory[seed_pointer+1],memory[seed_pointer+2]=seed&255,seed>>8,(serial*73)&255
        memory[0x6E75]=(0,1,128,255)[serial%4]
        # Создание как полной, так и переполняющейся матрицы, без изменения её размещения.
        for row in range(3):
            for column in range(3):
                memory[COEFFICIENTS[row][column]]=((127 if row==column else 0) if serial&1 else (serial+row*71+column*37)&255)
        if serial>=65536:
            # Проверка сумм одного знака у границы переполнения, без обхода реального генератора.
            random_word=step(seed,(serial*73)&255)['word']
            signs=(bool(random_word&128),bool(random_word&32768),bool(memory[0x6E75]))
            for row in COEFFICIENTS:
                for address,negative in zip(row,signs):memory[address]=129 if negative else 127
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0x617D,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,(serial*17)&255,serial&1,serial%3
        model=Class20Machine(memory.banks,initial);model.spawn20()
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True;simulator.run(start=0x617D,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM')
        assert not trace.writes and memory.o7ffd==16
        for bank,offset,_ in memory.writes:
            if bank==2 and stack-32<=offset+0x8000<stack:maximum_stack=max(maximum_stack,stack-offset-0x8000)
        paths.update(model.path);total+=1
        if total%16384==0:print(str(total)+' class20 cases passed',flush=True)
    assert paths['transform_overflow'] and paths['transform_complete'] and paths['no_free_record'],dict(paths)
    result=dict(passed=True,total_cases=total,paths=dict(paths),all_seed_words=True,
        actual_search_random_and_transposed_transform_executed=True,exact_registers_flags_r_sp=True,
        all_eight_banks_and_write_multiplicity_checked=True,maximum_additional_stack_bytes=maximum_stack,
        partial_outputs_on_overflow_preserved=True,all_input_products_exhausted=False,
        game_caller_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionClass20SpawnVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
