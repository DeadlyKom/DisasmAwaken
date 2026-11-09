"""Исходное вступление и переносимый загрузчик до передачи чтения TR-DOS."""
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT, original_memory
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from IntroScreenCodec import decode, physical


class IntroInput(PortTrace):
    def __init__(self, simulator, frames):
        super().__init__(simulator)
        self.frames = frames
        self.polls = 0

    def read_port(self, registers, port):
        if port == 0x7FFE and 0x6A4E <= registers[PC] < 0x6A59:
            self.polls += 1
            return 190 if self.polls > self.frames else 255
        return 255


def main():
    flat = original_memory()
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    station_entry = disk[4 * 16:5 * 16]
    assert station_entry[:9] == b'STATIONFC'
    unpacked = decode(bytes(flat[0x89CB:]))['data']
    screen = bytearray(6912)
    for index, value in enumerate(unpacked):
        screen[physical(0x4000 + index) - 0x4000] = value
    for frames in (0, 1, 2, 300):
        banks = [bytearray([0] * 0x4000) for _ in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[2][:] = bytes(flat[0x8000:0xC000])
        memory = RecordedBanks(banks=banks, out7ffd=16)
        memory.roms = (list(rom), list(rom))
        memory.out7ffd(16)
        memory[0x5C00] = memory[0x5C04] = 255
        sim = Simulator(memory)
        trace = IntroInput(sim, frames)
        sim.set_tracer(trace)
        initial = get_registers({'PC': 0x6500, 'SP': 0x5FFF, 'IY': 0x5C3A}, None, False)
        initial[27] = 1
        sim.registers[:] = initial
        sim.run(0x6500, 0x5D3B, interrupts=True)
        assert trace.polls == min(300, frames + 1), frames
        assert sim.registers[SP] == (0x5FFF if frames == 300 else 0x5FF9), frames
        assert bytes(memory[0x65B4:0x65B6]) == bytes.fromhex('FF 5F')
        assert bytes(memory[0x5D3B:0x5D3B + 0x100]) == bytes(flat[0x65B7:0x66B7])
        assert bytes(memory[0x6E31:0x6ECB]) == bytes(flat[0x8931:0x89CB])
        sim.run(0x5D3B, 0x3D13, interrupts=True)
        r = sim.registers
        assert (r[3], r[14], r[26], r[27]) == (10, 0x3F, 0, 1), frames
        assert r[10:12] == [0x5C, 0x3A]
        assert bytes(memory[0x5CDD:0x5CE6]) == station_entry[:9]
        assert bytes(memory.banks[7][:6912]) == screen == bytes(memory.banks[5][:6912])
        assert memory.o7ffd == 0x18

        def return_from_dos():
            sp = r[SP]
            r[PC] = memory[sp] + 256 * memory[sp + 1]
            r[SP] = sp + 2

        r[3] = 4
        return_from_dos()
        sim.run(r[PC], 0x3D13)
        assert r[0] == 4 and r[3] == 8
        put(memory, 0x5CDD, station_entry)
        return_from_dos()
        sim.run(r[PC], 0x3D13)
        assert r[2:8] == [0xC0, 5, station_entry[15], station_entry[14], 0x60, 0]
        assert bytes(memory[r[SP]:r[SP] + 2]) == b'\x00\x63' and r[SP] == 0x5FFD
    report = dict(passed=True, total_cases=4, actual_final_effect_frames=[0, 1, 2, 300],
                  actual_intro_initialization_and_screen_unpack=True, real_rom_executed=True,
                  saved_intro_stack_address=0x65B4, saved_intro_stack_value=0x5FFF,
                  trdos_search_and_info_stubbed=True, stops_at_sector_read_entry=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroStationTransitionVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
