"""Фактические рамки копировщика в одном полётном и двух шумовых кадрах.

Документация: ../../../Docs/ControlsBufferCopy.md#стеки-двух-подтверждённых-вызывающих-путей
"""
from hashlib import sha256
import json
from pathlib import Path

from CheckActionNoiseExit import (
    NoiseIrqMemory, NoiseMatrix, NOISE_ENTRY, PERIOD, ROM128, ROOT,
    irq_noise_frame, put, disk_payload, run_to,
)
from TraceFlight import main as trace_flight
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, IYh, IYl
from ReferenceControlsTextDisplay import pixel_address
from CheckStationFlightCycle import DISK, ENTRIES
from CheckActionParameterActivation import flat_action


class CopyStackMemory(NoiseIrqMemory):
    """Регистрация физических записей длины и двух байтов возврата CALL C879."""
    def __init__(self):
        super().__init__()
        self.length_writes = []
        self.copy_call_writes = []

    def __setitem__(self, address, value):
        if hasattr(self, 'registers') and isinstance(address, int):
            pc = self.registers[PC]
            bank = self.o7ffd & 7
            if bank == 1 and address in (0xDB01, 0xDB02):
                self.length_writes.append(dict(pc=pc, address=address, value=value, bank=bank))
            if getattr(self, 'executing_pc', None) == 0xC879:
                self.copy_call_writes.append(dict(address=address, value=value,
                                                  bank=5 if address < 0x8000 else 2 if address < 0xC000 else bank))
        super().__setitem__(address, value)


class CopyObserver:
    def __init__(self, cpu):
        self.cpu = cpu
        self.pending = None
        self.calls = []

    def observe(self, _frame, memory, registers):
        pc, sp = registers[PC], registers[SP]
        # Simulator меняет PC внутри CALL до записи возврата, запоминается адрес до шага.
        memory.executing_pc = pc
        if pc in (0xAAAC, 0x6082):
            assert bytes(memory[pc:pc + 3]) == bytes.fromhex('cd70c8')
        if pc == 0xC870 and memory.o7ffd & 7 == 1:
            assert self.pending is None
            self.pending = dict(input_SP=sp, external_return=int.from_bytes(memory[sp:sp + 2], 'little'),
                                length_before=bytes(memory.banks[1][0x1B01:0x1B03]).hex(),
                                source=bytes(memory[0x8000:0x8C00]),
                                first_write=len(memory.copy_call_writes))
        if pc == 0xC879 and memory.o7ffd & 7 == 1:
            assert self.pending is not None and sp == self.pending['input_SP']
            assert bytes(memory[pc:pc + 3]) == bytes.fromhex('cd82c8')
        if self.pending is not None and pc == self.pending['external_return']:
            call = self.pending
            assert sp == call['input_SP'] + 2
            writes = memory.copy_call_writes[call['first_write']:]
            assert sorted((row['address'], row['value'], row['bank']) for row in writes) == [
                (call['input_SP'] - 2, 0x7C, 2), (call['input_SP'] - 1, 0xC8, 2)], writes
            assert bytes(memory.banks[1][0x1B01:0x1B03]).hex() == call['length_before']
            for y in range(96):
                address = pixel_address(y, 0)
                assert bytes(memory[address:address + 32]) == call['source'][y * 32:y * 32 + 32]
            self.calls.append(dict(input_SP=call['input_SP'], external_return=call['external_return'],
                                   final_SP=sp, call_pc=0xC879, call_writes=writes,
                                   copied_bytes_compared=3072, bank1_PackedLength_unchanged=True))
            self.pending = None


