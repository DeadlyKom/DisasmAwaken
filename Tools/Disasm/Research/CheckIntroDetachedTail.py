"""Условное исполнение замкнутых последовательностей из хвоста AWAKEN.B."""
import json
import re

from CheckIntro import A, PC, ROOT, SP, Simulator, execute, original_memory
from skoolkit.pagingtracer import Memory
from skoolkit import ROM48, ROM128
from skoolkit.simutils import F, IFF, get_registers


WAIT = 0x74CD
POLL = 0x74D1
KEY_BYTE = 0x5C08
COPY_TO_BANK = 0x74D8
COPY_FROM_BANK = 0x74E4
RETURN = 0x3FFF


def check_wait(image):
    memory = image.copy()
    sim = Simulator(memory)
    for key in range(1, 256):
        memory[KEY_BYTE] = key ^ 255
        sim.registers[:] = get_registers({'PC': WAIT, 'SP': 0xBFFE, 'AF': key * 256 + 0xFF}, None, False)
        before = sim.registers.copy()
        poll_count = 0
        for _ in range(15):
            if sim.registers[PC] == RETURN:
                break
            if sim.registers[PC] == POLL:
                assert memory[KEY_BYTE] == 0
                poll_count += 1
                if poll_count == 3:
                    memory[KEY_BYTE] = key
            sim.run()
        else:
            raise AssertionError(key)
        flags = (key & 0xA8) | (4 if key.bit_count() % 2 == 0 else 0)
        assert poll_count == 3 and memory[KEY_BYTE] == key
        assert sim.registers[A:F + 1] == [key, flags] and sim.registers[SP] == 0xC000
        assert sim.registers[2:12] == before[2:12] and sim.registers[16:24] == before[16:24]
    expected = image.copy()
    expected[KEY_BYTE] = 255
    assert memory == expected
    return 255


class KeyMemory(list):
    def __setitem__(self, address, value):
        if address == KEY_BYTE and hasattr(self, 'registers'):
            self.key_writes.append((self.registers[PC], value))
        super().__setitem__(address, value)


class KeyboardMatrix:
    def __init__(self, key):
        self.key = key
        self.reads = []

    def read_port(self, registers, port):
        self.reads.append(port)
        if self.key is not None and not port & 1:
            row, bit = self.key
            if not port & (1 << (8 + row)):
                return 255 ^ (1 << bit)
        return 255


def check_rom_wait(image):
    matrix = (b'\x00zxcv', b'asdfg', b'qwert', b'12345', b'09876', b'poiuy', b'\rlkjh', b' \x00mnb')
    keys = [(None, 0)] + [((row, bit), code) for row, keys in enumerate(matrix) for bit, code in enumerate(keys)]
    result = []
    for rom_path in (ROM48, ROM128[1]):
        with open(rom_path, 'rb') as handle:
            rom = handle.read()
        assert rom[0x0308:0x030B] == bytes.fromhex('32 08 5c')
        for key, expected in keys:
            memory = KeyMemory(image)
            memory[:0x4000] = rom
            memory[0x5C00] = memory[0x5C04] = 255
            memory[0x5C3B] = 8
            memory[KEY_BYTE] = 0xA5
            sim = Simulator(memory, {'PC': WAIT, 'SP': 0xBFFE, 'IY': 0x5C3A}, {'iff': 1, 'im': 1})
            matrix_input = KeyboardMatrix(key)
            sim.set_tracer(matrix_input)
            registers = sim.registers
            memory.registers, memory.key_writes = registers, []
            for _ in range(5):
                sim.run()
            assert registers[PC] == POLL and memory[KEY_BYTE] == 0 and registers[IFF]
            assert sim.accept_interrupt(registers, memory, 0x74D5)
            for _ in range(1000):
                if registers[PC] == POLL:
                    break
                sim.run()
            else:
                raise AssertionError((rom_path, key, registers[PC]))
            writes = [(0x74CE, 0)] + ([(0x0308, expected)] if expected else [])
            assert memory.key_writes == writes and memory[KEY_BYTE] == expected
            assert matrix_input.reads == [0xFEFE, 0xFDFE, 0xFBFE, 0xF7FE, 0xEFFE, 0xDFFE, 0xBFFE, 0x7FFE]
            assert registers[SP] == 0xBFFE and registers[IFF]
            for _ in range(4 if expected else 3):
                sim.run()
            if expected:
                flags = (expected & 0xA8) | (4 if expected.bit_count() % 2 == 0 else 0)
                assert registers[PC] == RETURN and registers[SP] == 0xC000
                assert registers[A:F + 1] == [expected, flags]
            else:
                assert registers[PC] == POLL and registers[SP] == 0xBFFE
        result.append(dict(rom='48.rom' if rom_path == ROM48 else '128-1.rom', cases=len(keys),
                           returns=sum(bool(expected) for _, expected in keys), writer_pc=0x0308))
    return result


