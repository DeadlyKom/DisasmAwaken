"""E1B9..E1D0, масштаб из заголовка и три смещения JR, отдельная граница без исполнения соседнего обхода."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckScreenUpdate import PortTrace, put
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh


def check_original_bound_mantissas(flat, objects):
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    banks[4][:len(objects)] = objects
    distinct_headers = set()
    passed_by_delta = Counter()
    for index in range(0, 256, 2):
        pointer = flat[0x9E00 + index] | flat[0x9E01 + index] << 8
        offset = pointer - 0xC000
        mantissa, exponent = objects[offset:offset + 2]
        assert 1 <= exponent <= 5 and 1 <= mantissa <= 120
        distinct_headers.add(pointer)
        original = mantissa << (exponent - 1)
        # Подготовка компоненты на один выше половины исходной границы.
        component = original // 2 + 1
        for delta in (0, 4):
            memory = RecordedBanks(banks=[bank.copy() for bank in banks], out7ffd=0x10)
            memory.banks[4][offset] = mantissa + delta
            put(memory, 0xBFFE, b'\xB9\xE1')
            put(memory, 0xAF48, component.to_bytes(2, 'little'))
            put(memory, 0xAF56, b'\x00\x00')
            put(memory, 0xAF69, b'\x00\x00')
            memory[0xE507] = 1
            cpu = Simulator(memory, {'PC': 0xAACC, 'SP': 0xBFFE, 'AF': index << 8})
            ports = PortTrace(cpu)
            cpu.set_tracer(ports)
            cpu.run(stop=0xE1B9)
            assert cpu.registers[6:8] == [exponent, mantissa + delta]
            cpu.run(stop=0xE1D1)
            scaled = (mantissa + delta) << (exponent - 1)
            assert cpu.registers[6:8] == [scaled >> 8, scaled & 255]
            assert int.from_bytes(memory[0xE2C5:0xE2C7], 'little') == scaled
            # Проверка действительного допуска CALL при изменении одного байта заголовка.
            dispatched = False
            for _ in range(45):
                pc = cpu.registers[PC]
                if pc == 0xE213:
                    break
                dispatched |= pc == 0xE506
                cpu.run()
            else:
                raise AssertionError((index, delta, cpu.registers[PC]))
            assert dispatched == bool(delta) and cpu.registers[SP] == 0xC000
            assert ports.writes == [(0x7FFD, 0x14), (0x7FFD, 0x10)]
            passed_by_delta[delta] += 1
    assert passed_by_delta == {0: 128, 4: 128} and len(distinct_headers) == 95
    return dict(original_even_indices=128, distinct_physical_headers=len(distinct_headers),
                original_mantissas_rejected_component=passed_by_delta[0],
                increased_mantissas_admitted_dispatch=passed_by_delta[4],
                banked_read_scaling_and_dispatch_gate_executed=True,
                dispatch_inhibit_set_in_fixture=True)


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter()
    def check(mantissa,exponent,flags=255):
        assert 1<=exponent<=6
        memory.recording=False
        for address in (0xE1C8,0xE232,0xE26B):memory[address]=0xFE
        memory[0xE2C5:0xE2C7]=[0x34,0x12]
        initial=get_registers({'AF':0xA500|flags,'HL':(exponent<<8)|mantissa,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xE1B9},None,False)
        serial=counts.total();initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);shift=exponent-1;scaled=mantissa<<shift
        f=sub8_flags(6,exponent)
        if shift:
            previous=mantissa<<(shift-1)
            f=(f&0xC4)|((scaled>>8)&0x28)|(16 if (previous&4095)*2>4095 else 0)
        # Проверка замкнутой таблицы F, нулевой HL не задаёт Z после цепочки ADD.
        closed_flags=2 if exponent==1 else 0 if exponent<=4 else (mantissa>>4)&8 if exponent==5 else 0x40|((mantissa>>3)&0x18)
        assert f==closed_flags,(mantissa,exponent,f,closed_flags)
        writes=[(0xE1C8,6-exponent),(0xE232,6-exponent),(0xE26B,6-exponent),(0xE2C5,scaled&255),(0xE2C6,scaled>>8)]
        for address,value in writes:expected[address]=value
        wanted[0:2]=[6-exponent,f];wanted[6:8]=[scaled>>8,scaled&255]
        wanted[PC],wanted[15]=0xE1D1,refresh(initial[15],7+exponent)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(0xE1B9,0xE1D1);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(mantissa,exponent,flags,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==writes,(mantissa,exponent,memory.writes,writes)
        counts['exponent_'+str(exponent)]+=1
    # Проверка всех допустимых сочетаний мантиссы и показателя, исходные флаги меняются отдельно.
    for exponent in range(1,7):
        for mantissa in range(256):check(mantissa,exponent,flags=mantissa^exponent)
    for flags in range(256):check(flags^165,1+flags%6,flags)
    # Проверка области применимости по всем 128 исходным чётным указателям OBJECT3D, без объявления игрового диапазона индексов.
    action=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();headers=[]
    for index in range(0,256,2):
        pointer=action[0x3E00+index]+256*action[0x3E01+index];offset=pointer-0xC000
        assert 0<=offset<len(objects)-1
        mantissa,exponent=objects[offset:offset+2];assert 1<=exponent<=6
        headers.append((mantissa,exponent));check(mantissa,exponent)
    bound_mantissas = check_original_bound_mantissas(baseline, objects)
    report=dict(passed=True,total_cases=counts.total(),cases_by_exponent=dict(counts),
        method='independent_integer_scaling_flags_and_patch_oracle',
        all_valid_header_words=True,valid_exponents=[1,2,3,4,5,6],original_even_table_headers_checked=128,
        original_header_exponents=sorted({h for _,h in headers}),
        original_header_bound_mantissa_use=bound_mantissas,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,
        closed_AF_table_checked_for_all_1536_valid_headers=True,
        execution_boundary='E1B9..E1D1, no continuation executed',maximum_additional_stack_bytes=0,
        invalid_exponents_executed=False,whole_projection_scan_proved=False,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionScaleHeaderVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
