"""Исходный запуск ENGINE, экран, IM2, сохранение регистров и таймер."""
import json

from CheckBankStripArchiveConsumer import ArchivePorts, ExtendedMemory
from CheckFighterArchiveConsumer import word
from CheckStationFlightCycle import DISK, put, run_to
from TraceFlight import A, IFF, PC, ROOT, SP, T, Simulator
from skoolkit.simutils import B, C, D, E, H, HALT, I, IM, L


ENGINE = DISK[0x8B100:0x8C15B]
RETURN = 0x5BFF
STACK = 0x6000


class EngineMemory(ExtendedMemory):
    stack_writes = None
    instruction_pc = None

    def observe_instruction(self, pc):
        self.instruction_pc = pc

    def __setitem__(self, address, value):
        super().__setitem__(address, value)
        if self.stack_writes is not None and 0x4500 <= address < 0x463F:
            self.stack_writes.setdefault(address, set()).add(self.instruction_pc)


def enter_call(cpu, address):
    put(cpu.memory, STACK - 2, RETURN.to_bytes(2, 'little'))
    cpu.registers[SP] = STACK - 2
    cpu.registers[PC] = address


def call(cpu, address):
    enter_call(cpu, address)
    run_to(cpu, RETURN)
    assert cpu.registers[SP] == STACK


def init_prefix(mode):
    memory = EngineMemory()
    put(memory, 0x4000, ENGINE)
    memory[0x5F5E] = mode
    cpu = Simulator(memory, {'PC': 0x4000, 'SP': 0x6790},
                    config={'fast_ldir': False, 'fast_djnz': False})
    memory.cpu = cpu
    cpu.set_tracer(ArchivePorts(memory))
    run_to(cpu, 0x4024)
    assert cpu.registers[SP] == STACK
    assert word(memory, 0x503E) == 0x4842 ^ 0x4895
    assert word(memory, 0x4FB6) == (0x4FB8, 0x4FCF, 0x4FE5)[mode]
    return cpu


def check_screen_and_vector(cpu):
    memory, registers = cpu.memory, cpu.registers
    shadow = memory.banks[7]
    shadow[:] = b'\xA5' * len(shadow)
    main = bytearray(memory.banks[5][:0x1B00])
    # Код селектора расположен в основном экране и сохраняет выбранную страницу.
    main[0x5012 - 0x4000] = 7
    call(cpu, 0x4072)
    assert memory.o7ffd == 0x1F and cpu.tracer.pages == [0x1F]
    assert bytes(shadow) == bytes(0x1800) + b'\x07' * 0x300 + b'\xA5' * 0x2500
    assert bytes(memory.banks[5][:0x1B00]) == main
    assert tuple(registers[i] for i in (H, L, D, E, B, C)) == (0xDA, 0xFF, 0xDB, 0x00, 0, 0)

    memory[0x5DFF], memory[0x5F01], memory[0x5F5E], memory[0x5F62] = 0xB1, 0xB2, 0xB3, 0xB4
    call(cpu, 0x40B1)
    assert (registers[I], registers[IM], registers[IFF]) == (0x5E, 2, 1)
    assert tuple(registers[i] for i in (H, L, D, E, B, C, A)) == (0x46, 0x3F, 0x5F, 1, 0, 0, 0x5E)
    assert bytes(memory[0x5E00:0x5F01]) == b'\x5F' * 257
    assert bytes(memory[0x5F5F:0x5F62]) == bytes.fromhex('C3 3F 46')
    assert [memory[a] for a in (0x5DFF, 0x5F01, 0x5F5E, 0x5F62)] == [0xB1, 0xB2, 0xB3, 0xB4]


