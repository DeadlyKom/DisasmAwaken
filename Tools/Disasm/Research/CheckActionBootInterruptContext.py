"""Режимы CPU от условного DOS-возврата до первой DI StartFlight.

Документация: ../../../Docs/ActionFlightCycle.md#режимы-cpu-на-границе-startflight
"""
from itertools import product
import json

from CheckStationFlightCycle import payload
from TraceFlight import ROOT, PC, SP, Memory, Ports, Simulator, main as trace
from skoolkit.simutils import get_registers


class ReachedStart(Exception):
    pass


class NoIRQ(Simulator):
    def accept_interrupt(self,registers,memory,prev_pc):
        self.suppressed_requests += 1
        return False


def main():
    data = payload(17)
    assert (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()==data
    profiles = []
    for i,im,iff in product((0,0x80,0xFF),range(3),range(2)):
        memory = Memory(out7ffd=0x10)
        for index,value in enumerate(data):
            memory[0x6000+index] = value
        cpu = NoIRQ(memory,config={'fast_ldir':False,'fast_djnz':False})
        cpu.suppressed_requests = 0
        cpu.registers[:] = get_registers(dict(PC=0x6000,SP=0x5FFF,IY=0x5C3A),None,False)
        calls = []
        def observe(frame,ram,registers):
            if registers[PC]==0x3D13:
                # Задание явного CPU-постусловия подставленного DOS, оригинальная ROM здесь не исполняется.
                registers[14],registers[27],registers[26] = i,im,iff
                calls.append(registers[2]*256+registers[3])
            if registers[PC]==0xA82D:
                raise ReachedStart
        try:
            trace(['--frames','1'],boot_simulator=cpu,instruction_observer=observe,
                  ports_factory=Ports,save_reports=False)
        except ReachedStart:
            pass
        else:
            raise AssertionError('Не достигнута граница StartFlight')
        r = cpu.registers
        # Проверка состояния до выполнения первой DI, стек содержит исходный HL загрузчика.
        assert calls and (r[14],r[27],r[26],r[SP],memory.o7ffd)==(i,im,iff,0xBFFE,0x19)
        assert memory[0xBFFE]+256*memory[0xBFFF]==0x623D
        assert memory[0xA82D]==0xF3
        before = list(r)
        cpu.run()
        assert r[PC]==0xA82E and r[26]==0 and r[14]==i and r[27]==im
        assert all(r[n]==before[n] for n in (*range(15),*range(16,24)))
        profiles.append(dict(dos_I=i,dos_IM=im,dos_IFF=iff,final_I=i,final_IM=im,
            before_DI_IFF=before[26],after_DI_IFF=r[26],dos_calls=len(calls),
            suppressed_scheduled_requests=cpu.suppressed_requests))
    report = dict(passed=True,total_cases=len(profiles),profiles=profiles,
        original_action_boot_executed=True,DOS_CPU_postconditions_supplied=True,
        no_claim_that_real_DOS_produces_all_these_modes=True,
        boundary=0xA82D,first_instruction=0xF3,SP=0xBFFE,saved_HL=0x623D,
        IRQ_execution_suppressed=True,real_DOS_executed=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionBootInterruptContextVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items() if key!='profiles'},indent=2))


if __name__=='__main__':
    main()
