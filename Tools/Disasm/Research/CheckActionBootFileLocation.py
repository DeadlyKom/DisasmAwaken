"""Поиск шести ключей ACTION настоящим TR-DOS с моделью контроллера.

Документация: ../../../Docs/ActionBootFileKeys.md#координаты-каталога-и-физический-номер-сектора
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckBootBankFileReads import boot_memory, FileReadPorts, ROOT, ENTRIES, DISK, payload, run_with_rom, Simulator
from skoolkit.simutils import PC, SP, A, F, H, L


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    parser.add_argument('--load',action='store_true',help='после поиска исполнить исходную загрузку файла')
    args = parser.parse_args()
    basic = (ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    dos = args.dos_rom.read_bytes()
    assert len(basic) == len(dos) == 16384
    assert sha256(dos).hexdigest() == 'e21d37271d087eab5ef8f88d8f3a58c8c19da1fa857b9790eaa974b231db9e13'
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    assert sha256(DISK).hexdigest() == manifest['sha256']
    rows = []; load_rows = []
    # Проверка всех шести неизменённых ключей и двух исходных положений головки.
    for key_address, slot in ((0x42D0,21),(0x42D9,20),(0x42E2,23),(0x42EB,22),(0x42F4,25),(0x42FD,24)):
        entry = ENTRIES[slot]
        directory = DISK[slot*16:(slot+1)*16]
        assert directory[13:16] == bytes((entry['sector_count'],entry['first_sector'],entry['first_track']))
        for cylinder in (0,9):
            memory = boot_memory(basic,17)
            assert bytes(memory[0x42AB:0x42C6]) == payload(17)[0xEE:0x109]
            assert bytes(memory[key_address:key_address+9]) == directory[:9]
            memory[0x7FFE:0x8000] = bytes.fromhex('ff7f')
            cpu = Simulator(memory,dict(PC=0x42AB,SP=0x7FFE,HL=key_address,IY=0x5C3A))
            ports = FileReadPorts(cylinder)
            cpu.set_tracer(ports)
            visited, keyboard_checks = run_with_rom(cpu,basic,dos,
                lambda image: memory.__setitem__(slice(0,16384),image),0x7FFF)
            r = cpu.registers
            # Проверка прочитанного заголовка и преобразования нулевого номера сектора в физический.
            expected = entry['first_track']*256+entry['first_sector']+1
            assert bytes(memory[0x5CDD:0x5CED]) == directory
            assert r[H]*256+r[L] == expected and r[A] == entry['sector_count']
            assert r[PC] == 0x7FFF and r[SP] == 0x8000
            assert ports.attempts and all(track == 0 for track,sector in ports.attempts)
            rows.append(dict(slot=slot,key_address=key_address,key_hex=directory[:9].hex(),
                initial_cylinder=cylinder,catalogue_sector_zero_based=entry['first_sector'],
                physical_sector=r[L],logical_track=r[H],sector_count=r[A],final_AF=r[A]*256+r[F],
                final_HL=expected,final_SP=r[SP],catalogue_reads=[list(pair) for pair in ports.attempts],
                observed_rom_sites={format(k,'04X'):v for k,v in visited.items()},keyboard_checks=keyboard_checks))
            if args.load:
                # Проверка обоих входов загрузки без подмены функции TR-DOS 0E.
                destination = {21:0xEC00,23:0xDADE}.get(slot,0xC000)
                start = 0x42C6 if destination == 0xC000 else 0x42C9
                assert bytes(memory[0x42C6:0x42D0]) == payload(17)[0x109:0x113]
                size = entry['allocated_length']
                assert destination+size < 65536
                memory[destination-1:destination+size+1] = bytes((0xA5,))*(size+2)
                memory[0x7FFE:0x8000] = bytes.fromhex('ff7f')
                r[PC],r[SP] = start,0x7FFE
                r[H],r[L] = (0x13,0x57) if start == 0x42C6 else (destination>>8,destination&255)
                first_read = len(ports.attempts)
                run_with_rom(cpu,basic,dos,
                    lambda image: memory.__setitem__(slice(0,16384),image),0x7FFF)
                physical = DISK[entry['offset']:entry['offset']+size]
                assert bytes(memory[destination:destination+size]) == physical
                assert memory[destination-1] == memory[destination+size] == 0xA5
                first = entry['offset']//256
                expected_reads = [(index//16,index%16+1) for index in range(first,first+entry['sector_count'])]
                catalogue_reads = [(0,1),(0,2),(0,2)]
                assert ports.attempts[first_read:] == catalogue_reads+expected_reads
                assert r[PC] == 0x7FFF and r[SP] == 0x8000
                assert (r[H]*256+r[L],r[A]*256+r[F],r[2]*256+r[3],r[4]*256+r[5]) == (0xFF54,0xFF98,slot,0x0100)
                load_rows.append(dict(slot=slot,entry=start,destination=destination,
                    ignored_HL_input=0x1357 if start==0x42C6 else None,
                    logical_bytes=entry['length'],physical_bytes=size,suffix_bytes=size-entry['length'],
                    catalogue_reads=catalogue_reads,data_reads=expected_reads,final_HL=r[H]*256+r[L],final_AF=r[A]*256+r[F],
                    final_registers=list(r[:24]),final_SP=r[SP],guard_bytes_preserved=True))
    assert len(rows)==12 and sum(row['physical_sector']==16 for row in rows)==2
    report = dict(passed=True,original_disk_sha256=manifest['sha256'],
        dos_rom_sha256=sha256(dos).hexdigest(),basic_rom_sha256=sha256(basic).hexdigest(),
        original_bootstrap_instructions_and_keys_matched=True,whole_selected_directory_record_matched=True,
        prepared_system_variables=True,prepared_5D06=9,prepared_5D0C=255,
        real_TRDOS_search_0A_and_read_directory_08=True,controller_and_ROM_paging_modelled=True,
        file_data_sectors_read=False,IRQ_executed=False,disk_errors_or_missing_files_proved=False,
        natural_caller_entry_proved=False,native_execution=False,assembly_executed=False,profiles=rows)
    if args.load:
        assert len(load_rows)==12
        report.update(file_data_sectors_read=True,load_profiles=load_rows,ordinary_file_load_tail_executed=True)
    path=ROOT/('Tools/Disasm/Reports/ActionBootFileLoadVerification.json' if args.load else 'Tools/Disasm/Reports/ActionBootFileLocationVerification.json')
    report = json.loads(json.dumps(report))
    if path.exists():
        assert json.loads(path.read_bytes())==report
    else:
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('12 загрузок исходными входами с TR-DOS 5.04T' if args.load else '12 поисков шести исходных ключей с TR-DOS 5.04T, CONTROL возвращает физический сектор 16')


if __name__=='__main__':
    main()
