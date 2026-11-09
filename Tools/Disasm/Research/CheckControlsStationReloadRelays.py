"""Перенесённые стадии STATIONF по 4000 и 4200, граница TR-DOS и условное восстановление 481 байта."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckActionTextQueueCalls import Ports
from CheckControlsTextQueue import payload,base_memory
from CheckMusic import Simulator,get_registers,PC
from CheckScreenUpdate import put


def main():
    source=payload(23);station=payload(4);flat=flat_action();baseline=[bytearray([160+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000]);baseline[1]=bytearray(base_memory()[0xC000:]);baseline[0]=bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=17);simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports);counts=Counter()
    for entry,offset in ((0x4000,0x1CB),(0x4200,0x245)):
        copied=source[offset:offset+256];assert copied[49:58]==b'STATIONFC'
        for serial in range(256):
            memory.recording=False
            for bank,raw in zip(memory.banks,baseline):bank[:]=raw
            memory.out7ffd(17);put(memory,entry,copied)
            saved=bytes((serial+i*73)&255 for i in range(481))
            if entry==0x4200:put(memory,0x4000,saved)
            initial=get_registers({'PC':entry,'SP':0x5FFF,'AF':serial*257,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x1234},None,False)
            initial[14]=serial;initial[26]=serial&1;initial[27]=serial%3
            expected=[bytearray(b) for b in memory.banks];expected[5][0x1CDD:0x1CE6]=b'STATIONFC';expected[5][0x1CF9]=0
            return_pc=0x6300 if entry==0x4000 else 0x421F;expected[5][0x1FFD:0x1FFF]=return_pc.to_bytes(2,'little')
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True;ports.events=[]
            for _ in range(200):
                if simulator.registers[PC]==0x3D13:break
                simulator.run()
            else:raise AssertionError(('нет TR-DOS',hex(entry)))
            memory.recording=False;r=simulator.registers
            assert memory.banks==expected and ports.events==([(0x7FFD,31),(0x7FFD,24)] if entry==0x4000 else [(0x7FFD,24)]) and memory.o7ffd==24
            wanted_de=0x6300 if entry==0x4000 else 0x5CE6
            assert r[:8]==[0,0x44,0,14,wanted_de>>8,wanted_de&255,(entry+58)>>8,(entry+58)&255],r[:8]
            assert r[8:10]==initial[8:10] and r[10:13]==[0x5C,0x3A,0x5FFD]
            if entry==0x4000:assert r[14]==63 and r[26:28]==[0,1]
            else:assert r[14]==initial[14] and r[26:28]==initial[26:28]
            expected_writes=[(5,0x1CDD+i,v) for i,v in enumerate(b'STATIONFC')]+[(5,0x1CF9,0),(5,0x1FFE,return_pc>>8),(5,0x1FFD,return_pc&255)]
            assert Counter(memory.writes)==Counter(expected_writes)
            counts['direct_before_TRDOS' if entry==0x4000 else 'state_before_TRDOS']+=1
            if entry==0x4000:continue
            # Создание условного успешного внешнего возврата, дисковая служба здесь не исполняется.
            memory.recording=False;put(memory,0x6000,station);put(memory,entry,copied)
            returned=list(r);returned[12]=0x5FFF;returned[24]=0x421F;returned[0]=serial;returned[1]=serial;returned[26]=serial&1
            expected=[bytearray(b) for b in memory.banks];expected[2][0x183B:0x183B+481]=saved
            simulator.registers[:]=returned;memory.writes=[];memory.recording=True;ports.events=[]
            for _ in range(1000):
                if simulator.registers[PC]==0x6300:break
                simulator.run()
            else:raise AssertionError('нет границы свежего STATIONF')
            memory.recording=False;r=simulator.registers
            assert memory.banks==expected and not ports.events and memory.o7ffd==24
            assert r[2:8]==[0,0,0x9A,0x1C,0x41,0xE1] and r[0]==serial and r[12]==0x5FFF and r[26]==0
            assert r[8:12]==returned[8:12] and r[14]==returned[14] and r[27]==returned[27]
            assert Counter(memory.writes)==Counter((2,0x183B+i,v) for i,v in enumerate(saved))
            counts['conditional_state_return']+=1
    result=dict(passed=True,total_cases=counts.total(),phases=dict(counts),actual_relocated_4000_and_4200_code_executed=True,
        TRDOS_C=14,file_key='STATIONFC',state_restore_bytes=481,full_eight_banks_and_write_multiplicity_checked=True,
        main_and_preserved_registers_I_IM_IFF_SP_checked=True,full_R_T_and_postload_F_checked=False,
        successful_load_is_explicit_external_assumption=True,fresh_STATIONF_entry_6300=True,TRDOS_executed=False,assembly_executed=False,native_execution=False)
    for stem in ('ControlsDirectStationRelay','ControlsStateStationRelay'):
        (ROOT/('Tools/Disasm/Reports/'+stem+'Verification.json')).write_text(json.dumps(result,indent=2)+'\n','utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
