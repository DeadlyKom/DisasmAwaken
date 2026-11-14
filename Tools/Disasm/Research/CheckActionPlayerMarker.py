"""MARK OF PLAYER и проверка StateCode цели #1A на ближнем пути ракеты."""
from hashlib import sha256
import json
from zipfile import ZipFile

from CheckActionArchivedPlayerPanel import compare_player
from CheckActionParameterActivation import flat_action
from CheckControlsArchivedHyperEffect import read_entry
from CheckPreviewCoordinateMultiply import Memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckIntro import ROOT


def check_player_link(original):
    memory = Memory(list(original))
    cpu = Simulator(memory)
    cases = 0
    success = failure = 0
    for free_slot in (*range(25), None):
        for shooter in (0, 12, 24):
            for old_link in (0, 0x7F, 0xFF):
                memory.recording = False
                memory[:] = original
                for index in range(25):
                    address = 0xA100 + 64 * index
                    memory[address:address + 2] = [0, 128 if index == free_slot else 1]
                    memory[address + 24] = 0
                memory[0xA740:0xA742] = [128, 128]
                memory[0xA78B] = old_link
                memory[0xA78C] = 0x80
                memory[0xBFFE:0xC000] = [255, 63]
                cpu.registers[:] = get_registers(dict(PC=0x60E8, SP=0xBFFE, AF=0x0A5A,
                    BC=shooter * 256 + 0x1A, HL=0x1357, DE=0x2468, IX=0xA700,
                    IY=0x5C3A, **{'^AF':0, '^HL':0, '^DE':0, '^BC':0}), None, False)
                memory.writes = []
                memory.recording = True
                for _ in range(1024):
                    if cpu.registers[PC] == 0x3FFF:
                        break
                    cpu.run()
                else:
                    raise AssertionError(('Не завершён создатель', free_slot, shooter, old_link))
                link_writes = [(a, v) for a, v in memory.writes if a == 0xA78B]
                assert memory[0xA78A] == 255 and cpu.registers[SP] == 0xC000
                if free_slot is None:
                    assert not link_writes and memory[0xA78B] == old_link and memory[0xA78C] == 0x80
                    failure += 1
                else:
                    assert link_writes == [(0xA78B, free_slot)]
                    assert memory[0xA78B] == free_slot and memory[0xA78C] == 0x82
                    child = 0xA100 + 64 * free_slot
                    assert memory[child + 13] == shooter and memory[child + 15] == 0x1A
                    assert memory[child + 18] == 0x11
                    success += 1
                cases += 1
    return dict(cases=cases, successful_creations=success, no_slot_profiles=failure,
                all_25_allocatable_slots=True, player_link_address=0xA78B,
                exact_single_link_write=True, no_slot_preserves_player_link=True,
                marker_preserved=True, real_creator_and_helpers=True,
                native_game_creation_reachability_proved=False)


def main():
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    provenance = compare_player(archive_path)
    with ZipFile(archive_path) as archive:
        _, source, _ = read_entry(archive.read('awk1.trd'), b'3DTABS  a')
    rows = source.split(b'\r')
    declaration = b'\x06\x8c\x05g\x06\x83#FF;MARK OF PLAYER'
    assert declaration in rows[rows.index(b'PLAYER:'):rows.index(b'VOXCOR:')]
    original = flat_action()
    assert provenance['current_player'] == 0xA780 and original[0xA78A] == 255
    assert 0xA100 + 64 * 0x1A + 10 == 0xA78A
    memory = Memory(list(original))
    cpu = Simulator(memory)
    entry, stop, projectile = 0xF61B, 0xF62C, 0xA700
    symbols = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())
    release_entry = symbols['Action.MarkRecordForReuse.Entry']
    assert original[0xF625] == 0x7E
    skipped = released = 0
    for value in range(256):
        memory.recording = False
        memory[:] = original
        memory[projectile:projectile + 2] = [0x34, 0x12]
        memory[projectile + 10] = 8
        memory[projectile + 15] = 0x1A
        memory[projectile + 24] = 0x23
        memory[0xA78A] = value
        memory[0xBFFE:0xC000] = [255, 63]
        cpu.registers[:] = get_registers(dict(PC=entry, SP=0xBFFE, IX=projectile,
                                              IY=0xA780, HL=0x1357, DE=0x2468,
                                              BC=0x369C, AF=0xA55A), None, False)
        memory.writes = []
        memory.recording = True
        visited = []
        marker_read_seen = False
        for _ in range(64):
            if cpu.registers[PC] == stop:
                break
            if cpu.registers[PC] == 0xF625:
                assert cpu.registers[6] * 256 + cpu.registers[7] == 0xA78A
                marker_read_seen = True
            visited.append(cpu.registers[PC])
            cpu.run()
        else:
            raise AssertionError(('Не достигнут MarkArrival', value))
        assert marker_read_seen
        assert cpu.registers[SP] == 0xBFFE and memory[0xA78A] == value
        writes = [(a, v) for a, v in memory.writes if projectile <= a < projectile + 64]
        if value == 255:
            assert not writes and memory[projectile:projectile + 2] == [0x34, 0x12]
            assert memory[projectile + 24] == 0x23 and release_entry not in visited
            skipped += 1
        else:
            assert writes == [(projectile + 1, 128), (projectile, 0), (projectile + 24, 255)]
            assert release_entry in visited
            released += 1
    report = dict(passed=True, archive_sha256=digest, source='awk1.trd:3DTABS.a:PLAYER',
                  declaration_cp866_hex=declaration.hex(), matched_player_bytes=provenance['authored_bytes'],
                  player_index=0x1A, player_address=0xA780, marker_address=0xA78A,
                  original_marker=255, cases=256, skip_release_cases=skipped, release_cases=released,
                  entry=entry, stop_before_mark_arrival=stop, original_index_and_release_helpers=True,
                  exact_projectile_writes=True, effective_marker_read_verified=True,
                  marker_reader=0xF625, caller_and_movement_prepared=True,
                  complete_arrival_and_effect_executed=False, assembly_executed=False,
                  irq_executed=False, native_execution=False)
    report['player_incoming_missile_link'] = check_player_link(original)
    (ROOT / 'Tools/Disasm/Reports/ActionPlayerMarkerVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Проверены все 256 значений маркера цели #1A, FF сохраняет текущую ракету.')


if __name__ == '__main__':
    main()
