"""Полный локальный домен F211 для уже созданной физической записи.

Документация: ../../../Docs/ActionPeriodicClass3State.md#начальный-порог-состояния-02
Дополнительный контекст: ../../../Docs/ActionChildSpawn.md#начальный-байт-11-и-состояние-ребёнка
"""
from collections import Counter
from ReferenceControlsPointRespawn import cp_flags, refresh


def verify_local_threshold(memory, cpu, initial, child):
    # Порог читается из настоящего результата создателя, состояние обязано быть 02.
    assert memory[child + 10] == 2
    threshold = memory[child + 17]
    saved_banks = [bytearray(bank) for bank in memory.banks]
    branches = Counter()
    # Проверка каждого младшего байта и всех входных F на сохранённой дочерней записи.
    for low in range(256):
        for flags in range(256):
            registers = list(initial)
            registers[24] = 0xF211
            registers[0:2] = [0xA5, flags]
            registers[7] = low
            registers[8:10] = [child >> 8, child & 255]
            registers[14], registers[15] = (low + flags) & 255, (low + flags * 73) & 255
            registers[25], registers[26], registers[27] = flags * 17, flags & 1, flags % 3
            cpu.registers[:] = registers
            memory.writes = []
            memory.recording = True
            # Исполнение заканчивается на первой границе выбранного ребёнка.
            for _ in range(3):
                cpu.run()
            memory.recording = False
            expected = list(registers)
            expected[0:2] = [low, cp_flags(low, threshold)]
            expected[15] = refresh(registers[15], 4)
            expected[24] = 0xF217 if low < threshold else 0xF222
            expected[25] += 30 if low < threshold else 35
            assert list(cpu.registers) == expected, (low, flags, 'registers')
            assert not memory.writes and memory.o7ffd == 16
            assert memory.banks == saved_banks, (low, flags, 'RAM')
            branches['below' if low < threshold else 'at_or_above'] += 1
    return branches
