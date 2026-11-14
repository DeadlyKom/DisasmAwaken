"""Сбор до #80 и повторная продажа полного грузового байта исходным LANG."""
import json

from CheckActionParameterActivation import flat_action
from CheckActionTextQueueCalls import Memory, Ports
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
from CheckOriginalTradeScript import LangWorkspaceMemory, make_context
from CheckScreenUpdate import PortTrace, put
from CheckStationFlightCycle import ENTRIES


def collect(old):
    raw = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, address in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = raw[address:address + 0x4000]
    banks[1][:] = base_memory()[0xC000:]
    memory = Memory(banks=banks, out7ffd=16)
    cpu = Simulator(memory)
    cpu.set_tracer(Ports(memory))
    memory[0x7318], memory[0x9B1B] = 1, 0
    put(memory, 0x9BD2, [old, 200])
    memory[0x9BD4] = old
    put(memory, 0xA100, bytes(6))
    for offset, value in ((10, 4), (16, 77), (17, 1), (18, 0x13), (24, 0), (35, 0)):
        memory[0xA100 + offset] = value
    put(memory, 0xBFFE, [255, 63])
    cpu.registers[:] = get_registers(dict(PC=0x7317, SP=0xBFFE, IX=0xABCD, IY=0x5C3A), None, False)
    for _ in range(7000):
        if cpu.registers[PC] == 0x3FFF:
            break
        cpu.run()
    else:
        raise AssertionError('Сбор не вернулся')
    assert cpu.registers[SP] == 0xC000
    assert memory[0x9BD4] == old + 1 and memory[0x9BD2] == old + 1
    assert bytes(memory[0xA100:0xA102]) == b'\0\x80'
    return dict(old=old, amount=1, result=memory[0x9BD4], current=memory[0x9BD2],
                limit=memory[0x9BD3], kind=0, original_rule_byte=raw[0x741D])


def sell_twice(cargo):
    _, _, banks = make_context()
    lang = (ROOT / (ENTRIES[5]['path'] + '.sectors.bin')).read_bytes()
    assert len(lang) == 0x1000
    banks[6][:len(lang)] = lang
    memory = LangWorkspaceMemory(banks=[bank.copy() for bank in banks], out7ffd=0x16)
    cpu = Simulator(memory)
    cpu.set_tracer(PortTrace(cpu))
    memory.registers = cpu.registers
    memory[0x6306], memory[0x983A] = 0x16, 11
    memory[0x7026] = memory[0x7068] = 0
    memory[0x984A], memory[0x9851] = 255, 200
    for address, size in ((0x9852, 60), (0x988E, 52), (0x98F6, 14)):
        put(memory, address, bytes(size))
    put(memory, 0x984E, b'\0\0')
    memory[0x9555], memory[0x9556], memory[0x9852] = 10, 5, cargo
    put(memory, 0x6E8B, [10, 0])
    put(memory, 0x9CA6, [0xDE, 0xF3])
    put(memory, 0xF3DE, [0x8A, 0x6E, 1, 1])
    memory[0x9A82] = memory[0x6E91] = 0xA7
    outcomes = []
    for turn in range(2):
        put(memory, 0x7FFE, [255, 63])
        cpu.registers[:] = get_registers(dict(PC=0xC000, SP=0x7FFE, IX=0x2468, IY=0x5C3A), None, False)
        for _ in range(220000):
            if cpu.registers[PC] == 0x3FFF:
                break
            cpu.run()
        else:
            raise AssertionError(('Сценарий не вернулся', cargo, turn))
        assert cpu.registers[SP] == 0x8000
        assert bytes(memory.banks[6][0xA8F:0x1000]) == lang[0xA8F:0x1000]
        outcomes.append(dict(cargo=memory[0x9852], stock=memory[0x9555],
                             credits=int.from_bytes(memory[0x984E:0x9850], 'little')))
    expected = ([dict(cargo=128, stock=10, credits=640), dict(cargo=128, stock=10, credits=1280)]
                if cargo == 128 else [dict(cargo=0, stock=11, credits=5)] * 2)
    assert outcomes == expected, (cargo, outcomes)
    return outcomes


def main():
    rows = []
    for old in (0, 127):
        pickup = collect(old)
        rows.append(dict(pickup=pickup, sell_all_twice=sell_twice(pickup['result'])))
    report = dict(passed=True, profiles=rows, original_collection_and_lang_instructions=True,
                  original_trade_script_unchanged=True, inter_module_cargo_byte_passed_to_fixture=True,
                  docking_and_saved_context_transfer_executed=False,
                  lang_sector_tail_loaded_as_fixture=True,
                  complete_native_reachability_proved=False, intended_high_bit_purpose_proved=False,
                  irq_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/OwnedCargoHighBitCompositionVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Подтверждены сбор 127+1=#80 и две продажи #80 с кредитами 640 и 1280.')


if __name__ == '__main__':
    main()
