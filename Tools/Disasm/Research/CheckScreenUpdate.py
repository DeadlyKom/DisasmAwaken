"""Проверка двух экранов в восьми физических банках с исходными OUT и кодом указателя."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.pagingtracer import SliceableMemory,PagingTracer
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,SP
from CheckInsetFrame import bitmap_address


class PortTrace(PagingTracer):
    def __init__(self,simulator):
        self.simulator = simulator
        self.out7ffd = simulator.memory.o7ffd
        self.border = self.outfe = self.outfffd = 0
        self.ay = [0]*16
        self.writes = []

    def write_port(self,registers,port,value,offset):
        self.writes.append((port,value))
        super().write_port(registers,port,value,offset)


def put(memory,address,data):
    for index,value in enumerate(data):
        memory[address+index] = value


def pointer_image(screen,source,x,y):
    result = screen.copy()
    for row in range(min(8,192-y)):
        offset = 32*(x&7)+4*row
        address = bitmap_address(y+row,x//8)-0x4000
        result[address] = (result[address]&source[offset])^source[offset+1]
        if x < 248:
            result[address+1] = (result[address+1]&source[offset+2])^source[offset+3]
    return result


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = SliceableMemory(banks=[[(page*53+i*17)&255 for i in range(16384)] for page in range(8)],out7ffd=0x10)
    put(memory,0x6000,source)
    put(memory,0x6322,source[0x5CE:0x2238])
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for instruction in region["instructions"]:
                if 0x41B7 <= instruction["address"] < 0x41E3:
                    raw = bytes.fromhex(instruction["hex"])
                    assert raw == source[instruction["offset"]:instruction["offset"]+len(raw)]
                    put(memory,instruction["address"],raw)
    simulator = Simulator(memory)
    simulator.run(start=0x41B7,stop=0x41E3)
    base_banks = [bank.copy() for bank in memory.banks]
    initial = get_registers({"SP":0x7FFE,"HL":0x1357,"DE":0x247A,"BC":0x36C9,
                             "IX":0x2468,"IY":0x5C3A,"^HL":0x369C,"^DE":0x47AD,
                             "^BC":0x58BE,"^AF":0x69CF},None,False)
    coordinates = ((0,0),(7,7),(248,184),(255,191))
    cases = list(product(range(32),coordinates,(False,True),(0,1,0x80,0xFF)))
    cases += [(0x10,(255,191),True,flags) for flags in range(256)]
    port_count = 0
    for old,(x,y),active,flags in cases:
        # Создание независимого банкового пространства, фиксированные 5 и 2 алиасны окну при их выборе.
        memory = SliceableMemory(banks=[bank.copy() for bank in base_banks],out7ffd=old)
        simulator = Simulator(memory)
        trace = PortTrace(simulator)
        simulator.set_tracer(trace)
        screen = [(i*73+(i>>8)*19+old*11+flags*13)&255 for i in range(6912)]
        put(memory,0x4000,screen)
        put(memory,0x8600,[0]*768)
        put(memory,0x6307,[x,y])
        memory[0x6306] = old
        memory[0x6548] = 0xA5
        put(memory,0x6575,[0xCC]*16)

        def run(start,entry_flags):
            put(memory,0x7FFE,[0xFF,0x3F])
            simulator.registers[:] = initial
            simulator.registers[A],simulator.registers[F] = old^flags,entry_flags
            simulator.run(start=start,stop=0x3FFF)
            if simulator.registers[SP] != 0x8000:
                raise ValueError("Не восстановлен стек банкового обновления")

        if active:
            run(0x6413,flags)
        expected_snapshot = pointer_image(screen,source,x,y) if active else screen
        if memory[0x4000:0x5B00] != expected_snapshot:
            raise ValueError("Не подготовлен исходный указатель перед банковым снимком")
        bank7_tail = memory.banks[7][6912:].copy()
        foreign = {page:memory.banks[page].copy() for page in (0,1,3,4,6)}
        trace.writes.clear()
        run(0xA49F,flags)
        total = 0x17+expected_snapshot[-1]
        expected_f = (flags&0xC1)|(total&8)|((total&2)<<4)
        if (simulator.registers[A],simulator.registers[F],memory[0x6306],memory[0x9B16],trace.out7ffd) != (
                0x18,expected_f,0x18,1,0x18):
            raise ValueError("Не совпали AF, тень или порт начала обновления")
        if memory.memory[3] is not memory.banks[0] or trace.writes != [(0x7FFD,0x17),(0x7FFD,0x18)]:
            raise ValueError("Не совпали окно банка и последовательность OUT начала обновления")
        if (memory.banks[7][:6912] != expected_snapshot or memory.banks[7][6912:] != bank7_tail
                or memory[0x4000:0x5B00] != screen or memory[0x6548] != (1 if active else 0xA5)):
            raise ValueError("Не совпали два экрана либо порядок копирования и восстановления указателя")
        for reg in (*range(2,12),*range(16,24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Начало обновления изменило сохраняемый регистр")
        # Имитация рисования новой сцены только в базовый экран, скрытый экран обязан оставаться снимком.
        new_screen = [value^((old+flags+0x5A)&255) for value in screen]
        put(memory,0x4000,new_screen)
        if memory.banks[7][:6912] != expected_snapshot:
            raise ValueError("Запись базового экрана изменила отображаемый снимок")
        end_flags = flags^0xA5
        run(0xA496,end_flags)
        if (simulator.registers[A],simulator.registers[F],memory[0x6306],memory[0x9B16],trace.out7ffd,memory[0x6548]) != (
                0x10,end_flags,0x10,0,0x10,0):
            raise ValueError("Не совпали AF или состояние завершения обновления")
        if memory[0x4000:0x5B00] != pointer_image(new_screen,source,x,y) or memory.banks[7][:6912] != expected_snapshot:
            raise ValueError("Не совпал новый экран с указателем либо повреждён старый снимок")
        if trace.writes != [(0x7FFD,0x17),(0x7FFD,0x18),(0x7FFD,0x10)]:
            raise ValueError("Не совпала полная последовательность аппаратных страниц")
        for page,original in foreign.items():
            if memory.banks[page] != original:
                raise ValueError("Банковое обновление изменило постороннюю физическую страницу")
        for reg in (*range(2,12),*range(16,24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Завершение обновления изменило сохраняемый регистр")
        port_count += len(trace.writes)
    report = dict(passed=True,method="original_screen_update_with_eight_physical_banks_paging_and_cursor_pixels",
                  cases=len(cases),out_writes=port_count,screen_bytes=6912,banks_modeled=8,
                  page_lock_initially_clear=True,pointer_owner_fixture=0,source_sha256=hashlib.sha256(source).hexdigest(),
                  snapshot_contains_original_cursor=True,base_restored_after_snapshot=True,
                  interrupt_handler_executed=False,native_execution_verified=False,assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/ScreenUpdateVerification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
