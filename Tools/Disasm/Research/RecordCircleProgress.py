"""Фиксация геометрических доказательств и конкретного пользовательского результата, без сборки."""
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compiled-lines', type=int)
    parser.add_argument('--work-seconds', type=float)
    parser.add_argument('--sources-changed', action='store_true')
    parser.add_argument('--byte-match-line-omitted', action='store_true')
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
                     ('ActionParameterActivation', 'action_parameter_activation'), ('ControlsParameterActivation', 'controls_parameter_activation'),
                     ('ControlsThreeRowGlyph', 'controls_three_row_glyph'), ('ControlsGlyphIndicators', 'controls_glyph_indicators'),
                     ('ControlsSixRowGauge', 'controls_six_row_gauge'), ('ActionGaugeWrapper','action_gauge_wrapper'),
                     ('ActionPreferredByte','action_preferred_byte'), ('ActionPanelGauges','action_panel_gauges'),
                     ('ActionNearZeroWord','action_near_zero_word')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():
            continue
        proof = read(tag+'Verification')
        assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key] = dict(cases=proof['total_cases'], exact_registers_flags_r_sp_and_all_ram=True,
            game_meaning_proved=False, assembly_executed=False, irq_executed=False, native_execution=False)
        if tag=='ControlsParameterActivation':
            checkpoint[key].update(method=proof['method'],independent_complete_child_oracle=False,
                maximum_additional_stack_bytes=10,wrapper_extra_refresh_m1=64)
        if tag=='ActionGaugeWrapper':
            checkpoint[key].update(method=proof['method'],independent_complete_child_oracle=False,
                maximum_additional_stack_bytes=4,wrapper_extra_refresh_m1=20)
        if tag=='ActionPanelGauges':
            checkpoint[key].update(method=proof['method'],independent_complete_child_oracle=False,
                maximum_additional_stack_bytes=6,second_request_preserved=True,
                other_five_requests_cleared=True,sixth_gauge_range=[0,46])
        for suffix in ('Verification', 'Classification'):
            path = 'Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionParameterEntrySplitClassification.json').exists():
        assert read('ActionParameterEntrySplitClassification')['passed']
        path = 'Tools/Disasm/Reports/ActionParameterEntrySplitClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsThreeRowGlyphsClassification.json').exists():
        assert read('ControlsThreeRowGlyphsClassification')['passed']
        checkpoint['controls_three_row_glyphs'] = dict(typed_bytes=192, physical_records=32,
            structure='FThreeRowGlyphPhase', shapes=['Plus','Cross','Solid','Hollow'],
            remaining_return_table_bytes_unclassified=32)
        path = 'Tools/Disasm/Reports/ControlsThreeRowGlyphsClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionGlyphIndicatorStateClassification.json').exists():
        assert read('ActionGlyphIndicatorStateClassification')['passed']
        checkpoint['action_glyph_indicator_state']=dict(typed_bytes=12,physical_records=4,
            structures=['FGlyphIndicatorControl','FGlyphIndicatorXY','FGlyphIndicatorYX'],
            unknown_fields=['Control.Unknown83'],full_vector_game_meaning_proved=False)
        path='Tools/Disasm/Reports/ActionGlyphIndicatorStateClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsRasterReturnsClassification.json').exists():
        proof=read('ControlsRasterReturnsVerification')
        assert proof['passed'] and read('ControlsRasterReturnsClassification')['passed']
        checkpoint['controls_raster_returns_partial']=dict(typed_bytes=32,physical_records=16,cases=proof['total_cases'],
            stopped_before_selected_tail=True,full_rasterizer_proved=False,unknown_e291_status_preserved=True)
        checkpoint['controls_three_row_glyphs']['remaining_return_table_bytes_unclassified']=0
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ControlsRasterReturns'+suffix+'.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsRasterBackgroundVerification.json').exists():
        proof=read('ControlsRasterBackgroundVerification')
        assert proof['passed'] and proof['full_e291_proved'] is False
        checkpoint['controls_raster_background_partial']=dict(cases=proof['total_cases'],
            stopped_before_object_pass=True,full_e291_proved=False,
            every_ram_byte_and_write_checked=True,exact_registers_flags_sp_and_refresh=True)
        path='Tools/Disasm/Reports/ControlsRasterBackgroundVerification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    for tag in ('ControlsObjectProjection','ControlsObjectGlyphs','ControlsObjectStems','ControlsObjectFilter'):
        if (ROOT/('Tools/Disasm/Reports/'+tag+'Verification.json')).exists():
            proof=read(tag+'Verification')
            assert proof['passed'] and proof['full_e291_proved'] is False
            checkpoint.setdefault('controls_object_pass_partial',{})[tag]=dict(cases=proof['total_cases'],
                full_e291_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
            path='Tools/Disasm/Reports/'+tag+'Verification.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsObjectGlyphDataClassification.json').exists():
        proof=read('ControlsObjectGlyphDataClassification')
        assert proof['passed']
        checkpoint['controls_object_glyph_data']=dict(typed_bytes=672,physical_records=132,
            unknown_fields=proof['unknown_clear_record_fields'],full_e291_proved=False)
        path='Tools/Disasm/Reports/ControlsObjectGlyphDataClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsGaugeMasksClassification.json').exists():
        proof=read('ControlsGaugeMasksClassification')
        assert proof['passed']
        checkpoint['controls_gauge_masks']=dict(typed_bytes=7,physical_records=7,unused_by_this_consumer_indices=[0])
        path='Tools/Disasm/Reports/ControlsGaugeMasksClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionPreferredByteStateClassification.json').exists():
        assert read('ActionPreferredByteStateClassification')['passed']
        checkpoint['action_preferred_byte_state']=dict(typed_bytes=2,physical_records=1,
            structure='FPreferredBytePair',game_meaning_proved=False)
        path='Tools/Disasm/Reports/ActionPreferredByteStateClassification.json'
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
    if (ROOT/'Tools/Disasm/Reports/ActionKeyDispatchPrefixVerification.json').exists():
        proof=read('ActionKeyDispatchPrefixVerification')
        assert proof['passed'] and proof['unknown_6f1d_status_preserved'] and not proof['handlers_executed']
        checkpoint['action_key_dispatch_prefix_partial']=dict(cases=proof['total_cases'],
            stopped_before_handler=True,full_dispatcher_proved=False,unknown_status_preserved=True,
            raw_return_epilogue_cases=65536,
            pending_epilogue_source_publication=not (ROOT/'Tools/Disasm/Reports/ActionKeyScanFrameClassification.json').exists(),
            overlapping_last_pointer='704B..704C -> C0C9',upper_bank_for_last_handler_unproved=True)
        path='Tools/Disasm/Reports/ActionKeyDispatchPrefixVerification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionKeyScanFrameClassification.json').exists():
        proof=read('ActionKeyScanFrameClassification')
        assert proof['passed'] and proof['confirmed_instructions']==5
        checkpoint['action_key_scan_frame']=dict(confirmed_code_bytes=7,confirmed_instructions=5,
            proof_case_count=65536,proof_case_subset='restore_frame',additional_model_run=False,
            unknown_dispatcher_status_preserved=True)
        path='Tools/Disasm/Reports/ActionKeyScanFrameClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionKeyScanTablesClassification.json').exists():
        proof=read('ActionKeyScanTablesClassification');ignore=read('ActionIgnoreKeyVerification')
        assert proof['passed'] and ignore['passed']
        checkpoint['action_key_scan_tables']=dict(typed_bytes=106,physical_pointer_records=26,physical_input_records=27,
            overlapping_pointer_not_duplicated=True,confirmed_code_bytes=1,confirmed_instructions=1)
        checkpoint['action_ignore_key']=dict(cases=256,method=ignore['method'],
            other_keyboard_handlers_proved=False,original_dispatch_and_restore_executed=True)
        for path in ('Tools/Disasm/Reports/ActionKeyScanTablesClassification.json','Tools/Disasm/Reports/ActionIgnoreKeyVerification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionMissileStockVerification.json').exists():
        proof=read('ActionMissileStockVerification')
        assert proof['passed'] and not proof['caller_handlers_executed']
        checkpoint['action_missile_stock_research']=dict(cases=proof['total_cases'],
            source_published=(ROOT/'Tools/Disasm/Reports/ActionMissileStockClassification.json').exists(),
            text_evidence_bank=1,subtype_meaning_of_two_counters_proved=False,caller_handlers_executed=False)
        path='Tools/Disasm/Reports/ActionMissileStockVerification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionMissileStockClassification.json').exists():
        proof=read('ActionMissileStockClassification')
        assert proof['passed']
        checkpoint['action_missile_stock']=dict(cases=65536,typed_bytes=2,physical_records=1,
            confirmed_code_bytes=9,confirmed_instructions=7,subtype_meaning_of_two_counters_proved=False,
            caller_handlers_proved=False)
        path='Tools/Disasm/Reports/ActionMissileStockClassification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionMissileLaunchClassification.json').exists():
        proof=read('ActionMissileLaunchVerification');classification=read('ActionMissileLaunchClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_missile_launch_check']=dict(cases=proof['total_cases'],method=proof['method'],
            independent_complete_child_oracle=False,described_functions=2,typed_bytes=3,
            maximum_additional_stack_bytes=18,missile_launch_itself_proved=False,
            queue_silent_drop_and_end_boundary_checked=True)
        for path in ('Tools/Disasm/Reports/ActionMissileLaunchVerification.json','Tools/Disasm/Reports/ActionMissileLaunchClassification.json'):
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
        build_date=datetime.fromisoformat(build['checked_at_utc'].replace('Z','+00:00')).astimezone(
            timezone(timedelta(hours=3))).date().isoformat()
        checkpoint['last_user_confirmed_build'].update(date=build_date, errors=0, warnings=0,
            compiled_lines=args.compiled_lines, work_seconds=args.work_seconds,
            full_image_byte_identical=True, size=len(image), checked_at_utc=build['checked_at_utc'],
            source_changes_after_build=False, codex_assembler_executed=False,
            observation='Пользователь подтвердил Ctrl+B, число строк и время сохранены из его сообщения')
        checkpoint['last_user_confirmed_build'].update(user_reported_byte_identity_line=not args.byte_match_line_omitted,
            byte_identity_verified_from_existing_report_and_image=True)
        checkpoint['manual_build_check'].update(status='passed', checked_at_utc=build['checked_at_utc'],
            sha256=digest, source_changes_after_build=False, current_source_assembly_verified=True)
        checkpoint['last_verified_build_artifact'].update(checked_at_utc=build['checked_at_utc'],
            sha256=digest, source_changes_after_build=False)
    (ROOT/'Tools/Disasm/Reports/InteractionCheckpoint.json').write_bytes(
        (json.dumps(checkpoint, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps({key: checkpoint[key] for key in ('fragments', 'described', 'unknown', 'unproved_contracts')}, indent=2))


if __name__ == '__main__':
    main()
