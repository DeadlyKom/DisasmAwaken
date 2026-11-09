"""Ограниченная модель исполнения ACTION с подменённым интерфейсом TR-DOS.

Не является проверкой загрузки в настоящем эмуляторе. Нужна для наблюдения
переключений банков и создаваемого кода, без изменения оригинальных файлов.
"""

from pathlib import Path
import json
import argparse
import sys
import time


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import Memory
from skoolkit.simutils import A, F, B, C, D, E, H, L, SP, PC, T, IFF


class Ports:
    def __init__(self, memory):
        self.memory = memory
        self.events = []

    def write_port(self, registers, port, value, offset):
        if port & 0x8002 == 0:
            self.memory.out7ffd(value)
            self.events.append(dict(pc=registers[PC], value=value, bank=value & 7))

    def read_port(self, registers, port):
        return 0 if port & 255 in (0x1F, 0xDF) else 255


class FlightCycleChecks:
    """Контроль стека и реальных банков на входе и выходе полётного кадра."""
    STARTUP_PAGES = {0xA833: 0x1E, 0xA83E: 0x1E, 0xA843: 0x10, 0xA84B: 0x11,
                     0xA84E: 0x10, 0xA851: 0x10, 0xA858: 0x10}

    FRAME_CALLS = (
        (0xA867, 0x10), (0xA86A, 0x10), (0xA86F, 0x10), (0xA872, 0x11),
        (0xA875, 0x11), (0xA87A, 0x11), (0xA87D, 0x10), (0xA880, 0x10),
        (0xA8C8, 0x10), (0xA8CF, 0x10), (0xA8D2, 0x10), (0xA8D5, 0x10),
        (0xA8D8, 0x10), (0xA8DD, 0x10), (0xA8E0, 0x11), (0xA8E5, 0x11),
        (0xA8E8, 0x10), (0xA97E, 0x10), (0xA983, 0x10), (0xAA87, 0x14),
        (0xAA8A, 0x10), (0xAA9F, 0x10), (0xAAA3, 0x11), (0xAAA6, 0x11),
        (0xAAA9, 0x11), (0xAAAC, 0x11), (0xAAAF, 0x11), (0xAAB2, 0x11),
        (0xAAB5, 0x11), (0xAAB8, 0x11), (0xAABB, 0x11), (0xAAC0, 0x11),
    )
    FRAME_CALL_SITES = dict(FRAME_CALLS)

    def __init__(self):
        self.calls = []
        self.startup = []
        self.loop_sp = None
        self.start_sp = None
        self.de = None
        self.frame_returns = 0
        self.loop_entries = 0
        self.legacy_parameters = None
        self.legacy_execution_visits = 0

    def observe(self, pc, registers, memory):
        sp = registers[SP]
        page = memory.o7ffd
        if 0x5E1F <= pc < 0x5EDB:
            self.legacy_execution_visits += 1
        if pc == 0x4267:
            assert page == 0x19 and self.legacy_parameters is None
            assert bytes(memory[0x5CDD + index] for index in range(9)) == b'CONTROL0C'
            position = (memory[0x5CEB] + 1) & 255
            assert (registers[H], registers[L], registers[A]) == (memory[0x5CEC], position, memory[0x5CEA])
            self.legacy_parameters = dict(track=registers[H], sector=position, sector_count=registers[A],
                                          old_opcode=memory[0x5E1F], old_count_opcode=memory[0x5E22])
        elif pc == 0x426D:
            params = self.legacy_parameters
            assert (memory[0x5E20], memory[0x5E21], memory[0x5E23]) == (
                params['sector'], params['track'], params['sector_count'])
            assert (memory[0x5E1F], memory[0x5E22]) == (params['old_opcode'], params['old_count_opcode'])
        if pc == 0xA82D:
            from PackedResourceCodec import decode
            from ReferenceActionLogRatio import EXP, LOG

            self.start_sp = sp
            assert page == 0x19 and sp == 0xBFFE and not registers[IFF]
            assert (memory[sp], memory[sp + 1]) == (0x3D, 0x62)
            assert (memory[0xAA9A], memory[0xA8BC]) == (1, 0x2E)
            for start, data in (
                (0x9100, bytes(word & 255 for word in LOG)), (0x9200, bytes(word >> 8 for word in LOG)),
                (0x9300, bytes(EXP)), (0x9400, bytes((0x8000 + 32 * i) >> 8 for i in range(256))),
                (0x9500, bytes((32 * i) & 255 for i in range(256))),
                (0x9600, bytes(i // 8 for i in range(256))), (0x9700, bytes(128 >> (i % 8) for i in range(256))),
            ):
                assert bytes(memory[start + i] for i in range(256)) == data, hex(start)
            files = ROOT / 'Tools/Disasm/Extracted/Active'
            panel = decode((files / '25_PANEL.C.bin').read_bytes())['data']
            objects = (files / '24_OBJECT3D.C.bin').read_bytes()
            assert bytes(memory.banks[6][:len(panel)]) == panel
            assert bytes(memory.banks[4][:len(objects)]) == objects
            for address, value in ((0xECA3, 0), (0xECAA, 0xEC7E), (0xEC5D, 0xEC80)):
                assert memory[address] + 256 * memory[address + 1] == value
        if pc in self.STARTUP_PAGES:
            assert self.start_sp is not None and page == self.STARTUP_PAGES[pc], (pc, page)
            assert sp == self.start_sp - (2 if pc == 0xA858 else 0), (pc, sp, self.start_sp)
            assert not registers[IFF], pc
            self.startup.append(pc)
            if pc == 0xA83E:
                assert bytes(memory.banks[5][:0x1B00]) == bytes(memory.banks[6][:0x1B00])
            elif pc == 0xA851:
                self.de = registers[D], registers[E]
            elif pc == 0xA858:
                assert (registers[D], registers[E]) == (0xF1, 0xAB)
        if pc in self.FRAME_CALL_SITES:
            self.calls.append((pc, page))
            assert sp == self.loop_sp - 2, (pc, sp)
        if pc == 0xA859:
            if self.loop_sp is None:
                self.loop_sp = sp
                assert sp == self.start_sp and not registers[IFF]
                assert (registers[D], registers[E]) == self.de
                assert (registers[H], registers[L], registers[A], registers[F]) == (0xC5, 0x46, 0x10, 0x42)
            self.loop_entries += 1
            assert sp == self.loop_sp and page == 0x10, (pc, sp, page)
        elif pc == 0xA85E:
            assert self.loop_sp is not None and sp == self.loop_sp - 2 and page == 0x10
            assert (memory[sp], memory[sp + 1]) == (0x5C, 0xA8)
        elif pc == 0xA85C:
            assert sp == self.loop_sp and page == 0x10, (pc, sp, page)
            assert tuple(self.calls) == self.FRAME_CALLS, self.calls
            assert registers[A] == 16 and registers[F] == 0x42 and registers[D:E + 1] == [0, 64]
            marker = registers[8] * 256 + registers[9]
            assert (memory[marker], memory[marker + 1]) == (128, 128)
            self.calls.clear()
            self.frame_returns += 1

    def report(self, entries, loads):
        assert self.startup == list(self.STARTUP_PAGES)
        assert self.loop_entries == entries and self.frame_returns == entries - 1
        expected_loads = ((25, 0xC000, 6), (20, 0xC000, 3), (21, 0xEC00, 3),
                          (22, 0xC000, 1), (23, 0xDADE, 1), (24, 0xC000, 4))
        assert tuple((item["slot"], item["address"], item["bank"]) for item in loads) == expected_loads
        return dict(passed=True, total_cases=1, method="bounded_skoolkit_with_trdos_stub",
                    startup_page_checkpoints=[dict(pc=pc, page=self.STARTUP_PAGES[pc]) for pc in self.startup],
                    complete_frame_returns=self.frame_returns, frame_entries=entries,
                    frame_call_sites=[dict(pc=pc, page=page) for pc, page in self.FRAME_CALLS],
                    loop_entry_sp=self.loop_sp, child_frame_return_address=0xA85C,
                    legacy_control0_parameters=self.legacy_parameters, legacy_runtime_execution_visits=self.legacy_execution_visits,
                    panel_bytes_compared=0x1B00, boot_table_bytes_compared=1792, loads=loads, real_boot_verified=False, assembly_executed=False)


def main(arguments=None, scan_observer=None, *, boot_simulator=None, save_reports=True,
         ports_factory=Ports, instruction_observer=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", choices=("flight", "station"), default="flight")
    parser.add_argument("--frames", type=int, default=3)
    parser.add_argument("--verify-flight-cycle", action="store_true")
    args = parser.parse_args(arguments)
    if args.verify_flight_cycle and (args.region != "flight" or args.frames < 2):
        parser.error("--verify-flight-cycle requires flight and at least two frame entries")
    cycle = FlightCycleChecks() if args.verify_flight_cycle else None
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    disk = (ROOT / "Tools/Disasm/Disk/original.trd").read_bytes()
    start = 0x6000 if args.region == "flight" else 0x6300
    if boot_simulator is None:
        memory = Memory(out7ffd=0x10)
        sim = Simulator(memory, {"PC":start, "SP":0x5FFF, "IY":0x5C3A},
                        config={"fast_ldir":False, "fast_djnz":False})
        filename = "17_ACTION.C.bin" if args.region == "flight" else "04_STATIONF.C.bin"
        action = (ROOT / "Tools/Disasm/Extracted/Active" / filename).read_bytes()
        for index, value in enumerate(action):
            memory[0x6000 + index] = value
    else:
        sim = boot_simulator
        memory = sim.memory
        assert sim.registers[PC] == start
    registers = sim.registers
    ports = ports_factory(memory)
    sim.set_tracer(ports)
    selected = None
    loads = []
    visited = {}
    calls = set()
    reason = "instruction_limit"
    started = time.monotonic()
    next_frame = 70908
    main_count = 0

    # Исполнение ограничено числом инструкций, временем и числом входов в полётный кадр.
    for step in range(2000000):
        pc = registers[PC]
        bank = memory.o7ffd & 7 if pc >= 0xC000 else -1
        key = f"{bank}:{pc:04X}"
        visited.setdefault(key, bytes(memory[(pc+i)&65535] for i in range(4)).hex())
        if memory[pc] in (0xCD, 0xC4, 0xCC, 0xD4, 0xDC, 0xE4, 0xEC, 0xF4, 0xFC):
            calls.add((memory.o7ffd & 7, pc, memory[(pc+1)&65535] + 256*memory[(pc+2)&65535]))
        if cycle:
            cycle.observe(pc, registers, memory)
        if scan_observer is not None and pc == 0x6F1D:
            scan_observer(main_count, memory, registers)
        if instruction_observer is not None:
            instruction_observer(main_count, memory, registers)
        if pc == (0xA85E if args.region == "flight" else 0x9A81):
            main_count += 1
            if main_count >= args.frames:
                reason = "requested_frame_entries"
                break
        if step % 100000 == 0:
            if save_reports:
                print(f"step={step} pc={pc:04X} bank={memory.o7ffd & 7} frames={main_count}", flush=True)
            if time.monotonic() - started > 35:
                reason = "wall_time_limit"
                break
        if pc == 0x3D13:
            function = registers[C]
            name = bytes(memory[0x5CDD+i] for i in range(9))
            if function in (0x0A, 0x0E):
                matches = [e for e in manifest["entries"] if not e["deleted"] and
                           disk[e["slot"]*16:e["slot"]*16+9] == name]
                if len(matches) != 1:
                    reason = "unsupported_file_search_" + name.hex()
                    break
                selected = matches[0]
                if function == 0x0A:
                    registers[C] = selected["slot"]
            elif function == 0x08:
                selected = next(e for e in manifest["entries"] if e["slot"] == registers[A])
            if selected:
                header = disk[selected["slot"]*16:selected["slot"]*16+16]
                for index, value in enumerate(header):
                    memory[0x5CDD+index] = value
            if function == 0x0E:
                address = registers[H]*256 + registers[L]
                if registers[A] != 3:
                    address = selected["parameter"]
                data = disk[selected["offset"]:selected["offset"]+selected["length"]]
                if address + len(data) > 65536:
                    reason = "unsupported_load_wrap"
                    break
                for index, value in enumerate(data):
                    memory[address+index] = value
                loads.append(dict(slot=selected["slot"], address=address, length=len(data), bank=memory.o7ffd & 7))
            elif function == 0x05:
                address = registers[H]*256+registers[L]
                offset = (registers[D]*16+registers[E])*256
                length = (registers[B] or 256)*256
                if address + length > 65536 or offset + length > len(disk):
                    reason = "unsupported_sector_wrap"
                    break
                for index, value in enumerate(disk[offset:offset+length]):
                    memory[address+index] = value
                loads.append(dict(offset=offset, address=address, length=length, bank=memory.o7ffd & 7))
            elif function not in (0x08, 0x0A):
                reason = f"unsupported_trdos_{function:02X}"
                break
            registers[F] &= 0xFE
            stack = registers[SP]
            registers[PC] = memory[stack] + 256*memory[(stack+1)&65535]
            registers[SP] = (stack+2)&65535
        elif pc < 0x4000:
            reason = f"unsupported_rom_{pc:04X}"
            break
        else:
            sim.run()
            if registers[T] >= next_frame:
                next_frame = (registers[T]//70908+1)*70908
                if registers[IFF]:
                    sim.accept_interrupt(registers, memory, pc)
    report = dict(method="bounded_skoolkit_with_trdos_stub", real_boot_verified=False,
                  reason=reason, steps=step, frame_entries=main_count, loads=loads,
                  paging=ports.events, calls=[list(c) for c in sorted(calls)], visited=visited)
    if cycle:
        assert reason == "requested_frame_entries", (reason, main_count)
        result = cycle.report(main_count, loads)
        if scan_observer is not None or not save_reports:
            return result
        (ROOT / "Tools/Disasm/Reports/ActionFlightCycleVerification.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return
    if not save_reports:
        return report
    snapshots = ROOT / "Tools/Disasm/Research/ModelScreens"
    snapshots.mkdir(parents=True, exist_ok=True)
    for page in (5, 7):
        (snapshots / f"{args.region}_bank{page}.scr").write_bytes(bytes(memory.banks[page][:6912]))
    target = ROOT / ("Tools/Disasm/Reports/FlightModel.json" if args.region == "flight"
                     else "Tools/Disasm/Reports/StationModel.json")
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("STOP", reason, "steps", step, "unique", len(visited), "loads", loads)


if __name__ == "__main__":
    main()
