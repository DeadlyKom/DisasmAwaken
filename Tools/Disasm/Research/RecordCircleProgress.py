"""Фиксация геометрических доказательств и конкретного пользовательского результата, без сборки."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compiled-lines', type=int)
    parser.add_argument('--work-seconds', type=float)
    parser.add_argument('--sources-changed', action='store_true')
    args = parser.parse_args()
    assert (args.compiled_lines is None) == (args.work_seconds is None)
    assert not (args.sources_changed and args.compiled_lines is not None)
    def read(name):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    inventory, audit, checkpoint = read('Inventory'), read('ConformanceAudit'), read('InteractionCheckpoint')
    for name in ('SourceVerification', 'DocumentationVerification', 'SourceLabelsVerification', 'FilePlacementVerification'):
        assert read(name)['passed']
    assert audit['registered_functions'] == inventory['fragments']
    checkpoint.update(fragments=inventory['fragments'], described=inventory['described'], unknown=inventory['unknown'],
        instruction_count=inventory['instructions'], unclassified_bytes=inventory['physical_bytes_by_kind']['unclassified'],
        unproved_contracts=audit['unknown_contract_fragments'], named_without_contract=audit['named_fragments_without_proved_contract'])
    for key in ('remaining_by_region', 'pending_by_region', 'remaining_unknown_by_region'):
        checkpoint[key] = dict(Music=0, **audit['pending_by_region'])
    for tag, key in (('ControlsCircleSetup', 'controls_circle_setup'), ('ControlsCircleSpan', 'controls_circle_span')):
        proof = read(tag+'Verification')
        assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key] = dict(cases=proof['total_cases'], report='Tools/Disasm/Reports/'+tag+'Verification.json',
            exact_registers_flags_r_sp_and_all_ram=True, whole_large_renderer_proved=False,
            assembly_executed=False, irq_executed=False, native_execution=False)
    partial = read('ControlsCircleInteriorVerification')
    assert partial['passed']
    checkpoint['controls_circle_interior_partial'] = dict(cases=partial['total_cases'], modeled_rows=partial['modeled_rows'],
        all_output_registers_proved=False, full_renderer_proved=False, unknown_status_preserved=True)
    assert read('ControlsCircleWorkClassification')['passed']
    checkpoint['controls_circle_work'] = dict(typed_bytes=12, physical_records=1,
        structure='FCircleRasterWork', mode_full_game_meaning_proved=False)
    for stem in ('ControlsCircleSetupVerification', 'ControlsCircleSetupClassification',
                 'ControlsCircleSpanVerification', 'ControlsCircleSpanClassification',
                 'ControlsCircleEntrySplitClassification', 'ControlsCircleWorkClassification',
                 'ControlsCircleInteriorVerification'):
        assert read(stem)['passed']
        path = 'Tools/Disasm/Reports/'+stem+'.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsWordRandomClassification.json').exists():
        proof = read('ControlsWordRandomVerification')
        assert proof['passed'] and read('ControlsWordRandomClassification')['passed']
        assert read('ActionWordRandomStateClassification')['passed']
        checkpoint['controls_word_random'] = dict(cases=proof['total_cases'],
            physical_state_bytes=4, exact_registers_flags_r_sp_and_all_ram=True,
            all_32_bit_states_exhausted=False, period_proved=False, assembly_executed=False)
        for stem in ('ControlsWordRandomVerification', 'ControlsWordRandomClassification', 'ActionWordRandomStateClassification'):
            path = 'Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    for tag, key in (('ActionRegionType', 'action_region_type'), ('ControlsSeededParameters', 'controls_seeded_parameters'),
                     ('ControlsParameterTables', 'controls_parameter_tables'), ('ActionApplyParameters', 'action_apply_parameters'),
                     ('ActionParameterActivation', 'action_parameter_activation')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():
            continue
        proof = read(tag+'Verification')
        assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key] = dict(cases=proof['total_cases'], exact_registers_flags_r_sp_and_all_ram=True,
            game_meaning_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
        for suffix in ('Verification', 'Classification'):
            path = 'Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionParameterEntrySplitClassification.json').exists():
        assert read('ActionParameterEntrySplitClassification')['passed']
        path = 'Tools/Disasm/Reports/ActionParameterEntrySplitClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsParameterCoefficientsClassification.json').exists():
        assert read('ControlsParameterCoefficientsClassification')['passed']
        checkpoint['controls_parameter_coefficients'] = dict(typed_bytes=45, physical_records=15,
            structure='FParameterCoefficient', overlapping_h4_template_preserved=True,
            shared_mutation_writer_bank=1, shared_mutation_target_bank=5, target_original_action_offset=0xAC8)
        path = 'Tools/Disasm/Reports/ControlsParameterCoefficientsClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    partial_path = ROOT/'Tools/Disasm/Reports/ControlsRatioInsideVerification.json'
    if partial_path.exists():
        proof = read('ControlsRatioInsideVerification')
        assert proof['passed'] and proof['unknown_status_preserved']
        checkpoint['controls_ratio_inside_partial'] = dict(cases=proof['total_cases'],
            domain=proof['domain'], whole_procedure_proved=False, refresh_and_stack_values_proved=False,
            unknown_status_preserved=True, assembly_executed=False)
        path = 'Tools/Disasm/Reports/ControlsRatioInsideVerification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if args.sources_changed:
        checkpoint['manual_build_check'].update(status='passed_before_latest_source_changes',
            source_changes_after_build=True, current_source_assembly_verified=False)
        checkpoint['last_user_confirmed_build']['source_changes_after_build'] = True
        checkpoint['last_verified_build_artifact']['source_changes_after_build'] = True
    if args.compiled_lines is not None:
        build = read('BuildVerification')
        image = (ROOT/'Awakenv02.trd').read_bytes()
        assert build['status']=='passed' and build['byte_identical'] is True
        assert image==(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes() and len(image)==655360
        digest = hashlib.sha256(image).hexdigest()
        checkpoint['last_user_confirmed_build'].update(date='2026-11-02', errors=0, warnings=0,
            compiled_lines=args.compiled_lines, work_seconds=args.work_seconds,
            full_image_byte_identical=True, size=len(image), checked_at_utc=build['checked_at_utc'],
            source_changes_after_build=False, codex_assembler_executed=False,
            observation='Пользователь подтвердил Ctrl+B, число строк и время сохранены из его сообщения')
        checkpoint['manual_build_check'].update(status='passed', checked_at_utc=build['checked_at_utc'],
            sha256=digest, source_changes_after_build=False, current_source_assembly_verified=True)
        checkpoint['last_verified_build_artifact'].update(checked_at_utc=build['checked_at_utc'],
            sha256=digest, source_changes_after_build=False)
    (ROOT/'Tools/Disasm/Reports/InteractionCheckpoint.json').write_bytes(
        (json.dumps(checkpoint, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps({key: checkpoint[key] for key in ('fragments', 'described', 'unknown', 'unproved_contracts')}, indent=2))


if __name__ == '__main__':
    main()
