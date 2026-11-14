"""Реальные CALL/RET кадровой модели и замечания к описаниям Corrupt.

Наблюдение не расширяет локальный договор фрагмента до целой цепочки.
Документация: ../../../Docs/ActionCallRegisterObservations.md
"""
from collections import Counter
import contextlib
from hashlib import sha256
import io
import json
import re

import CheckActionNonemptyRenderFrame as model
import CheckActionWideProjectionLoop as wide_model
from CheckMusic import PC, SP
from CheckIntro import ROOT
from CheckStationFlightCycle import payload


BYTE_NAMES = ['A', 'F', 'B', 'C', 'D', 'E', 'H', 'L', 'IXH', 'IXL', 'IYH', 'IYL',
              "A'", "F'", "B'", "C'", "D'", "E'", "H'", "L'"]
BYTE_INDICES = [*range(12), *range(16, 24)]
ALIASES = {name: {index} for name, index in zip(BYTE_NAMES, BYTE_INDICES)}
for pair, indices in {'HL': (6, 7), 'DE': (4, 5), 'BC': (2, 3), 'AF': (0, 1),
                      "HL'": (22, 23), "DE'": (20, 21), "BC'": (18, 19),
                      "AF'": (16, 17), 'IX': (8, 9), 'IY': (10, 11)}.items():
    ALIASES[pair] = set(indices)
TOKEN = re.compile(r"(?<![A-Za-z0-9_])(" + '|'.join(
    re.escape(name) for name in sorted(ALIASES, key=len, reverse=True)) + r")(?![A-Za-z0-9_'])")
CALLS = {0xCD, 0xC4, 0xCC, 0xD4, 0xDC, 0xE4, 0xEC, 0xF4, 0xFC}
RETURNS = {0xC9, 0xC0, 0xC8, 0xD0, 0xD8, 0xE0, 0xE8, 0xF0, 0xF8}
FUNCTIONS = {}
OBSERVATIONS = {}
INSTANCES = []
DISCARDED = Counter()
LOCAL_BOUNDARIES = {
    ('Action', 0xD511): dict(continuation=0xD229,
        symbol='Action.PolygonFillRows.CheckRow', document='Docs/ActionPolygonPreparation.md',
        source_qualification='контракт непустого случая относится к границе JP D229, а не к конечному RET всего заполнителя'),
    ('Action', 0xD5F9): dict(continuation=0xD694,
        symbol='Action.ProjectRenderVertexGroup.Entry', document='Docs/ActionVertexProducts.md',
        source_qualification='результаты этого договора относятся к границе D694, а не к возврату полного вызова'),
}


def region(memory, address):
    if 0x6000 <= address < 0x7F8F:
        return 'Action'
    if address >= 0xC000:
        return {0: 'Action', 1: 'Controls'}.get(memory.o7ffd & 7)
    return None


def corrupt_text(path):
    result, inside = [], False
    for line in (ROOT / path).read_text(encoding='utf-8').splitlines():
        if '; Corrupt:' in line:
            inside = True
        elif inside:
            if '; Note:' in line or not line.lstrip().startswith(';'):
                break
            result.append(line.split(';', 1)[1].strip())
    return ' '.join(result)


