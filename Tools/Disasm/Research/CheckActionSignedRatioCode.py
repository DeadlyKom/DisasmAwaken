"""AE24 с настоящим AE73, исходной таблицей 9A00, двумя видами отказа и четырьмя знаковыми ветвями."""
from collections import Counter
import hashlib,json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh
from CheckControlsComponentCompare import logical_flags
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionSignedRatioCode import evaluate


def profiles():
    for word in range(65536):
        for denominator in (0,1,256,32767,32768,65535):yield word,denominator,word&255,'all_numerator_words'
    for word in range(65536):
        for numerator in (0,1,511,32768,65535):yield numerator,word,word&255,'all_denominator_words'
    for af in range(65536):
        for numerator,denominator in ((1,256),(65535,1)):yield numerator,denominator,af,'all_input_AF'
    edges=(0,1,2,127,128,255,256,257,511,512,32767,32768,32769,65534,65535)
    for numerator in edges:
        for denominator in edges:yield numerator,denominator,0xA55A,'word_edges'
    randomizer=random.Random(0xAE24)
    for _ in range(8192):yield randomizer.randrange(65536),randomizer.randrange(65536),randomizer.randrange(65536),'mixed_pairs'


def main():
    flat=flat_action();flat[0x9100:0x9200]=[v&255 for v in LOG];flat[0x9200:0x9300]=[v>>8 for v in LOG];flat[0x9300:0x9400]=EXP
    table=bytes(flat[0x9A00:0x9B00]);banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in memory.banks]
    expected=[bytearray(b) for b in baseline];simulator=Simulator(memory);counts=Counter();paths=Counter();indices=set();touched=set()

    def page(address):return 5 if address<0x8000 else 2 if address<0xC000 else 0

    for numerator,denominator,af,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=expected[bank][offset]=baseline[bank][offset]
        touched=set();stack=0x8002 if serial&1 else 0xBFFE
        for address,value in ((stack,255),(stack+1,63)):
            bank=page(address);memory[address]=value;expected[bank][address&0x3FFF]=value;touched.add((bank,address&0x3FFF))
        initial=get_registers({'AF':af,'HL':numerator,'DE':denominator,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':(serial*73)&65535,
            'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0xAE24},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        result=evaluate(numerator,denominator,table);wanted=list(initial);writes=[]

        def put(address,value):
            bank=page(address);offset=address&0x3FFF
            expected[bank][offset]=value;writes.append((bank,offset,value));touched.add((bank,offset))

        def put_word(address,value):put(address,value&255);put(address+1,value>>8)

        # Создание независимой ожидаемой рамки знака, исходного знаменателя и настоящего CALL AE73.
        sign_byte=(numerator>>8)^(denominator>>8)
        put_word(stack-2,(sign_byte<<8)|logical_flags(sign_byte));put_word(stack-4,denominator);put_word(stack-6,0xAE36)
        for address,value in result['writes']:put(address,value)
        for position,key in ((6,'hl'),(4,'de'),(2,'bc')):wanted[position:position+2]=[result[key]>>8,result[key]&255]
        wanted[0:2]=result['af'];wanted[16:18]=result['alternate_af']
        wanted[15]=refresh(initial[15],result['refresh_m1']);wanted[SP],wanted[PC]=stack+2,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0xAE24,stop=0x3FFF);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(numerator,denominator,result,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert Counter(writes)==Counter(memory.writes),(numerator,denominator,'writes',writes,memory.writes)
        assert all(memory.banks[bank][offset]==expected[bank][offset] for bank,offset in touched),(numerator,denominator,'RAM')
        counts[kind]+=1;paths[result['path']]+=1
        if result['table_index'] is not None:indices.add(result['table_index'])
        if counts.total()%65536==0:print(str(counts.total())+' cases passed',flush=True)
    assert all(a==b for a,b in zip(expected,memory.banks))
    zero=evaluate(0,0,table)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        all_numerator_and_denominator_words_on_slices=True,all_input_AF_on_two_sign_paths=True,
        actual_logarithmic_divider_executed=True,independent_numeric_parent_oracle=True,
        original_ratio_code_table_sha256=hashlib.sha256(table).hexdigest(),table_indices_observed=sorted(indices),
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        memory_proof_method='exact_logged_writes_and_touched_values_each_case_plus_final_eight_bank_comparison',
        maximum_additional_stack_bytes=6,original_zero_pair_code=zero['af'][0],original_minimum_signed_words_preserved=True,
        divider_overflow_and_shifted_range_rejection_proved=True,custom_quadrant_rules_preserved=True,
        ordinary_atan2_equivalence_proved=False,hardware_bus_stack_write_order_proved=False,
        complete_input_pair_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==860385
    (ROOT/'Tools/Disasm/Reports/ActionSignedRatioCodeVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='table_indices_observed'},indent=2))


if __name__=='__main__':main()
