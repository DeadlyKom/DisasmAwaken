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
    if (ROOT/'Tools/Disasm/Reports/ModifiedCodePathsVerification.json').is_file():
        paths_proof=read('ModifiedCodePathsVerification')
        assert paths_proof['passed'] and paths_proof['existing_but_wrong_target_path_probe_rejected']
        checkpoint['modified_code_path_boundaries']=dict(
            records=paths_proof['records_checked'],
            physical_target_ranges=paths_proof['physical_target_ranges_checked'],
            target_paths_without_physical_context=paths_proof['target_paths_without_physical_context'],
            all_records_have_physical_target_context=False,assembly_executed=False)
        report_path='Tools/Disasm/Reports/ModifiedCodePathsVerification.json'
        if report_path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(report_path)
    assert audit['registered_functions'] == inventory['fragments']
    checkpoint['unregistered_object_state_callbacks']=audit['unregistered_object_state_callbacks']
    checkpoint['registered_object_state_callbacks']=audit['registered_object_state_callbacks']
    checkpoint['unregistered_class_callbacks']=audit['unregistered_class_callbacks']
    checkpoint['registered_class_callbacks']=audit['registered_class_callbacks']
    checkpoint['unique_class_handler_targets']=audit['unique_class_handler_targets']
    # Проверка обязательных условий целостности до записи новой контрольной точки.
    for key in ('unlinked_functions','missing_includes_or_resources','missing_include_order','modified_code_path_errors',
                'unresolved_global_references','duplicate_global_definitions',
                'global_reference_case_mismatches','source_files_outside_graph','python_duplicate_literal_keys'):
        assert not audit[key],(key,audit[key])
    assert not audit['totals'].get('missing_continuation',0),audit['totals']
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
    if (ROOT/'Tools/Disasm/Reports/ActionMissileConsumeClassification.json').exists():
        proof=read('ActionMissileConsumeVerification');classification=read('ActionMissileConsumeClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_missile_consume']=dict(cases=proof['total_cases'],method=proof['method'],
            independent_complete_child_oracle=False,confirmed_code_bytes=39,confirmed_instructions=19,
            maximum_additional_stack_bytes=18,sequential_four_queue_requests_checked=True,
            auxiliary_counter_game_meaning_proved=False,rocket_object_creation_proved=False)
        for path in ('Tools/Disasm/Reports/ActionMissileConsumeVerification.json','Tools/Disasm/Reports/ActionMissileConsumeClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionTypeDeltaClassification.json').exists():
        proof=read('ActionTypeDeltaVerification');classification=read('ActionTypeDeltaClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_type_delta']=dict(cases=proof['total_cases'],method=proof['method'],
            described_functions=1,typed_bytes=16,physical_records=16,parent_unknown_preserved=True,
            game_meaning_of_state_and_mode_proved=False)
        for path in ('Tools/Disasm/Reports/ActionTypeDeltaVerification.json','Tools/Disasm/Reports/ActionTypeDeltaClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionRecordIndexClassification.json').exists():
        proof=read('ActionRecordIndexVerification');classification=read('ActionRecordIndexClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_record_index']=dict(cases=proof['total_cases'],method=proof['method'],
            described_functions=4,removed_unknown_fragments=2,maximum_additional_stack_bytes=4,
            every_ram_byte_and_write_multiplicity_checked=True,hardware_bus_write_order_proved=False,
            record_field_meanings_proved=False)
        for path in ('Tools/Disasm/Reports/ActionRecordIndexVerification.json','Tools/Disasm/Reports/ActionRecordIndexClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionRecordSearchClassification.json').exists():
        proof=read('ActionRecordSearchVerification');classification=read('ActionRecordSearchClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_record_search']=dict(cases=proof['total_cases'],method=proof['method'],
            explicit_end_marker_and_skip_ff=True,termination_requires_reachable_match_or_marker=True,
            game_array_limit_proved=False,record_field_game_meanings_proved=False)
        for path in ('Tools/Disasm/Reports/ActionRecordSearchVerification.json','Tools/Disasm/Reports/ActionRecordSearchClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionRecordIteratorClassification.json').exists():
        proof=read('ActionRecordIteratorVerification');classification=read('ActionRecordIteratorClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_record_iterator']=dict(cases=proof['total_cases'],method=proof['method'],
            described_functions=2,all_step_words=True,all_header_state_pairs=True,all_requested_actual_code_pairs=True,
            found_ff_returns_z_set=True,maximum_additional_stack_bytes=2,game_array_limit_proved=False)
        for path in ('Tools/Disasm/Reports/ActionRecordIteratorVerification.json','Tools/Disasm/Reports/ActionRecordIteratorClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionPatchSwapClassification.json').exists():
        proof=read('ActionPatchSwapVerification');classification=read('ActionPatchSwapClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_patch_swap']=dict(cases=proof['total_cases'],method=proof['method'],
            confirmed_code_bytes=43,confirmed_instructions=13,full_words_including_opcode_prefixes_swapped=True,
            self_modifying_word_writers_registered=6,consumer_executed=False,game_meaning_of_patch_pairs_proved=False)
        for path in ('Tools/Disasm/Reports/ActionPatchSwapVerification.json','Tools/Disasm/Reports/ActionPatchSwapClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionScaledMultiplyClassification.json').exists():
        proof=read('ActionScaledMultiplyVerification');classification=read('ActionScaledMultiplyClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_scaled_multiply']=dict(cases=proof['total_cases'],method=proof['method'],
            exact_registers_flags_refresh_sp=True,coefficient_80_original_zero_result_preserved=True,
            no_memory_writes=True,sp_unchanged=True,jp_ix_continuation=True)
        for path in ('Tools/Disasm/Reports/ActionScaledMultiplyVerification.json','Tools/Disasm/Reports/ActionScaledMultiplyClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionPatchedVectorClassification.json').exists():
        proof=read('ActionPatchedVectorVerification');classification=read('ActionPatchedVectorClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_patched_vector']=dict(cases=proof['total_cases'],method=proof['method'],
            described_functions=1,independent_complete_child_oracle=False,all_six_overflow_sites=True,
            original_carry_from_negative_products_preserved=True,sp_is_arithmetic_scratch_and_not_restored=True,
            partial_output_writes_preserved=True,jp_iy_continuation=True)
        for path in ('Tools/Disasm/Reports/ActionPatchedVectorVerification.json','Tools/Disasm/Reports/ActionPatchedVectorClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionVectorWrapperClassification.json').exists():
        proof=read('ActionVectorWrapperVerification');classification=read('ActionVectorWrapperClassification')
        assert proof['passed'] and classification['passed']
        checkpoint['action_vector_wrapper']=dict(cases=proof['total_cases'],method=proof['method'],
            independent_complete_child_oracle=False,matrix_transposed_before_compute_and_restored_after=True,
            sp_restored_before_second_call=True,ix_iy_restored=True,partial_outputs_returned_on_overflow=True,
            maximum_additional_stack_bytes=6,wrapper_refresh_m1=65)
        for path in ('Tools/Disasm/Reports/ActionVectorWrapperVerification.json','Tools/Disasm/Reports/ActionVectorWrapperClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionObjectRecordsClassification.json').exists():
        proof=read('ActionObjectRecordsClassification');assert proof['passed']
        checkpoint['action_object_records']=dict(typed_bytes=1664,physical_records=26,initial_slots=25,
            nested_structure_sizes=[2,6,64],physical_symbol_bindings=1794,
            all_field_game_meanings_proved=False,runtime_array_limit_proved=False)
        from ActionObjectRecords import KNOWN as record_known_fields, layout as record_layout
        record_size, record_fields=record_layout('FActionRecord')
        assert record_size==64
        checkpoint['action_object_records'].update(
            named_byte_fields_with_at_least_one_proved_use={format(offset,'02X'):value[0]
                for offset,value in sorted(record_known_fields.items())},
            unknown_byte_offsets=[format(offset,'02X') for name,offset in record_fields.items() if name.startswith('Unknown')],
            component_world_units_proved=False)
        for stem in ('ActionStateCodeNameVerification','ActionRecordPhaseNaming','ActionRecordTimingFieldNaming',
                     'NamedSourceReferenceReconciliation','ExplicitMutationTargetCompletion'):
            if not (ROOT/'Tools/Disasm/Reports'/(stem+'.json')).is_file():continue
            assert read(stem)['passed']
            report_path='Tools/Disasm/Reports/'+stem+'.json'
            if report_path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(report_path)
        for path in ('Tools/Disasm/Reports/ActionObjectRecordsResearchVerification.json','Tools/Disasm/Reports/ActionObjectRecordsClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
        if (ROOT/'Tools/Disasm/Reports/ActionObjectRecordsAssemblyObservation.json').exists():
            observed=read('ActionObjectRecordsAssemblyObservation');assert observed['passed']
            checkpoint['action_object_records']['user_assembled_nested_symbols_checked']=1794
            if (ROOT/'Tools/Disasm/Reports/ActionRecordPhaseNaming.json').is_file():
                checkpoint['action_object_records'].update(source_renames_after_assembly_observation=True,
                    current_field_names_assembly_verified=False)
            path='Tools/Disasm/Reports/ActionObjectRecordsAssemblyObservation.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionMissileCreationClassification.json').exists():
        created=read('ActionMissileCreationVerification');lost=read('ActionLostMissileTargetVerification')
        assert created['passed'] and lost['passed'] and read('ActionMissileCreationClassification')['passed']
        checkpoint['action_missile_creation']=dict(cases=created['total_cases']+lost['total_cases'],
            created_path_cases=created['total_cases'],lost_target_path_cases=lost['total_cases'],
            independent_complete_child_oracle=False,confirmed_code_bytes=151,confirmed_instructions=72,
            real_ay_bank0_pointer_and_banked_text_distinguished=True,maximum_additional_stack_bytes=18,
            physical_record_fields_used=True,stock_not_decremented_here=True,missile_movement_proved=False)
        for path in ('Tools/Disasm/Reports/ActionMissileCreationVerification.json','Tools/Disasm/Reports/ActionLostMissileTargetVerification.json',
                     'Tools/Disasm/Reports/ActionMissileCreationClassification.json'):
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionMissileRequestsClassification.json').exists():
        proof=read('ActionMissileRequestsVerification');publication=read('ActionMissileRequestsClassification')
        assert proof['passed'] and publication['passed']
        checkpoint['action_missile_requests']=dict(cases=proof['total_cases'],paths=proof['paths'],
            described_functions=4,confirmed_code_bytes=79,confirmed_instructions=36,
            class_code_of_target_proved=True,capture_cleared_before_creation=True,
            stock_only_consumed_after_creation=True,maximum_additional_stack_bytes=20,
            independent_complete_child_oracle=False,temporary_stack_contents_independently_checked=False,
            refresh_and_timing_checked=False,assembly_executed=False)
        for stem in ('ActionMissileRequestsVerification','ActionMissileRequestsClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionAyEffectsClassification.json').exists():
        proof=read('ActionAyEffectsVerification');assert proof['passed'] and read('ActionAyEffectsClassification')['passed']
        checkpoint['action_ay_effects']=dict(cases=proof['total_cases'],described_functions=1,
            exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,
            exact_ports_and_reads_checked=True,maximum_additional_stack_bytes=0,
            channel_c_uses_r_threshold_not_single_bit=True,real_ay_hardware_executed=False,
            ay_readback_model=proof['ay_readback_model'],assembly_executed=False)
        for stem in ('ActionAyEffectsVerification','ActionAyEffectsClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionAyStreamsClassification.json').exists():
        proof=read('ActionAyStreamPlaybackVerification');assert proof['passed'] and read('ActionAyStreamsClassification')['passed']
        checkpoint['action_ay_streams']=dict(physical_frames=proof['physical_frames'],terminators=proof['streams'],physical_bytes=proof['physical_stream_bytes'],
            unclassified_neighbor_bytes=742-proof['physical_stream_bytes'],sequences=proof['sequences'],ticks=proof['ticks'],
            original_stream_addresses_used=True,actual_ay_hardware_executed=False,assembly_executed=False)
        for stem in ('ActionAyStreamPlaybackVerification','ActionAyStreamsClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionRecordLinkEventClassification.json').exists():
        proof=read('ActionRecordLinkEventVerification');assert proof['passed'] and read('ActionRecordLinkEventClassification')['passed']
        checkpoint['action_record_link_event']=dict(cases=proof['total_cases'],paths=proof['paths'],
            described_functions=1,exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
            maximum_additional_stack_bytes=0,pending_pointer_producer_proved=False,game_event_meaning_proved=False,
            independent_complete_child_oracle=False,assembly_executed=False)
        for stem in ('ActionRecordLinkEventVerification','ActionRecordLinkEventClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionProjectedCaptureClassification.json').exists():
        proof=read('ActionProjectedCaptureVerification');publication=read('ActionProjectedCaptureClassification')
        assert proof['passed'] and publication['passed']
        checkpoint['action_projected_capture']=dict(cases=proof['total_cases'],paths=proof['paths'],
            described_functions=1,new_explicit_unknown_fragments=2,confirmed_code_bytes=749,
            confirmed_instructions=390,proved_local_code_bytes=91,exact_registers_flags_refresh_sp=True,
            every_ram_byte_and_write_multiplicity_checked=True,maximum_additional_stack_bytes=0,
            pending_record_written_from_alternate_hl=True,whole_projection_scan_proved=False,
            upstream_record_iteration_proved=False,assembly_executed=False)
        checkpoint['action_record_link_event']['local_pending_pointer_writer_proved']=True
        for stem in ('ActionProjectedCaptureVerification','ActionProjectedCaptureClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionLogarithmTableClassification.json').exists():
        proof=read('ActionLogarithmTableVerification');assert proof['passed'] and read('ActionLogarithmTableClassification')['passed']
        checkpoint['action_logarithm_table']=dict(cases=proof['total_cases'],generated_table_bytes=512,
            previously_named_contract_proved=True,exact_registers_flags_refresh_sp=True,
            every_ram_byte_and_write_multiplicity_checked=True,maximum_additional_stack_bytes=4,
            refresh_m1=proof['refresh_m1'],consumer_ratio_proved=False,assembly_executed=False)
        for stem in ('ActionLogarithmTableVerification','ActionLogarithmTableClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionExponentialTableClassification.json').exists():
        proof=read('ActionExponentialTableVerification');assert proof['passed'] and read('ActionExponentialTableClassification')['passed']
        checkpoint['action_exponential_table']=dict(cases=proof['total_cases'],generated_table_bytes=256,
            previously_named_contract_proved=True,exact_registers_flags_refresh_sp=True,
            every_ram_byte_and_write_checked=True,maximum_additional_stack_bytes=0,
            refresh_m1=proof['refresh_m1'],consumer_ratio_proved=False,assembly_executed=False)
        for stem in ('ActionExponentialTableVerification','ActionExponentialTableClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionLogRatioClassification.json').exists():
        proof=read('ActionLogRatioVerification');assert proof['passed'] and read('ActionLogRatioClassification')['passed']
        checkpoint['action_log_ratio']=dict(cases=proof['total_cases'],paths=proof['paths'],
            exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,
            actual_tables_from_verified_integer_generator_formulas=True,
            maximum_additional_stack_bytes=0,original_zero_and_negative_denominator_behavior_preserved=True,
            self_modifying_shift_displacements_checked=True,assembly_executed=False)
        for key in ('action_logarithm_table','action_exponential_table'):
            checkpoint[key]['local_consumer_ratio_proved']=True
        for stem in ('ActionLogRatioVerification','ActionLogRatioClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionObjectHeaderClassification.json').exists():
        proof=read('ActionObjectHeaderVerification');assert proof['passed'] and read('ActionObjectHeaderClassification')['passed']
        checkpoint['action_object_header']=dict(cases=proof['total_cases'],cases_by_fixture=proof['cases_by_fixture'],
            exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
            maximum_additional_stack_bytes=4,real_out_and_eight_banks=True,
            valid_game_index_range_proved=False,object_header_field_meanings_proved=False,assembly_executed=False)
        for stem in ('ActionObjectHeaderVerification','ActionObjectHeaderClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionScaleHeaderClassification.json').exists():
        proof=read('ActionScaleHeaderVerification');assert proof['passed'] and read('ActionScaleHeaderClassification')['passed']
        checkpoint['action_scale_header']=dict(cases=proof['total_cases'],proved_local_code_bytes=24,
            confirmed_instructions=13,original_even_table_headers_checked=128,
            exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,
            maximum_additional_stack_bytes=0,whole_projection_scan_proved=False,assembly_executed=False)
        for stem in ('ActionScaleHeaderVerification','ActionScaleHeaderClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionProjectedBoundsClassification.json').exists():
        proof=read('ActionProjectedBoundsVerification');assert proof['passed'] and read('ActionProjectedBoundsClassification')['passed']
        checkpoint['action_projected_bounds']=dict(cases=proof['total_cases'],paths=proof['paths'],
            proved_local_code_bytes=118,confirmed_instructions=55,children_executed_without_stubs=True,
            independent_complete_child_oracle=False,exact_registers_flags_refresh_sp=True,
            every_ram_byte_and_write_multiplicity_checked=True,partial_writes_preserved=True,
            maximum_additional_stack_bytes=2,whole_projection_scan_proved=False,assembly_executed=False)
        for stem in ('ActionProjectedBoundsVerification','ActionProjectedBoundsClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionProjectionClipClassification.json').exists():
        proof=read('ActionProjectionClipVerification');assert proof['passed'] and read('ActionProjectionClipClassification')['passed']
        checkpoint['action_projection_clip']=dict(cases=proof['total_cases'],paths=proof['paths'],
            proved_local_code_bytes=134,confirmed_instructions=79,physical_table_bytes=256,
            physical_table_records=256,exact_registers_flags_refresh_sp=True,every_ram_byte_checked=True,
            no_memory_writes=True,maximum_additional_stack_bytes=0,whole_projection_scan_proved=False,assembly_executed=False)
        for stem in ('ActionProjectionClipVerification','ActionProjectionClipClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionVectorReverseClassification.json').exists():
        proof=read('ActionVectorReverseVerification');assert proof['passed'] and read('ActionVectorReverseClassification')['passed']
        checkpoint['action_vector_reverse']=dict(cases=proof['total_cases'],confirmed_code_bytes=63,
            confirmed_instructions=42,self_modifying_writers_registered=4,exact_registers_flags_refresh_sp=True,
            every_ram_byte_and_write_multiplicity_checked=True,components_negated_without_halving=True,
            original_8000_wrap_preserved=True,maximum_additional_stack_bytes=0,game_units_proved=False,assembly_executed=False)
        for stem in ('ActionVectorReverseVerification','ActionVectorReverseClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionStationTransferClassification.json').exists():
        proof=read('ActionStationTransferVerification');assert proof['passed'] and read('ActionStationTransferClassification')['passed']
        checkpoint['action_station_transfer']=dict(cases=proof['total_cases'],confirmed_code_bytes=11,
            confirmed_instructions=4,exact_registers_flags_refresh_sp=True,
            every_physical_ram_byte_and_write_multiplicity_checked=True,all_64_initial_paging_values=True,
            maximum_additional_stack_bytes=4,external_return_not_consumed=True,station_disk_load_executed=False,assembly_executed=False)
        for stem in ('ActionStationTransferVerification','ActionStationTransferClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionCloseRecordClassification.json').exists():
        proof=read('ActionCloseRecordVerification');assert proof['passed'] and read('ActionCloseRecordClassification')['passed']
        checkpoint['action_close_record']=dict(cases=proof['total_cases'],paths=proof['paths'],described_functions=3,
            confirmed_code_bytes=86,confirmed_instructions=44,exact_registers_flags_refresh_sp=True,
            every_physical_ram_byte_and_write_multiplicity_checked=True,maximum_additional_stack_bytes=4,
            auxiliary_entry_native_caller_proved=False,station_disk_load_executed=False,assembly_executed=False)
        for stem in ('ActionCloseRecordVerification','ActionCloseRecordClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionCloseBoundsClassification.json').exists():
        proof=read('ActionCloseBoundsVerification');assert proof['passed'] and read('ActionCloseBoundsClassification')['passed']
        checkpoint['action_close_bounds']=dict(cases=proof['total_cases'],paths=proof['paths'],proved_local_code_bytes=66,
            exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
            carry_propagated_between_axes=True,maximum_additional_stack_bytes=10,
            station_transfer_retains_six_parent_stack_bytes=True,whole_projection_scan_proved=False,assembly_executed=False)
        for stem in ('ActionCloseBoundsVerification','ActionCloseBoundsClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionAimDataClassification.json').exists():
        proof=read('ActionAimDataClassification')
        assert proof['passed']
        checkpoint['action_aim_data']=dict(proof)
        path='Tools/Disasm/Reports/ActionAimDataClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag, key in (('ActionAimFollow', 'action_aim_follow'), ('ActionRenderQueueInsert', 'action_render_queue_insert'),
                     ('ActionRenderQueueControl', 'action_render_queue_control')):
        if (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():
            proof = read(tag+'Verification')
            assert proof['passed'] and read(tag+'Classification')['passed']
            checkpoint[key] = dict(proof)
            for stem in (tag+'Verification', tag+'Classification'):
                path = 'Tools/Disasm/Reports/'+stem+'.json'
                if path not in checkpoint['passed_reports']:
                    checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionRenderQueueLoadVerification.json').exists():
        proof=read('ActionRenderQueueLoadVerification')
        assert proof['passed']
        checkpoint['action_render_queue_load']=dict(proof)
        path='Tools/Disasm/Reports/ActionRenderQueueLoadVerification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionQueuedObjectClassification.json').exists():
        checkpoint.pop('action_render_continuation',None)
    elif (ROOT/'Tools/Disasm/Reports/ActionRenderContinuationClassification.json').exists():
        proof=read('ActionRenderContinuationClassification')
        assert proof['passed'] and proof['semantic_status']=='unknown'
        checkpoint['action_render_continuation']=dict(proof)
        for stem in ('ActionRenderContinuationVerification','ActionRenderContinuationClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('ActionBank4Writes','action_bank4_writes'),('ActionRenderCoefficients','action_render_coefficients'),('ActionRenderMatrix','action_render_matrix'),('ActionObjectCopy','action_object_copy'),('ActionPerspective','action_perspective'),('ActionVertexGroup','action_vertex_group'),('ActionVertexProducts','action_vertex_products'),('ActionObjectVertices','action_object_vertices'),('ActionVertexAbort','action_vertex_abort'),('ActionVertexCodes','action_vertex_codes'),('ActionListedCodes','action_listed_codes'),('ActionSignedMultiply','action_signed_multiply'),('ActionFaceOrientation','action_face_orientation'),('ActionSignedDivision','action_signed_division'),('ActionClipProducts','action_clip_products'),('ActionClipIntersections','action_clip_intersections'),('ActionClipComparisons','action_clip_comparisons'),('ActionClipPointWriters','action_clip_point_writers'),('ActionClipCases','action_clip_cases')):
        if (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():
            proof=read(tag+'Verification')
            assert proof['passed'] and read(tag+'Classification')['passed']
            checkpoint[key]=dict(proof)
            for stem in (tag+'Verification',tag+'Classification'):
                path='Tools/Disasm/Reports/'+stem+'.json'
                if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('ActionPolygon','action_polygon'),('ActionSingleEdge','action_single_edge'),('ActionLineRaster','action_line_raster'),
                    ('ActionPolygonPreparation','action_polygon_preparation'),('ActionPolygonRowSelection','action_polygon_row_selection'),
                    ('ActionPolygonLeftEdge','action_polygon_left_edge'),('ActionPolygonRightEdge','action_polygon_right_edge'),
                    ('ActionPolygonRightShortStep','action_polygon_right_short_step'),('ActionPolygonFillRows','action_polygon_fill_rows'),
                    ('ActionPolygonSelectRight','action_polygon_select_right'),('ActionPolygonWrapLeft','action_polygon_wrap_left'),
                    ('ActionPolygonWrapRight','action_polygon_wrap_right'),('ActionPolygonWrapLeftTop','action_polygon_wrap_left_top'),
                    ('ActionPolygonWrapRightTop','action_polygon_wrap_right_top'),('ActionPolygonReturn','action_polygon_return'),
                    ('ActionPacketRenderer','action_packet_renderer'),('ActionClippedPacketRenderer','action_clipped_packet_renderer'),
                    ('ActionQueuedObject','action_queued_object'),('ActionWorkBuffer','action_work_buffer')):
        if (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():
            proof=read(tag+'Verification')
            assert proof['passed'] and read(tag+'Classification')['passed']
            checkpoint[key]=dict(proof)
            for suffix in ('Verification','Classification'):
                path='Tools/Disasm/Reports/'+tag+suffix+'.json'
                if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for stem,key in (('ActionLineMasksDataClassification','action_line_masks_data'),
                     ('ActionClipPointsDataClassification','action_clip_points_data'),
                     ('ActionLineModesVerification','action_line_modes'),
                     ('ActionLineModesRegistration','action_line_modes_registration'),
                     ('ActionClipTableAliasVerification','action_clip_table_alias'),
                     ('ActionPolygonFillBitmapVerification','action_polygon_fill_profile'),
                     ('ActionPolygonFlowNamesVerification','action_polygon_flow_names'),
                     ('ActionModelPacketsVerification','action_model_packets'),
                     ('ThreeDOverlayMirrorVerification','three_d_overlay_mirror'),
                     ('ActionClipInternalLabelsVerification','action_clip_internal_labels')):
        if (ROOT/('Tools/Disasm/Reports/'+stem+'.json')).exists():
            proof=read(stem);assert proof['passed']
            checkpoint[key]=dict(proof)
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ThreeDOverlayMirrorClassification.json').exists():
        assert read('ThreeDOverlayMirrorClassification')['passed']
        checkpoint['three_d_overlay_mirror_publication']=read('ThreeDOverlayMirrorClassification')
        path='Tools/Disasm/Reports/ThreeDOverlayMirrorClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionPolygonFillBitmapVerification.json').exists():
        checkpoint.pop('action_polygon_fill_partial',None)
    if (ROOT/'Tools/Disasm/Reports/ActionRenderPhasesClassification.json').exists():
        proof=read('ActionRenderPhasesClassification')
        assert proof['passed']
        checkpoint['action_render_phases']=dict(proof)
        path='Tools/Disasm/Reports/ActionRenderPhasesClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionObjectPointersClassification.json').exists():
        proof=read('ActionObjectPointersClassification')
        assert proof['passed']
        checkpoint['action_object_pointers']=dict(proof)
        path='Tools/Disasm/Reports/ActionObjectPointersClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    partial_path = ROOT/'Tools/Disasm/Reports/ControlsRatioInsideVerification.json'
    if partial_path.exists():
        proof = read('ControlsRatioInsideVerification')
        assert proof['passed'] and proof['unknown_status_preserved']
        checkpoint['controls_ratio_inside_partial'] = dict(cases=proof['total_cases'],
            domain=proof['domain'], whole_procedure_proved=False, refresh_and_stack_values_proved=False,
            source_status_when_partial_check_was_published="unknown",
            later_whole_ratio_classification=(ROOT/"Tools/Disasm/Reports/ControlsProjectionAlgorithmClassification.json").exists(),
            assembly_executed=False)
        path = 'Tools/Disasm/Reports/ControlsRatioInsideVerification.json'
        if path not in checkpoint['passed_reports']:
            checkpoint['passed_reports'].append(path)
    for tag,key in (('IntroAttributeWriter','intro_attribute_writer'),
                    ('IntroTextureScale','intro_texture_scale'),('IntroScatter','intro_scatter'),
                    ('IntroPointerSampler','intro_pointer_sampler'),('IntroScrolledSampler','intro_scrolled_sampler'),
                    ('FinalHalt','final_halt'),('BootstrapRelocation','bootstrap_relocation'),
                    ('IntroLookupTransfer','intro_lookup_transfer')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():
            continue
        proof=read(tag+'Verification')
        assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],exact_registers_except_R=True,
            all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            proof_report='Tools/Disasm/Reports/'+tag+'Verification.json',
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('IntroScreen','intro_screen'),('ActionUnpack','action_unpack')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():continue
        proof=read(tag+'Verification')
        assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],exact_registers_except_R=True,
            full_logical_RAM_including_stack=proof.get('full_logical_RAM_including_stack',False),
            full_logical_RAM_except_stack_residue=proof.get('full_logical_RAM_except_stack_residue',False),
            write_multiplicity_proved=proof.get('write_multiplicity_proved',False),
            physical_banks_separately_proved=False,proof_report='Tools/Disasm/Reports/'+tag+'Verification.json',
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('IntroWaitInterrupt','intro_wait_interrupt'),
                    ('IntroPresentAttributes','intro_present_attributes'),('IntroInterlacedFrame','intro_interlaced_frame'),
                    ('IntroLookupContinuation','intro_lookup_continuation')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():continue
        proof=read(tag+'Verification')
        assert proof['passed'] and proof['irq_executed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],exact_registers_except_R=True,
            write_multiplicity_proved=True,irq_model_execution=True,actual_ROM_instructions_executed=True,
            physical_banks_separately_proved=proof.get('all_physical_ram_bytes_proved',False),
            rom_profile_sha256=proof['rom_sha256'],proof_report='Tools/Disasm/Reports/'+tag+'Verification.json',
            assembly_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionRandomClusterClassification.json').exists():
        proof=read('ActionFoldedRandomVerification');cluster=read('ActionRandomClusterClassification')
        assert proof['passed'] and cluster['passed'] and proof['original_stream_entries']==15
        checkpoint['action_folded_random']=dict(cases=proof['total_cases'],stream_entries=15,
            physical_state_records=15,typed_state_bytes=45,exact_registers_including_R=True,
            all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            core_refresh_m1=63,wrapper_refresh_m1=66,full_24_bit_domain_proved=False,
            period_and_uniformity_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
        for stem in ('ActionFoldedRandomVerification','ActionFoldedRandomClassification',
                     'ActionFoldedRandomDataClassification','ActionRandomClusterClassification'):
            assert read(stem)['passed']
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('ActionRecordReuse','action_record_reuse'),
                    ('ActionOffsetRestore','action_offset_restore'),('ActionRecordSelection','action_record_selection'),
                    ('ActionRecordScale','action_record_scale'),('ActionIYRecordReuse','action_iy_record_reuse'),
                    ('ActionClassReuse','action_class_reuse'),('ActionRejectRecord','action_reject_record'),
                    ('ActionRecordWarningReturn','action_record_warning_return'),
                    ('ActionRecordBaseReset','action_record_base_reset'),('ActionClass14Reuse','action_class14_reuse'),
                    ('ActionBankedBufferInit','action_banked_buffer_init'),
                    ('ActionThirdGlyphPublish','action_third_glyph_publish'),('ActionThirdGlyphStack','action_third_glyph_stack'),
                    ('ActionThirdGlyphVector','action_third_glyph_vector'),
                    ('ActionComponentEncoding','action_component_encoding'),('ActionComponentStack','action_component_stack'),
                    ('ActionComponentTransform','action_component_transform')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():continue
        proof=read(tag+'Verification')
        assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],exact_registers_including_R=True,
            all_physical_ram_bytes_proved=proof['all_physical_ram_bytes_proved'],
            write_multiplicity_proved=True,hardware_bus_stack_write_order_proved=False,
            proof_report='Tools/Disasm/Reports/'+tag+'Verification.json',
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionRecordUpdateClassification.json').exists():
        proof=read('ActionRecordUpdateVerification')
        assert proof['passed'] and read('ActionRecordUpdateClassification')['passed']
        checkpoint['action_record_update']=dict(cases=proof['total_cases'],exact_registers_except_R=True,
            refresh_R_proved=False,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            actual_children_and_banked_queue_executed=True,partial_component_updates_preserved_on_rejection=True,
            queue_results=proof['queue_results'],full_component_product_exhausted=False,
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ActionRecordUpdate'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionCachedRootClassification.json').exists():
        proof=read('ActionCachedRootVerification')
        assert proof['passed'] and read('ActionCachedRootClassification')['passed']
        checkpoint['action_cached_root']=dict(cases=proof['total_cases'],cases_by_entry=proof['cases_by_entry'],
            exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            ordinary_root_domain=proof['ordinary_root_domain'],different_upper_domain=proof['different_upper_domain'],
            original_upper_table_behavior_preserved=True,domain_validity_in_game_callers_proved=False,
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ActionCachedRoot'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsRootCacheDataClassification.json').exists():
        proof=read('ControlsRootCacheDataClassification');assert proof['passed']
        checkpoint['controls_root_cache_data']=dict(typed_bytes=768,physical_records=768,
            original_upper_rows_preserved=23,original_lower_exceptions_preserved=3,
            formula_used_to_generate_build_data=False,assembly_executed=False)
        path='Tools/Disasm/Reports/ControlsRootCacheDataClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionComponentWorkClassification.json').exists():
        proof=read('ActionComponentWorkClassification');assert proof['passed']
        checkpoint['action_component_work']=dict(typed_bytes=9,physical_records=3,existing_structure_reused='FComponent24',
            neighbor_bytes_preserved=90,assembly_executed=False)
        path='Tools/Disasm/Reports/ActionComponentWorkClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsProjectionAlgorithmClassification.json').exists():
        proof=read('ControlsBodyProjectionVerification');ratio=read('ControlsProjectionRatioVerification')
        assert proof['passed'] and ratio['passed'] and read('ControlsProjectionAlgorithmClassification')['passed']
        checkpoint['controls_projection_algorithm']=dict(cases=proof['total_cases'],ratio_cases=ratio['total_cases'],
            exact_registers_except_R=True,all_nonstack_physical_ram_proved=True,
            parent_nonstack_write_multiplicity_proved=True,maximum_additional_stack_bytes=6,
            stack_residue_values_and_R_proved=False,partial_projection_writes_preserved=True,
            full_component_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
        for stem in ('ControlsBodyProjectionVerification','ControlsProjectionRatioVerification','ControlsProjectionAlgorithmClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsProjectionGateClassification.json').exists():
        proof=read('ControlsProjectionGateVerification');assert proof['passed'] and read('ControlsProjectionGateClassification')['passed']
        checkpoint['controls_projection_gate']=dict(cases=proof['total_cases'],exact_registers_except_R=True,
            all_nonstack_physical_ram_and_write_multiplicity_proved=True,maximum_additional_stack_bytes=8,
            fixed_reference_component=2,stack_residue_values_and_R_proved=False,
            full_component_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ControlsProjectionGate'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionClassDispatchClassification.json').exists():
        proof=read('ActionClassDispatchVerification');assert proof['passed'] and read('ActionClassDispatchClassification')['passed']
        checkpoint['action_class_dispatch']=dict(cases=proof['total_cases'],exact_registers_including_R=True,
            all_physical_ram_bytes_proved=True,cpu_stack_written=False,execution_stopped_after_indirect_jump=True,
            target_handler_semantics_proved=False,class_domain_in_all_game_writers_proved=False,assembly_executed=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ActionClassDispatch'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionClassHandlersClassification.json').exists():
        proof=read('ActionClassHandlersClassification');assert proof['passed']
        checkpoint['action_class_handlers']=dict(typed_bytes=52,physical_records=26,structure='FClassHandler',
            neighboring_code_not_part_of_table=True,assembly_executed=False)
        path='Tools/Disasm/Reports/ActionClassHandlersClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('ActionLinkOverride','action_link_override'),('ActionClass9Link','action_class9_link'),('ActionIgnoredClasses','action_ignored_classes'),('ActionRecordsExcept6And7','action_records_except_6_and_7'),
                    ('ActionRecords6Or7','action_records_6_or_7'),('ActionRecords5Or14','action_records_5_or_14'),
                    ('ActionRandomFilteredRecord','action_random_filtered_record')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():continue
        proof=read(tag+'Verification');assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],exact_registers_including_R=True,
            all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            maximum_additional_stack_bytes=0 if tag in ('ActionLinkOverride','ActionClass9Link','ActionIgnoredClasses') else 6,
            full_game_field_meanings_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
        if tag=='ActionRandomFilteredRecord':
            checkpoint[key].update(actual_stream_10_executed=True,random_gate_threshold=160,gate_result=26,
                random_distribution_and_period_proved=False,complete_24_bit_state_domain_exhausted=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionClass0LinkClassification.json').exists():
        proof=read('ActionClass0LinkVerification');assert proof['passed'] and read('ActionClass0LinkClassification')['passed']
        checkpoint['action_class0_link']=dict(cases=proof['total_cases'],cases_by_entry=proof['cases_by_entry'],
            exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            maximum_additional_stack_bytes=8,zero_override_still_continues=True,random_distribution_and_period_proved=False,
            complete_state_and_list_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ActionClass0Link'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionPreferredDispatchClassification.json').exists():
        proof=read('ActionPreferredRecordVerification');assert proof['passed'] and read('ActionPreferredDispatchClassification')['passed']
        checkpoint['action_preferred_record']=dict(cases=proof['total_cases'],cases_by_entry=proof['cases_by_entry'],
            exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            maximum_additional_stack_bytes=6,priority_0_then_7_then_5_preserved=True,
            class3_prevents_class18_update=True,only_first_class18_updated=True,bases_reset_on_all_returns=True,
            complete_state_and_list_product_exhausted=False,random_distribution_and_period_proved=False,
            assembly_executed=False,irq_executed=False,native_execution=False)
        stems=['ActionPreferredRecordVerification']
        for tag in ('ActionPreferredApply','ActionPreferredChance','ActionPreferredZeroBridge','ActionPreferredSevenBridge','ActionPreferredDispatch'):
            stems.extend([tag+'Verification',tag+'Classification'])
        for stem in stems:
            assert read(stem)['passed']
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('ActionAbsSigned32','action_abs_signed32'),('ActionContextWordPairs','action_context_word_pairs'),
                    ('ActionVectorHighMaximum','action_vector_high_maximum'),('ActionSignedRatioCode','action_signed_ratio_code')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():continue
        proof=read(tag+'Verification');assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],exact_registers_including_R=True,
            all_physical_ram_bytes_proved=True,maximum_additional_stack_bytes=6 if tag=='ActionSignedRatioCode' else 0,
            full_game_meaning_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
        if tag=='ActionVectorHighMaximum':checkpoint[key].update(complete_three_byte_product_exhausted=True)
        if tag=='ActionSignedRatioCode':checkpoint[key].update(original_zero_pair_code=21,
            ordinary_atan2_equivalence_proved=False,table_indices_observed=len(proof['table_indices_observed']))
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionSignedRatioCodesClassification.json').exists():
        proof=read('ActionSignedRatioCodesClassification');assert proof['passed']
        checkpoint['action_signed_ratio_codes']=dict(typed_bytes=256,physical_records=256,structure='FSignedRatioCode',
            original_bytes_preserved=True,formula_used_to_generate_build_data=False,observed_table_indices=proof['observed_table_indices'],assembly_executed=False)
        path='Tools/Disasm/Reports/ActionSignedRatioCodesClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionHalfDeltaCodesClassification.json').exists():
        proof=read('ActionHalfDeltaCodesVerification');assert proof['passed'] and read('ActionHalfDeltaCodesClassification')['passed']
        checkpoint['action_half_delta_codes']=dict(cases=proof['total_cases'],exact_registers_except_R=True,
            all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,maximum_additional_stack_bytes=14,
            real_ports_and_eight_banks=True,initial_7ffd_values=proof['initial_7ffd_values'],final_7ffd=16,
            proven_delta_range=[-32767,32767],root_input_upper_bound=0x7FFE,
            multiplication_second_operand_8000_unreachable=True,bad_upper_root_table_domain_unreachable_for_this_caller=True,
            refresh_R_proved=False,complete_six_word_product_exhausted=False,
            assembly_executed=False,irq_executed=False,native_execution=False)
        if 'action_cached_root' in checkpoint:
            checkpoint['action_cached_root'].update(caller_AD5A_domain_proved=True,caller_AD5A_upper_bound=0x7FFE)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ActionHalfDeltaCodes'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('ActionRecordCodeStep','action_record_code_step'),('ActionClass3LinkCount','action_class3_link_count')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():continue
        proof=read(tag+'Verification');assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],all_physical_ram_bytes_proved=True,
            exact_registers_including_R=tag=='ActionClass3LinkCount',
            assembly_executed=False,irq_executed=False,native_execution=False)
        if tag=='ActionRecordCodeStep':
            checkpoint[key].update(exact_direct_registers_including_R=True,exact_root_registers_except_R=True,
                maximum_additional_stack_bytes=16,asymmetric_step_rules_preserved=True,
                root_refresh_R_proved=False,complete_five_byte_product_exhausted=False)
        else:
            checkpoint[key].update(cpu_stack_written=False,maximum_additional_stack_bytes=0,
                count_saturates_at_two=True,complete_list_product_exhausted=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key in (('ActionFoldedNearWords','action_folded_near_words'),('ActionClampVectorWords','action_clamp_vector_words')):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():continue
        proof=read(tag+'Verification');assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],exact_registers_including_R=True,
            all_physical_ram_bytes_proved=True,maximum_additional_stack_bytes=6 if tag=='ActionClampVectorWords' else 0,
            assembly_executed=False,irq_executed=False,native_execution=False)
        if tag=='ActionFoldedNearWords':checkpoint[key].update(signed_interval=[-60,59],complete_three_word_product_exhausted=False)
        else:checkpoint[key].update(signs_read_from_original_bit23=True,complete_three_dword_product_exhausted=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for tag,key,depth,with_r in (('ActionWideTargetStep','action_wide_target_step',16,False),
            ('ActionNearVectorSearch','action_near_vector_search',4,True),('ActionSelectWideTarget','action_select_wide_target',16,False)):
        if not (ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists():continue
        proof=read(tag+'Verification');assert proof['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],exact_registers_including_R=with_r,
            exact_registers_except_R=not with_r,all_physical_ram_bytes_proved=True,
            maximum_additional_stack_bytes=depth,write_multiplicity_and_stack_residue_proved=True,
            complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/'+tag+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionWideVectorsClassification.json').exists():
        proof=read('ActionWideVectorsClassification');assert proof['passed']
        checkpoint['action_wide_vectors']=dict(typed_bytes=72,physical_records=6,nested_structures=True,
            original_bytes_preserved=True,neighbor_bytes_preserved=18,game_count_bound_proved=False,assembly_executed=False)
        path='Tools/Disasm/Reports/ActionWideVectorsClassification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionControlDecayClassification.json').exists():
        proof=read('ActionControlDecayVerification');assert proof['passed'] and read('ActionControlDecayClassification')['passed']
        checkpoint['action_control_decay']=dict(cases=proof['total_cases'],exact_registers_including_R=True,
            all_physical_ram_bytes_proved=True,write_multiplicity_and_stack_residue_proved=True,maximum_additional_stack_bytes=6,
            delayed_channel_gate_reads_old_value_before_latch=True,phase_is_circular_rotation_not_boolean_toggle=True,
            complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ActionControlDecay'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    for proof_tag,key,entry_tags,size in (
        ('ActionControlKeys','action_control_keys',('ActionKeyTurnNegative','ActionKeyTurnPositive','ActionKeyXNegative','ActionKeyXPositive','ActionKeyYNegative','ActionKeyYPositive'),210),
        ('ActionGaugeWordKeys','action_gauge_word_keys',('ActionKeyGaugeIncrease','ActionKeyGaugeDecrease'),71)):
        if not all((ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists() for tag in entry_tags):continue
        proof=read(proof_tag+'Verification');assert proof['passed']
        for tag in entry_tags:assert read(tag+'Verification')['passed'] and read(tag+'Classification')['passed']
        checkpoint[key]=dict(cases=proof['total_cases'],entries=len(entry_tags),confirmed_code_bytes=size,
            exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            cpu_stack_written=False,assembly_executed=False,irq_executed=False,native_execution=False)
        if proof_tag=='ActionControlKeys':checkpoint[key].update(complete_counter_value_products_all_six_entries=True)
        else:checkpoint[key].update(complete_word_limit_product_exhausted=False,original_sign_and_bit4_checks_preserved=True)
        stems=[proof_tag+'Verification']+[tag+suffix for tag in entry_tags for suffix in ('Verification','Classification')]
        for stem in stems:
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if all((ROOT/('Tools/Disasm/Reports/'+tag+'Classification.json')).exists() for tag in ('ActionBankedCallback','ActionBankedCallbackReturn')):
        proof=read('ActionBankedCallbackCombinedVerification');assert proof['passed'] and proof['total_cases']==786432
        checkpoint['action_banked_callback']=dict(cases=proof['total_cases'],dispatch_cases=393216,return_cases=393216,
            exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_and_stack_residue_proved=True,
            maximum_additional_stack_bytes=4,real_ports_and_lock_behaviour=True,dispatch_stopped_after_indirect_jump=True,
            callback_semantics_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
        stems=['ActionBankedCallbackCombinedVerification']+[tag+suffix for tag in ('ActionBankedCallback','ActionBankedCallbackReturn') for suffix in ('Verification','Classification')]
        for stem in stems:
            assert read(stem)['passed'];path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsCircleInteriorFullClassification.json').exists():
        proof=read('ControlsCircleInteriorFullVerification');assert proof['passed'] and read('ControlsCircleInteriorFullClassification')['passed']
        checkpoint['controls_circle_interior_full']=dict(cases=proof['total_cases'],modeled_rows=proof['modeled_rows'],
            exact_registers_except_R=True,refresh_R_proved=False,all_physical_ram_bytes_proved=True,
            all_nonpixel_values_and_write_multiplicity_proved=True,pixel_write_multiplicity_proved=False,
            maximum_additional_stack_bytes=8,stack_positions=proof['stack_positions'],horizontal_unclipped_domain=True,
            vertical_clipping_proved=True,whole_large_renderer_proved=False,
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ControlsCircleInteriorFull'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsCircleHalfClassification.json').exists():
        proof=read('ControlsCircleHalfVerification');assert proof['passed'] and read('ControlsCircleHalfClassification')['passed']
        checkpoint['controls_circle_half']=dict(cases=proof['total_cases'],modeled_rows=proof['modeled_rows'],
            exact_registers_except_R=True,refresh_R_proved=False,all_physical_ram_bytes_proved=True,
            all_nonpixel_values_and_write_multiplicity_proved=True,pixel_write_multiplicity_proved=False,
            all_valid_x_y_pairs_both_directions=True,initial_norm_upper_bound=65025,all_input_AF_both_directions=True,
            initial_same_byte_exit_preserved=True,maximum_additional_stack_bytes=6,horizontal_clipping_kernels_proved=False,
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ControlsCircleHalf'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsClippedCircleHalfClassification.json').exists():
        proof=read('ControlsClippedCircleHalfVerification');assert proof['passed'] and read('ControlsClippedCircleHalfClassification')['passed']
        checkpoint['controls_clipped_circle_half']=dict(cases=proof['total_cases'],modeled_rows=proof['modeled_rows'],
            transitions_to_unclipped_kernel=proof['transitions_to_unclipped_kernel'],exact_registers_except_R=True,
            all_physical_ram_bytes_proved=True,all_nonpixel_values_and_write_multiplicity_proved=True,
            original_EXX_active_exit_preserved=True,pixel_write_multiplicity_proved=False,
            all_256_AFprime_thresholds_on_selected_geometry=True,complete_input_product_exhausted=False,
            maximum_additional_stack_bytes=6,whole_large_renderer_proved=False,
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ControlsClippedCircleHalf'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsCircleKernelsClassification.json').exists():
        proof=read('ControlsCircleKernelsVerification');assert proof['passed'] and read('ControlsCircleKernelsClassification')['passed']
        checkpoint['controls_circle_kernels']=dict(aggregate_model_cases=proof['total_cases'],
            proof_is_report_aggregation=True,entry_states_restricted_to_documented_initializers=True,
            arbitrary_internal_entry_states_exhausted=False,normal_and_both_clipped_kernels_named=True,
            separate_push_resume_fragment=True,whole_large_renderer_proved=False,
            assembly_executed=False,irq_executed=False,native_execution=False)
        for stem in ('ControlsCircleKernelsVerification','ControlsCircleKernelsClassification','ControlsLeftCoreSplitClassification'):
            assert read(stem)['passed'];path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsStationRelocationClassification.json').exists():
        proof=read('ControlsStationRelocationVerification');assert proof['passed'] and read('ControlsStationRelocationClassification')['passed']
        checkpoint['controls_station_relocation']=dict(cases=proof['total_cases'],copied_bytes=256,
            exact_registers_including_R=True,all_physical_ram_bytes_proved=True,copy_write_order_in_emulator_proved=True,
            cpu_stack_written=False,stopped_after_JP_4000=True,relocated_payload_not_executed=True,
            assembly_executed=False,irq_executed=False,native_execution=False)
        for suffix in ('Verification','Classification'):
            path='Tools/Disasm/Reports/ControlsStationRelocation'+suffix+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsStationPrepareClassification.json').exists():
        proof=read('ControlsStationPrepareVerification');assert proof['passed'] and read('ControlsStationPrepareClassification')['passed']
        checkpoint['controls_station_prepare']=dict(cases=proof['total_cases'],exact_registers_including_R=True,
            all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,saved_bytes=512,relocated_bytes=256,
            attribute_bytes_cleared=768,original_SP_discarded=True,final_SP=0x5FFF,final_IM=1,final_I=63,final_IFF=0,
            stopped_before_payload_4200=True,TRDOS_and_station_file_not_executed=True,
            assembly_executed=False,irq_executed=False,native_execution=False)
        for stem in ('ControlsStationPrepareVerification','ControlsStationPrepareCodeClassification','ControlsStationPrepareClassification'):
            assert read(stem)['passed'];path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionSubtractWorkVectorClassification.json').exists():
        proof=read('ActionSubtractWorkVectorVerification');assert proof['passed'] and read('ActionSubtractWorkVectorClassification')['passed']
        assert read('ActionWorkVectorDataClassification')['passed']
        checkpoint['action_subtract_work_vector']=dict(cases=proof['total_cases'],exact_registers_including_R=True,
            all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,typed_bytes=9,nested_signed_components=3,
            low_word_written_before_overflow_return=True,overflow_high_byte_and_later_components_unchanged=True,
            cpu_stack_written=False,observed_m1_min=proof['observed_m1_min'],observed_m1_max=proof['observed_m1_max'],
            complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
        for stem in ('ActionSubtractWorkVectorVerification','ActionSubtractWorkVectorClassification','ActionWorkVectorEntrySplitClassification','ActionWorkVectorDataClassification'):
            assert read(stem)['passed'];path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ActionRefreshPanelClassification.json').exists():
        proof=read('ActionRefreshPanelVerification');assert proof['passed'] and read('ActionRefreshPanelClassification')['passed']
        digits=read('ControlsBcdExactVerification');assert digits['passed']
        checkpoint['action_refresh_panel']=dict(cases=proof['total_cases'],bcd_exact_child_cases=digits['total_cases'],
            exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            port_writes=14,final_7ffd=17,maximum_additional_stack_bytes=8,tail_jump_keeps_external_return_frame=True,
            locked_configuration_outside_contract=True,assembly_executed=False,irq_executed=False,native_execution=False)
        for stem in ('ControlsBcdExactVerification','ActionRefreshPanelVerification','ActionRefreshPanelClassification'):
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsCircleDispatchVerification.json').exists():
        proof=read('ControlsCircleDispatchVerification');assert proof['passed'] and proof['stopped_before_raster_children']
        checkpoint['controls_circle_dispatch_partial']=dict(cases=proof['total_cases'],destinations=proof['targets'],
            exact_registers_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
            stopped_before_raster_children=True,whole_renderer_proved=False,unknown_status_preserved=True,
            assembly_executed=False,irq_executed=False,native_execution=False)
        path='Tools/Disasm/Reports/ControlsCircleDispatchVerification.json'
        if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    if (ROOT/'Tools/Disasm/Reports/ControlsVerticalCircleSliceClassification.json').exists():
        proof=read('ControlsVerticalCircleSliceVerification')
        assert proof['passed'] and read('ControlsVerticalCircleSliceClassification')['passed']
        checkpoint['controls_vertical_circle_slice']=dict(cases=proof['total_cases'],
            tangent_root_FF_cases=proof['tangent_root_FF_cases'],modeled_rows=proof['modeled_rows'],
            exact_registers_except_R=True,tangent_draws_no_pixels=True,tangent_saved_SP_unchanged=True,
            maximum_additional_stack_bytes=14,full_D340_proved=False,assembly_executed=False)
        for stem in ('ControlsVerticalCircleSliceVerification','ControlsVerticalCircleSliceClassification','ControlsVerticalSliceSplitClassification'):
            assert read(stem)['passed']
            path='Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:checkpoint['passed_reports'].append(path)
    circle_chain = (
        ('controls_horizontal_circle', 'ControlsHorizontalCircle', ('ControlsHorizontalCircleClassification', 'ControlsHorizontalCircleStartSplitClassification', 'ControlsHorizontalCircleEndSplitClassification')),
        ('controls_corner_circle_slice', 'ControlsCornerCircleSlice', ('ControlsCornerCircleSliceClassification',)),
        ('controls_full_width_circle', 'ControlsFullWidthCircle', ('ControlsFullWidthCircleClassification', 'ControlsFullWidthCircleSplitClassification')),
        ('controls_large_circle', 'ControlsLargeCircle', ('ControlsLargeCircleClassification',)),
        ('controls_body_draw', 'ControlsBodyDraw', ('ControlsBodyDrawClassification',)),
        ('projected_body_entry', 'ProjectedBodyEntry', ('ControlsProjectDrawBodyClassification', 'ActionDrawBankedBodyClassification')),
    )
    for key, tag, classifications in circle_chain:
        if not all((ROOT/'Tools/Disasm/Reports'/(stem+'.json')).exists() for stem in classifications):
            continue
        proof = read(tag+'Verification')
        assert proof['passed'] and all(read(stem)['passed'] for stem in classifications)
        checkpoint[key] = dict(cases=proof['total_cases'], exact_registers_except_R=True,
            projection_scratch_values_not_proved=proof.get('projection_scratch_values_not_proved', False),
            assembly_executed=False, native_execution=False)
        for stem in (tag+'Verification', *classifications):
            path = 'Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    follow_on_reports = (
        ('action_body_transform', 'ActionBodyTransform', ('ActionBodyTransformClassification', 'ActionTransformWorkVectorClassification', 'ActionRestoreBodyStackClassification')),
        ('action_object_state_dispatch_partial', 'ActionObjectStateDispatch', ('ActionObjectStateHandlersClassification', 'ActionClass18StateClassification')),
        ('action_object_phase_handlers', 'ActionObjectPhaseHandlers', ('ActionObjectOffsetRiseClassification', 'ActionObjectOffsetFallClassification', 'ActionObjectPhaseWaitClassification')),
        ('action_object_offset_transfer', 'ActionObjectOffsetTransfer', ('ActionObjectOffsetTransferClassification',)),
        ('action_object_offset_vector', 'ActionObjectOffsetVector', ('ActionObjectOffsetVectorClassification', 'ActionObjectOffsetCoefficientsClassification')),
    )
    for key, tag, classifications in follow_on_reports:
        if not all((ROOT/'Tools/Disasm/Reports'/(stem+'.json')).exists() for stem in classifications):
            continue
        proof = read(tag+'Verification')
        assert proof['passed'] and all(read(stem)['passed'] for stem in classifications)
        checkpoint[key] = dict(cases=proof['total_cases'],
            stopped_after_indirect_JP=proof.get('stopped_after_indirect_JP', False),
            aggregate_boundary_and_continuation_checks=proof.get('aggregate_boundary_and_continuation_checks', False),
            assembly_executed=False, native_execution=False)
        for stem in (tag+'Verification', *classifications):
            path = 'Tools/Disasm/Reports/'+stem+'.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
    effect_reports = ('ActionVisualEffectWalkVerification', 'ActionVisualEffectTransferVerification',
                      'VoxelEffectProjectionVerification', 'VoxelEffectDrawEntryVerification',
                      'VoxelSpriteClipBoundsVerification', 'VoxelSpriteSolidRasterVerification',
                      'VoxelSpriteSampleRasterVerification')
    if all((ROOT / 'Tools/Disasm/Reports' / (stem + '.json')).is_file() for stem in effect_reports):
        proofs = {stem: read(stem) for stem in effect_reports}
        assert all(proof['passed'] and not proof['assembly_executed'] for proof in proofs.values())
        checkpoint['visual_effect_boundaries'] = dict(
            cases_by_report={stem: proof['total_cases'] for stem, proof in proofs.items()},
            whole_draw_proved=False, composed_raster_verified=True, assembly_executed=False, native_execution=False)
        for stem in effect_reports:
            path = 'Tools/Disasm/Reports/' + stem + '.json'
            if path not in checkpoint['passed_reports']:
                checkpoint['passed_reports'].append(path)
        for stem in ('ActionVisualEffectResumeClassification', 'ActionVisualEffectDataClassification',
                     'ActionMotionVectorTailVerification'):
            path = 'Tools/Disasm/Reports/' + stem + '.json'
            if (ROOT / path).is_file():
                assert read(stem)['passed']
                if path not in checkpoint['passed_reports']:
                    checkpoint['passed_reports'].append(path)
    motion_reports = ('ActionBodyModeTransitionVerification', 'ActionBodyVectorScheduleVerification',
                      'ActionSubtractTransformVectorVerification', 'ActionBodyVectorPanelVerification',
                      'ActionWideMotionPrefixVerification', 'ActionWideProjectionInputVerification',
                      'ActionWideProjectionLoopVerification', 'ActionRenderFrameSetupVerification',
                      'ActionBankedBasisRotationVerification', 'ActionObjectProjectionScanVerification',
                      'ActionObjectProjectionResumeVerification', 'ActionEmptyRenderFrameVerification',
                      'ActionNonemptyRenderFrameVerification', 'ActionLargeEffectEntryVerification',
                      'ActionLargeEffectChildrenVerification', 'ActionRecordEffectThresholdVerification',
                      'ActionObjectStateReturnVerification', 'ActionNoiseExitVerification',
                      'ActionBodyMotionVerification', 'ControlsTargetOverlayVerification',
                      'ActionMotionWithoutKeysVerification', 'ControlsRadarLoopVerification',
                      'ActionVisualEffectListVerification', 'ActionSpawnRecordFinishVerification',
                      'ActionSpawnScheduleVerification', 'ActionSpawnClassSelectionVerification',
                      'ActionSpawnModelSelectionVerification', 'ActionSpawnSmallEffectVerification',
                      'ActionSpawnNearClass12Verification', 'ActionSpawnFallbackVerification',
                      'ActionSpawnAlternateGateVerification', 'ActionSpawnTemplateEntryVerification',
                      'ActionSpawnTemplateLoopVerification', 'ActionSpawnAlternateRecordVerification',
                      'ActionFrameGatesVerification', 'ActionObjectWalkVerification',
                      'ControlsTemporaryModuleVerification', 'ActionFlightCycleVerification',
                      'IntroMirroredTextureVerification', 'IntroScrolledInitializationVerification',
                      'IntroScrolledFrameVerification', 'IntroColumnInitializationVerification',
                      'IntroLookupInitializationVerification', 'IntroLookupFrameEntryVerification',
                      'IntroMirroredCompositionVerification', 'IntroStationTransitionVerification',
                      'FinalCycleVerification', 'StationBootstrapVerification', 'ActionObjectWalkCompositionVerification',
                      'DatasMirrorVerification', 'SavedStateLayoutVerification', 'ActionOverlayProjectionVerification', 'FighterAssetsVerification', 'ActionDiagnosticQueueVerification', 'ClipAliasExecutionVerification', 'ActionDeltaRatioVerification', 'BasicProgramVerification', 'IntroCoordinateSeedVerification',
                      'IntroPhysicalParametersVerification', 'IntroScreenResourcesVerification',
                      'ActionDirectDecimalVerification', 'ActionApproachWordVerification',
                      'ActionRecordDistanceVerification', 'ActionSelectedRecordStepVerification',
                      'ActionClass18ProximityVerification', 'ActionSelectClass8Verification',
                      'ActionSelectedRecordProximityVerification', 'ActionClassHandlersVerification')
    if all((ROOT / 'Tools/Disasm/Reports' / (stem + '.json')).is_file() for stem in motion_reports):
        proofs = {stem: read(stem) for stem in motion_reports}
        assert all(proof['passed'] and not proof['assembly_executed'] for proof in proofs.values())
        checkpoint['body_motion_boundaries'] = dict(
            cases_by_report={stem: proof['total_cases'] for stem, proof in proofs.items()},
            empty_and_nonempty_frame_profiles_verified=True, assembly_executed=False, native_execution=False)
        for stem in motion_reports:
            path = 'Tools/Disasm/Reports/' + stem + '.json'
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