class ObservedSimulator(model.Simulator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_frames = []
        self.completed_calls = 0
        self.unwound_calls = 0
        INSTANCES.append(self)

    def run(self, start=None, stop=None, interrupts=False):
        # Модель вызывает только пошаговый run, иначе границы CALL/RET не наблюдаемы.
        assert start is None and stop is None and not interrupts
        before = tuple(self.registers)
        pc, stack = before[PC], before[SP]
        opcode = self.memory[pc]
        result = super().run()
        after = self.registers
        if opcode in CALLS and after[SP] == ((stack - 2) & 65535):
            key = (region(self.memory, after[PC]), after[PC])
            self.call_frames.append(dict(key=key, stack=after[SP],
                return_pc=(pc + 3) & 65535, registers=tuple(after), call_pc=pc))
        elif opcode in RETURNS and after[SP] == ((stack + 2) & 65535):
            for index in range(len(self.call_frames) - 1, -1, -1):
                frame = self.call_frames[index]
                if frame['stack'] != stack or frame['return_pc'] != after[PC]:
                    continue
                self.completed_calls += 1
                self.unwound_calls += len(self.call_frames) - index - 1
                for skipped in self.call_frames[index + 1:]:
                    DISCARDED[skipped['key'], skipped['call_pc'], frame['key'], pc] += 1
                del self.call_frames[index:]
                if frame['key'] in FUNCTIONS:
                    observation = OBSERVATIONS.setdefault(frame['key'],
                        dict(calls=0, changed=Counter(), examples={}))
                    observation['calls'] += 1
                    for name, reg in zip(BYTE_NAMES, BYTE_INDICES):
                        if frame['registers'][reg] != after[reg]:
                            observation['changed'][name] += 1
                            observation['examples'].setdefault(name, dict(call_pc=frame['call_pc'],
                                return_instruction=pc, before=frame['registers'][reg], after=after[reg]))
                break
        return result


def main():
    FUNCTIONS.clear()
    OBSERVATIONS.clear()
    INSTANCES.clear()
    DISCARDED.clear()
    FUNCTIONS.update({(row['region'], row['address']): row for row in json.loads(
        (ROOT / 'Tools/Disasm/Reports/Functions.json').read_bytes())
        if row['region'] in ('Action', 'Controls')})
    families = []
    for runner, original_name, output_name in [
            (model, 'ActionNonemptyRenderFrameVerification.json', 'ActionCallRegisterFramesVerification.json'),
            (wide_model, 'ActionWideProjectionLoopVerification.json', 'ActionCallRegisterWideVectorsVerification.json')]:
        original_report = ROOT / 'Tools/Disasm/Reports' / original_name
        original_digest = sha256(original_report.read_bytes()).hexdigest()
        original_simulator = runner.Simulator
        before = len(INSTANCES)
        runner.Simulator = ObservedSimulator
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                runner.main(output_name)
        finally:
            runner.Simulator = original_simulator
        assert sha256(original_report.read_bytes()).hexdigest() == original_digest
        families.append(dict(model=runner.__name__, profiles=len(INSTANCES) - before,
                             report='Tools/Disasm/Reports/' + output_name))
    rows = []
    for key, observed in sorted(OBSERVATIONS.items()):
        function = FUNCTIONS[key]
        text = corrupt_text(function['path'])
        allowed = set().union(*(ALIASES[token] for token in TOKEN.findall(text)))
        missing = [name for name, index in zip(BYTE_NAMES, BYTE_INDICES)
                   if name in observed['changed'] and index not in allowed]
        local = LOCAL_BOUNDARIES.get(key)
        if local:
            # Явная граница должна оставаться в текущем исходнике, одного списка исключений недостаточно.
            source = (ROOT / function['path']).read_text(encoding='utf-8')
            assert local['source_qualification'] in source
            assert (ROOT / local['document']).is_file()
            symbols = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())
            assert symbols[local['symbol']] == local['continuation']
        rows.append(dict(region=key[0], entry=key[1], path=function['path'],
            observed_returns=observed['calls'], observed_byte_changes=dict(observed['changed']),
            first_change_examples=observed['examples'], corrupt_text=text,
            changed_bytes_not_explicitly_listed=missing,
            reviewed_local_contract_boundary=local,
            requires_manual_contract_scope_review=bool(missing) and local is None))
    # Все пропущенные рамки в этих профилях относятся к исходному отказу проекции.
    assert DISCARDED == {
        (('Controls', 0xD0CA), 0xCF3F, ('Controls', 0xCF0B), 0xD155): 154,
        (('Controls', 0xD0CA), 0xCF61, ('Controls', 0xCF0B), 0xD155): 60,
    }
    control = payload(22)
    assert control[0x1152:0x1156] == bytes.fromhex('E1 F1 AF C9')
    for site in (0xCF3F, 0xCF61):
        assert control[site - 0xC000:site - 0xC000 + 3] == bytes.fromhex('CD CA D0')
    report = dict(passed=True, model_profiles=len(INSTANCES), families=families,
        functions_observed=len(rows),
        completed_calls=sum(cpu.completed_calls for cpu in INSTANCES),
        frames_discarded_by_nonlocal_returns=sum(cpu.unwound_calls for cpu in INSTANCES),
        discarded_frames=[dict(region=key[0], entry=key[1],
            path=FUNCTIONS.get(key, {}).get('path'), call_pc=call_pc,
            completed_outer_region=outer[0], completed_outer_entry=outer[1],
            outer_return_instruction=return_pc, count=count)
            for (key, call_pc, outer, return_pc), count in sorted(DISCARDED.items(), key=lambda row: repr(row[0]))],
        open_frames_at_final_boundary=sum(len(cpu.call_frames) for cpu in INSTANCES),
        functions_with_extra_whole_call_changes=sum(bool(row['changed_bytes_not_explicitly_listed']) for row in rows),
        functions_requiring_scope_review=sum(row['requires_manual_contract_scope_review'] for row in rows),
        functions=rows, original_reports_unchanged=True,
        nonlocal_projection_return=dict(discard_sequence=0xD152,
            original_bytes='E1 F1 AF C9', inner_entry=0xD0CA,
            outer_entry=0xCF0B, return_instruction=0xD155,
            calls_by_site={'CF3F': 154, 'CF61': 60}),
        fragment_contracts_not_automatically_treated_as_whole_call_contracts=True,
        missing_explicit_byte_is_not_automatic_contract_error=True,
        complete_register_contracts_proved=False, irq_executed=False,
        computed_jumps_and_tail_entries_not_separate_CALL_observations=True,
        assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionCallRegisterObservations.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'functions'}))


if __name__ == '__main__':
    main()