def check_interrupts(cpu):
    memory, registers, ports = cpu.memory, cpu.registers, cpu.tracer
    call(cpu, 0x4A8A)
    assert bytes(memory[0x4C8A:0x4C8C]) == b'\x99\x32'
    locations = {}
    for page in range(16):
        registers[A] = page
        call(cpu, 0x4FB1)
        selector = 0x18 | (page & 7) | ((page & 8) << 3)
        assert memory.o7ffd == selector
        for index in (*range(12), *range(16, 24)):
            registers[index] = (page * 53 + index * 37) & 255
        preserved = tuple(registers[index] for index in (*range(12), *range(16, 24)))
        registers[PC] = RETURN
        registers[T] = (registers[T] // cpu.frame_duration + 1) * cpu.frame_duration
        assert registers[IFF]
        ports.pages.clear()
        memory.stack_writes = {}
        assert cpu.accept_interrupt(registers, memory, 0x4048) and registers[PC] == 0x5F5F
        assert registers[SP] == 0x5FFE and word(memory, 0x5FFE) == RETURN
        run_to(cpu, RETURN, memory.observe_instruction)
        assert word(memory, 0x4669) == 0x5FFE and registers[SP] == STACK
        assert tuple(registers[index] for index in (*range(12), *range(16, 24))) == preserved
        assert registers[IFF] and registers[IM] == 2 and registers[I] == 0x5E
        assert ports.pages == [0x1F, selector] and memory.o7ffd == selector
        assert memory[0x5012] == memory[0x5013] == page
        assert memory[0x4C8B] == 49 - page and memory[0x4C8A] == 0x99
        start = min(memory.stack_writes)
        assert set(memory.stack_writes) == set(range(start, 0x463F))
        for address, writers in memory.stack_writes.items():
            locations.setdefault(address, set()).update(writers)
        memory.stack_writes = None
    assert set(locations) == set(range(0x4627, 0x463F))
    assert ENGINE[0x0627:0x063F] == bytes(24)
    word_writers = {f'{address:04X}': sorted(locations[address]) for address in range(0x4627, 0x463F, 2)}
    assert all(locations[address] == locations[address + 1] for address in range(0x4627, 0x463F, 2))
    assert list(word_writers.values()) == [
        [0x4FB4], [0x442E, 0x4435, 0x4CDF, 0x4CE2, 0x4CE5, 0x4CEB], [0x4653, 0x4656, 0x4659],
        [0x4652], [0x4651], [0x4650], [0x464F], [0x464C], [0x464B], [0x464A], [0x4649], [0x4647]]
    return dict(logical_pages=16, stack_start=0x4627, stack_end_exclusive=0x463F,
                stack_word_writers=word_writers,
                return_stack_operand=0x4669, main_and_alternate_registers_preserved=True)


def check_timer(cpu):
    memory, registers = cpu.memory, cpu.registers
    stopped = 0
    for seconds in range(100):
        for ticks in range(1, 51):
            memory[0x4C8A] = int(f'{seconds:02d}', 16)
            memory[0x4C8B] = ticks
            registers[IFF] = 1
            if seconds == 0 and ticks == 1:
                enter_call(cpu, 0x4A5C)
                run_to(cpu, 0x4A83)
                assert registers[IFF] == 0
                cpu.run()
                assert registers[HALT] and registers[PC] == 0x4A83
                registers[HALT] = 0
                stopped += 1
            else:
                call(cpu, 0x4A5C)
                assert registers[IFF] == 1
            expected = max(0, seconds - (ticks == 1))
            assert memory[0x4C8A] == int(f'{expected:02d}', 16)
            assert memory[0x4C8B] == (ticks - 1 or 50)
    assert stopped == 1
    call(cpu, 0x4A8A)
    for irq in range(1, 5000):
        call(cpu, 0x4A5C)
        assert (memory[0x4C8A] == 0) == (irq >= 4950)
    enter_call(cpu, 0x4A5C)
    run_to(cpu, 0x4A83)
    cpu.run()
    assert registers[HALT] and registers[PC] == 0x4A83 and registers[IFF] == 0
    return dict(seconds_values=100, irq_subticks=50, cases=5000, stopped_cases=stopped,
                zero_reached_after_irqs=4950, halt_after_irqs=5000, halt_pc=0x4A83)


def check_separate_transfer():
    cpu = init_prefix(0)
    memory, registers = cpu.memory, cpu.registers
    marker = bytes(range(0x91, 0xA1))
    put(memory, 0x5C26, marker)
    memory.out7ffd(0x5D)
    registers[PC] = 0x40A9
    run_to(cpu, 0x5C26)
    assert cpu.tracer.pages == [0x18] and memory[0x5012] == 0 and registers[SP] == STACK
    assert bytes(memory[0x5C26:0x5C36]) == marker
    assert b'\xA9\x40' not in ENGINE
    return dict(entry=0x40A9, destination=0x5C26, incoming_literal_in_engine=False,
                destination_untouched=True, destination_execution_proved=False)


def main():
    modes = [init_prefix(mode) for mode in range(3)]
    cpu = modes[0]
    check_screen_and_vector(cpu)
    irq = check_interrupts(cpu)
    timer = check_timer(cpu)
    result = dict(passed=True, memory_mode_targets=[word(cpu.memory, 0x4FB6) for cpu in modes],
                  shadow_bitmap_bytes=6144, shadow_attribute_bytes=768, im2_vector_bytes=257,
                  irq=irq, timer=timer, separate_transfer=check_separate_transfer(),
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveEngineStartupVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
