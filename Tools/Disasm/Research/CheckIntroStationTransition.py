"""Исходное вступление и переносимый загрузчик до передачи чтения TR-DOS.

Документация: ../../../Docs/IntroStationTransition.md#фактическая-цепочка-iy-и-irq
"""
from collections import Counter, defaultdict
from hashlib import sha256
import json

from CheckActionParameterActivation import RecordedBanks
from CheckIntro import ROOT, original_memory
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from IntroScreenCodec import decode, physical


WATCHED = {
    'lookup_successor': range(0x66A2, 0x66A3),
    'lookup_copy': range(0x5E26, 0x5E27),
    'saved_stack_and_neighbors': range(0x65B3, 0x65B7),
    'screen_tail_source': range(0x8F6B, 0x9000),
    'screen_tail_copy': range(0x746B, 0x7500),
}
STACK_SCRATCH = dict(zip(range(0xDC73, 0xDC77), WATCHED['saved_stack_and_neighbors']))
SCRATCH = {0xDCE2: 0x66A2, **STACK_SCRATCH, **dict(zip(range(0xE3AB, 0xE400), range(0x746B, 0x74C0)))}
ENTRY_CONTEXTS = (0x6D8D, 0x6638, 0x6C9C, 0x6DB6, 0x6AC1, 0x66FB, 0x6A4B, 0x661E, 0x66A3, 0x5D3B)


class IntroMemory(RecordedBanks):
    registers = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.accesses = defaultdict(set)
        self.watched = {address: name for name, addresses in WATCHED.items() for address in addresses}
        self.live_source_tail = set(WATCHED['screen_tail_source'])
        self.original_source_reads = defaultdict(set)
        self.first_source_writes = {}
        self.scratch_pending = set()
        self.scratch_copied = {}
        self.scratch_overwritten = defaultdict(set)
        self.scratch_reads = set()
        self.sample_pages = []
        self.entry_contexts = {}
        self.timed_steps = []

    def __getitem__(self, address):
        if self.registers is not None and isinstance(address, int):
            pc = self.registers[PC]
            if pc == 0x661E and address == pc:
                self.timed_steps.append((self.registers[2]*256+self.registers[3], self.registers[SP]))
            if pc in ENTRY_CONTEXTS and pc not in self.entry_contexts:
                r = self.registers
                self.entry_contexts[pc] = dict(IY=r[10] * 256 + r[11], SP=r[SP],
                    I=r[14], IM=r[27], IFF=r[26], paging=self.o7ffd,
                    HL=r[6]*256+r[7], DE=r[4]*256+r[5], BC=r[2]*256+r[3],
                    AF=r[0]*256+r[1], IX=r[8]*256+r[9])
            if pc == 0x6D9F and address & 0xFF == 0x40:
                self.sample_pages.append(address >> 8)
            if address in self.watched:
                self.accesses[self.watched[address], 'read', pc].add(address)
            if address in self.live_source_tail:
                self.original_source_reads[pc].add(address)
            if address in self.scratch_pending and self.o7ffd & 7 == 1:
                self.scratch_reads.add((pc, address))
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.registers is not None:
            pc = self.registers[PC]
            if address in self.watched:
                self.accesses[self.watched[address], 'write', pc].add(address)
            if address in self.live_source_tail:
                self.live_source_tail.remove(address)
                self.first_source_writes[address] = pc, value
            if address in SCRATCH and self.o7ffd & 7 == 1:
                if pc == 0x6D9F:
                    self.scratch_pending.add(address)
                    self.scratch_copied[address] = value
                elif address in self.scratch_pending:
                    self.scratch_pending.remove(address)
                    self.scratch_overwritten[pc, value].add(address)
        super().__setitem__(address, value)


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


class IntroCPU(Simulator):
    def __init__(self, memory):
        super().__init__(memory)
        self.irq_contexts = Counter()

    def accept_interrupt(self, registers, memory, prev_pc):
        iy = registers[10] * 256 + registers[11]
        if super().accept_interrupt(registers, memory, prev_pc):
            self.irq_contexts[prev_pc, iy] += 1
            return True
        return False


