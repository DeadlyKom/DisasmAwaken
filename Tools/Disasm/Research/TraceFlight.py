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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", choices=("flight", "station"), default="flight")
    parser.add_argument("--frames", type=int, default=3)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    disk = (ROOT / "Tools/Disasm/Disk/original.trd").read_bytes()
    memory = Memory(out7ffd=0x10)
    start = 0x6000 if args.region == "flight" else 0x6300
    sim = Simulator(memory, {"PC":start, "SP":0x5FFF, "IY":0x5C3A},
                    config={"fast_ldir":False, "fast_djnz":False})
    registers = sim.registers
    ports = Ports(memory)
    sim.set_tracer(ports)
    filename = "17_ACTION.C.bin" if args.region == "flight" else "04_STATIONF.C.bin"
    action = (ROOT / "Tools/Disasm/Extracted/Active" / filename).read_bytes()
    for index, value in enumerate(action):
        memory[0x6000 + index] = value
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
        if pc == (0xA85E if args.region == "flight" else 0x9A81):
            main_count += 1
            if main_count >= args.frames:
                reason = "requested_frame_entries"
                break
        if step % 100000 == 0:
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
