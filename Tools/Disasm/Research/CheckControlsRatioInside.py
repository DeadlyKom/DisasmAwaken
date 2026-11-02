"""Частичная модель D0CA только при 0<=N<=Q<=7FFFFF, без заявления полного договора."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory


def reference(numerator, divisor):
    if divisor<2:
        return dict(hl=((numerator<<23)>>8)&65535, de=((divisor<<23)>>8)&65535,
                    bc=0, a=0, f=0x42, normalized=False)
    # Расчёт общего сдвига по старшему установленному разряду делителя.
    shift = 24-divisor.bit_length()
    normalized_n, normalized_d = numerator<<shift, divisor<<shift
    high_n, high_d = normalized_n>>16, normalized_d>>16
    # Расчёт исходного восьмишагового частного, равенство коэффициентов допускает переполнение.
    quotient, remainder = 0, high_n
    for _ in range(8):
        expanded = 2*remainder
        accepted = expanded>=high_d
        remainder = ((expanded-high_d) if accepted else expanded)&255
        quotient = 2*quotient+accepted
    flags = (quotient&0xA8) | (0x40 if quotient==0 else 0) | (4 if quotient.bit_count()%2==0 else 0)
    return dict(hl=(high_n<<8)|(((normalized_n<<1)>>8)&255), de=quotient<<8,
                bc=(high_d<<8)|((normalized_n<<1)&255), a=remainder, f=flags, normalized=True)


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()

    def check(numerator, divisor, coordinate, kind):
        nonlocal touched
        assert 0<=numerator<=divisor<=0x7FFFFF and coordinate in (2,3)
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        memory[0xBFFC:0xC000] = [0xFE,0x3F,0xFF,0x3F]
        initial = get_registers({'AF': 0xA55A, 'HL': numerator>>8, 'DE': divisor>>8,
            'BC': ((divisor&255)<<8)|(numerator&255), '^AF': 0xDEF0,
            '^HL': 0x1234, '^DE': 0x5678, '^BC': 0xA000|coordinate,
            'IX': 0xABCD, 'IY': 0x5C3A, 'SP': 0xBFFC, 'PC': 0xD0CA}, None, False)
        initial[14], initial[26], initial[27] = divisor&255, numerator&1, divisor%3
        result = reference(numerator, divisor)
        wanted = list(initial)
        wanted[0:8] = [result['a'],result['f'],result['bc']>>8,result['bc']&255,
                        result['de']>>8,result['de']&255,result['hl']>>8,result['hl']&255]
        wanted[18], wanted[19], wanted[SP] = initial[18]|(4 if coordinate==3 else 8), coordinate-1, 0xBFFE
        before = list(memory)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(400):
            if simulator.registers[PC] in (0x3FFE,0x3FFF):
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',numerator,divisor))
        memory.recording = False
        assert simulator.registers[PC]==0x3FFE, ('неожиданный внешний выход',numerator,divisor)
        compared = (*range(13),14,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (numerator,divisor,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(0xBFF8<=address<0xBFFC for address,_ in memory.writes)
        assert memory[:0xBFF8]==before[:0xBFF8] and memory[0xBFFC:]==before[0xBFFC:]
        touched = {address for address,_ in memory.writes}
        counts[kind] += 1

    # Проверка всех слов делителя в младшем диапазоне с меняющейся долей числителя.
    for divisor in range(65536):
        check((divisor*73//256), divisor, 2+(divisor&1), 'small_divisors')
    print('Ratio inside small divisors complete',flush=True)
    # Проверка каждой допустимой пары старших нормализованных коэффициентов.
    for divisor_byte in range(128,256):
        for numerator_byte in range(divisor_byte+1):
            check(numerator_byte<<15, divisor_byte<<15, 2+(numerator_byte&1), 'coefficient_pairs')
    # Проверка обоих координатных флагов у равенства, нуля и непосредственно перед делителем.
    for divisor in (0,1,2,3,0xFF,0x100,0x101,0xFFFF,0x10000,0x10001,0x3FFFFF,0x400000,0x7FFFFF):
        for numerator in sorted({0,max(0,divisor-1),divisor}):
            for coordinate in (2,3):
                check(numerator,divisor,coordinate,'edges')
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),
        domain='0<=N<=Q<=7FFFFF, alternative C is 2 or 3',
        mathematical_normalization_and_byte_division=True,
        every_output_register_except_r_and_t_checked=True, exact_stack_return_target=True,
        nonstack_memory_unchanged=True, stack_write_values_and_r_proved=False,
        tiny_divisor_direct_return_preserved=True, outside_domain_proved=False,
        whole_procedure_proved=False, unknown_status_preserved=True,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsRatioInsideVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