def main():
    flat = original_memory()
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    assert sha256(rom).hexdigest() == 'd55daa439b673b0e3f5897f99ac37ecb45f974d1862b4dadb85dec34af99cb42'
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    intro_entry = next(row for row in json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_text(
        encoding='utf-8'))['entries'] if row['slot'] == 3)
    initializer_code = bytes(flat[0x6500:0x65B3])
    start = intro_entry['offset'] + 0x200
    assert initializer_code == disk[start:start + len(initializer_code)]
    station_entry = disk[4 * 16:5 * 16]
    assert station_entry[:9] == b'STATIONFC'
    unpacked = decode(bytes(flat[0x89CB:]))['data']
    screen = bytearray(6912)
    for index, value in enumerate(unpacked):
        screen[physical(0x4000 + index) - 0x4000] = value
    tail_profiles = []
    initializer_profiles = []
    for frames in (0, 1, 2, 300):
        banks = [bytearray([0] * 0x4000) for _ in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        banks[2][:] = bytes(flat[0x8000:0xC000])
        memory = IntroMemory(banks=banks, out7ffd=16)
        memory.roms = (list(rom), list(rom))
        memory.out7ffd(16)
        memory[0x5C00] = memory[0x5C04] = 255
        sim = IntroCPU(memory)
        trace = IntroInput(sim, frames)
        sim.set_tracer(trace)
        initial = get_registers({'PC': 0x6500, 'SP': 0x5FFF, 'IY': 0x5C3A,
            'IX':0xABCD, '^AF':0xA55A}, {'im':1, 'iff':0}, False)
        sim.registers[:] = initial
        memory.registers = sim.registers
        sim.run(0x6500, 0x5D3B, interrupts=True)
        memory.registers = None
        assert trace.polls == min(300, frames + 1), frames
        assert sim.registers[SP] == (0x5FFF if frames == 300 else 0x5FF9), frames
        assert bytes(memory[0x65B4:0x65B6]) == bytes.fromhex('FF 5F')
        assert bytes(memory[0x5D3B:0x5D3B + 0x100]) == bytes(flat[0x65B7:0x66B7])
        assert bytes(memory[0x6E31:0x6ECB]) == bytes(flat[0x8931:0x89CB])
        # Проверка бывшей области NOP, условный JP из хвоста пришёл бы после POP HL.
        assert bytes(memory[0x68ED:0x68EF]) == bytes.fromhex('E1 22')
        initializer_profiles.append(dict(final_effect_frames=frames,
            entries={f'{pc:04X}': context for pc, context in memory.entry_contexts.items()},
            loader_IY=sim.registers[10] * 256 + sim.registers[11],
            loader_SP=sim.registers[SP], loader_IFF=sim.registers[26],
            loader_AF=sim.registers[0]*256+sim.registers[1], loader_BC=sim.registers[2]*256+sim.registers[3],
            timed_callback_counters=[counter for counter,stack in memory.timed_steps],
            FRAMES_before_loader=int.from_bytes(memory[0x5C78:0x5C7B], 'little'),
            IRQ_contexts=[dict(PC=pc,IY=iy,count=count) for (pc,iy),count in sorted(sim.irq_contexts.items())]))
        # Проверка фактической непрерывной цепочки без подготовки IY на внутренних границах.
        expected_entries = {0x6D8D:0x5C3A, 0x6638:0x5CFF,
                            0x6C9C:0x5C29, 0x6DB6:0x5C0F, 0x6AC1:0x5C0F,
                            0x66FB:0x5C0F, 0x6A4B:0x5C0F}
        if frames:
            expected_entries.update({0x661E:0x5C0F,0x66A3:0x5C0F})
        assert {pc:row['IY'] for pc,row in memory.entry_contexts.items()} == expected_entries, frames
        assert memory.entry_contexts[0x6D8D]['HL'] == 0x6080, frames
        built = memory.entry_contexts[0x6638]
        assert {key:built[key] for key in ('HL','DE','BC','AF','IX','IY','IFF','paging')} == dict(
            HL=0x9300,DE=0xD300,BC=0,AF=0x1449,IX=0x6400,IY=0x5CFF,IFF=0,paging=0x14), frames
        assert sim.registers[10:12] == [0x5C,0x0F], frames
        assert sim.registers[8:10] == [0,0] and sim.registers[16:18] == [0xA5,0x5A], frames
        assert {iy for pc,iy in sim.irq_contexts} == {0x5C29,0x5C0F}, frames
        assert sum(sim.irq_contexts.values()) == 45 + 3 * frames, frames
        assert initializer_profiles[-1]['FRAMES_before_loader'] == 45 + 3 * frames, frames
        assert sim.registers[26] == int(frames in (0,300)), frames
        assert memory.timed_steps == [(300-i,0x5FF9) for i in range(frames)], frames
        if frames < 300:
            assert sim.registers[:4] == [0xBE,0x6A,0x7F,0xFE], frames
        memory.registers = sim.registers
        sim.run(0x5D3B, 0x3D13, interrupts=True)
        memory.registers = None
        original_copy = {0x66A2: flat[0x66A2]}
        original_copy.update(zip(WATCHED['saved_stack_and_neighbors'], bytes.fromhex('00 FF 5F 00')))
        original_copy.update({address: flat[address + 0x1B00] for address in range(0x746B, 0x74C0)})
        assert memory.scratch_copied == {address: original_copy[source] for address, source in SCRATCH.items()}
        assert not memory.scratch_pending and not memory.scratch_reads
        assert memory.scratch_overwritten == {(0x6A1B, 0xFF): set(SCRATCH)}
        assert memory.sample_pages == [(0xAD + row) & 255 for row in range(len(memory.sample_pages))]
        assert len(memory.sample_pages) == rom[0x00FF] == 206
        assert memory.accesses['screen_tail_source', 'read', 0x6526] == set(WATCHED['screen_tail_source'])
        assert memory.accesses['screen_tail_source', 'write', 0x6559] == {0x8F93}
        assert memory.accesses['screen_tail_source', 'read', 0x655B] == set(range(0x8F93, 0x9000))
        assert memory.accesses['screen_tail_source', 'write', 0x655B] == set(range(0x8F94, 0x9000))
        assert memory.original_source_reads == {0x6526: set(WATCHED['screen_tail_source'])}
        assert not memory.live_source_tail
        source_spans = ((0x6A1B, 0xFF, 0x8F6B, 0x8F93), (0x6559, 0, 0x8F93, 0x8F94),
                        (0x655B, 0, 0x8F94, 0x9000))
        assert memory.first_source_writes == {address: (pc, value) for pc, value, start, end in source_spans
                                             for address in range(start, end)}
        first_writes = [dict(pc=pc, value=value, start=start, end_exclusive=end)
                        for pc, value, start, end in source_spans]
        assert memory.accesses['screen_tail_copy', 'read', 0x651B] == set(WATCHED['screen_tail_copy'])
        assert memory.accesses['screen_tail_copy', 'write', 0x6526] == set(WATCHED['screen_tail_copy'])
        assert memory.accesses['screen_tail_copy', 'read', 0x6D9F] == set(range(0x746B, 0x74C0))
        assert {pc for name, mode, pc in memory.accesses if name == 'screen_tail_copy' and mode == 'read'} == {
            0x651B, 0x6D9F}
        assert memory.accesses['lookup_copy', 'write', 0x650A] == {0x5E26}
        assert not any(mode == 'read' and name == 'lookup_copy' for name, mode, _ in memory.accesses)
        stack_accesses = {(mode, f'{pc:04X}'): sorted(addresses) for (name, mode, pc), addresses in memory.accesses.items()
                          if name == 'saved_stack_and_neighbors'}
        assert stack_accesses == {('write', '6531'): [0x65B4, 0x65B5],
                                  ('read', '6D9F'): [0x65B3, 0x65B4, 0x65B5, 0x65B6]}, stack_accesses
        assert bytes(memory[0x65B3:0x65B7]) == bytes.fromhex('00 FF 5F 00')
        tail_profiles.append(dict(frames=frames, scratch_bank=1, scratch_reads_before_overwrite=0,
                                  screen_tail_original_reads=[dict(pc=0x6526, bytes=149)],
                                  screen_tail_first_writes=first_writes,
                                  sample_rows=len(memory.sample_pages), bank4_rows=0x1300 // 128,
                                  scratch_overwrites=[
                                      dict(pc=pc, value=value, byte_count=len(addresses))
                                      for (pc, value), addresses in sorted(memory.scratch_overwritten.items())
                                  ],
                                  accesses=[dict(region=name, mode=mode, pc=pc, byte_count=len(addresses))
                                            for (name, mode, pc), addresses in sorted(memory.accesses.items())]))
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
                  tail_access_profiles=tail_profiles,
                  detached_prefix_jp_target_after_generation=0x68EE,
                  generated_opcode_at_target=0x22, generated_pop_hl_before_target=0x68ED,
                  saved_intro_stack_address=0x65B4, saved_intro_stack_value=0x5FFF,
                  saved_stack_texture_copy=dict(bank=1, source=0x65B3, destination=0xDC73,
                                                data='00ff5f00', read_pc=0x6D9F, overwrite_pc=0x6A1B,
                                                reads_before_overwrite=0),
                  trdos_search_and_info_stubbed=True, stops_at_sector_read_entry=True, assembly_executed=False)
    report['initializer_entry_contexts'] = initializer_profiles
    report['initial_IM_IFF_explicit'] = True
    report['original_initializer_sha256'] = sha256(initializer_code).hexdigest()
    report['original_IY_chain_and_ROM_IRQ_contexts_executed'] = True
    report['native_execution'] = False
    report['nonzero_AF_alternate_preserved_before_loader'] = True
    report['IX_before_loader'] = 0
    report['BuildIntroTexture_original_entry_and_return_context_checked'] = True
    report['timed_effect_real_callback_counters_and_stack_checked'] = True
    report['early_space_exit_AF'] = 0xBE6A
    (ROOT / 'Tools/Disasm/Reports/IntroStationTransitionVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
