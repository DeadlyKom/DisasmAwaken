"""Шаг трёхбайтового генератора по независимой арифметической формуле, обмен активных наборов регистров."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from PackedRefreshTrace import PackedRefreshTrace


class RecordedMemory(bytearray):
    def __setitem__(self,key,value):
        if getattr(self,'recording',False):
            assert isinstance(key,int)
            self.writes.append((key,value))
        super().__setitem__(key,value)


def reference(word,high):
    reduced=(word-1)&65535
    accumulator=(high+(reduced>>10).bit_count())&255
    value=(reduced<<6)&65535
    # Расчёт четырёх сумм с отдельным учётом переносов в байт A, переносы предварительного word*8 не учитываются.
    for term in (((word<<3)&65535),word,word,word):
        total=value+term;accumulator=(accumulator+(total>>16))&255;value=total&65535
    assert value==(75*word-64)&65535
    intermediate=(accumulator<<8)+(value>>8)-(value&255)
    high1=(accumulator-int(intermediate<0))&255
    difference=value-(intermediate&65535);borrow=int(difference<0)
    new_word=(difference-1)&65535;new_high=(high1-borrow)&255
    flags=2|(new_high&0xA8)|(0x40 if new_high==0 else 0)|(0x10 if high1&15<borrow else 0)
    flags|=(4 if high1==128 and borrow else 0)|int(high1<borrow)
    return new_word,new_high,flags,value&255


def main():
    _,_,banks=make_context();memory=RecordedMemory(65536)
    for start,page in ((0x4000,5),(0x8000,2),(0xC000,0)):memory[start:start+16384]=bytes(banks[page])
    simulator=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    states=((0xA882,0xA8AC),(0xA87B,0xA8AF),(0xA89E,0xA8B2),(0xA8A5,0xA8B5),
            (0xA889,0xA8B8),(0xA890,0xA8BB),(0xA897,0xA8BE))
    # Проверка совпадения 61 команды ядра Station с разобранным ядром ACTION.
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text(encoding='utf-8'))
    regions={row['name']:row['instructions'] for row in flow}
    core=[row for row in regions['Station'] if 0xA8C1<=row['address']<0xA90D]
    action=[row for row in regions['Action'] if 0xEC08<=row['address']<0xEC54]
    assert len(core)==len(action)==61
    assert [row['hex'] for row in core]==[row['hex'] for row in action]
    assert sum(2 if bytes.fromhex(row['hex'])[0] in (0xCB,0xDD,0xED,0xFD) else 1 for row in core)==63
    rows=core+[row for row in regions['Station'] if any(entry<=row['address']<entry+7 for entry,_ in states)]
    trace=PackedRefreshTrace(rows,0)
    cases=0;total_m1=0;seeds={};iff_values=set();im_values=set()
    def execute(entry,address,word,high,direct=False):
        nonlocal cases,total_m1
        memory.recording=False
        memory[address:address+3]=bytes([word&255,word>>8,high]);memory[0x7FFE:0x8000]=bytes([255,63])
        simulator.registers[:]=initial;r=simulator.registers
        if direct:r[H],r[L]=address>>8,address&255
        r[14]=cases&255;r[15]=high;r[26]=cases&1;r[27]=cases%3
        saved_system=(r[14],r[26],r[27]);seeds.setdefault(entry,set()).add(r[15])
        im_values.add(r[27]);iff_values.add(r[26])
        trace.initial_r=r[15];trace.m1=trace.steps=0;trace.prefix_counts.clear()
        memory.writes=[];memory.recording=True
        r[24]=entry
        # Проверка каждой исходной команды, полного счёта M1 и изменения R.
        cost=63 if direct else 66
        for _ in range(61 if direct else 64):
            trace.before(memory,r[24],r[15]);simulator.run();trace.after(r[15])
        trace.finish(r[15]);memory.recording=False
        assert trace.m1==cost and r[24]==0x3FFF
        assert (r[14],r[26],r[27])==saved_system
        total_m1+=trace.m1
        expected,expected_high,flags,low=reference(word,high)
        assert memory[address:address+3]==bytes([expected&255,expected>>8,expected_high])
        assert (r[H]*256+r[L],r[A],r[F],r[SP])==(expected,expected_high,flags,0x8000)
        assert r[22]*256+r[23]==address and r[20]*256+r[21]==expected and (r[18],r[19])==(0,low)
        assert r[8:12]==initial[8:12]
        assert r[16:18]==initial[16:18]
        assert r[B]*256+r[C]==(0x58BE if direct else 0x36C9)
        assert r[D]*256+r[E]==(0x47AD if direct else 0x247A)
        # Проверка порядка записей состояния и двух использований одной стековой ячейки.
        assert memory.writes==[(0x7FFC,(address+2)&255),(0x7FFD,(address+2)>>8),
                              (address+2,expected_high),(address+1,expected>>8),(address,expected&255),
                              (0x7FFC,expected&255),(0x7FFD,expected>>8)]
        cases+=1
    # Проверка каждого младшего слова со старшими байтами, включающими оборачивание ADC и SBC.
    for word,high in product(range(65536),(0,1,128,255)):execute(0xA87B,0xA8AF,word,high)
    # Проверка всех семи физических обёрток и прямого ядра, оно намеренно возвращает другой активный набор.
    for (entry,address),value in product(states,range(256)):
        execute(entry,address,(value*257)^0xA55A,value)
        execute(0xA8C1,address,(value*257)^0x5AA5,value,True)
    # Проверка отдельного хвоста очистки ровно 30 двухбайтовых записей, конечный маркер остаётся прежним.
    for value in range(256):
        memory[0x9554:0x9593]=bytes((value+i*71)&255 for i in range(63))
        before=bytes(memory[0x9554:0x9593]);memory[0x7FFE:0x8000]=bytes([255,63])
        simulator.registers[:]=initial;r=simulator.registers;r[A],r[F]=value,value^0xA5
        simulator.run(start=0xA90D,stop=0x3FFF)
        expected=before[:1]+bytes(60)+before[61:]
        assert memory[0x9554:0x9593]==expected
        assert (r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C],r[A],r[SP])==(0x9590,0x9591,0,value,0x8000)
        flags=((value^0xA5)&0xC1)|(value&8)|((value&2)<<4)
        assert r[F]==flags
    assert all(len(values)==256 for values in seeds.values())
    assert iff_values=={0,1} and im_values=={0,1,2}
    report=dict(passed=True,method='original_three_byte_random_step_against_independent_word_carry_formula',
                cases=cases,all_low_words=True,exhaustive_high_bytes=[0,1,128,255],streams=7,
                clear_market_rows_cases=256,clear_market_bytes=60,
                direct_core_register_bank_exchange_verified=True,random_quality_or_period_proved=False,
                core_identical_to_Action_EC08=True,core_instruction_count=61,core_m1=63,wrapper_m1=66,
                full_m1_total=total_m1,every_instruction_and_R_step_checked=True,
                all_initial_R_values_per_entry=True,I_IM_IFF_preserved=True,
                ordered_model_writes_checked=True,hardware_stack_bus_order_proved=False,
                full_joint_register_cartesian=False,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/RandomStateVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
