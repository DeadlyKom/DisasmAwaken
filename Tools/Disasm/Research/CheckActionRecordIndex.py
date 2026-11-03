"""Коды записей с шагом 64, полный адресный диапазон, настоящие IX/IY-обёртки."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def add_flags(a,b):
    value=a+b;result=value&255
    return (result&0xA8)|(64 if not result else 0)|(16 if (a&15)+(b&15)>15 else 0)|(
        4 if (~(a^b)&(a^result)&128) else 0)|int(value>255)


def decode(address):
    high,low=address>>8,address&255;difference=(high-0xA1)&255
    index=(((address-0xA100)&65535)//64)&255
    shifted=(low*4)&255
    flags=(shifted&128)|(64 if not shifted else 0)|(4 if shifted.bit_count()%2==0 else 0)|(
        index&0x28)|((difference>>6)&1)
    return index,flags,(address&0xFF00)|shifted


def main():
    original=flat_action();memory=Memory(original);simulator=Simulator(memory);counts=Counter();touched=set()
    def check(entry,value,flags=0):
        nonlocal touched
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=original[address]
        memory[0xBFFE:0xC000]=[255,63]
        initial=get_registers({'AF':(value&255)*256+flags,'HL':value if entry==0xE6C7 else 0x1357,
            'DE':0x2468,'BC':0x369C,'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':value if entry==0xE6B5 else 0xABCD,'IY':value if entry==0xE6BE else 0x5C3A,
            'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);writes=[]
        if entry==0xE6A7:
            pointer=0xA100+value*64
            wanted[0:2]=[pointer>>8,add_flags(value>>2,0xA1)]
            wanted[6:8]=[pointer>>8,pointer&255];m1=12
        else:
            index,f,pointer=decode(value);wanted[0:2]=[index,f]
            if entry==0xE6C7:wanted[6:8]=[pointer>>8,pointer&255];m1=9
            else:
                # Создание эталона всех записей сохранённого HL, временного индекса и возврата CALL.
                ret=0xE6BC if entry==0xE6B5 else 0xE6C5
                writes=[(0xBFFD,0x13),(0xBFFC,0x57),(0xBFFB,value>>8),(0xBFFA,value&255),
                    (0xBFFB,ret>>8),(0xBFFA,ret&255)];m1=16
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        expected=list(memory)
        for address,byte in writes:expected[address]=byte
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(20):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',entry,value))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(hex(entry),hex(value),flags,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(entry,value,memory.writes,writes)
        touched={address for address,_ in writes};counts[format(entry,'04X')]+=1
    # Проверка каждого входного AF прямого преобразования, флаги не влияют на адрес.
    for value in range(256):
        for flags in range(256):check(0xE6A7,value,flags)
    print('Encoder: 65536 AF cases passed',flush=True)
    # Проверка всех HL, IX и IY, диапазон допустимых записей алгоритмом не ограничивается.
    for entry in (0xE6C7,0xE6B5,0xE6BE):
        for value in range(65536):check(entry,value,value&255)
        print(format(entry,'04X')+': all 65536 addresses passed',flush=True)
    # Проверка обратимости всех исходных кодов и отсутствия влияния смещения внутри 64-байтовой записи.
    for value in range(256):
        for offset in range(64):assert decode(0xA100+value*64+offset)[0]==value
    report=dict(passed=True,total_cases=counts.total(),cases_by_entry=dict(counts),
        method='independent_address_division_and_bit_formulas_with_real_wrappers',
        all_encoder_af=True,all_decoder_hl=True,all_wrapper_ix=True,all_wrapper_iy=True,
        round_trip_and_all_record_offsets_checked=True,exact_registers_flags_refresh_sp=True,
        every_ram_byte_and_write_multiplicity_checked=True,hardware_bus_write_order_proved=False,maximum_additional_stack_bytes=4,
        encoder_m1=12,decoder_m1=9,wrapper_m1=16,range_checks_absent=True,
        record_field_meanings_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordIndexVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
