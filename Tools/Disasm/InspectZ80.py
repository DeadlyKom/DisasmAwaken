"""Чтение исходных Z80-инструкций, без сборки и исполнения игры."""

from pathlib import Path
from types import SimpleNamespace
import argparse
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.disassembler import Disassembler


class Instruction:
    def __init__(self, address, operation, data):
        self.address = address
        self.operation = operation.replace("$", "#").upper()
        self.bytes = bytes(data)
        self.variant = 0


def decoder(memory):
    return Disassembler(list(memory), SimpleNamespace(
        asm_hex=True, asm_lower=False, defb_size=16, defm_size=64,
        defw_size=8, handle_rst=False, imaker=Instruction, opcodes="", wrap=False))


def entry(slot):
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    return next(item for item in manifest["entries"] if item["slot"] == slot)


def memory_for(slot, origin=None, offset=0, sectors=False):
    item = entry(slot)
    origin = item["parameter"] if origin is None else origin
    path = ROOT / (item["path"] + (".sectors.bin" if sectors else ".bin"))
    data = path.read_bytes()[offset:]
    # Проверка границ представления до размещения исходных байтов.
    if not 0 <= origin < 65536 or origin + len(data) > 65536:
        raise ValueError("Блок не помещается в 64K, укажите доказанный адрес или смещение")
    memory = bytearray(65536)
    memory[origin:origin + len(data)] = data
    return memory


def listing(memory, start, end):
    return "\n".join(
        f"{i.address:04X}  {i.bytes.hex(' '):<13}  {i.operation}"
        for i in decoder(memory).disassemble(start, end, "h"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slot", type=int)
    parser.add_argument("start", type=lambda value: int(value, 0))
    parser.add_argument("end", type=lambda value: int(value, 0))
    parser.add_argument("--origin", type=lambda value: int(value, 0))
    parser.add_argument("--offset", type=lambda value: int(value, 0), default=0)
    parser.add_argument("--sectors", action="store_true")
    args = parser.parse_args()
    print(listing(memory_for(args.slot, args.origin, args.offset, args.sectors),
                  args.start, args.end))