def main():
    memory = CopyStackMemory()
    rom = Path(ROM128[1]).read_bytes()
    assert sha256(rom).hexdigest() == '8d93c3342321e9d1e51d60afcd7d15f6a7afd978c231b43435a7c0757c60b9a3'
    memory.roms = (memory.roms[0], list(rom))
    memory.out7ffd(16)
    put(memory, 0x6000, disk_payload(17))
    memory[0x5C00] = memory[0x5C04] = 255
    memory[0x5C3B] = 8
    cpu = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A}, {'im': 1},
                    config={'frame_duration': PERIOD, 'int_active': 36})
    memory.registers = cpu.registers
    original_action = flat_action()
    # Проверка физических вызывающих инструкций, обе передают управление C870.
    for address in (0xAAAC, 0x6082):
        assert bytes(original_action[address:address + 3]) == bytes.fromhex('cd70c8')
        offset = address - 0x6000 + (0x23D if address < 0x8000 else 0)
        assert disk_payload(17)[offset:offset + 3] == bytes.fromhex('cd70c8')
    observer = CopyObserver(cpu)
    flight = trace_flight(['--frames', '2', '--verify-flight-cycle'], boot_simulator=cpu,
                          save_reports=False, instruction_observer=observer.observe)
    assert flight['complete_frame_returns'] == 1
    assert len(observer.calls) == 1 and observer.calls[0]['input_SP'] == 0xBFFA
    # Подготовка условия разрушения корабля, дальнейший путь кадра исполняется исходным кодом.
    memory[0x6693] = 0x2E
    run_to(cpu, NOISE_ENTRY)
    assert cpu.registers[SP] == 0xBFFC
    noise_entry_sp = cpu.registers[SP]
    cpu.set_tracer(NoiseMatrix(cpu, 100))
    # Проверка первых двух кадров, включая действительные входы и возвраты ROM IM 1.
    previous_iy = 0x5C3A
    for _ in range(2):
        _, previous_iy, _, _ = irq_noise_frame(cpu, previous_iy)
        run_to(cpu, 0xC870, lambda _pc: observer.observe(0, memory, cpu.registers))
        observer.observe(0, memory, cpu.registers)
        target = observer.pending['external_return']
        cpu.run()
        run_to(cpu, target, lambda _pc: observer.observe(0, memory, cpu.registers))
        observer.observe(0, memory, cpu.registers)
        assert cpu.registers[IYh] * 256 + cpu.registers[IYl] == previous_iy
    assert len(observer.calls) == 3 and observer.pending is None
    assert [row['input_SP'] for row in observer.calls] == [0xBFFA, 0xBFF8, 0xBFF8]
    assert [row['external_return'] for row in observer.calls] == [0xAAAF, 0x6085, 0x6085]
    parent = disk_payload(22)[0x870:0x882]
    assert bytes(memory[0xC870:0xC882]) == parent
    assert parent == DISK[ENTRIES[22]['offset'] + 0x870:ENTRIES[22]['offset'] + 0x882]
    # Проверка исходной загрузки CONTROL, её два нуля не являются вычисленным писателем.
    assert memory.length_writes == [dict(pc=0x3D13, address=address, value=0, bank=1)
                                    for address in (0xDB01, 0xDB02)], memory.length_writes
    report = dict(passed=True, method='bounded_original_code_with_TRDOS_stub_and_real_noise_ROM_IRQ',
                  flight_frames_completed=1, noise_frames_copied=2, noise_entry_SP=noise_entry_sp,
                  calls=observer.calls, bank1_length_initial_load_writes=memory.length_writes,
                  bank1_length_runtime_writes=[],
                  selected_rom_sha256=sha256(rom).hexdigest(),
                  original_disk_sha256=sha256(DISK).hexdigest(),
                  original_parent_code_sha256=sha256(parent).hexdigest(),
                  ship_destruction_condition_prepared=True, all_game_caller_stacks_proved=False,
                  temporary_module_natural_length_writer_proved=False,
                  real_boot_verified=False, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/BufferCopyCallerStacksVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены стеки и пиксели одного полётного и двух шумовых вызовов копировщика.')


if __name__ == '__main__':
    main()
