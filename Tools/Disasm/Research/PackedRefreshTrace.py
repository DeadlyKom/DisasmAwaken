"""Подсчёт M1 по исходным кодам HR, отдельно от изменения R симулятором.

Документация: ../../../Docs/UnpackResource.md#регистр-обновления-r
"""
from collections import Counter


class PackedRefreshTrace:
    def __init__(self, instructions, initial_r):
        self.instructions = {row['address']: bytes.fromhex(row['hex']) for row in instructions}
        self.initial_r = initial_r
        self.m1 = 0
        self.steps = 0
        self.prefix_counts = Counter()

    def before(self, memory, pc, r):
        # Проверка физического кода, включая каждое повторное выполнение LDIR/LDDR.
        raw = self.instructions[pc]
        assert bytes(memory[pc:pc + len(raw)]) == raw, ('изменён код HR', pc)
        assert raw not in (bytes.fromhex('ed4f'), bytes.fromhex('ed5f'))
        # Подсчёт выборок префикса и команды, DD CB с адресной формой здесь отсутствует.
        if raw[0] in (0xCB, 0xDD, 0xED, 0xFD):
            assert raw[1] not in (0xCB, 0xDD, 0xED, 0xFD)
            self.increment = 2
        else:
            self.increment = 1
        self.previous_r = r
        self.prefix_counts[raw.hex()] += 1

    def after(self, r):
        # Проверка каждого приращения и сохранности bit7, не только конечного остатка.
        expected = (self.previous_r & 0x80) | ((self.previous_r + self.increment) & 0x7F)
        assert r == expected, ('R после команды HR', r, expected)
        self.m1 += self.increment
        self.steps += 1

    def finish(self, r):
        expected = (self.initial_r & 0x80) | ((self.initial_r + self.m1) & 0x7F)
        assert r == expected
        return dict(initial_R=self.initial_r, final_R=r, m1=self.m1,
                    stepped_instructions=self.steps)
