"""Два исходных переносчика, все физические записи и передача управления через PUSH/RET."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from Analyze import payload


def main():
    counts={};profiles=[]
    for region,slot,entry,source,destination,size in (
        ('StationBoot',4,0x6300,0x6319,0x4000,0x2B5),
        ('ActionBoot',17,0x6000,0x6043,0x4200,0x1FA)):
        raw=payload(slot)
        base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
        for index,value in enumerate(raw):
            address=0x6000+index
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            base[bank][address&0x3FFF]=value
        source_data=raw[source-0x6000:source-0x6000+size]
        memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
        simulator=Simulator(memory);cases=0
        fixtures=[(16,flags,stack) for flags in range(256) for stack in (0x5FFE,0xBFFE,0x9AFE)]
        if region=='ActionBoot':fixtures=[(paging,paging*4+variant,0xBFFE if variant&1 else 0x5FFE)
            for paging in range(64) for variant in range(4)]
        for paging,flags,stack in fixtures:
            memory.recording=False
            for bank in range(8):memory.banks[bank][:]=base[bank]
            memory.out7ffd(paging)
            initial=get_registers({'AF':((flags*73)&255)*256+flags,
                'HL':0x1234,'DE':0x5678,'BC':0x9ABC,'IX':0xDEF0,'IY':0x5C3A,
                '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
                'SP':stack,'PC':entry},None,False)
            initial[14],initial[26],initial[27]=flags,flags&1,flags%3
            expected=[bytearray(b) for b in memory.banks];writes=[]

            def put(address,value,bank=None):
                if bank is None:bank=5 if address<0x8000 else 2 if address<0xC000 else paging&7
                expected[bank][address&0x3FFF]=value
                writes.append((bank,address&0x3FFF,value))

            wanted=list(initial)
            if region=='StationBoot':
                # Очистка атрибутов, затем перенос всех исходных байтов, включая данные загрузчика.
                for address in range(0x5800,0x5B00):put(address,0)
                final_paging=paging;ports_expected=[]
                final_a=initial[0]
                szc=flags&0xC1
            else:
                # Очистка реального банкового экрана, при запрете 7FFD остаётся прежний физический банк.
                shadow_bank=paging&7 if paging&32 else 7
                for address in range(0xC000,0xDB00):put(address,0,shadow_bank)
                for address in range(0x4000,0x5801):put(address,0)
                put(0x5800,0x38)
                for address in range(0x5801,0x5981):put(address,0x38)
                put(0x5980,7)
                for address in range(0x5981,0x5B00):put(address,7)
                final_paging=paging if paging&32 else 0x18
                ports_expected=[(0xFE,0),(0x7FFD,0x17),(0x7FFD,0x18)]
                final_a=0x18;szc=0x40
                wanted[18:24]=[0,0,0xDB,0,0xDA,0xFF]
            # Создание внутреннего адреса передачи управления не потребляет внешний возврат.
            put(stack-1,destination>>8);put(stack-2,destination&255)
            for index,value in enumerate(source_data):put(destination+index,value)
            sum_byte=(final_a+source_data[-1])&255
            final_f=szc|(sum_byte&8)|((sum_byte&2)<<4)
            wanted[0:8]=[final_a,final_f,0,0,(destination+size)>>8,(destination+size)&255,
                (source+size)>>8,(source+size)&255]
            wanted[PC]=destination
            simulator.registers[:]=initial
            ports=PortTrace(simulator);simulator.set_tracer(ports)
            memory.writes=[];memory.recording=True
            simulator.run(start=entry,stop=destination);memory.recording=False
            # Проверка регистров перед первым выполнением перемещённого кода и точных физических записей.
            compared=(*range(15),*range(16,25),26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(region,paging,flags,
                [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert ports.writes==ports_expected and memory.o7ffd==final_paging
            assert all(a==b for a,b in zip(expected,memory.banks)),(region,paging,flags,'RAM')
            assert Counter(writes)==Counter(memory.writes),(region,paging,flags,'writes')
            assert simulator.registers[SP]==stack
            cases+=1
        counts[region]=cases
        profiles.append(dict(region=region,entry=entry,source=source,destination=destination,size=size))
    report=dict(passed=True,total_cases=sum(counts.values()),cases_by_region=counts,profiles=profiles,
        all_initial_flags_values=True,all_A_values_for_station=True,
        all_six_bit_paging_values_for_action=True,locked_paging_for_action=True,
        all_registers_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        exact_ports=True,external_return_not_consumed=True,relocated_code_executed=False,
        assembly_executed=False,native_execution=False,irq_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/BootstrapRelocationVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
