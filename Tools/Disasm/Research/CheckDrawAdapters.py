"""Проверка исходной инициализации индексов и всех двухинструкционных обёрток рисования."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, SP


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    # Восстановление реального переноса низкого станционного кода, плоская дисковая копия имеет другие смещения.
    memory[0x6322:0x7F8C] = source[0x5CE:0x2238]
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    for region in flow:
        if region["name"] == "StationBoot":
            for instruction in region["instructions"]:
                if 0x4257 <= instruction["address"] < 0x4278:
                    raw = bytes.fromhex(instruction["hex"])
                    if source[instruction["offset"]:instruction["offset"]+len(raw)] != raw:
                        raise ValueError("Не совпали исходные байты загрузчика индексов")
                    memory[instruction["address"]:instruction["address"]+len(raw)] = raw
    functions = json.loads((ROOT / "Tools/Disasm/Reports/Functions.json").read_text(encoding="utf-8"))
    items = json.loads((ROOT / "Tools/Disasm/Reports/InterfaceItems.json").read_text(encoding="utf-8"))
    adapters = []
    for function in functions:
        if function["region"] != "Station" or not function["name"].startswith("DrawItem"):
            continue
        address = function["address"]
        if function["end_offset"]-function["offset"] == 6 and memory[address:address+6] == [0x21, 0, 0, 0xC3, 0xDF, 0xC2]:
            index = int(function["name"][8:])
            if items[index]["values"][11] != address:
                raise ValueError("Обёртка не соответствует исходному указателю DrawHandler")
            adapters.append(dict(index=index, address=address, path=function["path"]))
    if len(adapters) != 21:
        raise ValueError("Изменился состав исследованного семейства обёрток")
    simulator = Simulator(memory)
    simulator.run(start=0x4257, stop=0x4278)
    for item in items:
        address = item["values"][11]
        if memory[address+1:address+3] != list(item["index"].to_bytes(2, "little")):
            raise ValueError("Загрузчик не записал индекс в операнд DrawHandler")
        # Поле +5 остаётся исходным TextIndex, цикл не пишет туда индекс элемента.
        if memory[0xF0FD+16*item["index"]+5] != item["values"][5]:
            raise ValueError("Инициализация неожиданно изменила TextIndex")
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    cases = 0
    for adapter in adapters:
        for flags in range(256):
            for old_hl in (0, 65535):
                simulator.registers[:] = initial
                simulator.registers[A], simulator.registers[F] = flags ^ 0xA5, flags
                simulator.registers[H], simulator.registers[L] = old_hl >> 8, old_hl & 255
                before = simulator.registers.copy()
                simulator.run(start=adapter["address"], stop=0xC2DF)
                if simulator.registers[H]*256+simulator.registers[L] != adapter["index"]:
                    raise ValueError("Обёртка не передала свой индекс в общий рисователь")
                for reg in (*range(6), *range(8, 12), *range(16, 24), SP):
                    if simulator.registers[reg] != before[reg]:
                        raise ValueError("Обёртка изменила параметр до хвостового входа")
                cases += 1
    # Отключение через исходный обработчик списка, изменяемые слова индексов остаются нетронутыми.
    pointers = [byte for adapter in adapters for byte in adapter['address'].to_bytes(2, 'little')]+[0xA5, 1]
    memory[0x3000:0x3000+len(pointers)] = pointers
    memory[0x7FFE:0x8000] = [0xFF, 0x3F]
    simulator.registers[:] = initial
    simulator.registers[H], simulator.registers[L] = 0x30, 0
    simulator.run(start=0x9C59, stop=0x3FFF)
    disabled_cases = 0
    for adapter in adapters:
        for flags in range(256):
            for old_hl in (0, 65535):
                simulator.registers[:] = initial
                simulator.registers[A], simulator.registers[F] = flags ^ 0xA5, flags
                simulator.registers[H], simulator.registers[L] = old_hl >> 8, old_hl & 255
                before = simulator.registers.copy()
                simulator.run(start=adapter['address'], stop=0x3FFF)
                for reg in (*range(12), *range(16, 24)):
                    if simulator.registers[reg] != before[reg]:
                        raise ValueError("Отключённая обёртка изменила регистр")
                if simulator.registers[SP] != 0x8000:
                    raise ValueError("Отключённая обёртка не выполнила обычный RET")
                disabled_cases += 1
    simulator.registers[:] = initial
    simulator.registers[H], simulator.registers[L] = 0x30, 0
    simulator.run(start=0x9C68, stop=0x3FFF)
    for adapter in adapters:
        address = adapter['address']
        if memory[address:address+6] != [0x21, adapter['index'], 0, 0xC3, 0xDF, 0xC2]:
            raise ValueError("Включение не восстановило LD HL с прежним индексом")
    report = dict(method="original_loader_patch_and_draw_adapter_entry_verification", passed=True,
                  cases=cases, initialized_handlers=len(items), adapters=adapters,
                  source_sha256=hashlib.sha256(source).hexdigest(), actual_low_code_relocation_used=True,
                  bank_zero_is_fixture_precondition=True, common_renderer_executed_in_separate_model=True,
                  disabled_adapter_cases=disabled_cases, original_list_patchers_executed=True,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/DrawAdapterVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "adapters"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
