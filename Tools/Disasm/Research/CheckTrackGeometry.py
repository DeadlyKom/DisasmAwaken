"""Полный исходный цикл перемещения и размера, входные кадры задаются явно без исполнения ISR."""
from pathlib import Path
from itertools import product
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "Tools/Disasm"), str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1")]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, PC, SP
from CheckGlyphRenderer import and_flags


def signed(value):
    return value-256 if value & 128 else value


def select_action(geometry, pixel, flags):
    x,y,w,h = geometry
    px,py = pixel
    cx,cy = px//8,py//8
    minimum = 3 if flags & 0xC0 == 0 else 2 if flags & 0xC0 == 0x40 else 1
    if y < 0 or x+w >= 32 and (x & 255) > 29:
        return "none" if flags & 4 else "move",minimum
    corner = cx+1 == ((x+w)&255) and cy+1 == ((y+h)&255)
    lower = corner if h == 1 or minimum == 2 else cy+1 == ((y+h)&255)
    if lower and (px|py)&0xF8:
        return "none" if flags & 2 else "resize",minimum
    if lower or cy == y:
        return "none" if flags & 4 else "move",minimum
    return "none",minimum


def move_axis(position,size,delta,screen):
    return max(1-size,min(screen-1,position+delta))


def resize_axis(position,size,delta,screen,minimum):
    proposed = (size+delta)&255
    value = size if proposed & 128 else proposed
    value = max(minimum,min(screen,value))
    return max(1-position,min(screen-position,value))


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    memory[0x6322:0x7F8C] = source[0x5CE:0x2238]
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for i in region["instructions"]:
                if 0x41B7 <= i["address"] < 0x41E3:
                    raw = bytes.fromhex(i["hex"])
                    assert raw == source[i["offset"]:i["offset"]+len(raw)]
                    memory[i["address"]:i["address"]+len(raw)] = raw
    simulator = Simulator(memory)
    simulator.run(start=0x41B7,stop=0x41E3)
    dis = decoder(memory)
    initial = get_registers({"SP":0x7FFE,"HL":0x1357,"DE":0x247A,"BC":0x36C9,
                             "IX":0x2468,"IY":0x5C3A,"^HL":0x369C,"^DE":0x47AD,
                             "^BC":0x58BE,"^AF":0x69CF},None,False)
    baseline = [(i*73+(i>>8)*19+17)&255 for i in range(8192)]
    observed = {}
    counts = {"move":0,"resize":0,"none":0}
    wakeups = spins = multi = 0
    motion = (0x6586,0x6587,0x6588,0x6589,0x66E8,0x66E9,0x66EA,0x66EB)
    mutable = {0xC9B0,0xC9B3,0xC9BE,0xCA1F,0xCA76,0xCA7B,0xCAAB,0xCAB0,0xCADE}

    def trace_step():
        pc = simulator.registers[PC]
        if 0xC87C <= pc < 0xCB1C and f"{pc:04X}" not in observed:
            instruction = dis.disassemble(pc,pc+1,"h")[0]
            raw = bytes(memory[pc:pc+len(instruction.bytes)])
            if raw == source[pc-0x6000:pc-0x6000+len(raw)]:
                observed[f"{pc:04X}"] = raw.hex()
            elif pc not in mutable:
                raise ValueError(f"Непредусмотренная подмена инструкции #{pc:04X}")
        simulator.run()

    def execute(geometry,pixel,flags,zero,frames,key=0,spin=False,owner=1,invalid_index=False):
        nonlocal wakeups,spins,multi
        x,y,w,h = geometry
        px,py = pixel
        action,minimum = select_action(geometry,pixel,flags) if owner and not invalid_index else ("none",None)
        current = list(geometry)
        for fx,fy in frames:
            dx,dy = fx//2-64,fy//2-48
            if action == "move":
                current[0] = move_axis(current[0],current[2],dx,32)
                current[1] = move_axis(current[1],current[3],dy,24)
            elif action == "resize":
                current[2] = resize_axis(current[0],current[2],dx,32,minimum)
                current[3] = resize_axis(current[1],current[3],dy,24,minimum)
        final_pointer = [px,py]
        if action == "move":
            ox,oy = (px-8*x)&255,(py-8*y)&255
            final_pointer = [8*max(0,min(31,(ox>>3)+current[0]))+(ox&7),
                             8*max(0,min(23,(oy>>3)+current[1]))+(oy&7)]
        elif action == "resize":
            cell = (px//8+current[2]-w)&255
            cell = 0 if cell & 128 else cell
            final_pointer = [((cell<<3)&255)|(px&7),(((current[1]+current[3]-1)<<3)&255)|(py&7)]
        record = 0xF0FD+16*key
        original = [x&255,y&255,w,h,flags,0,0,0x68,x&255,y&255,w,h,0,0x70,0xAB,0xCD]
        memory[record:record+16] = original
        memory[0x4000:0x6000] = baseline
        memory[0x8600:0x8900] = [0]*768
        cell = 0x8600+32*(py//8)+px//8
        memory[cell] = owner
        memory[0x8500:0x8502] = [0,0xFF] if invalid_index else list(key.to_bytes(2,"little"))
        memory[0x6307:0x6309] = [px,py]
        memory[0x6548] = 1
        memory[0x9B16] = 0x5A
        memory[0x9A82] = 0xA5
        memory[0xCA20] = flags
        for address in motion:
            memory[address] = 0
        for address in (0x66EC,0x6585,0x66ED,0x658A):
            memory[address] = 0
        memory[0x7FFE:0x8000] = [0xFF,0x3F]
        simulator.registers[:] = initial
        original_a = (flags*73+key+17)&255
        simulator.registers[A],simulator.registers[F] = original_a,0x40 if zero else 1
        simulator.registers[PC] = 0xC87C
        hold = 1 if zero else 2
        iteration = 0
        spun = False
        local_wakes = 0
        for _ in range(100000):
            pc = simulator.registers[PC]
            if pc == 0x3FFF:
                break
            if pc in (0xC951,0xCA40):
                if action == "none" or iteration >= len(frames):
                    raise ValueError("Непредусмотренное ожидание перемещения")
                if spin and not spun:
                    fx,fy = 128,96
                    motion_value = 0
                    spun = True
                    spins += 1
                else:
                    fx,fy = frames[iteration]
                    motion_value = 1
                memory[0x6307:0x6309] = [fx,fy]
                memory[0x66ED] = hold
                memory[motion[iteration % 8]] = motion_value
                # Проверка исходного HALT перед явным пробуждением, ISR не исполняется.
                assert memory[pc] == 0x76
                observed[f"{pc:04X}"] = "76"
                simulator.registers[PC] += 1
                local_wakes += 1
            elif pc in (0xC9AD,0xCAD5):
                iteration += 1
                memory[0x66ED] = hold if iteration < len(frames) else 0
                assert memory[pc] == 0x76
                observed[f"{pc:04X}"] = "76"
                simulator.registers[PC] += 1
                local_wakes += 1
            else:
                trace_step()
        else:
            raise ValueError("Цикл изменения геометрии не завершился")
        expected_record = [value&255 for value in current]+original[4:] if action != "none" else original
        expected_f = and_flags(original_a)
        if action != "none":
            expected_f = (expected_f & 0xC4)|(original_a & 0x28)|1
        if (memory[record:record+16] != expected_record or memory[0x6307:0x6309] != final_pointer
                or memory[0x4000:0x6000] != baseline):
            raise ValueError(f"Не совпала геометрия, указатель либо фон {geometry}/{pixel}/{flags:02X}/{action}/{frames}, "
                             f"actual={memory[record:record+4]}/{memory[0x6307:0x6309]}, expected={current}/{final_pointer}")
        if (simulator.registers[A],simulator.registers[F],simulator.registers[SP],memory[0x9B16],memory[0x9A82]) != (
                original_a,expected_f,0x8000,1 if action != "none" else 0x5A,0 if action != "none" else 0xA5):
            raise ValueError("Не совпал договор возврата либо запрос перестроения")
        for reg in (*range(2,12),*range(16,24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Не восстановлен исходный контекст интерактивного действия")
        if local_wakes != (2*len(frames)+int(spin) if action != "none" else 0):
            raise ValueError("Не совпала последовательность ожиданий")
        counts[action] += 1
        wakeups += local_wakes
        multi += int(action != "none" and len(frames)>1)

    geometries = ((0,0,1,1),(3,4,8,6),(24,18,8,6),(30,22,2,2),(-3,-2,8,6),(-5,4,8,4),(6,-2,4,8),(0,0,32,24))
    samples = ((128,96),(255,191),(0,0),(130,98),(64,40))
    for geometry in geometries:
        x,y,w,h = geometry
        left,right,top,bottom = max(0,x),min(31,x+w-1),max(0,y),min(23,y+h-1)
        cells = {(left,top),(right,top),(left,bottom),(right,bottom),((left+right)//2,(top+bottom)//2)}
        for flags,zero,(cx,cy) in product(range(256),(False,True),cells):
            frames = [samples[flags % len(samples)]]
            if flags & 0x20:
                frames.append(samples[(flags+2) % len(samples)])
            execute(geometry,(8*cx+(flags&7),8*cy+((flags>>3)&7)),flags,zero,frames,
                    key=45 if flags & 0x80 else 0,spin=bool(flags&0x10))
    for value in range(256):
        execute((0,0,4,4),(value,0),value,bool(value&1),[(128,96)],owner=0)
        execute((0,0,4,4),(value,0),value,bool(value&1),[(128,96)],invalid_index=True)
    # Проверка отдельного внутреннего выхода CA11 с уже сформированными вложенным и основным кадрами.
    words = (0x1111,0x2222,0x36C9,0x247A,0x1357,0x5ACF,0x2468,0x3FFF)
    memory[0x7FF0:0x8000] = [b for word in words for b in word.to_bytes(2,"little")]
    simulator.registers[:] = initial
    simulator.registers[SP],simulator.registers[PC] = 0x7FF0,0xCA11
    while simulator.registers[PC] != 0x3FFF:
        trace_step()
    assert simulator.registers[SP] == 0x8000 and (simulator.registers[A],simulator.registers[F]) == (0x5A,0x0D)
    report = dict(passed=True,method="original_geometry_tracker_against_clipped_move_resize_and_explicit_input_frames",
                  cases=sum(counts.values()),by_action=counts,modeled_wakeups=wakeups,wait_spins=spins,multi_iteration_cases=multi,
                  source_sha256=hashlib.sha256(source).hexdigest(),original_visited=observed,
                  interrupt_handler_executed=False,input_hardware_executed=False,native_execution_verified=False,assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/TrackGeometryVerification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "original_visited"},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
