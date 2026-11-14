"""Все значения одного кода в исходном снимке, включая ключ за физической таблицей.

Документация: ../../../Docs/AuxiliaryMapPoints.md#полный-байтовый-домен-отдельного-кода
"""
from collections import Counter
from hashlib import sha256
import json

from CheckMapScene import ROOT, marker
from CheckRowHighlight import make_context
from CheckStationFlightCycle import payload
from CheckMusic import Simulator, get_registers, PC, SP


def main():
    _,source,banks = make_context()
    assert bytes(source)==payload(7)
    memory = bytearray(65536)
    memory[0x4000:0x8000] = bytes(banks[5])
    memory[0x8000:0xC000] = bytes(banks[2])
    memory[0xC000:0xC000+len(source)] = source
    cpu = Simulator(memory)
    initial = get_registers(dict(SP=0x7FFE,HL=0x1357,DE=0,BC=0x369C,
        AF=0x5A5D,IX=0x2468,IY=0x5C3A),None,False)
    memory[0x7FFE:0x8000] = bytes.fromhex('ff3f')
    cpu.registers[:] = initial
    cpu.run(0xC49B,0x3FFF)
    cpu.registers[:] = initial
    cpu.registers[6],cpu.registers[7] = 95,127
    cpu.run(0xD0C3,0x3FFF)
    memory[0x6300:0x6306] = bytes.fromhex('fdfdffff8060')
    bitmap = bytes((i*73+19)&255 for i in range(6912))
    memory[0x4000:0x5B00] = bitmap
    baseline = memory.copy()
    original_codes = bytes(memory[0x99A3:0x99AF])
    assert original_codes==bytes([0,0]+[1]*8+[0,0x81])
    cases = outside_key_calls = 0
    outcomes = Counter()
    for position in range(11):
        for value in range(256):
            memory[:] = baseline
            memory[0x99A3+position] = value
            snapshot = bytes(memory[0x997B:0x99AF])
            expected = bytearray(bitmap)
            calls = []
            # Поиск отрицательной границы и расчёт фактически выбранных четырёхбайтовых ключей.
            for index,code in enumerate(memory[0x99A3:0x99AF]):
                if code>=128:
                    stop_index = index
                    break
                if code==0:
                    continue
                address = 0x997B+4*index
                a,b,c,d = memory[address:address+4]
                calls.append((address,a,b,c,d))
                marker(expected,source,0xCEC3,a*256+c,b*256+d,0xFFFD,0xFFFD,128,96)
            else:
                raise AssertionError('Исходный соседний 81 должен завершить проход')
            cpu.registers[:] = initial
            cpu.registers[PC] = 0xC0F9
            observed = []
            for _ in range(30000):
                pc = cpu.registers[PC]
                if pc==0xC124:
                    break
                if pc==0xC231:
                    r = cpu.registers
                    observed.append((r[8]*256+r[9],r[5],r[4],r[3],r[2]))
                cpu.run()
            else:
                raise AssertionError((position,value,'Цикл не завершился'))
            # Проверка исходных вызовов рисователя, выхода и сохранения входных данных.
            assert observed==calls,(position,value,observed,calls)
            assert cpu.registers[SP]==0x7FFE
            assert cpu.registers[8]*256+cpu.registers[9]==0x997B+4*stop_index
            assert cpu.registers[6]*256+cpu.registers[7]==0x99A4+stop_index
            assert memory[0x4000:0x5B00]==expected,(position,value,'экран')
            assert bytes(memory[0x997B:0x99AF])==snapshot,(position,value,'входные данные')
            outside_key_calls += any(address==0x99A3 for address,*_ in calls)
            outcomes['zero' if value==0 else 'positive' if value<128 else 'negative'] += 1
            cases += 1
    assert cases==2816 and outside_key_calls==127
    report = dict(passed=True,cases=cases,positions=11,values_per_position=256,
        code_value_counts=dict(outcomes),positive_last_code_reads_codes_as_key_cases=outside_key_calls,
        physical_map_sha256=sha256(source).hexdigest(),
        entry=0xC0F9,stop=0xC124,viewport=[128,96],origin=[0xFFFD,0xFFFD],
        actual_marker_without_stubs=True,exact_marker_arguments_and_stop_pointers=True,
        bitmap_and_attributes_compared=True,input_keys_codes_and_adjacent_guard_preserved=True,
        full_joint_code_space_exhausted=False,global_unknown_field_roles_proved=False,
        IRQ_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/MapAuxiliaryCodeDomainVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
