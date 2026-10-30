"""Проверка трёх публичных музыкальных входов на оригинальных байтах MUZ1.C."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, PC, SP, D, E, F, IYh, IYl, IFF


class AyPorts:
    def __init__(self, source):
        self.events = []
        self.selected = 0
        self.registers = [0xFF] * 16
        self.source = source
        self.visited = {}

    def observe(self, memory, pc):
        # Сохранение только совпадающих исходных инструкций, изменённые операнды не выдаются за оригинал.
        offset = pc - 0xDB00
        if 0 <= offset <= len(self.source) - 4:
            data = bytes(memory[pc:pc + 4])
            if data == self.source[offset:offset + 4]:
                self.visited.setdefault(f"{pc:04X}", data.hex())

    def write_port(self, registers, port, value, offset):
        self.events.append(dict(port=port, value=value))
        # Проверка частично декодируемого адреса AY, OUTI использует в том числе зеркало #BEFD.
        if port & 0xC002 == 0xC000:
            self.selected = value & 15
        elif port & 0xC002 == 0x8000:
            self.registers[self.selected] = value


def word(memory, address):
    return memory[address] + 256 * memory[address + 1]


def invoke(simulator, address, limit=100000):
    memory = simulator.memory
    memory[0xBFFE:0xC000] = [0xFF, 0x3F]
    simulator.registers[SP] = 0xBFFE
    simulator.registers[PC] = address
    for steps in range(limit):
        if simulator.registers[PC] == 0x3FFF:
            if simulator.registers[SP] != 0xC000:
                raise ValueError("Не восстановлен музыкальный стек")
            return steps
        simulator.tracer.observe(memory, simulator.registers[PC])
        simulator.run()
    raise ValueError("Музыкальный вход не вернулся в установленной границе")


def require(condition, text):
    if not condition:
        raise ValueError(text)


def main():
    source = (ROOT / "Tools/Disasm/Extracted/Active/10_MUZ1.C.bin").read_bytes()
    memory = [0] * 65536
    memory[0xDB00:0xDB00 + len(source)] = source
    simulator = Simulator(memory)
    simulator.registers[:] = get_registers({"IY": 0x5C3A}, None, False)
    ports = AyPorts(source)
    simulator.set_tracer(ports)
    initialize_steps = invoke(simulator, 0xDB00)
    expected_mute = [item for register in range(13, -1, -1)
                     for item in (dict(port=0xFFFD, value=register), dict(port=0xBFFD, value=0))]
    require(ports.events == expected_mute, "Инициализация не завершилась обнулением 14 регистров AY")
    require(simulator.registers[IFF] == 0, "Инициализация неожиданно разрешила прерывания")
    # Проверка 48 абсолютных адресов, созданных из двух исходных таблиц указателей PT3.
    for index in range(48):
        expected = (word(memory, 0xE700 + 105 + 2 * index) + 0xE700) & 65535
        require(word(memory, 0xDBA0 + 2 * index) == expected, "Неверно преобразован указатель PT3")
    # Проверка последовательности позиций до первого возврата на петлю либо до явного ограничения.
    frames = []
    positions = []
    previous_position = word(memory, 0xDF98)
    looped = False
    for tick in range(12000):
        ports.events = []
        steps = invoke(simulator, 0xDB05)
        require(simulator.registers[IYh] * 256 + simulator.registers[IYl] == 0x5C3A,
                "Проигрыватель изменил IY")
        if tick < 150:
            frames.append(dict(tick=tick, steps=steps, port_writes=len(ports.events),
                               ay_registers=ports.registers[:14]))
        current_position = word(memory, 0xDF98)
        if current_position != previous_position:
            positions.append(dict(tick=tick, next_position_pointer=current_position))
            if current_position < previous_position:
                require(current_position == word(memory, 0xDF9F) + 1, "Возврат не совпал с исходным указателем петли")
                looped = True
                break
            previous_position = current_position
    require(looped, "За 12000 тиков не достигнута петля списка позиций")
    require(any(any(frame["ay_registers"][8:11]) for frame in frames), "За 150 тиков не появились ненулевые уровни каналов")
    # Проверка остановки именно через #DB08 и отсутствия изменений вне временного стека.
    ports.events = []
    before = memory.copy()
    stop_steps = invoke(simulator, 0xDB08)
    require(ports.events == expected_mute, "Вход #DB08 не обнулил 14 регистров AY")
    changes = [address for address, (left, right) in enumerate(zip(before, memory))
               if left != right and address not in (0xBFFE, 0xBFFF)]
    require(not changes, "Остановка звука неожиданно изменила память проигрывателя")
    # Проверка полей двух исполненных обработчиков длительностей независимо от текущей композиции.
    gate_checks = []
    for entry, destinations in ((0xDDCA, (0xDE97, 0xDE9F)), (0xDE0A, (0xE2E7, 0xE2E3))):
        for first, second in ((0, 0), (1, 255), (127, 2)):
            memory[0x7000:0x7002] = [first, second]
            simulator.registers[:] = get_registers({"DE": 0x7000, "F": 0xA5}, None, False)
            invoke(simulator, entry)
            require([memory[d] for d in destinations] == [first, second], "Не совпали поля длительностей канала")
            require(simulator.registers[E] == 2 and simulator.registers[D] == 0x70,
                    "Неверно продвинут поток длительностей")
            require(simulator.registers[F] == 0xA5, "Обработчик длительности изменил флаги")
            gate_checks.append(dict(entry=entry, first=first, second=second))
    report = dict(method="isolated_original_z80_bytes_and_ay_port_trace", real_audio_test=False,
                  full_tune_verified=False, source_sha256=hashlib.sha256(source).hexdigest(),
                  public_entries=dict(initialize=0xDB00, play_frame=0xDB05, stop=0xDB08),
                  initialize_steps=initialize_steps, absolute_pointers_checked=48,
                  ticks_checked=tick + 1, position_list_loop_verified=looped,
                  positions=positions, original_visited=ports.visited,
                  stop_steps=stop_steps, stop_port_writes=ports.events,
                  stop_memory_changes=changes, gate_checks=gate_checks, frames=frames, passed=True)
    (ROOT / "Tools/Disasm/Reports/MusicVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Music inputs verified: DB00 initialize, DB05 play, DB08 mute")
    print(f"Checked: 48 relocated pointers, {tick + 1} ticks to position loop, 28 mute port writes, restored SP, preserved IY")


if __name__ == "__main__":
    main()
