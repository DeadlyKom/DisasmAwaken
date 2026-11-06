"""66D2..6726, знаковое вычитание 16 из 24 бит и частичная запись при переполнении."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh

FIELDS=(0x9B78,0x9B7B,0x9B7E)
OPERANDS=(0xE5B3,0xE5D2,0xE5ED)


def profiles():
    # Проверка каждого знакового вычитаемого у обеих границ переполнения каждой компоненты.
    for position in range(3):
        for delta in range(65536):
            for value in (0x7FFFFF,0x800000):
                values=[0x123456,0x234567,0x345678];deltas=[0,0,0]
                values[position]=value;deltas[position]=delta
                yield values,deltas,(delta*73)&65535,'all_deltas_at_signed_bounds'
        # Проверка каждого младшего слова отдельно от границ старшего байта.
        for low in range(65536):
            values=[0x123456,0x234567,0x345678];deltas=[0,0,0]
            values[position]=(((low*109)&255)<<16)|low;deltas[position]=(low*73+0x8001)&65535
            yield values,deltas,low,'all_low_words_each_position'
    # Проверка каждого старшего байта при заёме и без него, положительных и отрицательных вычитаемых.
    for position in range(3):
        for high in range(256):
            for low in (0,65535):
                for delta in (0,1,0x7FFF,0x8000,0xFFFF):
                    values=[0,0,0];deltas=[0,0,0];values[position]=(high<<16)|low;deltas[position]=delta
                    yield values,deltas,high,'all_high_bytes_and_borrow_edges'
    # Проверка независимости результата от каждого входного AF.
    for af in range(65536):yield [0x123456,0xFEDCBA,0x7FFFFF],[0x1234,0xFFFF,0x8000],af,'all_input_AF'
    randomizer=random.Random(0x66D2)
    # Проверка смешанных трёхкомпонентных проходов и раннего прекращения на каждом поле.
    for _ in range(8192):yield [randomizer.randrange(1<<24) for _ in range(3)],[randomizer.randrange(65536) for _ in range(3)],randomizer.randrange(65536),'mixed_vectors'


def evaluate(initial,values,deltas):
    wanted=list(initial);writes=[];m1=0;stopped=None
    for index,(value,delta,address) in enumerate(zip(values,deltas,FIELDS)):
        low=value&65535;high=value>>16;sign=255 if delta&0x8000 else 0;borrow=int(low<delta)
        result=(low-delta)&65535;wide_high=high-sign-borrow;new_high=wide_high&255
        flags=(new_high&0xA8)|(64 if not new_high else 0)|((high^sign^new_high)&16)|2
        flags|=4 if (high^sign)&(high^new_high)&128 else 0
        flags|=int(wide_high<0)
        # Расчёт независимого знакового результата, переполнение проверяется до записи старшего байта.
        signed_value=value-(1<<24) if value&0x800000 else value
        signed_delta=delta-65536 if delta&0x8000 else delta
        exact=signed_value-signed_delta;overflow=not -(1<<23)<=exact<(1<<23)
        assert overflow==bool(flags&4) and (exact&0xFFFFFF)==(new_high<<16)|result
        writes.extend(((address,result&255),(address+1,result>>8)))
        wanted[0:8]=[new_high,flags,initial[2],sign,delta>>8,delta&255,result>>8,result&255]
        # Все три участка до условного RET имеют по 14 M1 без DEC C, отрицательное слово добавляет один M1.
        m1+=14+int(sign!=0)
        if overflow:stopped=index;break
        writes.append((address+2,new_high));m1+=1
    else:m1+=1
    wanted[12],wanted[15],wanted[24]=initial[12]+2,refresh(initial[15],m1),0x3FFF
    return wanted,writes,stopped,m1


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(bank) for bank in memory.banks]
    simulator=Simulator(memory);counts=Counter();paths=Counter();costs=set();touched=set()
    for values,deltas,af,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        old_page=(0x10,0x18,0x30,0x38)[serial%4];memory.out7ffd(old_page)
        stack=(0x8008,0xBFFE)[serial&1];setup={stack:255,stack+1:63}
        for address,value in zip(FIELDS,values):
            for n in range(3):setup[address+n]=(value>>(8*n))&255
        for address,value in zip(OPERANDS,deltas):setup[address],setup[address+1]=value&255,value>>8
        for address,value in setup.items():memory[address]=value
        touched={(0 if address>=0xC000 else 2,address&0x3FFF) for address in setup}
        initial=get_registers({'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0x66D2},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted,writes,stopped,m1=evaluate(initial,values,deltas)
        expected=[(2,address&0x3FFF,value) for address,value in writes]
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        simulator.run(start=0x66D2,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,values,deltas,stopped,m1,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert Counter(memory.writes)==Counter(expected),(serial,'write_multiplicity')
        final=dict(setup);final.update(writes)
        assert all(memory[address]==value for address,value in final.items()),(serial,'RAM_values')
        assert not trace.writes and memory.o7ffd==old_page,(serial,'ports_or_page')
        counts[kind]+=1;paths['complete' if stopped is None else 'overflow_component_'+str(stopped)]+=1;costs.add(m1)
        if counts.total()%65536==0:print(str(counts.total())+' cases passed',flush=True)
    # Проверка всех восьми банков после последней фикстуры, лишние записи запрещены в каждом сценарии.
    for address,value in final.items():baseline[0 if address>=0xC000 else 2][address&0x3FFF]=value
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        all_signed_16bit_deltas_at_both_24bit_bounds_each_component=True,all_low_words_each_component=True,
        all_high_bytes_and_selected_borrow_edges_each_component=True,all_input_AF=True,
        low_word_written_before_overflow_return=True,overflow_high_byte_and_later_components_unchanged=True,
        cpu_stack_written=False,observed_m1_min=min(costs),observed_m1_max=max(costs),
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionSubtractWorkVectorVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
