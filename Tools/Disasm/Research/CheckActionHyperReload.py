"""Копия 4200, подготовка реального вызова TR-DOS и условный успешный хвост после внешней загрузки."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckActionTextQueueCalls import Ports
from CheckMusic import Simulator,get_registers,PC
from CheckScreenUpdate import put


def main():
    original=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();flat=flat_action();copied=bytes(flat[0x71CB:0x722E]);assert len(copied)==99 and copied[90:]==b'ACTION  C'
    baseline=[bytearray([160+i]*16384) for i in range(8)];baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000]);baseline[7]=bytearray([77]*16384)
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=31);simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports)
    counts=Counter()
    for serial in range(256):
        memory.recording=False
        for bank,raw in zip(memory.banks,baseline):bank[:]=raw
        memory.out7ffd(31);put(memory,0x4200,copied);state=bytes((serial+i*73)&255 for i in range(481));put(memory,0x9BBD,state)
        initial=get_registers({'PC':0x4200,'SP':0xBFFE,'AF':serial*257,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x1234},None,False)
        initial[14]=serial;initial[26]=serial&1;initial[27]=serial%3
        expected=[bytearray(b) for b in memory.banks];expected[5][0:481]=state;expected[5][0x1CDD:0x1CE6]=b'ACTION  C';expected[5][0x1CF9]=0;expected[5][0xFFE:0x1000]=(0x4234).to_bytes(2,'little')
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;ports.events=[]
        for _ in range(2000):
            if simulator.registers[PC]==0x3D13:break
            simulator.run()
        else:raise AssertionError('TR-DOS boundary not reached')
        memory.recording=False;r=simulator.registers
        assert memory.banks==expected and ports.events==[(0x7FFD,24)] and memory.o7ffd==24
        assert r[:8]==[0,0x44,0,14,0x5C,0xE6,0x42,0x63],r[:8]
        assert r[8:10]==initial[8:10] and r[10:13]==[0x5C,0x3A,0x4FFE] and r[14]==63 and r[26:28]==[0,1]
        expected_writes=[(5,i,v) for i,v in enumerate(state)]+[(5,0x1CDD+i,v) for i,v in enumerate(b'ACTION  C')]+[(5,0x1CF9,0),(5,0xFFF,0x42),(5,0xFFE,0x34)]
        assert Counter(memory.writes)==Counter(expected_writes)
        counts['before_TRDOS']+=1
        # Создание только условного успешного окружения внешнего TR-DOS, это не исполнение дисковой службы.
        memory.recording=False;put(memory,0x6000,original);put(memory,0x4200,copied)
        return_registers=list(r);return_registers[12]=0x5000;return_registers[24]=0x4234;return_registers[0]=serial;return_registers[1]=serial;return_registers[26]=serial&1
        expected=[bytearray(b) for b in memory.banks];expected[2][0x1BBD:0x1BBD+481]=state
        for address,value in ((0x9B79,255),(0x9B7A,5),(0x9B7C,255),(0x9B7F,0)):expected[2][address&0x3FFF]=value
        simulator.registers[:]=return_registers;memory.writes=[];memory.recording=True;ports.events=[]
        for _ in range(1000):
            if simulator.registers[PC]==0x6000:break
            simulator.run()
        else:raise AssertionError('new ACTION boundary not reached')
        memory.recording=False;r=simulator.registers
        assert memory.banks==expected and not ports.events and memory.o7ffd==24
        assert r[:8]==[0,0x44,0,0,0x9D,0x9E,0x41,0xE1] and r[12]==0x5FFF and r[26]==0,r[:13]
        assert r[8:12]==return_registers[8:12] and r[14]==return_registers[14] and r[27]==return_registers[27]
        expected_writes=[(2,0x1BBD+i,v) for i,v in enumerate(state)]+[(2,a&0x3FFF,v) for a,v in ((0x9B79,255),(0x9B7A,5),(0x9B7C,255),(0x9B7F,0))]
        assert Counter(memory.writes)==Counter(expected_writes)
        counts['conditional_successful_return']+=1
    result=dict(passed=True,total_cases=counts.total(),phases=dict(counts),actual_relocated_code_executed=True,
        saved_and_restored_bytes=481,not_512=True,file_key=b'ACTION  C'.decode(),TRDOS_entry=0x3D13,TRDOS_C=14,
        complete_RAM_and_write_multiplicity_compared=True,main_and_preserved_registers_I_IM_IFF_SP_checked=True,
        return_load_is_explicit_external_assumption=True,fresh_ACTION_6000_boundary_proved=True,
        full_R_T_checked=False,TRDOS_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionHyperReloadVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
