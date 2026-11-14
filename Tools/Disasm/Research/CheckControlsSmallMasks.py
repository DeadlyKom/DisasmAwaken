"""D9B0, два набора упакованных затравок и фактические записи масок малых тел."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags
from ReferenceControlsPointRespawn import refresh


def main():
    original=base_memory()
    memory=Memory(original)
    simulator=Simulator(memory)
    counts=Counter()
    def check(radius,selector,main_flags,alternate_flags,kind):
        memory.recording=False
        memory[0xD990:0xD99C]=original[0xD990:0xD99C]
        memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':radius*256+main_flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':selector*256+alternate_flags,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xD9B0},None,False)
        initial[14],initial[15],initial[26],initial[27]=selector,main_flags,selector&1,selector%3
        seed=original[(0xD987 if selector else 0xD97E)+radius]
        transitions=seed&7
        mask=seed&0xF8
        signed=mask-256 if mask&128 else mask
        # Вычисление всех ступеней знаковым сдвигом числовой затравки.
        rows=[(signed>>index)&255 for index in range(transitions)]
        rows += [((signed>>transitions)&255)]*radius
        final_mask=original[0xD987+radius]&0xF8
        writes=[(0xD990+index,value) for index,value in enumerate(rows)]+[(0xD990,final_mask)]
        expected=list(memory)
        for address,value in writes:
            expected[address]=value
        wanted=list(initial)
        wanted[0:2]=[final_mask,and_flags(final_mask)]
        wanted[2]=0
        wanted[4:6]=[0,radius]
        wanted[6:8]=[(0xD987+radius)>>8,(0xD987+radius)&255]
        wanted[16:18]=[radius,main_flags]
        wanted[SP],wanted[15]=0xC000,refresh(main_flags,20+bool(selector)+5*transitions+3*radius)
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        for _ in range(140):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',radius,selector))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (radius,selector,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes)
        counts[kind]+=1
    # Проверка всех значений селектора, включая ненулевые байты с установленным разрядом 7.
    for radius in range(2,9):
        for selector in range(256):
            for main_flags in (0,1,0x5A,0xFF):
                check(radius,selector,main_flags,selector^255,'selectors')
    # Проверка каждого исходного F, буквально возвращаемого в альтернативном AF после обмена.
    for radius in range(2,9):
        for main_flags in range(256):
            for selector in (0,1,128,255):
                check(radius,selector,main_flags,main_flags^255,'saved_flags')
    # На входах вне договора прослеживаем записи до первого изменения кода.
    invalid_cases = 0
    for radius in (0, 1):
        for selector in (0, 1):
            memory.recording = False
            memory[0xD990:0xD9B0] = [0xA5] * 32
            memory[0xD9B0] = original[0xD9B0]
            simulator.registers[:] = get_registers(
                {'AF': radius << 8, '^AF': selector << 8, 'SP': 0xBFFE, 'PC': 0xD9B0}, None, False)
            memory.writes = []
            memory.recording = True
            for _ in range(160):
                simulator.run()
                if len(memory.writes) == 33:
                    break
            else:
                raise AssertionError(('первое перекрытие кода', radius, selector))
            memory.recording = False
            assert memory.writes == [(address, 0) for address in range(0xD990, 0xD9B1)]
            assert memory[0xD9B0] == 0 and original[0xD9B0] == 0x5F
            invalid_cases += 1
    result=dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),
        all_valid_radii=True,all_selector_bytes=True,all_main_flag_bytes=True,
        primary_mask_signed_shift_preserved=True,first_row_always_overridden_from_alternate=True,
        every_ram_byte_and_write_checked=True,exact_registers_flags_and_r=True,
        maximum_written_bytes=12,physical_seed_bytes=18,radius_0_1_outside_contract=True,
        invalid_cases_to_first_code_overwrite=invalid_cases, invalid_mask_tail_bytes_written=20,
        first_overwritten_code_address=0xD9B0,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsSmallMasksVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
