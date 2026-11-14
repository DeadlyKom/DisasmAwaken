"""R и рамки возвратов исходной группы отсечения карты.

Документация: ../../../Docs/ClipCases.md#r-и-рамки-возвратов
"""
from hashlib import sha256
import json

from CheckClipSegment import ROOT, Simulator, get_registers, make_context, record, outcode
from CheckGlyphRenderer import compare_flags
from ReferenceControlsPointRespawn import refresh
from skoolkit.simutils import PC, SP, R, A, F, H, L, B, C, I, IM, IFF


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    # Проверка физических источников KARTA и станционного фиксированного окна.
    for slot in (4,7):
        row = next(x for x in manifest['entries'] if x['slot'] == slot)
        assert (ROOT/(row['path']+'.sectors.bin')).read_bytes() == disk[row['offset']:row['offset']+row['allocated_length']]
    _,source,banks = make_context()
    original = bytearray(65536)
    original[0x4000:0x8000],original[0x8000:0xC000] = bytes(banks[5]),bytes(banks[2])
    original[0xC000:0xC000+len(source)] = source
    flow = next(x for x in json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes()) if x['name'] == 'Map')
    # Проверка исходных инструкций диспетчера, всех случаев и арифметических помощников.
    checked_bytes = 0
    for row in flow['instructions']:
        if row['slot'] == 7 and 0xD48B <= row['address'] < 0xDDB0:
            raw = bytes.fromhex(row['hex'])
            assert original[row['address']:row['address']+len(raw)] == raw
            checked_bytes += len(raw)
    common = bytes.fromhex('3a3bde d1 d1 fe04 c9')
    assert original[0xD4DD:0xD4E5] == common
    profiles = []

    def execute(kind,start,stack,initial_r,size,first=None,second=None,block=0):
        memory = bytearray(original)
        memory[0xDE3B] = size
        memory[0xDE39],memory[0xDE3A] = 0xFF,block
        if first is not None:
            memory[0xDE2F:0xDE39] = record(first)+record(second)
        memory[stack:0x8000] = (bytes.fromhex('ddd4')*((0x7FFE-stack)//2))+bytes.fromhex('ff3f')
        cpu = Simulator(memory)
        cpu.registers[:] = get_registers(dict(PC=start,SP=stack,HL=0x1357,DE=0x247A,
            BC=0x36C9,AF=0x5A5D,IX=0x2468,IY=0x5C3A,I=0x3C,IM=2,IFF=0,R=initial_r,
            **{'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF}),None,False)
        initial = cpu.registers[:]
        m1 = 0
        # Подсчёт M1 по достигнутым опкодам, повторные префиксы и LD R,A исключаются.
        for _ in range(20000):
            pc = cpu.registers[PC]
            if pc == 0x3FFF:
                break
            opcode = memory[pc]
            if opcode in (0xDD,0xFD):
                assert memory[(pc+1)&65535] not in (0xDD,0xFD,0xED,0xCB)
            assert memory[pc:pc+2] not in (b'\xed\x4f',b'\xed\x5f')
            m1 += 2 if opcode in (0xCB,0xED,0xDD,0xFD) else 1
            cpu.opcodes[opcode]()
            assert cpu.registers[R] == refresh(initial_r,m1)
        else:
            raise AssertionError(('instruction_limit',kind,start))
        r = cpu.registers
        assert r[SP] == 0x8000
        assert (r[I],r[IM],r[IFF]) == (initial[I],initial[IM],initial[IFF])
        assert r[10:12] == initial[10:12] and r[18:24] == initial[18:24]
        output_size = memory[0xDE3B]
        normal = (r[A],r[F]) == (output_size,compare_flags(output_size,4))
        special = (r[A],r[F],r[H]*256+r[L],r[B]*256+r[C]) == (0xD4,0x81,0xD5B0,0xD3)
        assert normal or special
        if kind == 'common_return':
            assert normal and output_size == size and m1 == 5
        profiles.append(dict(kind=kind,entry=start,initial_R=initial_r,final_R=r[R],
            observed_M1=m1,first=first,second=second,corner_block=block,
            normal_return=normal,special_return=special,output_size=output_size,
            input_SP=stack,final_SP=r[SP]))

    # Проверка независимого договора общего возврата при всех байтовых размерах.
    for size in range(256):
        for initial_r in (0,0x95):
            execute('common_return',0xD4DD,0x7FFA,initial_r,size)
    points = [(x,y) for x in (-64,64,300) for y in (-64,64,300)]
    pairs = set()
    # Проверка всех пар зон через настоящий диспетчер и прямые табличные входы.
    for first in points:
        for second in points:
            c1,c2 = outcode(*first),outcode(*second)
            pairs.add((c1,c2))
            index = 16*c1+c2
            target = original[0xDE00+index] | original[0xDF00+index] << 8
            for initial_r in (0,0x95):
                execute('dispatch',0xD48B,0x7FFE,initial_r,0xA7,first,second)
                for block in (0,1):
                    execute('direct_case',target,0x7FF8,initial_r,0,first,second,block)
    assert len(pairs) == 81
    assert any(p['special_return'] for p in profiles if p['kind'] == 'dispatch')
    assert any(p['final_R'] != p['initial_R'] for p in profiles if p['kind'] == 'dispatch')
    result = dict(passed=True,method='original_map_clip_calls_per_instruction_refresh_and_stack_witnesses',
        original_disk_sha256=manifest['sha256'],checked_physical_code_bytes=checked_bytes,
        cases=len(profiles),common_return_cases=512,dispatch_cases=162,direct_case_cases=324,
        outcode_pairs=81,common_return_exact_M1=5,initial_R_codes=[0,0x95],profiles=profiles,
        R_checked_after_every_instruction=True,all_coordinate_values_proved=False,
        all_runtime_phases_proved=False,IRQ_executed=False,calls_stubbed=False,
        native_execution=False,assembly_executed=False)
    path = ROOT/'Tools/Disasm/Reports/MapClipReturnRefreshVerification.json'
    data = (json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
    if path.exists():
        assert json.loads(path.read_bytes()) == json.loads(data)
    else:
        path.write_bytes(data)
    print(json.dumps({k:v for k,v in result.items() if k != 'profiles'},ensure_ascii=False))


if __name__ == '__main__':
    main()
