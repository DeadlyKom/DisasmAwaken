"""DC9B, все AF и все значения каждого копируемого байта, цель 4000 не исполняется."""
import json
from collections import Counter
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import refresh


def main():
    original=base_memory();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[1]=bytearray(original[0x4000:0x8000]),bytearray(original[0x8000:0xC000]),bytearray(original[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=17);simulator=Simulator(memory);counts=Counter()
    for serial in range(65792):
        memory.recording=False;af=serial if serial<65536 else ((serial&255)*257)
        blob=bytes(original[0xDCA9:0xDDA9]) if serial<65536 else bytes((index*73+serial)&255 for index in range(256))
        memory.banks[1][0x1CA9:0x1DA9]=blob;memory.banks[5][:256]=bytes([serial&255])*256
        initial=get_registers({'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xDC9B},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);addition=(initial[0]+blob[-1])&255
        wanted[1]=(initial[1]&0xC1)|(addition&8)|((addition&2)<<4)
        wanted[2:8]=[0,0,0x41,0,0xDD,0xA9];wanted[15]=refresh(initial[15],516);wanted[24]=0x4000
        expected=[bytearray(bank) for bank in memory.banks];expected[5][:256]=blob
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        simulator.run(start=0xDC9B,stop=0x4000);memory.recording=False
        assert wanted[:25]==simulator.registers[:25] and wanted[26:28]==simulator.registers[26:28],(serial,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert memory.writes==[(5,index,value) for index,value in enumerate(blob)],(serial,'copy_writes')
        assert all(a==b for a,b in zip(memory.banks,expected)),(serial,'physical_RAM')
        assert not trace.writes and memory.o7ffd==17,(serial,'ports')
        counts['all_AF_original_source' if serial<65536 else 'all_source_byte_values']+=1
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),all_input_AF=True,
        every_source_byte_value_at_every_offset=True,complete_source_block_product_exhausted=False,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_values_multiplicity_and_emulator_order_proved=True,
        no_cpu_stack_or_port_writes=True,stopped_after_JP_4000=True,relocated_payload_not_executed=True,
        copied_bytes=256,refresh_m1=516,station_file_or_TRDOS_not_executed=True,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ControlsStationRelocationVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
