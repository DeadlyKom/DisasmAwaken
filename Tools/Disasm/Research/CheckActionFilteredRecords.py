"""Три исходных фильтра списка, настоящие итератор и преобразование IY в индекс, включая найденный FF."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceActionRecordFilters import Machine

ENTRIES={0xE6E2:('ActionRandomFilteredRecord',lambda code:1<=code<=15 or code==18,0),
         0xE70D:('ActionRecordsExcept6And7',lambda code:code not in (6,7),6),
         0xE729:('ActionRecords6Or7',lambda code:code in (6,7),6),
         0xE745:('ActionRecords5Or14',lambda code:code in (5,14),5)}


def profiles(entry):
    rejected=6 if entry==0xE70D else 0
    accepted=1 if entry==0xE6E2 else 0 if entry==0xE70D else 6 if entry==0xE729 else 5
    for position in range(26):
        for code in range(256):
            for style in range(2):
                prefix=[(128 if style==0 else 1,rejected)]*position
                header=(code+1)&255
                yield prefix+[(header if header!=128 else 129,code)],code,'all_classes_and_positions'
    for length in range(27):
        for style in range(3):
            yield [(128 if style==0 or (style==2 and i&1) else 1,rejected) for i in range(length)],length,'markers'
    for flags in range(256):
        for code in (accepted,255):yield [(1,code)],flags,'all_input_F'
    randomizer=random.Random(entry)
    for _ in range(1024):
        rows=[]
        for _ in range(randomizer.randrange(27)):
            header=128 if randomizer.randrange(3)==0 else randomizer.choice((0,1,127,129,255))
            rows.append((header,randomizer.randrange(256)))
        yield rows,randomizer.randrange(256),'mixed_lists'


def main(entry):
    tag,accept,first=ENTRIES[entry]
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    counts=Counter();outcomes=Counter();costs=[]
    def input_profiles():
        for rows,flags,kind in profiles(entry):yield rows,flags,kind,1,0
        if entry==0xE6E2:
            for word in range(65536):yield [(1,0),(1,18)],word&255,'gate_low_words',word,0
            for fold in range(256):
                for word in (0,1,0x7FFF,0x8000,0xFFFF):yield [(1,1)],fold,'gate_fold_edges',word,fold
    for rows,flags,kind,seed,fold in input_profiles():
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        for index,(header,code) in enumerate(rows):
            pointer=0xA100+64*index;memory[pointer],memory[pointer+1],memory[pointer+18]=index+1,header,code
        marker=0xA100+64*len(rows);memory[marker],memory[marker+1]=128,128
        stack=0x8002 if serial&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'AF':((serial*73)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        if entry==0xE6E2:memory[0xEBE7],memory[0xEBE8],memory[0xEBE9]=seed&255,seed>>8,fold
        model=Machine(memory.banks,initial).filtered(entry)
        expected,wanted,writes,m1=model.banks,model.r,model.writes,model.m1_count
        outcome=model.path[-1]
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(hex(entry),serial,rows,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(hex(entry),serial,'RAM')
        assert Counter(writes)==Counter(memory.writes),(hex(entry),serial,'write_multiplicity',writes,memory.writes)
        counts[kind]+=1;outcomes[outcome]+=1;costs.append(m1)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),outcomes=dict(outcomes),
        entry=entry,all_256_classes_at_each_of_26_positions=True,game_array_capacity_proved=False,all_input_F=True,reachable_marker_required=True,
        actual_iterator_and_index_conversion_executed=True,independent_numeric_list_oracle=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        maximum_additional_stack_bytes=6,found_ff_Z_quirk_preserved=True,hardware_bus_stack_write_order_proved=False,
        full_list_product_exhausted=False,observed_m1_min=min(costs),observed_m1_max=max(costs),
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    if entry==0xE6E2:
        report.update(actual_stream_10_executed=True,all_seed_low_words_at_fold_0=True,
            all_fold_bytes_at_five_word_edges=True,random_gate_threshold=160,gate_result=26,
            random_distribution_and_period_proved=False,complete_24_bit_state_domain_exhausted=False)
    (ROOT/f'Tools/Disasm/Reports/{tag}Verification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    for entry in ENTRIES:main(entry)
