"""Исчерпывающая проверка осевых ограничений перемещения и размера на допустимом диапазоне ввода."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,H,L,D,E,B,C
from CheckTrackGeometry import move_axis,resize_axis


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    simulator = Simulator(memory)
    initial = get_registers({"SP":0x7FFE},None,False)
    counts = {"move_x":0,"move_y":0,"resize_x":0,"resize_y":0}
    for axis,screen,deltas in (("x",32,range(-64,64)),("y",24,range(-48,48))):
        for size in range(1,screen+1):
            for position in range(1-size,screen):
                for delta in deltas:
                    for minimum in (0,1,2,3):
                        simulator.registers[:] = initial
                        simulator.registers[D],simulator.registers[E] = (4,size) if axis == "x" else (size,4)
                        simulator.registers[B],simulator.registers[C] = (0,position&255) if axis == "x" else (position&255,0)
                        simulator.registers[H],simulator.registers[L] = (0,delta&255) if axis == "x" else (delta&255,0)
                        if minimum:
                            for address in (0xCA77,0xCA7C,0xCAAC,0xCAB1):
                                memory[address] = minimum
                            start,stop = 0xCA60,0xCACA
                            expected = resize_axis(position,size,delta,screen,minimum)
                        else:
                            start,stop = 0xC971,0xC9AB
                            expected = move_axis(position,size,delta,screen)&255
                        simulator.run(start=start,stop=stop)
                        actual = simulator.registers[L if axis == "x" else H]
                        if actual != expected:
                            raise ValueError(f"Не совпало ограничение {axis}/{size}/{position}/{delta}/{minimum}: {actual} != {expected}")
                        counts[("resize_" if minimum else "move_")+axis] += 1
    report = dict(passed=True,method="original_axis_clamps_exhaustive_valid_size_position_and_half_pixel_delta",
                  cases=sum(counts.values()),by_axis=counts,source_sha256=hashlib.sha256(source).hexdigest(),
                  full_tracker_executed=False,irq_enabled=False,assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/GeometryClampsVerification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
