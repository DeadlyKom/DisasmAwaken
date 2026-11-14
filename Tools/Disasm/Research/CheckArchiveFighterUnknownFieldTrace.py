"""Наблюдение исходных обращений к неизвестным байтам бойцов в модели ENGINE."""
from collections import Counter
import contextlib
import io
import json
from hashlib import sha256

import CheckFighterArchiveConsumer as model
from CheckArchiveEngineSource import ARCHIVE, ROOT
from CheckMusic import get_registers, PC


UNKNOWN = {base + offset for base in (0x4842, 0x4895) for offset in (8, 10)}
POSITIVE = {base + offset for base in (0x4842, 0x4895) for offset in (7, 9)}
SCENE_UNKNOWN = {0x4A51, 0x4A52, 0x4A56}
SCENE_POSITIVE = {0x4A55}
ACCESSES = Counter()
OBSERVED_PCS = set()
WATCHED = UNKNOWN | POSITIVE | SCENE_UNKNOWN | SCENE_POSITIVE


class FieldWatch:
    def record_fields(self, kind, address):
        if not getattr(self, 'executing_original_instruction', False):
            return
        pc = self.field_cpu.registers[PC]
        if 0x4000 <= pc < 0x5100:
            OBSERVED_PCS.add(pc)
        addresses = (address,) if isinstance(address, int) else range(*address.indices(65536))
        for target in addresses:
            if target in WATCHED:
                ACCESSES[kind, pc, target] += 1

    def __getitem__(self, address):
        self.record_fields('read', address)
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        self.record_fields('write', address)
        return super().__setitem__(address, value)


class WatchedMemory(FieldWatch, model.ExtendedMemory):
    pass


class WatchedBootMemory(FieldWatch, model.FighterBootMemory):
    pass


class WatchedSimulator(model.Simulator):
    def __init__(self, memory, *args, **kwargs):
        super().__init__(memory, *args, **kwargs)
        self.field_memory = memory
        memory.field_cpu = self

    def run(self, *args, **kwargs):
        previous = getattr(self.field_memory, 'executing_original_instruction', False)
        self.field_memory.executing_original_instruction = True
        try:
            return super().run(*args, **kwargs)
        finally:
            self.field_memory.executing_original_instruction = previous


def controls():
    memory = WatchedMemory()
    raw = (ARCHIVE / '46_ENGINE.C.sectors.bin').read_bytes()
    model.put(memory, 0x4000, raw)
    cpu = WatchedSimulator(memory)
    assert memory[0x4791] == 0x7E and memory[0x479E] == 0x77
    for address in sorted(UNKNOWN | SCENE_UNKNOWN):
        memory[address] = 0x5A
        before = ACCESSES.copy()
        cpu.registers[:] = get_registers(dict(PC=0x4791, HL=address), None, False)
        cpu.run()
        assert cpu.registers[0] == 0x5A
        assert ACCESSES['read', 0x4791, address] == before['read', 0x4791, address] + 1
        cpu.registers[:] = get_registers(dict(PC=0x479E, HL=address, AF=0xA500), None, False)
        cpu.run()
        assert memory[address] == 0xA5
        assert ACCESSES['write', 0x479E, address] == before['write', 0x479E, address] + 1
    ACCESSES.clear()


def main(report_name='ArchiveFighterUnknownFieldTraceVerification.json',
         model_report_name='ArchiveFighterFieldAccessModelVerification.json'):
    controls()
    OBSERVED_PCS.clear()
    prior_path = ROOT / 'Tools/Disasm/Reports/FighterArchiveConsumerVerification.json'
    prior_report = prior_path.read_bytes()
    original = model.Simulator, model.ExtendedMemory, model.FighterBootMemory
    model.Simulator, model.ExtendedMemory, model.FighterBootMemory = WatchedSimulator, WatchedMemory, WatchedBootMemory
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            model.main(report_name=model_report_name)
    finally:
        model.Simulator, model.ExtendedMemory, model.FighterBootMemory = original
    assert prior_path.read_bytes() == prior_report
    rows = [dict(kind=kind, pc=pc, address=address, count=count)
            for (kind, pc, address), count in sorted(ACCESSES.items())]
    positives = [row for row in rows if row['address'] in POSITIVE]
    unknown = [row for row in rows if row['address'] in UNKNOWN]
    scene_unknown = [row for row in rows if row['address'] in SCENE_UNKNOWN]
    scene_positive = [row for row in rows if row['address'] in SCENE_POSITIVE]
    assert {row['address'] for row in positives if row['kind'] == 'read'} == POSITIVE
    assert {row['address'] for row in positives if row['kind'] == 'write'} == POSITIVE
    assert {row['address'] for row in scene_positive if row['kind'] == 'read'} == SCENE_POSITIVE
    assert {row['address'] for row in scene_positive if row['kind'] == 'write'} == SCENE_POSITIVE
    static = json.loads((ROOT / 'Tools/Disasm/Reports/ArchiveFighterUnknownFieldsInspection.json').read_bytes())
    indirect = {row['pc'] for row in static['unresolved_other_indirect_operations'] + static['block_operations']}
    report = dict(passed=True, unknown_addresses=sorted(UNKNOWN), positive_addresses=sorted(POSITIVE),
                  original_instruction_read_write_controls=8, outside_instruction_accesses_excluded=True,
                  positive_field_accesses=positives, unknown_field_accesses=unknown,
                  scene_unknown_addresses=sorted(SCENE_UNKNOWN), scene_positive_addresses=sorted(SCENE_POSITIVE),
                  scene_unknown_field_accesses=scene_unknown, scene_positive_field_accesses=scene_positive,
                  scene_original_instruction_read_write_controls=6,
                  model_report='Tools/Disasm/Reports/' + model_report_name,
                  prior_consumer_report_preserved=True, global_unusedness_proved=False,
                  prior_consumer_report_sha256=sha256(prior_report).hexdigest(),
                  indirect_source_sites_observed=sorted(indirect & OBSERVED_PCS),
                  indirect_source_sites_not_observed=sorted(indirect - OBSERVED_PCS),
                  pc_observation_does_not_prove_mutable_opcode_identity=True,
                  cpu_interrupt_acceptance_outside_run_not_observed=True,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports' / report_name).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Неизвестные байты бойцов, групп обращений:', len(unknown),
          'контрольных групп:', len(positives))


if __name__ == '__main__':
    main()
