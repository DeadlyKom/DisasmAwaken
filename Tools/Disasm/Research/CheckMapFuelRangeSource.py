"""Два топливных байта, показываемая дальность и радиус дуги, все исходные пары.

Документация: ../../../Docs/MapScene.md
Документация: ../../../Docs/SystemInfoPanel.md
"""
from collections import Counter
from hashlib import sha256
import json

from CheckRowHighlight import ROOT, Simulator, make_context
from skoolkit.simutils import get_registers, A, F, B, C, H, L, PC, R, T


class Memory(list):
    recording = False

    def __setitem__(self, key, value):
        if self.recording:
            assert isinstance(key, int)
            self.writes.append((key, value))
        super().__setitem__(key, value)


def add_flags(left, right):
    total = left+right
    value = total&255
    return ((value&0xA8) | (0x40 if value == 0 else 0) |
        (0x10 if (left&15)+(right&15) > 15 else 0) |
        (4 if (~(left^right)&(left^value)&128) else 0) | int(total > 255))


def main():
    # Проверка оригинала, обоих машинных фрагментов и текстов двух топливных строк.
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(disk).hexdigest() == manifest['sha256']
    entries = {row['slot']:row for row in manifest['entries']}
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    station, map_source, banks = make_context()
    for slot, data in ((4,station),(7,map_source)):
        entry = entries[slot]
        assert bytes(data) == disk[entry['offset']:entry['offset']+entry['allocated_length']]
    base = [0]*65536
    base[0x4000:0x8000], base[0x8000:0xC000] = banks[5], banks[2]
    base[0xC000:0xC000+len(map_source)] = map_source
    witnesses = []
    for region, slot, start, stop in [('Map',7,0xC003,0xC012), ('Station',4,0x76A5,0x76B2)]:
        rows = [row for area in flow if area['name'] == region for row in area['instructions']
                if start <= row['address'] < stop]
        raw = b''.join(bytes.fromhex(row['hex']) for row in rows)
        assert len(raw) == stop-start
        for row in rows:
            assert row['slot'] == slot
            encoded = bytes.fromhex(row['hex'])
            offset = entries[slot]['offset']+row['offset']
            assert disk[offset:offset+len(encoded)] == encoded
            assert bytes(base[row['address']:row['address']+len(encoded)]) == encoded
        witnesses.append(dict(region=region,start=start,stop_before=stop,
                              original_hex=raw.hex(),sha256=sha256(raw).hexdigest()))
    names = (ROOT/'Source/Station/Resources/EquipmentNames.bin').read_bytes()
    assert names.split(b'\r')[1:3] == ['Топливо МРП'.encode('cp866'),'Топливо ЛНП'.encode('cp866')]
    assert station[0x8E57:0x8E57+len(names)] == names
    template = (ROOT/'Source/Station/Resources/SystemInfoTemplate.bin').read_bytes()
    assert station[0x8A9B:0x8A9B+len(template)] == template
    assert template.split(b'\r',1)[0].decode('cp866') == 'Топлива на:         сл'
    memory = Memory(base)
    cpu = Simulator(memory)
    # Положительный контроль наблюдателя, запись исполняется самим CPU.
    memory[0x3000:0x3005] = bytes.fromhex('3E6B32AEDF')
    cpu.registers[:] = get_registers(dict(PC=0x3000),None,False)
    memory.writes, memory.recording = [], True
    cpu.run(); cpu.run()
    memory.recording = False
    assert memory.writes == [(0xDFAE,0x6B)]
    memory[0xDFAE] = base[0xDFAE]
    counts = Counter()
    # Перебор всех сырых пар, включая отрицательные коды, маркер 80 и ненулевые оба вида.
    for word in range(65536):
        low, high = word&255, word>>8
        distance = high if high else low//2
        radius = 3*distance&255
        memory[0x988E:0x9890] = [low,high]
        for carry in (0,1):
            for name,start,stop in [('range',0x76A5,0x76B2),('radius',0xC003,0xC012)]:
                initial = get_registers(dict(PC=start,SP=0x7FFE,HL=0x1357,DE=0x247A,
                    BC=0x36C9,AF=0x5A5C|carry,IX=0x2468,IY=0x5C3A,
                    R=(low^high), **{'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF}),None,False)
                cpu.registers[:] = initial
                before = memory.copy()
                memory.writes, memory.recording = [], True
                steps = 0
                while cpu.registers[PC] != stop:
                    assert steps < 16
                    cpu.run()
                    steps += 1
                memory.recording = False
                expected = initial.copy()
                expected[PC] = stop
                expected[H], expected[L] = high, low
                if name == 'range':
                    expected[A],expected[F],expected[B],expected[C] = 0,0x44,0,distance
                    assert steps == (7 if high else 9)
                    assert memory.writes == [] and memory == before
                else:
                    expected[A],expected[F],expected[L] = radius,add_flags(2*distance&255,distance),distance
                    assert steps == (8 if high else 10)
                    assert memory.writes == [(0xDFAE,radius)]
                    before[0xDFAE] = radius
                    assert memory == before
                expected[R] = (initial[R]&128)|((initial[R]+steps)&127)
                assert all(cpu.registers[index] == expected[index] for index in range(len(initial)) if index != T), (name,word,carry)
                counts[name] += 1
    result = dict(passed=True,method='original_range_and_radius_prefixes_all_raw_fuel_pairs',
        original_disk_sha256=manifest['sha256'],original_instruction_witnesses=witnesses,
        raw_word_values=65536,input_carry_values=[0,1],cases_by_prefix=dict(counts),
        fuel_rows=['Топливо МРП','Топливо ЛНП'],fuel_addresses=[0x988E,0x988F],
        original_panel_caption=template.split(b'\r',1)[0].decode('cp866'),
        original_equipment_names_sha256=sha256(names).hexdigest(),
        original_panel_template_sha256=sha256(template).hexdigest(),
        displayed_distance='high if high != 0 else low//2',radius='(3*displayed_distance)&255',
        all_registers_except_T_and_all_RAM_and_writes_checked=True,positive_probe_passed=True,
        raw_codes_not_inverse_decoded_by_these_readers=True,
        arbitrary_raw_pairs_not_claimed_as_valid_gameplay=True,
        current_formula_changes_not_made=True,full_panel_and_map_not_executed_here=True,
        physical_distance_units_or_global_reachability_proved=False,
        irq_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/MapFuelRangeSourceVerification.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,cases_by_prefix=dict(counts),raw_word_values=65536),indent=2))


if __name__ == '__main__':
    main()
