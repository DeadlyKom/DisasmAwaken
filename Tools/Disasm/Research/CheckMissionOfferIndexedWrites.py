"""Косвенная запись восьми промежуточных байтов предложения через исходный LANG.

Документация: ../../../Docs/MissionOffer.md#условный-писатель-через-lang
Текст присваивания подставляется в RAM модели, исходники игры не меняются.
"""
from collections import Counter
from hashlib import sha256
import json

from CheckRowHighlight import SliceableMemory
from CheckScreenUpdate import PortTrace, put
from CheckStationFlightCycle import DISK, ROOT, payload
from ProbeShipPreviewCallbacks import make_context
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, get_registers


STATE = 0x983B
QUANTITIES = 0x98F6
TARGETS = tuple(range(0x98B4, 0x98BC))
SCRIPT = 0xCA8F


class ObservedMemory(SliceableMemory):
    recording = False

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.recording and isinstance(address, int) and address in TARGETS:
            self.target_reads.append((address, self.registers[PC], value))
        return value

    def __setitem__(self, address, value):
        if self.recording and isinstance(address, int) and STATE <= address < STATE + 512:
            self.state_writes.append((address, self.registers[PC], value))
        super().__setitem__(address, value)


def main():
    _, _, banks = make_context()
    banks = [bytearray(bank) for bank in banks]
    lang = payload(5)
    banks[6][:len(lang)] = lang
    # Исходный сценарий заканчивается первым полным нулём, байт команды i в нём отсутствует вообще.
    original_script = lang[SCRIPT - 0xC000:]
    original_script = original_script[:original_script.index(0) + 1]
    assert len(original_script) == 1161 and b'i' not in original_script
    original = payload(4)[STATE - 0x6000:STATE - 0x6000 + 512]
    assert len(original) == 512
    memory = ObservedMemory(banks=banks, out7ffd=0x16)
    cpu = Simulator(memory)
    cpu.set_tracer(PortTrace(cpu))
    memory.registers = cpu.registers
    initial = get_registers({'PC': 0xC000, 'SP': 0x7FFE, 'IY': 0x5C3A}, None, False)
    counts = Counter()
    profiles = []
    values = (0, 35, 127, 128, 255, 256, 65535)
    for target in TARGETS:
        # Обратный расчёт явного десятичного номера с учётом DEC HL и оборачивания суммы.
        number = (target - QUANTITIES + 1) & 65535
        assert 1 <= number <= 65535 and len(str(number)) == 5
        assert (QUANTITIES + number - 1) & 65535 == target
        for old in range(256):
            for value in values:
                memory.recording = False
                block = bytearray(original)
                block[target - STATE] = old
                put(memory, STATE, block)
                # Строка заменяет только текст сценария, выполняется настоящий интерпретатор LANG.
                text = f'=i{number}:{value}\r'.encode('ascii') + b'\0'
                put(memory, SCRIPT, text)
                put(memory, 0x7FFE, b'\xFF\x3F')
                memory[0x6306] = 0x16
                cpu.registers[:] = initial
                memory.target_reads, memory.state_writes = [], []
                memory.recording = True
                for _ in range(25000):
                    if cpu.registers[PC] == 0x3FFF:
                        break
                    cpu.run()
                else:
                    raise AssertionError(('нет возврата', target, old, value, cpu.registers[PC]))
                memory.recording = False
                # Первый читатель захватывает адрес, Store повторно читает прежний бит 7 перед записью.
                assert memory.target_reads == [(target, 0xC1DC, old), (target, 0xC6DC, old)], (
                    target, old, value, memory.target_reads)
                stored = (value & 255) ^ (255 if old & 128 else 0)
                assert memory.state_writes == [(target, 0xC6E2, stored)], (
                    target, old, value, memory.state_writes)
                block[target - STATE] = stored
                assert bytes(memory[STATE:STATE + 512]) == block
                assert cpu.registers[SP] == 0x8000 and memory.o7ffd == 0x16
                counts[target] += 1
        profiles.append(dict(address=target, decimal_script_index=number, cases=counts[target]))
    assert counts.total() == 8 * 256 * len(values)
    report = dict(passed=True, cases=counts.total(), profiles=profiles,
        original_disk_sha256=sha256(DISK).hexdigest(), lang_sha256=sha256(lang).hexdigest(),
        original_market_script_bytes=len(original_script),
        original_market_script_sha256=sha256(original_script).hexdigest(),
        original_market_script_contains_literal_i=False,
        runtime_script_mutations_excluded=False,
        all_old_byte_values=True, right_values=list(values),
        original_lang_instructions_executed=True, substituted_script_text=True,
        exact_target_reads_and_state_writes=True, all_512_state_bytes_compared=True,
        ordinary_stack_return_and_bank_preserved=True,
        original_script_contains_these_assignments_proved=False,
        original_game_data_purpose_proved=False, global_writer_graph_complete=False,
        irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/MissionOfferIndexedWritesVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, cases=counts.total(), profiles=profiles), indent=2))


if __name__ == '__main__':
    main()
