"""Наблюдение двух сохраняемых байтов узла в полном модельном кадре E020.

Документация: ../../../Docs/ActionRenderQueueInsert.md
"""
from collections import Counter
import contextlib
from hashlib import sha256
import io
import json

import CheckActionNonemptyRenderFrame as model
from CheckMusic import Simulator, get_registers
from CheckIntro import ROOT
from ActionModelPhysicalData import AUTHORED_PRIMARY_NAMES,AUTHORED_TAIL_NAMES,model_name,model_path


UNKNOWN = {0x8F00 + node * 14 + field for node in range(18) for field in (1, 2)}
INSTANCES = []


class WatchedMemory(model.RenderStackMemory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queue_accesses = Counter()
        self.initial_unknown = {}
        serial = len(INSTANCES)
        # Различимые ненулевые шаблоны исключают зависимость результата от исходных нулей.
        for index, address in enumerate(sorted(UNKNOWN)):
            value = ((serial * 73 + index * 17) % 255) + 1
            self[address] = value
            self.initial_unknown[address] = value
        INSTANCES.append(self)

    def observe_queue(self, kind, address):
        if not self.executing or not isinstance(address, int):
            return
        if 0x8F00 <= address < 0x8FFC:
            self.queue_accesses[kind, self.instruction[0], self.instruction[1], address] += 1

    def __getitem__(self, address):
        self.observe_queue('read', address)
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        # Конструктор базового класса ещё не установил признак executing.
        if hasattr(self, 'executing'):
            self.observe_queue('write', address)
        super().__setitem__(address, value)


def positive_control():
    memory = WatchedMemory(banks=[bytearray(0x4000) for _ in range(8)], out7ffd=16)
    memory[0x4000], memory[0x4001] = 0x7E, 0x77
    cpu = Simulator(memory)
    for address in sorted(UNKNOWN):
        cpu.registers[:] = get_registers({'HL': address, 'PC': 0x4000}, None, False)
        for pc, opcode in ((0x4000, 0x7E), (0x4001, 0x77)):
            memory.instruction = (5, pc, opcode)
            memory.executing = True
            cpu.run()
            memory.executing = False
    assert sum(memory.queue_accesses.values()) == 72
    assert {address for _, _, _, address in memory.queue_accesses} == UNKNOWN
    return 72


def main():
    controls = positive_control()
    INSTANCES.clear()
    original_class = model.RenderStackMemory
    original_report = ROOT / 'Tools/Disasm/Reports/ActionNonemptyRenderFrameVerification.json'
    original_digest = sha256(original_report.read_bytes()).hexdigest()
    model.RenderStackMemory = WatchedMemory
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            model.main('RenderQueueSkippedBytesFrameVerification.json')
    finally:
        model.RenderStackMemory = original_class
    assert sha256(original_report.read_bytes()).hexdigest() == original_digest
    accesses = Counter()
    for memory in INSTANCES:
        accesses.update(memory.queue_accesses)
        assert not memory.executing
        assert all(memory[address] == value for address, value in memory.initial_unknown.items())
    unknown = {key: count for key, count in accesses.items() if key[3] in UNKNOWN}
    assert not unknown
    reads = sum(count for (kind, _, _, _), count in accesses.items() if kind == 'read')
    writes = sum(count for (kind, _, _, _), count in accesses.items() if kind == 'write')
    assert reads and writes
    offsets = sorted({(address - 0x8F00) % 14 for _, _, _, address in accesses})
    assert offsets == [0, *range(3, 14)]
    frame = json.loads((ROOT / 'Tools/Disasm/Reports/RenderQueueSkippedBytesFrameVerification.json').read_bytes())
    # Сопоставление проверенных индексов и дополнительных указателей со всеми именованными пакетами.
    flat=model.flat_action()
    primary=[flat[address] | flat[address+1]<<8 for address in range(0x9E00,0x9F00,2)]
    tail=[profile['pointer'] for profile in frame['physical_tail_model_profiles']]
    assert frame['catalogue_profiles']==128 and frame['original_object_bank_used']
    assert set(primary)=={0xC000+offset for offset in AUTHORED_PRIMARY_NAMES}
    assert set(tail)=={0xC000+offset for offset in AUTHORED_TAIL_NAMES}
    coverage=[]
    for kind,pointers in (('original_main_table',primary),('substituted_tail_pointer',tail)):
        for pointer in sorted(set(pointers)):
            offset=pointer-0xC000;path=model_path(offset)
            assert (ROOT/path).is_file()
            coverage.append(dict(kind=kind,pointer=pointer,name=model_name(offset),source_path=path))
    assert len(coverage)==102
    report = dict(passed=True, complete_frame_profiles=len(INSTANCES),
        regular_profiles=frame['total_cases'],
        extra_model_pointer_profiles=len(frame['physical_tail_model_profiles']),
        observed_only_inside_original_simulator_instruction=True,
        positive_control_reads_and_writes=controls,
        queue_reads=reads, queue_writes=writes, observed_node_offsets=offsets,
        unknown_byte_accesses=0, nonzero_unknown_templates_preserved=True,
        watched_unknown_bytes=len(UNKNOWN), original_report_unchanged=True,
        model_catalogue_coverage=dict(original_main_table_indices=128,distinct_main_packets=95,
            substituted_tail_packets=7,named_packets=coverage,
            catalogue_pose=[0,0,0],catalogue_depth=0x2200,
            all_model_pose_and_scene_combinations_exhausted=False),
        global_unusedness_proved=False, original_padding_intent_proved=False,
        interrupt_acceptance_exercised=False, full_input_product_exhausted=False,
        assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/RenderQueueSkippedBytesVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
