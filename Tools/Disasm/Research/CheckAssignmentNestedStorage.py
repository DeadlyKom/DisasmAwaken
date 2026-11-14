"""Физическая граница рабочей записи присваивания с вложенным RHS.

Документация: ../../../Docs/AssignmentPipeline.md#граница-вложенности-присваивания
"""
from hashlib import sha256
import json

from CheckExpressionControl import LangWorkspaceMemory, PC
from CheckAssignPipeline import ROOT, Simulator, get_registers, SP


class AssignmentMemory(LangWorkspaceMemory):
    """Расширяет окно учёта записей до максимальной глубины этой проверки."""

    def __setitem__(self, address, value):
        if 0xCA7B <= address < 0xCA99 and self.o7ffd & 7 == 6:
            self.writes.add(address)
        super().__setitem__(address, value)


def main():
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    sources = {entry['slot']: (ROOT / (entry['path'] + '.sectors.bin')).read_bytes()
               for entry in manifest['entries'] if entry['slot'] in (4, 5)}
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    # Сверка всех моделируемых секторных данных непосредственно с исходным образом.
    for entry in manifest['entries']:
        if entry['slot'] in sources:
            assert sources[entry['slot']] == disk[entry['offset']:entry['offset'] + entry['allocated_length']]
    flat = bytearray(65536)
    flat[0x6000:] = sources[4]
    flat[0xC000:0xC000 + len(sources[5])] = sources[5]
    fields = {'c': (0x984E, 2), 'u': (0x984B, 1), 'J': (0x9851, 1),
              'g': (0x9852, 1), 'G': (0x9555, 1),
              'o': (0x988E, 1), 'i': (0x98F6, 1)}
    profiles = []
    for field, (destination, size) in fields.items():
        for depth in range(7):
            rhs = '1'
            for _ in range(depth):
                rhs = '(1+' + rhs + ')'
            text = (field + ':' + rhs + '\x00').encode('ascii')
            for stack in (0x7FF0, 0xBFF0):
                banks = [bytearray(0x4000) for _ in range(8)]
                banks[5][:] = flat[0x4000:0x8000]
                banks[2][:] = flat[0x8000:0xC000]
                banks[6][:] = flat[0xC000:]
                memory = AssignmentMemory(banks=banks, out7ffd=0x16)
                # Сброс селекторов индексных полей, все семь путей используют первую запись.
                for address in (0x7068, 0x7026, 0x7217, 0x71B9, 0x73D8, 0x737D):
                    memory[address] = 0
                for offset in range(size):
                    memory[destination + offset] = 0
                for offset, value in enumerate(text):
                    memory[0xB000 + offset] = value
                memory[stack], memory[stack + 1] = 255, 63
                original_script = bytes(memory.banks[6][0xA8F:])
                initial = get_registers({'PC': 0xC09F, 'SP': stack, 'IX': 0xB000,
                                         'IY': 0x5C3A, '^HL': 0xB800}, None, False)
                cpu = Simulator(memory)
                cpu.registers[:] = initial
                memory.registers = cpu.registers
                # Исполнение ограничено входом NextCommand, сам сценарий после записи не запускается.
                for instructions in range(30000):
                    if cpu.registers[PC] == 0xC00C:
                        break
                    cpu.run()
                else:
                    raise AssertionError((field, depth, 'NextCommand not reached'))
                end = 0xCA81 + 4 * depth
                # Независимый расчёт по числу незавершённых троек Left, Operator, Right.
                assert memory.writes == set(range(0xCA7B, end)), (field, depth, memory.writes)
                value = sum(memory[destination + offset] << (8 * offset) for offset in range(size))
                assert value == depth + 1, (field, depth, value)
                assert cpu.registers[SP] == stack and cpu.registers[22:24] == [0xB8, 0]
                assert cpu.registers[8:10] == [0xB0, len(text) - 1]
                assert bytes(memory[stack:stack + 2]) == bytes((255, 63))
                # Проверка границы торгового сценария и сохранности всей остальной его части.
                overwritten = max(0, end - 0xCA8F)
                actual_script = bytes(memory.banks[6][0xA8F:])
                assert actual_script[overwritten:] == original_script[overwritten:]
                assert (actual_script != original_script) == bool(overwritten)
                profiles.append(dict(writer=field, nested_groups=depth, stack=stack,
                                     result=value, workspace_end_exclusive=end,
                                     script_bytes_written=overwritten, instructions=instructions))
    report = dict(passed=True, total_cases=len(profiles), profiles=profiles,
                  original_trd_sha256=sha256(disk).hexdigest(),
                  source_sha256={str(slot): sha256(data).hexdigest() for slot, data in sources.items()},
                  method='original_assignment_and_all_numeric_children_until_NextCommand',
                  all_seven_writers=True, maximum_nested_groups=6,
                  first_tested_depth_overwriting_script=4, calls_stubbed=False,
                  synthetically_nested_RHS=True, original_scripts_reaching_depth_4_proved=False,
                  arbitrary_expression_shapes_proved=False, all_registers_proved=False,
                  irq_executed=False, native_execution=False, assembly_executed=False)
    target = ROOT / 'Tools/Disasm/Reports/AssignmentNestedStorageVerification.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key not in ('profiles', 'source_sha256')},
                     ensure_ascii=False))


if __name__ == '__main__':
    main()
