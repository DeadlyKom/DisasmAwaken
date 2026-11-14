"""Условный дисковый цикл остаточного CONTROL с ROM и моделью портов."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckBank4Index import WriteMemory


class SectorPorts:
    """Модель обмена через 1F/3F/5F/7F/FF, готовность и ошибки задаются профилем."""

    def __init__(self, disk, retry):
        self.disk = disk
        self.retry = retry
        self.attempts = []
        self.commands = []
        self.side = self.track = self.sector = None
        self.current = b''
        self.cursor = 0
        self.status = 0

    def write_port(self, registers, port, value, offset):
        low = port & 255
        if low == 0xFF:
            self.side = int(not (value & 0x10))
        elif low == 0x3F:
            self.track = value
        elif low == 0x5F:
            self.sector = value
        elif low == 0x1F:
            self.commands.append(value)
            if value == 0x80:
                track = self.track * 2 + self.side
                start = (track * 16 + self.sector - 1) * 256
                self.current = self.disk[start:start + 256]
                assert len(self.current) == 256
                self.cursor = 0
                self.status = 4 if self.retry and not self.attempts else 0
                self.attempts.append((track, self.sector))

    def read_port(self, registers, port, offset=0):
        low = port & 255
        if low == 0xFF:
            return 0x40 if self.cursor < len(self.current) else 0x80
        if low == 0x1F:
            return self.status
        if low == 0xFE:
            return 0xFF
        assert low == 0x7F and self.cursor < len(self.current), hex(port)
        value = self.current[self.cursor]
        self.cursor += 1
        return value


def run_with_rom(simulator, basic_rom, dos_rom, set_rom, stop, *, step_limit=1000000, initial_dos=False):
    dos_paged = initial_dos
    if dos_paged:
        set_rom(dos_rom)
    visited_rom = Counter()
    keyboard_checks = 0
    for _ in range(step_limit):
        pc = simulator.registers[PC]
        if pc == stop:
            return visited_rom, keyboard_checks
        # Модель выбора ROM при выборке команды, включая возврат через RAM 5CC2.
        if dos_paged and pc >= 0x4000:
            set_rom(basic_rom)
            dos_paged = False
        elif not dos_paged and 0x3D00 <= pc < 0x3E00:
            set_rom(dos_rom)
            dos_paged = True
        if dos_paged and pc in (0x2740, 0x2A53, 0x2F55, 0x2F59, 0x3D2F, 0x3FE5):
            visited_rom[pc] += 1
        keyboard_checks += not dos_paged and pc == 0x1F54
        simulator.run()
    raise AssertionError(('граница возврата не достигнута', hex(stop), hex(simulator.registers[PC])))


def check_call_bridge(rom, source):
    # Проверка исходного остаточного кода, размещение в 5ED6 является условием модели.
    code=source[0x136:0x13B]
    assert code==bytes.fromhex('dde5c32f3d') and rom[0x3D2F:0x3D31]==bytes.fromhex('00c9')
    m=WriteMemory(banks=[bytearray(16384) for _ in range(8)],out7ffd=16)
    m.memory[0]=rom
    for offset,value in enumerate(code):m[0x5ED6+offset]=value
    s=Simulator(m)
    initial=get_registers({'HL':0x1357,'DE':0x2468,'BC':0x369C,'AF':0xA55A,
        '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0},None,False)
    seeds=set();cases=0

    def check(ix,stack):
        nonlocal cases
        m.recording=False
        s.registers[:]=initial;r=s.registers
        r[8:10]=[ix>>8,ix&255];r[10:12]=[(ix^0xBEEF)>>8,(ix^0xBEEF)&255]
        r[1]=ix&255;r[14]=ix>>8;r[15]=(ix*73)&255;r[26]=ix&1;r[27]=ix%3
        r[SP]=stack;r[PC]=0x5ED6;before=list(r);seeds.add(r[15])
        m.cpu_writes=[];m.recording=True
        # Передача в мост ROM, две команды дают три M1 и создают только слово IX.
        s.run();s.run()
        wanted=list(before);wanted[SP]=stack-2;wanted[PC]=0x3D2F
        wanted[15]=(before[15]&128)|((before[15]+3)&127)
        assert all(r[i]==wanted[i] for i in range(len(r)) if i!=25)
        assert Counter(m.cpu_writes)==Counter(((stack-2,ix&255),(stack-1,ix>>8)))
        # NOP и RET снимают IX, произвольный полученный адрес дальше не исполняется.
        s.run();s.run();m.recording=False
        wanted[SP]=stack;wanted[PC]=ix;wanted[15]=(before[15]&128)|((before[15]+5)&127)
        assert all(r[i]==wanted[i] for i in range(len(r)) if i!=25)
        assert Counter(m.cpu_writes)==Counter(((stack-2,ix&255),(stack-1,ix>>8)))
        cases+=1

    for ix in range(65536):check(ix,0x7FFE)
    for stack in (0x4002,0x8000,0xBFFE,0xC000):
        for ix in (0,1,0x3D2F,0x5ED6,0x7FFF,0xFFFF):check(ix,stack)
    assert seeds==set(range(256))
    return dict(cases=cases,all_65536_IX_targets=True,initial_R_values=256,
        own_prefix_m1=3,including_ROM_NOP_RET_m1=5,exact_registers_except_T=True,
        exact_CPU_write_addresses_values_and_multiplicity=True,hardware_bus_write_order_proved=False,
        ROM_already_selected_in_fixture=True,ROM_paging_proved_by_this_probe=False,
        arbitrary_target_not_executed=True,all_joint_inputs_exhausted=False,
        legacy_copy_placement_is_fixture=True,game_entry_proved=False,irq_executed=False)


def check_rom(path, basic_rom, source, disk):
    rom = path.read_bytes()
    assert len(rom) == 16384
    assert rom[0x2A53:0x2A56] == bytes.fromhex('ed 79 c9')
    assert rom[0x3D2F:0x3D31] == bytes.fromhex('00 c9')
    assert rom[0x3FE5:0x3FF0] == bytes.fromhex('db ff e6 c0 28 fa f8 ed a2 18 f5')
    assert rom[0x2740:0x2745] == bytes.fromhex('db 1f 32 cd 5c')
    assert rom[0x2F55] == 0x3E and rom[0x2F56] in (0x18, 0x1B)
    assert rom[0x2F57:0x2F65] == bytes.fromhex('d3 1f db ff e6 80 28 fa c5 cd fd 3d c1 c9')
    bridge=check_call_bridge(rom,source)
    visited_rom = Counter()
    profiles = []
    for track, sector, count, retry in ((0, 1, 3, False), (0, 16, 3, False), (1, 16, 3, False), (1, 16, 2, True)):
        memory = bytearray(65536)
        memory[:16384] = basic_rom
        memory[0x5E1F:0x5EDB] = source[0x7F:0x13B]
        # Исходный RET системного переходника, установленный TR-DOS по 2FBE.
        memory[0x5CC2] = 0xC9
        memory[0x5D16] = 0xC7
        memory[0x7FFE:0x8000] = bytes.fromhex('ff 7f')
        simulator = Simulator(memory, {'PC': 0x5E4D, 'SP': 0x7FFE, 'BC': count << 8,
                                       'DE': track << 8 | sector, 'HL': 0x9005})
        ports = SectorPorts(disk, retry)
        simulator.set_tracer(ports)
        r = simulator.registers
        def set_rom(image):
            memory[:16384] = image
        executed, keyboard_checks = run_with_rom(simulator, basic_rom, rom, set_rom, 0x7FFF)
        visited_rom.update(executed)
        first = track * 16 + sector - 1
        sequence = [(index // 16, index % 16 + 1) for index in range(first, first + count)]
        assert ports.attempts == (sequence[:1] if retry else []) + sequence
        assert ports.commands.count(0x58) == int(track % 2 == 1 and sector + count > 16)
        assert keyboard_checks == len(ports.attempts)
        assert bytes(memory[0x9005:0x9005 + count * 256]) == disk[first * 256:(first + count) * 256]
        assert memory[0x9004] == memory[0x9005 + count * 256] == 0 and r[SP] == 0x8000
        next_track, next_sector = divmod(first + count, 16)
        assert r[2] == 0 and r[4:6] == [next_track, next_sector + 1]
        assert r[22:24] == [0x90 + count, 5]
        profiles.append(dict(start_track=track, start_sector=sector, count=count, attempts=ports.attempts,
                             commands=ports.commands, keyboard_checks=keyboard_checks, retry_first=retry,
                             next_track=next_track, next_sector=next_sector + 1, destination_end=0x9005 + count * 256))
    assert len(visited_rom) == 6
    return dict(rom=path.name, sha256=sha256(rom).hexdigest(), profiles=profiles,call_bridge=bridge,
                executed_rom_entries={f'{pc:04X}': count for pc, count in sorted(visited_rom.items())})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rom', nargs='+', type=Path)
    parser.add_argument('--basic-rom', type=Path,
                        default=ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    entry = next(row for row in manifest['entries'] if row['slot'] == 23)
    source = disk[entry['offset']:entry['offset'] + entry['length']]
    basic_rom = args.basic_rom.read_bytes()
    assert len(basic_rom) == 16384 and basic_rom[0x1F54:0x1F5A] == bytes.fromhex('3e 7f db fe 1f d8')
    results = [check_rom(path, basic_rom, source, disk) for path in args.rom]
    report = dict(passed=True, total_cases=sum(len(result['profiles']) for result in results),
                  original_control_worker_and_rom_INI_loop_executed=True, roms=results,
                  basic_rom=args.basic_rom.name, basic_rom_sha256=sha256(basic_rom).hexdigest(),
                  modelled_port_timing_and_rom_paging=True, rom_cleanup_executed=True,
                  legacy_copy_at_5DA0_is_fixture=True, game_entry_proved=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsLegacySectorReadVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'roms'}, indent=2))


if __name__ == '__main__':
    main()
