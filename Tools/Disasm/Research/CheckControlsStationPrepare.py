"""DCE3, три исходных LDIR, перестановка счётчика, замена SP и переход к копии 4200."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh


def main():
    original=base_memory();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[1]=bytearray(original[0x4000:0x8000]),bytearray(original[0x8000:0xC000]),bytearray(original[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=17);baseline=[bytearray(bank) for bank in memory.banks]
    simulator=Simulator(memory);counts=Counter();touched=set();flag_sums=set()
    for serial in range(8960):
        memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        if serial<4096:
            af=((serial//256)*17<<8)|(serial&255);blob=bytes(original[0x9BBD:0x9DBD]);payload=bytes(original[0xDD23:0xDE23]);kind='all_F_sixteen_A'
        elif serial<8704:
            af=(serial*73)&65535;blob=bytes((serial+index*109)&255 for index in range(512));payload=bytes((serial*3+index*73)&255 for index in range(256));kind='source_patterns_and_mixed_state'
        else:
            af=(serial*73)&65535;blob=bytes((serial+index*109)&255 for index in range(512));payload=bytes(original[0xDD23:0xDE23]);kind='all_counter_low_fixed_payload'
        for address,data in ((0x9BBD,blob),(0xDD23,payload)):
            bank=2 if address<0xC000 else 1;offset=address&0x3FFF;memory.banks[bank][offset:offset+len(data)]=data
        memory.banks[5][0x1800:0x1B00]=bytes((serial+index*31)&255 for index in range(768))
        initial=get_registers({'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0xABCD,'SP':(serial*109)&65535,'PC':0xDCE3},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);old_low,old_high=blob[2:4];saved=bytearray(blob);saved[2:4]=bytes((old_high,old_low))
        addition=(old_low+payload[-1])&255;flag_sums.add(addition)
        wanted[0:8]=[0x3F,(initial[1]&0xC1)|(addition&8)|((addition&2)<<4),0,0,0x43,0,0xDE,0x23]
        wanted[10:13]=[0x5C,0x3A,0x5FFF];wanted[14]=0x3F;wanted[15]=refresh(initial[15],3097)
        wanted[24],wanted[26],wanted[27]=0x4200,0,1
        writes=[(5,0x1800+index,0) for index in range(768)]
        writes.extend(((2,0x1BBF,old_high),(2,0x1BC0,old_low)))
        writes.extend((5,index,value) for index,value in enumerate(saved))
        writes.extend(((5,0x1FFD,0),(5,0x1FFE,0x42)))
        writes.extend((5,0x200+index,value) for index,value in enumerate(payload))
        expected=[bytearray(bank) for bank in memory.banks]
        for bank,offset,value in writes:expected[bank][offset]=value
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        simulator.run(start=0xDCE3,stop=0x4200);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(serial,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        # Проверка флагов последнего LDIR напрямую, H/N/PV сброшены, S/Z/Carry сохраняются от входа.
        assert simulator.registers[1]&0x16==0 and simulator.registers[1]&0xC1==initial[1]&0xC1
        assert Counter(writes)==Counter(memory.writes),(serial,'writes',Counter(writes)-Counter(memory.writes),Counter(memory.writes)-Counter(writes))
        assert all(a==b for a,b in zip(memory.banks,expected)),(serial,'physical_RAM')
        assert not trace.writes and memory.o7ffd==17,(serial,'ports')
        touched={(b,o) for b,o,_ in memory.writes};counts[kind]+=1
    assert len(flag_sums)==256
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),all_input_F=True,sixteen_input_A_values=True,
        all_256_final_LDIR_flag_sum_values=True,
        all_old_counter_byte_values_and_all_last_payload_values=True,all_saved_source_bytes_vary_over_full_byte_domain=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        overlapping_attribute_LDIR_clear_preserved=True,counter_middle_bytes_swapped_before_save=True,
        saved_bytes=512,relocated_bytes=256,attribute_bytes_cleared=768,refresh_m1=3097,
        original_SP_discarded=True,final_SP=0x5FFF,final_IM=1,final_I=63,final_IFF=0,
        stopped_before_payload_4200=True,TRDOS_and_station_file_not_executed=True,
        complete_source_block_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ControlsStationPrepareVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
