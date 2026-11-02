"""Четыре ядра CB00, семь битов множителя, знаковое слово и исходная единичная поправка."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory

KERNELS = ((0xCC7D,0xCCCA,0xCC7E,'HL'),(0xCCD1,0xCD1D,0xCCD2,'DE'),
           (0xCD48,0xCD95,0xCD49,'HL'),(0xCD9C,0xCDE8,0xCD9D,'DE'))


def main():
    base = base_memory()
    memory = Memory(base)
    simulator = Simulator(memory)
    counts = {}
    for entry,stop,operand,target in KERNELS:
        count = 0
        for coordinate in range(256):
            signed = coordinate if coordinate<128 else coordinate-256
            for coefficient in range(256):
                memory.recording = False
                memory[operand] = coefficient
                signed_coefficient = coefficient if coefficient<128 else coefficient-256
                magnitude = abs(signed)*(abs(signed_coefficient)&127)//128+1
                expected = (-magnitude if (coordinate^coefficient)&128 else magnitude)&65535
                initial = get_registers({'AF':coordinate*256+0x5A,'HL':0x1357,'DE':0x2468,'BC':0x3600+coordinate,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
                    'SP':0xBFFE,'PC':entry},None,False)
                simulator.registers[:] = initial
                memory.writes = []
                memory.recording = True
                for _ in range(80):
                    if simulator.registers[PC]==stop:
                        break
                    simulator.run()
                else:
                    raise AssertionError(('граница',hex(entry),coordinate,coefficient,hex(simulator.registers[PC])))
                memory.recording = False
                r = simulator.registers
                actual = r[6]*256+r[7] if target=='HL' else r[4]*256+r[5]
                assert actual==expected,(hex(entry),coordinate,coefficient,hex(actual),hex(expected))
                # Вычисление точных флагов сохранённого округлённого модуля после INC A.
                raw_product=abs(signed)*(abs(signed_coefficient)&127)
                rounded=raw_product//128+1
                rounded_flags=(rounded&0xA8) | (0x10 if (raw_product//128)&15==15 else 0) | (4 if raw_product//128==127 else 0) | ((raw_product>>6)&1)
                assert r[16:18]==[rounded,rounded_flags], ('alternate_af',hex(entry),coordinate,coefficient,r[16:18],[rounded,rounded_flags])
                marker=coordinate^coefficient
                if marker&128:
                    main_a=rounded^255
                    main_f=0x92 | (main_a&0x28)
                else:
                    main_a=marker
                    main_f=(marker&0xA8) | (0x40 if marker==0 else 0) | (4 if marker.bit_count()%2==0 else 0)
                assert r[:2]==[main_a,main_f], ('main_af',hex(entry),coordinate,coefficient,r[:2],[main_a,main_f])
                # Вычисление числа M1 по знаковой подготовке и единичным битам семиразрядного множителя.
                m1=43+3*int(coefficient>=128)+3*int(coordinate>=128)+(abs(signed_coefficient)&127).bit_count()+5*int(bool(marker&128))+int(target=='HL')
                expected_r=(initial[15]&128)|((initial[15]+m1)&127)
                assert r[15]==expected_r, ('refresh',hex(entry),coordinate,coefficient,r[15],expected_r)
                assert not memory.writes and r[SP]==initial[SP]
                assert r[2]==initial[2] and r[3]==abs(signed)
                assert all(r[i]==initial[i] for i in (8,9,10,11,14,18,19,20,21,22,23,26,27))
                other = r[4]*256+r[5] if target=='HL' else r[6]*256+r[7]
                assert other==0x1357
                count += 1
        counts[format(entry,'04X')] = count
    # Проверка неизменности всех байтов за исключением четырёх входных операндов тестовой оснастки.
    for _,_,operand,_ in KERNELS:
        memory[operand]=base[operand]
    assert memory==base
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_kernel=counts,
        all_signed_coordinate_and_coefficient_bytes=True,all_four_original_kernels=True,input_a_equals_c_as_in_caller=True,
        product_formula='sign * (floor(abs(coordinate) * (abs(coefficient) AND 127) / 128) + 1)',
        zero_product_unit_bias_preserved=True,coefficient_minus_128_low_seven_bits_preserved=True,
        exact_result_word=True,no_memory_writes=True,main_af_and_alternate_af_independently_proved=True,all_kernel_m1_counts_checked=True,
        whole_cb00_proved=False,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsPointProductsVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
