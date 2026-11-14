"""Независимое преобразование трёх векторов VOXAL0 с переносом накопителя IY.

Документация: ../../../Docs/VoxelBasisRotation.md#записи-стек-и-нулевые-углы
"""
from collections import Counter
import json
from math import cos, tau
from random import Random
from hashlib import sha256

from CheckEffects import ROOT, Simulator, get_registers, memory_image, seeded_formula, signed
from skoolkit.simutils import B, C, H, L, IYh, IYl, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def coefficients(source):
    values = tuple(source[0x2A00 + index] | source[0x2B00 + index] << 8 for index in range(256))
    assert tuple(map(signed, values)) == tuple(round(16384 * cos(tau * index / 256)) for index in range(256))
    return values


def reference(basis, angles, seed, table):
    words = list(basis)
    calls = []
    overflows = Counter()

    def product(left, right):
        nonlocal seed
        calls.append((left, right, seed))
        result = seeded_formula(left, right, seed)
        seed = (seed * 64 + 2 * abs(signed(left)) * (abs(signed(right)) & 63)) & 65535
        return result

    def add(first, second):
        total = signed(first) + signed(second)
        value = total & 65535
        if -32768 <= total <= 32767:
            return value
        overflows['positive' if total > 0 else 'negative'] += 1
        return 32767 if value == 32768 else (-value) & 65535

    def rotate(rows, angle, opposite):
        if angle == 0:
            return
        cosine, sine = table[angle], table[(angle - 64) & 255]
        first_sign = (-sine) & 65535 if opposite else sine
        second_sign = sine if opposite else (-sine) & 65535
        for column in range(3):
            first, second = (column * 3 + row for row in rows)
            x, y = words[first], words[second]
            words[first] = add(product(x, cosine), product(y, first_sign))
            words[second] = add(product(x, second_sign), product(y, cosine))

    rotate((0, 1), angles[2], False)
    stage1 = words[0::3] + words[1::3]
    rotate((1, 2), angles[0], False)
    stage2 = words[2::3]
    rotate((0, 2), angles[1], True)
    return words, seed, calls, stage1 + stage2, overflows