def check_copies(image):
    cases = 0
    for bank in range(8):
        for start, source, target in ((COPY_TO_BANK, 5, bank), (COPY_FROM_BANK, bank, 5)):
            for accumulator, flags in ((0x18, 0), (0xF7, 255)):
                banks = [bytearray(0x4000) for _ in range(8)]
                memory = Memory(banks=banks, out7ffd=0x10 | bank)
                for index, data in enumerate(banks):
                    data[:6912] = bytes((index * 37 + position * 19) & 255 for position in range(6912))
                banks[5][0x34CD:0x34EC] = image[WAIT:0x74EC]
                memory[0xBFFE], memory[0xBFFF] = RETURN & 255, RETURN >> 8
                expected = [data.copy() for data in banks]
                expected[target][:6912] = banks[source][:6912]
                sim = Simulator(memory, {'PC': start, 'SP': 0xBFFE, 'AF': accumulator * 256 + flags})
                for _ in range(6912 + 6):
                    if sim.registers[PC] == RETURN:
                        break
                    sim.run()
                else:
                    raise AssertionError((start, bank))
                final_sum = accumulator + banks[source][6911]
                expected_flags = (flags & 0xC1) | ((final_sum & 2) << 4) | (final_sum & 8)
                pointers = [0xDB, 0, 0x5B, 0] if start == COPY_TO_BANK else [0x5B, 0, 0xDB, 0]
                assert sim.registers[:8] == [accumulator, expected_flags, 0, 0, *pointers]
                assert sim.registers[SP] == 0xC000 and banks == expected and memory.o7ffd == 0x10 | bank
                cases += 1
    return cases


def main():
    image = original_memory()
    expected = bytes(image[0x8FCD:0x8FEC])
    assert expected == bytes.fromhex('af32085c3a085cb728fac9 2100401100c001001bedb0c9 2100c011004018f2')
    execute(image, {'PC': 0x651D}, stop=0x6528)
    assert bytes(image[WAIT:0x74EC]) == expected
    regions = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    observed = [region for region in regions if region['name'] in ('Basic', 'Intro', 'IntroUnpack')]
    assert len(observed) == 3
    branch = re.compile(r'^(?:CALL|JR|JP|DJNZ) (?:[A-Z]+,\s*)?#([0-9A-F]{4})$')
    for region in observed:
        for instruction in region['instructions']:
            if region['name'] == 'IntroUnpack' and instruction['offset'] >= 0x2CCD:
                continue
            match = branch.fullmatch(instruction['operation'])
            assert not match or not WAIT <= int(match[1], 16) < 0x74EC
    wait_cases, copy_cases = check_wait(image), check_copies(image)
    rom_cases = check_rom_wait(image)
    proof = dict(passed=True, total_cases=wait_cases + copy_cases, wait_cases=wait_cases,
                 screen_copy_cases=copy_cases, bounded_bytes=len(expected),
                 addresses=[WAIT, COPY_TO_BANK, COPY_FROM_BANK], physical_offset=0x2CCD,
                 original_relocation_executed=True, direct_entry_from_registered_intro_code=False,
                 byte_injected_in_exhaustive_255_value_profiles=True, original_keyboard_irq_profiles=rom_cases,
                 game_callers_proved=False, assembly_executed=False,
                 native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/IntroDetachedTailVerification.json'
    path.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
