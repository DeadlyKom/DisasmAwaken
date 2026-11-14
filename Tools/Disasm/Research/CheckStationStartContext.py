"""Полный запуск до последнего JP, независимые таблицы и конечный CPU-контекст.

Документация: ../../../Docs/StationBootstrap.md#передача-в-основной-цикл-станции
"""
import json

from CheckStationFlightCycle import payload, DISK, ENTRIES
from CheckMapViewCenter import reference
from PackedResourceCodec import decode
from TraceFlight import ROOT, PC, SP, A, B, C, D, E, F, H, L, Memory, Ports, Simulator, main as trace
from skoolkit.simutils import get_registers


class Finished(Exception):
    pass


class StartCPU(Simulator):
    def accept_interrupt(self,registers,memory,prev_pc):
        accepted = super().accept_interrupt(registers,memory,prev_pc)
        if accepted:
            self.accepted_interrupts.append(prev_pc)
        return accepted


class DevicePorts(Ports):
    def __init__(self,memory,joystick,mouse_x,mouse_y):
        super().__init__(memory)
        self.values = {0x021F:joystick,0xFBDF:mouse_x,0xFFDF:mouse_y}
        self.reads = []

    def read_port(self,registers,port):
        if port in self.values:
            value = self.values[port]
            self.reads.append((port,value))
            return value
        return super().read_port(registers,port)


