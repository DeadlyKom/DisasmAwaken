"""R, стек и исходные переходы семистрочного маркера.

Документация: ../../../Docs/MapPointMarker.md#r-и-пять-путей-отказа
"""
from hashlib import sha256
import collections
import json

from CheckMapPointMarker import ROOT, make_context, bitmap_address
from CheckMapRaster import ObservedMemory
from ReferenceControlsPointRespawn import refresh
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, PC, SP, R, I, IM, IFF, B, C, D, E


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    _, source, banks = make_context()
    entry = next(x for x in manifest['entries'] if x['slot'] == 7)
    assert bytes(source) == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    memory = ObservedMemory([0]*65536)
    memory[0x4000:0x8000] = banks[5]
    memory[0x8000:0xC000] = banks[2]
    memory[0xC000:0xC000+len(source)] = source
    cpu = Simulator(memory)
    memory[0x7FFE:0x8000] = [255, 63]
    cpu.registers[:] = get_registers(dict(SP=0x7FFE, DE=0), None, False)
    # Создание исходных таблиц для внутреннего начала X=8 и Y=16.
    cpu.run(start=0xC49B, stop=0x3FFF)
    memory[0x6300:0x6306] = [0x34, 0x78, 0x12, 0x56, 128, 96]
    sprite = bytes((i*73+19)&255 for i in range(128))
    memory[0xD800:0xD880] = sprite
    bitmap = bytes((i*53+(i>>8)*11+17)&255 for i in range(6912))
    flow = next(g for g in json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes()) if g['name'] == 'Map')
    code = {x['address']: bytes.fromhex(x['hex']) for x in flow['instructions']
            if x['slot'] == 7 and 0xC231 <= x['address'] < 0xC325}
    # Проверка физических инструкций, включая все общие хвосты развёрнутых строк.
    for address, raw in code.items():
        assert bytes(memory[address:address+len(raw)]) == raw
    counts = collections.Counter()
    costs = collections.defaultdict(set)
    initial_codes = collections.defaultdict(set)
    witnesses = []

    def execute(dx, dy, initial_r):
        px, py = (0x1234+dx+3)&65535, (0x5678+dy+3)&65535
        first, second = ((py>>8)<<8)|(px>>8), ((py&255)<<8)|(px&255)
        initial = get_registers(dict(PC=0xC231, SP=0x7FFE, HL=0xD800,
            DE=first, BC=second, AF=0x5A5C, IX=0x2468, IY=0x5C3A,
            I=0x3C, IM=2, IFF=0, R=initial_r,
            **{'^HL':0x369C, '^DE':0x47AD, '^BC':0x58BE, '^AF':0x69CF}), None, False)
        cpu.registers[:] = initial
        memory[0x4000:0x5B00] = bitmap
        memory[0x7FFE:0x8000] = [255, 63]
        memory.writes = []
        memory.recording = True
        m1, minimum_sp = 0, 0x7FFE
        for _ in range(256):
            pc = cpu.registers[PC]
            if pc == 0x3FFF:
                break
            assert pc in code and bytes(memory[pc:pc+len(code[pc])]) == code[pc]
            opcode = memory[pc]
            assert opcode not in (0xDD, 0xFD, 0xCB)
            assert bytes(memory[pc:pc+2]) not in (bytes.fromhex('ed4f'), bytes.fromhex('ed5f'))
            m1 += 2 if opcode == 0xED else 1
            cpu.opcodes[opcode]()
            assert cpu.registers[R] == refresh(initial_r, m1)
            minimum_sp = min(minimum_sp, cpu.registers[SP])
        else:
            raise AssertionError(('instruction_limit', dx, dy))
        memory.recording = False
        expected = bytearray(bitmap)
        addresses = []
        # Расчёт пути отказа независимо от исполненных PC и состояний флагов.
        if (dx&65535)>>8 or (dy&65535)>>8:
            kind, expected_m1 = 'word_reject', 33
        elif dx > 120:
            kind, expected_m1 = 'right_greater', 37
        elif dx == 120:
            kind, expected_m1 = 'right_equal', 38
        elif dy > 89:
            kind, expected_m1 = 'bottom_greater', 42
        elif dy == 89:
            kind, expected_m1 = 'bottom_equal', 43
        else:
            kind = 'draw'
            # Расчёт пересечений строковых групп и третей в шести переходах.
            boundaries = [q for q in range(16+dy+1, 16+dy+7) if q%8 == 0]
            thirds = sum(q%64 == 0 for q in boundaries)
            expected_m1 = 153+7*(len(boundaries)-thirds)+4*thirds
            phase = 16*(dx&7)
            for row in range(7):
                address = bitmap_address(16+dy+row, 1+dx//8)
                for byte in range(2):
                    addresses.append(address+byte)
                    expected[address+byte-0x4000] ^= sprite[phase+2*row+byte]
        r = cpu.registers
        assert m1 == expected_m1, (kind, dx, dy, m1, expected_m1)
        assert bytes(memory[0x4000:0x5B00]) == expected
        # Проверка полного множества записей без предположения о порядке шинных циклов PUSH.
        assert sorted(a for a, _ in memory.writes) == sorted(list(range(0x7FF8,0x7FFE))+addresses)
        assert minimum_sp == 0x7FF8 and r[SP] == 0x8000
        assert (r[I],r[IM],r[IFF]) == (initial[I],initial[IM],initial[IFF])
        assert r[8:12] == initial[8:12] and r[16:24] == initial[16:24]
        assert r[B]*256+r[C] == 0xD800
        counts[kind] += 1
        costs[kind].add(m1)
        initial_codes[kind].add(initial_r)
        if (dx in (0,7) and dy in (0,1,7,41,42,47,48,88)) or (kind != 'draw' and initial_r in (0,0x95)):
            witnesses.append(dict(path=kind,dx=dx,dy=dy,initial_R=initial_r,final_R=r[R],M1=m1,
                minimum_SP=minimum_sp,screen_writes=len(addresses)))

    # Проверка всех восьми фаз и всех допустимых строк исходного окна с тремя начальными R.
    for dx in range(8):
        for dy in range(89):
            for initial_r in (0,0x95,(dx*89+dy)&255):
                execute(dx,dy,initial_r)
    # Проверка каждого отдельного выхода при всех начальных значениях R.
    for dx,dy in ((256,0),(121,0),(120,0),(0,90),(0,89)):
        for initial_r in range(256):
            execute(dx,dy,initial_r)
    assert all(len(codes)==256 for codes in initial_codes.values())
    result = dict(passed=True,original_disk_sha256=manifest['sha256'],
        original_code_bytes_matched=sum(map(len,code.values())),cases_by_path=dict(counts),
        M1_by_path={k:sorted(v) for k,v in costs.items()},all_initial_R_codes_in_each_path=True,
        R_checked_after_every_instruction=True,temporary_stack_bytes=6,
        full_bitmap_and_write_addresses_checked=True,I_IM_IFF_preserved=True,
        original_viewport=[128,96],screen_origin=[8,16],drawn_phases=8,drawn_rows=89,
        all_input_words_or_viewports_proved=False,IRQ_executed=False,native_execution=False,
        assembly_executed=False,witnesses=witnesses)
    path = ROOT/'Tools/Disasm/Reports/MapPointMarkerRefreshVerification.json'
    if path.exists():
        assert json.loads(path.read_bytes()) == result
    else:
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='witnesses'},ensure_ascii=False))


if __name__ == '__main__':
    main()
