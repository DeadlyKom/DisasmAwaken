"""Записи R в существующей сквозной модели BASIC, загрузок, полёта и возврата.

Документация: ../../../Docs/ActionNoiseExit.md#источники-старшего-бита-r
"""
from hashlib import sha256
import json

import CheckAwakenBasicRun as basic_run
from CheckBootBankFileReads import check_intro_transition
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
from skoolkit.simutils import R


class RefreshObserver(Simulator):
    instances = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_refresh = self.registers[R]
        self.refresh_writes = []
        original = self.after_ED[0x4F]

        def write_refresh():
            pc, before = self.registers[PC], self.registers[R]
            original()
            self.refresh_writes.append(dict(pc=pc, before=before, after=self.registers[R]))

        self.after_ED[0x4F] = write_refresh
        self.instances.append(self)


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    original_report = reports / 'BootBankFileReadsVerification.json'
    preserved = sha256(original_report.read_bytes()).hexdigest()
    basic_path = ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom'
    dos_path = ROOT / 'Tools/Disasm/Research/Runtime/Unreal/rom/trdos504t.rom'
    basic, dos = basic_path.read_bytes(), dos_path.read_bytes()
    # Проверка наблюдателя настоящей инструкцией ROM с подготовленным старшим битом A.
    probe = RefreshObserver(list(dos) + [0] * 49152)
    probe.memory[0xBFF0:0xBFF2] = [0x37, 0x80]
    probe.registers[:] = get_registers(dict(SP=0xBFF0, R=0x5A), None, False)
    probe.run(start=0x2EBE, stop=0x2EC1)
    assert len(probe.refresh_writes) == 1
    assert probe.refresh_writes[0]['pc'] == 0x2EBF and probe.refresh_writes[0]['after'] == 0x80
    assert probe.registers[SP] == 0xBFF2
    RefreshObserver.instances.clear()
    previous_simulator = basic_run.Simulator
    basic_run.Simulator = RefreshObserver
    try:
        # Исходная модель сохраняет свои проверки секторов, памяти, кадров и банков.
        profile = check_intro_transition(basic, dos, 0, mark_context=False)
    finally:
        basic_run.Simulator = previous_simulator
    assert len(RefreshObserver.instances) == 1
    cpu = RefreshObserver.instances[0]
    assert cpu.initial_refresh == 0 and not cpu.refresh_writes
    assert not cpu.registers[R] & 0x80
    assert sha256(original_report.read_bytes()).hexdigest() == preserved
    report = dict(passed=True, original_disk_sha256=sha256((ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()).hexdigest(),
        basic_rom_sha256=sha256(basic).hexdigest(), dos_rom_sha256=sha256(dos).hexdigest(),
        initial_R=cpu.initial_refresh, final_R=cpu.registers[R], observed_LD_R_A=cpu.refresh_writes,
        original_opcode_observer_positive_control=probe.refresh_writes,
        boot_profile=profile, original_boot_report_sha256=preserved,
        original_boot_report_unchanged=True, basic_editor_and_machine_initial_state_prepared=True,
        modelled_fdc_and_rom_paging=True, trdos_calls_substituted=False,
        original_profile_gate_fixtures_retained=True,
        whole_native_reset_and_game_proved=False, all_possible_paths_proved=False,
        native_refresh_bit7_reachability_proved=False,
        native_execution=False, assembly_executed=False)
    (reports/'BootRefreshRegisterVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('BASIC to return: no LD R,A, R bit7 remained clear, original boot report unchanged')


if __name__ == '__main__':
    main()
