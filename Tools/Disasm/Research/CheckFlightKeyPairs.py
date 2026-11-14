"""Все пары текущих клавиш из одного подтверждённого входа полётного сканера.

Документация: ../../../Docs/ControlsTemporaryModule.md#пары-клавиш-в-одном-проходе-сканера
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json

from CheckActionParameterActivation import flat_action
from CheckFlightKeyPaths import ControlSourceMemory
from CheckStationFlightCycle import DISK, payload
from TraceFlight import ROOT, PC, SP, H, L, Simulator, Ports, main as trace


class SnapshotReady(Exception):
    pass


class PairPorts(Ports):
    def __init__(self,memory,pressed):
        super().__init__(memory)
        self.pressed = pressed
        self.reads = []

    def read_port(self,registers,port):
        if registers[PC]!=0x6F34:
            return super().read_port(registers,port)
        value = 255
        # Формирование активных низких битов для двух замкнутых клавиш выбранной строки.
        for row,mask in self.pressed:
            if port==(row<<8)|0xFE:
                value &= 255^mask
        self.reads.append((port,value))
        return value


def main():
    snapshot = {}
    def capture(frame,memory,registers):
        snapshot.update(banks=[bank.copy() for bank in memory.banks],
                        page=memory.o7ffd,registers=list(registers),frame=frame)
        raise SnapshotReady
    try:
        trace(['--frames','2'],scan_observer=capture,save_reports=False)
    except SnapshotReady:
        pass
    assert snapshot and snapshot['page']==0x10
    original = flat_action()
    assert (ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()==payload(17)
    matrix = [tuple(original[p:p+2]) for p in range(0x9D4C,0x9D82,2)]
    targets = [original[p]+256*original[p+1] for p in range(0x7017,0x704D,2)]
    keys = list(dict.fromkeys(matrix))
    assert len(keys)==26 and matrix[0]==matrix[-1]
    cases = []
    dispatch_totals = Counter()
    for pressed in combinations(keys,2):
        memory = ControlSourceMemory()
        for destination,saved in zip(memory.banks,snapshot['banks']):
            destination[:] = saved
        memory.out7ffd(snapshot['page'])
        assert [(memory[p],memory[p+1]) for p in range(0x9D4C,0x9D82,2)]==matrix
        assert [memory[p]+256*memory[p+1] for p in range(0x7017,0x704D,2)]==targets
        memory.watch_writes = True
        cpu = Simulator(memory)
        cpu.registers[:] = snapshot['registers']
        ports = PairPorts(memory,pressed)
        cpu.set_tracer(ports)
        expected = [targets[index] for index,pair in enumerate(matrix) if pair in pressed]
        observed = []
        returns = 0
        temporary_entries = set()
        # Исполнение одного полного прохода до начала спада клавиатурного состояния.
        for steps in range(200000):
            pc = cpu.registers[PC]
            bank = memory.o7ffd&7
            if pc==0x6F55:
                break
            if pc==0x6F4D:
                observed.append(cpu.registers[H]*256+cpu.registers[L])
            if pc==0x6F4E:
                returns += 1
            if bank==1 and 0xDADE<=pc<0xDB5D or 0x5DA0<=pc<0x5EDB:
                temporary_entries.add((bank,pc))
            cpu.run()
        else:
            raise AssertionError((pressed,'scanner did not finish',hex(pc)))
        assert observed==expected,(pressed,observed,expected)
        assert returns==len(expected)
        assert cpu.registers[SP]==snapshot['registers'][SP]
        assert len(ports.reads)==27
        assert not temporary_entries and not memory.control_writes,(pressed,temporary_entries,memory.control_writes)
        dispatch_totals.update(observed)
        cases.append(dict(keys=pressed,handlers=observed,instructions=steps))
    assert len(cases)==325
    report = dict(passed=True,cases=len(cases),profiles=cases,
        original_TRD_sha256=sha256(DISK).hexdigest(),actual_snapshot_key_and_target_tables_compared=True,
        matrix_entries=27,distinct_keys=26,duplicate_physical_key_dispatches_both_entries=True,
        snapshot_frame=snapshot['frame'],snapshot_SP=snapshot['registers'][SP],
        handler_dispatch_totals={f'{target:04X}':count for target,count in sorted(dispatch_totals.items())},
        all_selected_handlers_returned=True,scanner_SP_restored=True,
        temporary_module_entries=0,watched_control_source_or_length_writes=0,
        all_larger_chords_or_game_states_exhausted=False,
        natural_temporary_module_entry_proved=False,
        keyboard_response_only_during_scanner=True,IRQ_executed_during_pair_scan=False,
        boot_TRDOS_stub=True,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/FlightKeyPairsVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items() if key!='profiles'},indent=2))


if __name__=='__main__':
    main()