def main():
    source = (ROOT / 'Tools/Disasm/Extracted/Active/20_VOXAL0.C.bin').read_bytes()
    table = coefficients(source)
    original = memory_image()
    scratch = (0xE7AF, 0xE801, 0xE853, 0xE67B, 0xE6CD, 0xE71F, 0xE7BA, 0xE80C, 0xE85E)
    rng = Random(0xE500)
    calls = 0
    overflows = Counter()
    costs = []
    depths = []
    zero_costs = set()
    case_count = 0

    def check(basis, angles, seed):
        nonlocal calls, case_count
        memory = Memory(original)
        memory[0x9B00:0x9B12] = b''.join(word.to_bytes(2, 'little') for word in basis)
        memory[0x9B12:0x9B15] = angles
        simulator = Simulator(memory)
        r = simulator.registers
        initial = get_registers({'PC': 0xE500, 'SP': 0xBFFE, 'IY': seed, 'IX': 0x1357,
            'HL':0x1357, 'DE':0x2468, 'BC':0x369C, 'AF':0x5A00 | (case_count & 255),
            'I':case_count & 255, 'R':case_count & 255, '^AF':0xA55A,
            '^HL':0x2468, '^DE':0x369C, '^BC':0x47AD}, {'im':case_count % 3, 'iff':case_count & 1}, False)
        r[:] = initial
        words, ending_seed, products, stage_words, branch_counts = reference(basis, angles, seed, table)
        expected = list(memory)
        for address,value in zip(range(0x9B00,0x9B12,2), words):
            expected[address:address+2] = value.to_bytes(2,'little')
        for address,value in zip(scratch,stage_words):
            expected[address:address+2] = value.to_bytes(2,'little')
        if products:
            expected[0xE913] = (4 * abs(signed(products[-1][1]))) & 255
        memory.writes = []
        memory.recording = True
        m1 = depth = 0
        product_index = 0
        for _ in range(10000):
            if r[PC] == 0x3FFF:
                break
            if r[PC] == 0xE8A1:
                actual = (r[H] * 256 + r[L], r[B] * 256 + r[C], r[IYh] * 256 + r[IYl])
                assert product_index < len(products) and actual == products[product_index], (
                    angles, product_index, actual, products[product_index])
                product_index += 1
            # Подсчёт физических M1 по извлечённым опкодам, время тактов не моделируется.
            m1 += 2 if memory[r[PC]] in (0xCB,0xDD,0xED,0xFD) else 1
            simulator.run()
            depth = max(depth,0xBFFE-r[SP])
        else:
            raise AssertionError(('предел вращения', angles))
        memory.recording = False

        def word(address):
            return memory[address] + 256 * memory[address + 1]

        assert [word(address) for address in range(0x9B00, 0x9B12, 2)] == words
        actual_scratch = [word(address) for address in scratch]
        assert actual_scratch == stage_words, (angles, actual_scratch, stage_words)
        assert r[IYh] * 256 + r[IYl] == ending_seed and r[SP] == 0xC000
        assert r[8:10] == [0x13, 0x57] and product_index == len(products)
        assert all(r[i] == initial[i] for i in (14,26,27))
        assert r[15] == refresh(initial[15],m1)
        # Проверка неизменности RAM вне четырёх временных байтов CPU-стека.
        expected[0xBFFA:0xBFFE] = memory[0xBFFA:0xBFFE]
        assert memory == expected, angles
        addresses = Counter(address for address,value in memory.writes if not 0xBFFA <= address < 0xBFFE)
        wanted = Counter(dict.fromkeys(range(0x9B00,0x9B12),1))
        wanted.update({address+offset:1 for address in scratch for offset in (0,1)})
        if products:
            wanted[0xE913] = len(products)
        assert addresses == wanted, (angles,addresses-wanted,wanted-addresses)
        assert depth == (4 if products else 0)
        if not products:
            assert r[IYh]*256+r[IYl] == seed and r[16:24] == initial[16:24]
            assert r[0:8] == [0,0x54,*initial[2:6],words[-1]>>8,words[-1]&255]
            zero_costs.add(m1)
        costs.append(m1)
        depths.append(depth)
        case_count += 1
        calls += product_index
        overflows.update(branch_counts)

    edge = (0x8000, 0x7FFF, 0x4000, 0x3FFF, 0xFFFF, 0, 0xC000, 1, 0x8001)
    for axis in range(3):
        for angle in range(256):
            angles = [0, 0, 0]
            angles[axis] = angle
            check(edge, angles, (angle * 251) & 65535)
    for _ in range(1024):
        check(tuple(rng.randrange(65536) for _ in range(9)),
              [rng.randrange(256) for _ in range(3)], rng.randrange(65536))
    for seed in (1,127,128,255,256,32767,32768,65535):
        check(edge,[0,0,0],seed)
    assert overflows['positive'] and overflows['negative']
    report = dict(passed=True, total_cases=case_count, coefficients=256,
                  all_angles_per_axis=True, mixed_random_profiles=1024,
                  exact_product_arguments_and_seed=True, child_product_calls=calls,
                  exact_nine_final_and_nine_scratch_words=True, overflows=dict(overflows),
                  other_final_registers_independently_proved=False, assembly_executed=False, native_execution=False,
                  original_rotation_sha256=sha256(source[0x2500:0x28A1]).hexdigest(),
                  RAM_except_four_CPU_stack_bytes_compared=True, exact_nonstack_write_counts_checked=True,
                  maximal_CPU_stack_depth=max(depths), zero_angles_M1=sorted(zero_costs),
                  measured_M1_range=[min(costs),max(costs)],
                  R_checked_against_executed_opcode_M1=True, I_IM_IFF_preserved=True,
                  zero_angles_nonzero_IY_and_alternate_context_preserved=True,
                  independent_M1_formula_for_all_nonzero_paths_proved=False, IRQ_executed=False)
    (ROOT / 'Tools/Disasm/Reports/VoxelBasisRotationVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
