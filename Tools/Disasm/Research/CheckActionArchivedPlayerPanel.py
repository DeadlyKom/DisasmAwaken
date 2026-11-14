"""Декларация PLAYER в 3DTABS и обращения при выбросе груза и мины."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckActionParameterActivation import flat_action
from CheckActionTextQueueCalls import Memory, Ports
from CheckControlsArchivedHyperEffect import read_entry
from CheckControlsTextQueue import base_memory
from CheckMusic import PC, SP, Simulator, get_registers
from CheckIntro import ROOT
from ProbeShipPreviewCallbacks import payload


def compare_player(archive_path):
    with ZipFile(archive_path) as archive:
        original = archive.read('awk1.trd')
        origin, datas, _ = read_entry(original, b'DATAS   C')
        _, declarations, _ = read_entry(original, b'3DTABS  a')
        _, labels, _ = read_entry(original, b'LABELS  a')
        _, sp, _ = read_entry(archive.read('awk5.trd'), b'SP      C')
        _, plain_equ, _ = read_entry(archive.read('awk4.trd'), b'EQUS    C')
    label_names = (b'PLAYER', b'ACTION', b'Speed', b'SHILD', b'VOXCOR')
    addresses = (0xA880, 0xA88C, 0xA88F, 0xA894, 0xA895)
    for name, address in zip(label_names, addresses):
        assert re.search(rb'\r' + name + rb'\x06.\x04f' + str(address).encode() + rb'\r', labels)
    lines = declarations.split(b'\r')
    start, end = lines.index(b'PLAYER:'), lines.index(b'VOXCOR:')
    authored = bytearray()
    type_offset = None
    for line in lines[start + 1:end]:
        if b'\x05' not in line:
            continue
        directive = re.search(rb'\x05([gh])\x06\x83([0-9A-F#,]+)(?:;(.*))?$', line)
        assert directive, line
        kind, values, comment = directive.groups()
        if comment == b'TYPE':
            type_offset = len(authored)
        for value in values.split(b','):
            integer = int(value[1:], 16) if value.startswith(b'#') else int(value)
            authored.extend(integer.to_bytes(1 if kind == b'g' else 2, 'little'))
    assert len(authored) == 21 and type_offset == 0x12
    assert authored == datas[0xA880 - origin:0xA895 - origin] == sp[0x4880:0x4895] == payload(17)[0x4780:0x4795]
    # Проверка SHILD по авторскому адресу, позиции в записи и неизменённому начальному значению.
    assert authored[0x14] == 0x2E and 0xA780 + 0x14 == 0xA794
    # Сопоставление смещения TYPE не переносит старую ёмкость и размер записей в текущую игру.
    assert b'Type    EQU #12\r' in plain_equ
    assert b';#FF-' + 'ИГРОК'.encode('cp866') + b'\r' in plain_equ
    assert b'Olen    EQU #20\r' in plain_equ
    assert type_offset == 0x12 and authored[type_offset] == 0xFF
    return dict(archive_sha256=sha256(archive_path.read_bytes()).hexdigest(), authored_bytes=len(authored),
                archived_player=0xA880, archived_type_offset=type_offset, current_player=0xA780,
                current_type=0xA792, panel_hex=authored.hex(), labels_in_archive=len(addresses),
                archived_shield_address=0xA894, current_shield_address=0xA794,
                shield_offset_in_player=0x14, shield_initial_value=0x2E,
                shield_label_and_all_player_bytes_matched=True,
                archived_class_code_source='awk4.trd:EQUS.C',
                archived_player_class_code=0xFF, archived_class_code_offset=0x12,
                current_same_type_byte=0xA792,
                archived_EQUS_record_bytes=0x20, current_record_bytes=0x40,
                current_type_consumer_proved_by_provenance_only=False)


class PanelMemory(Memory):
    def __getitem__(self, address):
        value = super().__getitem__(address)
        if isinstance(address, int) and 0xA78D <= address < 0xA794 and self.recording:
            self.panel_reads.append((self.registers[PC], address, value))
        return value


def check_ejections():
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, address in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = flat[address:address + 0x4000]
    banks[1][:] = base_memory()[0xC000:]
    memory = PanelMemory(banks=[bank.copy() for bank in banks], out7ffd=0x10)
    memory.recording = False
    cpu = Simulator(memory)
    memory.registers = cpu.registers
    ports = Ports(memory)
    cpu.set_tracer(ports)
    for entry in (0x7594, 0x75CF):
        for high in range(256):
            for bank, original in zip(memory.banks, banks):
                bank[:] = original
            memory.out7ffd(0x10)
            memory[0xA85F] = 0
            memory[0xA101] = 0x80
            memory[0xA118] = 0
            memory[0x9BD4] = memory[0x9C14] = 1
            memory[0xA01C] = 0xFE
            for i in range(7):
                memory[0xA78D + i] = (high + i * 41) & 255
            memory[0xA790] = high
            memory[0xBFFE], memory[0xBFFF] = 0xFF, 0x3F
            cpu.registers[:] = get_registers({'SP': 0xBFFE}, None, False)
            memory.panel_reads, memory.writes, ports.events = [], [], []
            memory.recording = True
            cpu.run(entry, 0x3FFF)
            memory.recording = False
            assert memory.panel_reads == [(0x6494, 0xA790, high)]
            assert not any(bank == 2 and 0x278D <= address < 0x2794 for bank, address, _ in memory.writes)
            assert cpu.registers[SP] == 0xC000 and memory[0xA112] == 0x13
            assert memory[0xA110] == min(max(high - 30, 0), 69)
    return dict(ejection_profiles=512, sole_panel_range_read=0xA790, reader=0x6494,
                unclassified_neighbors_read_in_test=False, panel_range_writes=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    report = dict(passed=True, **compare_player(args.archive), **check_ejections(),
                  all_current_game_consumers_proved=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionArchivedPlayerPanelVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