def main():
    original = payload(4)
    assert (ROOT/'Tools/Disasm/Extracted/Active/04_STATIONF.C.bin').read_bytes()==original
    records = []
    for offset in range(0x90FD,len(original)-15,16):
        row = original[offset:offset+16]
        if row[0]==0x80:
            marker = 0x6000+offset
            break
        records.append((0x6000+offset,row))
    else:
        raise AssertionError('Не найден исходный ограничитель интерфейса')
    patches = {}
    for index,(_,row) in enumerate(records):
        handler = int.from_bytes(row[12:14],'little')
        patches[handler+1],patches[handler+2] = index,0
    map_index = patches[0x6DA9]
    map_row = records[map_index][1]
    size_word = (((((map_row[11]-3)&255)<<8)|((map_row[10]-2)&255))*8)&65535
    width,height = size_word&255,size_word>>8
    first = int.from_bytes(original[0x383F:0x3841],'little')
    second = int.from_bytes(original[0x3841:0x3843],'little')
    x=(first&255)*256+(second&255)
    y=(first>>8)*256+(second>>8)
    origin_x,origin_y,flags = reference(x,y,width,height)
    expected_de = (origin_y&255)*256+(origin_x&255)
    expected_bc = 0xFF00|(-(height>>1)&255)
    profiles = []
    backdrop_indices = set()
    screens = [row for row in json.loads((ROOT/'Tools/Disasm/Reports/Screens.json').read_text(encoding='utf-8')) if row['slot']==9]
    for seed in range(16):
        joystick = 1 if seed&1 else 0
        mouse_x = 255 if seed&2 else 254
        mouse_y = 255 if seed&4 else 253
        memory = Memory(out7ffd=0x10)
        for index,value in enumerate(original):
            memory[0x6000+index] = value
        cpu = StartCPU(memory,config={'fast_ldir':False,'fast_djnz':False})
        cpu.accepted_interrupts = []
        initial = get_registers(dict(PC=0x6300,SP=0x5FFF,IY=0x5C3A,R=seed,
            **{'^AF':0xA55A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC}),None,False)
        cpu.registers[:] = initial
        ports = DevicePorts(memory,joystick,mouse_x,mouse_y)
        backdrop = []
        def observe(frame,ram,registers):
            if registers[PC]==0x413E:
                backdrop.append(registers[A]&15)
            if registers[PC]==0x42B2:
                raise Finished
        try:
            trace(['--region','station','--frames','1'],boot_simulator=cpu,
                  ports_factory=lambda _:ports,instruction_observer=observe,save_reports=False)
        except Finished:
            pass
        else:
            raise AssertionError((seed,'Не достигнут последний JP загрузчика'))
        assert bytes(memory[0x42B2+i] for i in range(3))==bytes.fromhex('c3599a')
        # Проверка конечного перехода отдельно, без принятия IRQ после EI.
        cpu.run()
        r = cpu.registers
        assert not cpu.accepted_interrupts
        assert (r[PC],r[SP],r[14],r[26],r[27],memory.o7ffd)==(0x9A59,0x5FFF,0x80,1,2,0x10)
        assert r[13]==initial[13] and memory[0x6306]==0x10
        assert r[:8]==[original[0x39B3],flags,expected_bc>>8,expected_bc&255,expected_de>>8,expected_de&255,0x99,0x3D],(seed,r[:8])
        assert len(backdrop)==1
        screen = screens[backdrop[0]]
        start = ENTRIES[9]['offset']+screen['offset']
        decoded = decode(DISK[start:start+screen['packed_size']])
        tail_word = decoded['final_tail_word']
        alternate = initial[16:18]+[0,decoded['final_output_count_low'],tail_word>>8,tail_word&255,0x27,0x58]
        assert r[8]*256+r[9]==marker and r[10:12]==initial[10:12] and r[16:24]==alternate,(seed,hex(marker),list(r[8:12]),list(r[16:24]),alternate)
        # Проверка распакованного фона и пяти заменённых атрибутов, DAFC записывается дважды.
        expected_backdrop = bytearray(decoded['data'])
        assert len(expected_backdrop)==6912
        expected_backdrop[-5:] = bytes([0x38])*5
        assert bytes(memory.banks[3][:6912])==expected_backdrop
        # Проверка четырёх загруженных модулей вместе с их физическими секторными хвостами.
        for slot,bank,offset in ((7,1,0),(8,7,0x1B00),(5,6,0),(6,4,0)):
            item = ENTRIES[slot]
            expected_module = bytearray(DISK[item['offset']:item['offset']+item['allocated_length']])
            if slot==6:
                for address,size,value in ((0x200,2,0),(0x202,1,0),(0x20E,2,0),(0x212,2,0),
                    (0x218,2,0),(0x21A,2,0),(0x210,2,0),(0x216,2,0),
                    (0x20C,2,0x7FFF),(0x214,2,0x7FFF),(0x21C,2,0x7FFF)):
                    expected_module[address:address+size] = value.to_bytes(size,'little')
            assert bytes(memory.banks[bank][offset:offset+len(expected_module)])==expected_module,(seed,slot)
        # Проверка собственных экранных таблиц и исходных границ интерфейса.
        assert bytes(memory[0x8000+i] for i in range(257))==bytes([0x81])*257
        assert bytes(memory[0x8181+i] for i in range(3))==bytes.fromhex('c3ea9a')
        addresses=[0x4000|((line&7)<<8)|((line&0x38)<<2)|((line&0xC0)<<5) for line in range(256)]
        assert bytes(memory[0x8200+i] for i in range(256))==bytes(address>>8 for address in addresses)
        assert bytes(memory[0x8300+i] for i in range(256))==bytes(address&255 for address in addresses)
        assert bytes(memory[0x8400+i] for i in range(256))==bytes(i>>3 for i in range(256))
        for address,row in records:
            assert bytes(memory[address+i] for i in range(4))==row[8:12]
        assert all(memory[address]==value for address,value in patches.items())
        assert (memory[0x6304],memory[0x6305])==(width,height)
        assert memory[0x6639]==int(bool(joystick&31))&(~(original[0x39B0]&127)&255)
        assert memory[0x65A8]==int(mouse_x==255 and mouse_y==255)&(~(original[0x39AE]&127)&255)
        assert memory[0x9B62]==original[0x39B3] and memory[0x6309]+256*memory[0x630A]==0x993D
        assert ports.reads==[(0x021F,joystick),(0xFBDF,mouse_x),(0xFFDF,mouse_y)],(seed,ports.reads)
        assert len(backdrop)==1
        backdrop_indices.update(backdrop)
        profiles.append(dict(initial_R=seed,backdrop=backdrop[0],device_ports=ports.reads,
            final_AF=r[A]*256+r[F],final_BC=expected_bc,final_DE=expected_de,final_HL=0x993D,
            final_alternate_pairs=[r[i]*256+r[i+1] for i in (22,20,18,16)],
            final_IX=marker,final_IY=r[10]*256+r[11],final_SP=r[SP]))
    assert backdrop_indices==set(range(16))
    report = dict(passed=True,total_cases=len(profiles),profiles=profiles,
        original_interface_records=len(records),all_16_backdrops_observed=True,
        all_8_binary_device_predicate_combinations=True,
        map_dimensions=[width,height],map_origin=[origin_x,origin_y],
        four_loaded_modules_and_allocated_suffixes_compared=True,
        decoded_backdrop_except_five_replaced_attributes_compared=True,
        own_IM2_and_screen_tables_compared=True,restored_geometry_and_handler_indices_compared=True,
        final_registers_except_R_T_compared=True,final_I=0x80,final_IM=2,final_IFF=1,
        original_station_boot_executed=True,TRDOS_calls_substituted=True,
        initial_station_RAM_and_entry_prepared=True,independent_full_RAM_comparison=False,
        all_saved_settings_or_input_states_exhausted=False,IRQ_executed=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/StationStartContextVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items() if key!='profiles'},indent=2))


if __name__=='__main__':
    main()
