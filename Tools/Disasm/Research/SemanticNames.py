"""Подтверждённые имена внутренних входов и полей, не меняющие исходные команды."""

import re

DOCUMENTS = {
    **{("Station", address): "StationSpans.md" for address in
       (0xBF4E, 0xC093, 0xC0C9, 0xC436, 0xC626, 0xC165, 0xC16F, 0xC17B, 0xC1C0, 0xC1CF, 0xC1DE, 0xC1ED, 0xC1F2, 0xC21F, 0xC224)},
    ("Intro", 0x6BF6): "Intro.md", ("Intro", 0x6A2C): "Intro.md",
    ("Basic", 0x5D41): "Loader.md",
    **{("Map", address): "MapRaster.md" for address in (0xE57E, 0xE5AC, 0xE666, 0xE674)},
    ("Map", 0xE65D): "MapMath.md", ("Map", 0xE554): "MapMath.md",
    ("Music", 0xE6AE): "Music.md", ("Station", 0x9C77): "Interface.md",
    ("Station", 0x9EED): "Interface.md",
    **{("Station", address): "Font.md" for address in (0xBDA6, 0xBDCA)},
    **{("Station", address): "CellMap.md" for address in (0x9D96, 0x9DA6, 0xBE91, 0xBEAE, 0x9EC4, 0x9ED7)},
    **{("Station", address): "StationCore.md" for address in (0x6396, 0x639F, 0x63F1)},
    **{("Station", address): "Interface.md" for address in (0xBFAD, 0xBFF5, 0xC000)},
    **{("Station", address): "TextWindow.md" for address in (0xC039, 0xC233, 0xA3FF, 0xA436)},
    ("Voxel", 0xEC33): "Effects.md",
    **{("Text", address): "ScriptLanguage.md" for address in
       (0xC6EA, 0xC825, 0xC79C, 0xC7E3, 0xC1B9, 0xC7DA, 0xC900, 0xC918)},
}


def documentation_links(region, address):
    lines = [f"; Документация [{region}](../../Docs/FunctionDetails/{region}.md)"]
    if (region, address) in DOCUMENTS:
        document = DOCUMENTS[region, address]
        if isinstance(document, tuple):
            filename, title = document
            filename = filename if filename.endswith(".md") else filename + ".md"
        else:
            filename, title = document, document
        lines.append(f"; Подробный разбор [{title}](../../Docs/{filename})")
    return lines


LABELS = {
    ("Station", 0xBDAC): "NextChar", ("Station", 0xBDC4): "Saturate", ("Station", 0xBDC6): "ReturnWidth",
    ("Station", 0xBDD1): "NextChar", ("Station", 0xBDE9): "Saturate", ("Station", 0xBDEB): "ReturnWidth",
    ("Station", 0xBFC9): "ClipRight", ("Station", 0xBFD5): "ClipY",
    ("Station", 0xBFE1): "ClipBottom", ("Station", 0xBFED): "KeepFlags",
    ("Station", 0xBEB8): "FindFree", ("Station", 0xBED3): "ClipRight",
    ("Station", 0xBEDF): "ClipY", ("Station", 0xBEEB): "ClipBottom",
    ("Station", 0xBEF7): "MapAddress", ("Station", 0xBF07): "Row",
    ("Station", 0xBF09): "SpanBody",
    ("Station", 0xBE95): "NextPair", ("Station", 0xBEA0): "CheckHigh",
    ("Station", 0xBEAA): "Invalidate",
    ("Station", 0xC242): "ScaleX", ("Station", 0xC24D): "InsetX",
    ("Station", 0xC25F): "ScaleY", ("Station", 0xC26A): "InsetY",
    ("Station", 0xC011): "ClipRight", ("Station", 0xC01D): "ClipY",
    ("Station", 0xC029): "ClipBottom", ("Station", 0xC035): "RestoreIndex",
    ("Station", 0xC047): "ScaleX", ("Station", 0xC052): "StoreX",
    ("Station", 0xC062): "ScaleY", ("Station", 0xC06D): "StoreY",
    ("Station", 0xC64F): "SetFill", ("Station", 0xC652): "CharRow",
    ("Station", 0xC654): "PixelRow", ("Station", 0xC659): "SpanBody",
    ("Station", 0xC6A9): "NextChar",
    ("Station", 0xC09C): "SetBand",
    ("Station", 0xC0E1): "SeparatorRow", ("Station", 0xC0FE): "SeparatorSides",
    ("Station", 0xC110): "MiddleCount", ("Station", 0xC114): "MiddleRow",
    ("Station", 0xC136): "NextMiddle", ("Station", 0xC138): "BottomRow",
    ("Station", 0xC458): "Outline", ("Station", 0xC473): "MiddleCount",
    ("Station", 0xC476): "MiddleRow", ("Station", 0xC498): "NextMiddle",
    ("Station", 0xC49A): "BottomRow",
    ("Station", 0xBF6D): "LeftWidth", ("Station", 0xBF74): "CheckRight",
    ("Station", 0xBF86): "RightWidth", ("Station", 0xBF89): "RestoreAF",
    ("Station", 0xBF8A): "RowAddress", ("Station", 0xBF91): "RowCounter",
    ("Station", 0xC180): "Middle",
    **{("Station", address): label for start in (0xC1C0, 0xC1CF, 0xC1DE, 0xC1F2, 0xC224)
       for address, label in ((start + 8, "KeepLeft"), (start + 13, "KeepRight"))},
    ("Voxel", 0xEC36): "FindFree",
    ("Text", 0xC726): "ConvertDigits", ("Text", 0xC731): "AddTens",
    ("Text", 0xC746): "AddHundreds", ("Text", 0xC75F): "AddThousands",
    ("Text", 0xC77E): "AddTenThousands",
    ("Text", 0xC48F): "ReturnResult", ("Text", 0xC49A): "ReturnResult",
    ("Text", 0xC7E6): "NextBinding",
    ("Map", 0xE56A): "TryBit", ("Map", 0xE576): "NextBit",
    ("Map", 0xE5A4): "ReturnUp", ("Map", 0xE5A5): "AbortRaster",
    ("Map", 0xE5C1): "CheckLower", ("Map", 0xE5D1): "AbortRaster",
    ("Intro", 0x6A41): "UpdateStep",
}

MUSIC_VARIABLES = {
    0xE29D: "SlideCounterC", 0xE2CC: "SlideReloadC",
    0xE2A6: "SlideStepC", 0xE2AD: "SlideBranchC", 0xE2D5: "GateCounterC",
}
VISUAL_EFFECT_FIELDS = {
    0x00: "SavedHL", 0x01: "SavedHL + 1",
    0x02: "SavedDE", 0x03: "SavedDE + 1",
    0x04: "SavedBC", 0x05: "SavedBC + 1",
    0x06: "Mode", 0x07: "State",
    0x08: "FramePointer", 0x09: "FramePointer + 1",
    0x0A: "FirstFrame", 0x0B: "FirstFrame + 1",
    0x0C: "FrameCount", 0x0D: "FrameReload",
    0x0E: "FrameStride", 0x0F: "FrameStride + 1",
    0x10: "FrameWidth", 0x11: "FrameHeight",
}


from ActionPanelPhysicalData import name_operands as action_panel_physical_name_operands


def name_operands(region, function_address, operation):
    operation = action_panel_physical_name_operands(region, function_address, operation)
    if (region, function_address) == ("Action", 0xE020):
        operation = operation.replace('LD HL, #001B', 'LD HL, @FActionRecord.ViewPosition.X.High')
        operation = operation.replace('LD DE, #0020', 'LD DE, @FActionRecord.ViewPosition.Depth + @FActionWord')
    operation = confirmed_control_target_name_operands(region,function_address,operation)
    operation = flight_message_name_operands(region,function_address,operation)
    operation = action_boot_file_key_name_operands(region, function_address, operation)
    operation = intro_physical_parameter_name_operands(region, function_address, operation)
    operation = confirmed_call_target_name_operands(region, function_address, operation)
    operation = action_random_cluster_name_operands(region, function_address, operation)
    operation = intro_lookup_continuation_name_operands(region, function_address, operation)
    operation = intro_interlaced_frame_name_operands(region, function_address, operation)
    operation = intro_present_attributes_name_operands(region, function_address, operation)
    operation = intro_lookup_transfer_name_operands(region, function_address, operation)
    operation = intro_screen_name_operands(region, function_address, operation)
    operation = bootstrap_relocation_name_operands(region, function_address, operation)
    operation = intro_scrolled_sampler_name_operands(region, function_address, operation)
    operation = intro_pointer_sampler_name_operands(region, function_address, operation)
    operation = intro_texture_scale_name_operands(region, function_address, operation)
    operation = sum_squares8_name_operands(region, function_address, operation)
    operation = map_raster_setup_name_operands(region, function_address, operation)
    operation = map_distance_minimum_name_operands(region, function_address, operation)
    operation = nearest_map_variant_name_operands(region, function_address, operation)
    operation = visible_map_points_name_operands(region, function_address, operation)
    operation = nearest_visible_point_name_operands(region, function_address, operation)
    operation = arc_kernel_name_operands(region, function_address, operation)
    operation = arc_geometry_name_operands(region, function_address, operation)
    operation = arc_dispatcher_name_operands(region, function_address, operation)
    operation = map_scene_name_operands(region, function_address, operation)
    operation = animated_variant_name_operands(region, function_address, operation)
    operation = variant_count_name_operands(region, function_address, operation)
    operation = item_contour_switch_name_operands(region, function_address, operation)
    operation = periodic_variant_name_operands(region, function_address, operation)
    operation = map_panel_name_operands(region, function_address, operation)
    operation = item_move_guard_name_operands(region, function_address, operation)
    operation = map_pan_name_operands(region, function_address, operation)
    operation = system_traits_name_operands(region, function_address, operation)
    operation = system_info_panel_name_operands(region, function_address, operation)
    operation = map_selection_panel_name_operands(region, function_address, operation)
    operation = map_panel_event_name_operands(region, function_address, operation)
    operation = stored_point_edit_name_operands(region, function_address, operation)
    operation = stored_point_control_name_operands(region, function_address, operation)
    operation = decoded_message_name_operands(region, function_address, operation)
    operation = final_exit_name_operands(region, function_address, operation)
    operation = decoded_panel_name_operands(region, function_address, operation)
    operation = message_panel_name_operands(region, function_address, operation)
    operation = market_panel_helper_name_operands(region, function_address, operation)
    operation = panel_hover_name_operands(region, function_address, operation)
    operation = trade_numeric_column_name_operands(region, function_address, operation)
    operation = settings_parser_name_operands(region, function_address, operation)
    operation = scroll_body_clear_name_operands(region, function_address, operation)
    operation = scroll_window_name_operands(region, function_address, operation)
    operation = trade_panel_name_operands(region, function_address, operation)
    operation = control_panel_group_name_operands(region, function_address, operation)
    operation = ship_periodic_code_name_operands(region, function_address, operation)
    operation = ship_preview_callback_name_operands(region, function_address, operation)
    operation = introattributescanprefix_name_operands(region,function_address,operation)
    operation = introdetachedunpackgate_name_operands(region,function_address,operation)
    operation = controlsevenspanprefix_name_operands(region,function_address,operation)
    operation = action_record_scale_extra_entry_name_operands(region,function_address,operation)
    operation = introattributecounttail_name_operands(region,function_address,operation)
    operation = actionrandomclassgateentry_name_operands(region,function_address,operation)
    operation = stationallfilledband_name_operands(region,function_address,operation)
    operation = introdetachedtail_name_operands(region,function_address,operation)
    operation = archalflimitinputs_name_operands(region,function_address,operation)
    operation = drawcenteredwithoutowner_name_operands(region,function_address,operation)
    operation = controlsbodyprimarymask_name_operands(region,function_address,operation)
    operation = secondaryequipmentrows_name_operands(region,function_address,operation)
    operation = controlslegacyloadchain_name_operands(region,function_address,operation)
    operation = controlsresetflightcontext_name_operands(region,function_address,operation)
    operation = controlsstatestationrelay_name_operands(region,function_address,operation)
    operation = controlsdirectstationrelay_name_operands(region,function_address,operation)
    operation = actionhyperreload_name_operands(region,function_address,operation)
    operation = actionhyperjumppreparation_name_operands(region,function_address,operation)
    operation = actionhyperjump_name_operands(region,function_address,operation)
    operation = final_sync_name_operands(region,function_address,operation)
    operation = interface_special_name_operands(region,function_address,operation)
    operation = map_distance_render_name_operands(region,function_address,operation)
    operation = station_boot_resource_name_operands(region,function_address,operation)
    operation = actionboostadvance_name_operands(region,function_address,operation)
    operation = actionboostcommand_name_operands(region,function_address,operation)
    operation = actionantimissilecommand_name_operands(region,function_address,operation)
    operation = actiontractorcollect_name_operands(region,function_address,operation)
    operation = actionviewdirectioncommand_name_operands(region,function_address,operation)
    operation = actionreverseviewbasis_name_operands(region,function_address,operation)
    operation = actionejectcommands_name_operands(region,function_address,operation)
    operation = actionstationreturncommand_name_operands(region,function_address,operation)
    operation = actionfreeflightcommand_name_operands(region,function_address,operation)
    operation = actiontractormodecommand_name_operands(region,function_address,operation)
    operation = actionoverlaymodecommand_name_operands(region,function_address,operation)
    operation = action_target_commands_name_operands(region,function_address,operation)
    operation = intro_station_runtime_name_operands(region,function_address,operation)
    operation = action_equipment_name_operands(region,function_address,operation)
    operation = action_render_basis_name_operands(region,function_address,operation)
    operation = action_banked_parameter_build_name_operands(region,function_address,operation)
    operation = action_random_class_gate_name_operands(region,function_address,operation)
    operation = action_class20_spawn_name_operands(region,function_address,operation)
    operation = action_paired_aim_lines_name_operands(region,function_address,operation)
    operation = action_arrival_state_name_operands(region,function_address,operation)
    operation = action_linked_phase_state_name_operands(region,function_address,operation)
    operation = action_linked_target_state_name_operands(region,function_address,operation)
    operation = action_spawn_continue_name_operands(region,function_address,operation)
    operation = action_random_phase_step_name_operands(region,function_address,operation)
    operation = action_linked_motion_gate_name_operands(region,function_address,operation)
    operation = action_enter_timed_state_name_operands(region,function_address,operation)
    operation = action_timed_linked_state_name_operands(region,function_address,operation)
    operation = action_spawn_window_name_operands(region,function_address,operation)
    operation = action_spawn_current_link_name_operands(region,function_address,operation)
    operation = class17_spawn_name_operands(region,function_address,operation)
    operation = action_linked_overlay_name_operands(region,function_address,operation)
    operation = action_overlay_pair_name_operands(region,function_address,operation)
    operation = action_projected_pair_codes_name_operands(region,function_address,operation)
    operation = action_wide_vector_state_name_operands(region,function_address,operation)
    operation = action_class19_spawn_name_operands(region,function_address,operation)
    operation = action_class17_sweep_name_operands(region,function_address,operation)
    operation = action_small_effect_state_name_operands(region,function_address,operation)
    operation = action_linked_proximity_name_operands(region,function_address,operation)
    operation = action_class_refresh_name_operands(region,function_address,operation)
    operation = action_class8_spawn_gate_name_operands(region,function_address,operation)
    operation = action_periodic_class3_state_name_operands(region,function_address,operation)
    operation = action_acquire_local_state_name_operands(region,function_address,operation)
    operation = action_child_spawn_name_operands(region,function_address,operation)
    operation = action_linked_vectors_name_operands(region,function_address,operation)
    operation = action_linked_context_name_operands(region,function_address,operation)
    operation = action_timed_phase_state_name_operands(region,function_address,operation)
    operation = action_fast_phase_state_name_operands(region,function_address,operation)
    operation = action_local_offsets_name_operands(region,function_address,operation)
    operation = action_idle_state_name_operands(region,function_address,operation)
    operation = action_idle_base_reset_name_operands(region,function_address,operation)
    operation = action_timed_decay_state_name_operands(region,function_address,operation)
    operation = action_linked_near_state_name_operands(region,function_address,operation)
    operation = action_phase_near_state_name_operands(region,function_address,operation)
    operation = action_near_phase_name_operands(region,function_address,operation)
    operation = action_target_transition_name_operands(region,function_address,operation)
    operation = action_nearest_candidate_name_operands(region,function_address,operation)
    operation = action_candidate_gate_name_operands(region,function_address,operation)
    operation = action_candidate_class_name_operands(region,function_address,operation)
    operation = action_phase_transition_name_operands(region,function_address,operation)
    operation = action_class3_link_name_operands(region,function_address,operation)
    operation = action_class4_link_name_operands(region,function_address,operation)
    operation = action_class1_link_name_operands(region,function_address,operation)
    operation = action_class6_link_name_operands(region,function_address,operation)
    operation = action_class7_link_name_operands(region,function_address,operation)
    operation = action_class8_link_name_operands(region,function_address,operation)
    operation = action_class5_link_name_operands(region,function_address,operation)
    operation = action_class2_link_name_operands(region,function_address,operation)
    operation = action_selected_record_proximity_name_operands(region,function_address,operation)
    operation = action_select_class8_name_operands(region,function_address,operation)
    operation = action_class18_proximity_name_operands(region,function_address,operation)
    operation = action_selected_record_step_name_operands(region,function_address,operation)
    operation = action_record_distance_name_operands(region,function_address,operation)
    operation = action_approach_word_name_operands(region,function_address,operation)
    operation = action_direct_decimal_plain_name_operands(region,function_address,operation)
    operation = action_direct_decimal_scroll_name_operands(region,function_address,operation)
    operation = action_delta_ratio_name_operands(region,function_address,operation)
    operation = action_diagnostic_queue_name_operands(region,function_address,operation)
    operation = action_overlay_projection_name_operands(region,function_address,operation)
    operation = action_spawn_schedule_name_operands(region, function_address, operation)
    operation = action_spawn_record_finish_name_operands(region, function_address, operation)
    operation = action_visual_effect_list_name_operands(region, function_address, operation)
    operation = controls_radar_loop_name_operands(region, function_address, operation)
    operation = action_motion_without_keys_name_operands(region, function_address, operation)
    operation = controls_target_overlay_name_operands(region, function_address, operation)
    operation = action_body_motion_name_operands(region, function_address, operation)
    operation = action_body_mode_transition_name_operands(region, function_address, operation)
    operation = action_noise_exit_name_operands(region, function_address, operation)
    operation = action_object_state_return_name_operands(region, function_address, operation)
    operation = action_record_effect_threshold_name_operands(region, function_address, operation)
    operation = action_record_effect_resume_name_operands(region,function_address,operation)
    operation = action_large_effect_entry_name_operands(region, function_address, operation)
    operation = action_large_effect_continuation_name_operands(region,function_address,operation)
    operation = action_nonempty_render_frame_name_operands(region, function_address, operation)
    operation = action_banked_basis_rotation_name_operands(region, function_address, operation)
    operation = action_wide_projection_loop_name_operands(region, function_address, operation)
    operation = action_visual_effect_resume_name_operands(region,function_address,operation)
    operation = action_class18_state_name_operands(region, function_address, operation)
    operation = action_object_offset_coefficients_name_operands(region,function_address,operation)
    operation = action_object_offset_vector_name_operands(region,function_address,operation)
    operation = action_object_offset_transfer_name_operands(region,function_address,operation)
    operation = action_object_phase_wait_name_operands(region,function_address,operation)
    operation = action_object_offset_fall_name_operands(region,function_address,operation)
    operation = action_object_offset_rise_name_operands(region,function_address,operation)
    operation = action_body_transform_name_operands(region, function_address, operation)
    operation = action_restore_body_stack_name_operands(region,function_address,operation)
    operation = action_draw_banked_body_name_operands(region, function_address, operation)
    operation = controls_project_draw_body_name_operands(region, function_address, operation)
    operation = controls_body_draw_name_operands(region, function_address, operation)
    operation = controls_large_circle_name_operands(region, function_address, operation)
    operation = controls_full_width_circle_name_operands(region, function_address, operation)
    operation = controls_corner_circle_slice_name_operands(region, function_address, operation)
    operation = controls_horizontal_circle_name_operands(region, function_address, operation)
    operation = controls_vertical_circle_slice_name_operands(region, function_address, operation)
    operation = action_refresh_panel_name_operands(region, function_address, operation)
    operation = action_subtract_work_vector_name_operands(region, function_address, operation)
    operation = controls_circle_kernels_name_operands(region, function_address, operation)
    operation = controls_clipped_circle_half_name_operands(region, function_address, operation)
    operation = controls_station_prepare_name_operands(region, function_address, operation)
    operation = controls_station_relocation_name_operands(region, function_address, operation)
    operation = controls_circle_half_name_operands(region, function_address, operation)
    operation = controls_circle_interior_full_name_operands(region, function_address, operation)
    operation = action_banked_callback_name_operands(region, function_address, operation)
    operation = action_banked_callback_return_name_operands(region,function_address,operation)
    operation = action_key_gauge_decrease_name_operands(region,function_address,operation)
    operation = action_key_gauge_increase_name_operands(region,function_address,operation)
    operation = action_keyy_positive_name_operands(region,function_address,operation)
    operation = action_keyy_negative_name_operands(region,function_address,operation)
    operation = action_keyx_positive_name_operands(region,function_address,operation)
    operation = action_keyx_negative_name_operands(region,function_address,operation)
    operation = action_key_turn_positive_name_operands(region,function_address,operation)
    operation = action_key_turn_negative_name_operands(region,function_address,operation)
    operation = action_control_decay_name_operands(region, function_address, operation)
    operation = action_select_wide_target_name_operands(region, function_address, operation)
    operation = action_near_vector_search_name_operands(region, function_address, operation)
    operation = action_wide_target_step_name_operands(region, function_address, operation)
    operation = action_clamp_vector_words_name_operands(region, function_address, operation)
    operation = action_folded_near_words_name_operands(region, function_address, operation)
    operation = action_class3_link_count_name_operands(region, function_address, operation)
    operation = action_record_code_step_name_operands(region, function_address, operation)
    operation = action_half_delta_codes_name_operands(region, function_address, operation)
    operation = action_signed_ratio_code_name_operands(region, function_address, operation)
    operation = action_vector_high_maximum_name_operands(region, function_address, operation)
    operation = action_context_word_pairs_name_operands(region, function_address, operation)
    operation = action_abs_signed32_name_operands(region, function_address, operation)
    operation = action_preferred_dispatch_name_operands(region, function_address, operation)
    operation = action_preferred_seven_bridge_name_operands(region,function_address,operation)
    operation = action_preferred_zero_bridge_name_operands(region,function_address,operation)
    operation = action_preferred_chance_name_operands(region,function_address,operation)
    operation = action_preferred_apply_name_operands(region,function_address,operation)
    operation = action_class0_link_name_operands(region,function_address,operation)
    operation = action_ignored_classes_name_operands(region,function_address,operation)
    operation = action_class9_link_name_operands(region,function_address,operation)
    operation = action_random_filtered_record_name_operands(region,function_address,operation)
    operation = action_records5_or14_name_operands(region,function_address,operation)
    operation = action_records6_or7_name_operands(region,function_address,operation)
    operation = action_records_except6_and7_name_operands(region,function_address,operation)
    operation = action_link_override_name_operands(region,function_address,operation)
    operation = action_class_dispatch_name_operands(region, function_address, operation)
    operation = controls_projection_gate_name_operands(region, function_address, operation)
    operation = controls_projection_algorithm_name_operands(region, function_address, operation)
    operation = action_component_transform_name_operands(region, function_address, operation)
    operation = action_component_stack_name_operands(region,function_address,operation)
    operation = action_component_encoding_name_operands(region, function_address, operation)
    operation = action_cached_root_name_operands(region, function_address, operation)
    operation = action_third_glyph_vector_name_operands(region, function_address, operation)
    operation = action_third_glyph_stack_name_operands(region,function_address,operation)
    operation = action_third_glyph_publish_name_operands(region, function_address, operation)
    operation = action_banked_buffer_init_name_operands(region, function_address, operation)
    operation = action_class14_reuse_name_operands(region, function_address, operation)
    operation = action_record_base_reset_name_operands(region, function_address, operation)
    operation = action_record_update_name_operands(region, function_address, operation)
    operation = action_record_warning_return_name_operands(region,function_address,operation)
    operation = action_reject_record_name_operands(region, function_address, operation)
    operation = action_class_reuse_name_operands(region,function_address,operation)
    operation = actioniy_record_reuse_name_operands(region,function_address,operation)
    operation = action_record_scale_name_operands(region, function_address, operation)
    operation = action_record_selection_name_operands(region,function_address,operation)
    operation = action_offset_restore_name_operands(region, function_address, operation)
    operation = action_record_reuse_name_operands(region, function_address, operation)
    operation = action_folded_random_name_operands(region, function_address, operation)
    operation = action_unpack_name_operands(region, function_address, operation)
    operation = three_d_overlay_names(region, function_address, operation)
    operation = action_work_buffer_name_operands(region, function_address, operation)
    operation = action_queued_object_name_operands(region, function_address, operation)
    operation = action_clipped_packet_renderer_name_operands(region,function_address,operation)
    operation = action_packet_renderer_name_operands(region,function_address,operation)
    operation = action_polygon_flow_names(region, function_address, operation)
    operation = action_polygon_return_name_operands(region,function_address,operation)
    operation = action_polygon_wrap_right_top_name_operands(region,function_address,operation)
    operation = action_polygon_wrap_left_top_name_operands(region,function_address,operation)
    operation = action_polygon_wrap_right_name_operands(region,function_address,operation)
    operation = action_polygon_wrap_left_name_operands(region,function_address,operation)
    operation = action_polygon_select_right_name_operands(region,function_address,operation)
    operation = action_polygon_fill_rows_name_operands(region,function_address,operation)
    operation = action_polygon_right_edge_name_operands(region,function_address,operation)
    operation = action_polygon_right_short_step_name_operands(region,function_address,operation)
    operation = action_polygon_left_edge_name_operands(region,function_address,operation)
    operation = action_polygon_row_selection_name_operands(region,function_address,operation)
    operation = action_polygon_preparation_name_operands(region,function_address,operation)
    operation = action_line_raster_name_operands(region,function_address,operation)
    operation = action_single_edge_name_operands(region, function_address, operation)
    operation = action_polygon_name_operands(region, function_address, operation)
    operation = action_clip_cases_name_operands(region, function_address, operation)
    operation = action_clip_point_writers_name_operands(region, function_address, operation)
    operation = action_clip_comparisons_name_operands(region, function_address, operation)
    operation = action_clip_intersections_name_operands(region, function_address, operation)
    operation = action_clip_products_name_operands(region, function_address, operation)
    operation = action_signed_division_name_operands(region, function_address, operation)
    operation = action_face_orientation_name_operands(region,function_address,operation)
    operation = action_signed_multiply_name_operands(region, function_address, operation)
    operation = action_listed_codes_name_operands(region,function_address,operation)
    operation = action_vertex_codes_name_operands(region,function_address,operation)
    operation = action_vertex_abort_name_operands(region,function_address,operation)
    operation = action_object_vertices_name_operands(region,function_address,operation)
    operation = action_vertex_products_name_operands(region,function_address,operation)
    operation = action_vertex_group_name_operands(region,function_address,operation)
    operation = action_perspective_name_operands(region,function_address,operation)
    operation = action_object_copy_name_operands(region,function_address,operation)
    operation = action_render_matrix_name_operands(region, function_address, operation)
    operation = action_render_coefficients_name_operands(region, function_address, operation)
    operation = action_render_queue_control_name_operands(region, function_address, operation)
    operation = action_render_continuation_name_operands(region,function_address,operation)
    operation = action_render_queue_insert_name_operands(region, function_address, operation)
    operation = action_aim_follow_name_operands(region, function_address, operation)
    operation = action_close_bounds_name_operands(region, function_address, operation)
    operation = action_close_record_name_operands(region,function_address,operation)
    operation = action_station_transfer_name_operands(region,function_address,operation)
    operation = action_vector_reverse_name_operands(region,function_address,operation)
    operation = action_projection_clip_name_operands(region,function_address,operation)
    operation = action_projected_bounds_name_operands(region,function_address,operation)
    operation = action_scale_header_name_operands(region,function_address,operation)
    operation = action_object_header_name_operands(region, function_address, operation)
    operation = action_log_ratio_name_operands(region, function_address, operation)
    operation = action_exponential_table_name_operands(region,function_address,operation)
    operation = action_logarithm_table_name_operands(region,function_address,operation)
    operation = action_projected_capture_name_operands(region,function_address,operation)
    operation = action_record_link_event_name_operands(region, function_address, operation)
    operation = action_ay_effects_name_operands(region, function_address, operation)
    operation = action_missile_requests_name_operands(region,function_address,operation)
    operation = action_missile_creation_name_operands(region,function_address,operation)
    operation = action_vector_wrapper_name_operands(region,function_address,operation)
    operation = action_patched_vector_name_operands(region,function_address,operation)
    operation = action_scaled_multiply_name_operands(region, function_address, operation)
    operation = action_patch_swap_name_operands(region,function_address,operation)
    operation = action_record_iterator_name_operands(region, function_address, operation)
    operation = action_record_search_name_operands(region, function_address, operation)
    operation = action_record_index_name_operands(region,function_address,operation)
    operation = action_type_delta_name_operands(region,function_address,operation)
    operation = action_missile_consume_name_operands(region,function_address,operation)
    operation = action_missile_launch_name_operands(region,function_address,operation)
    operation = action_missile_stock_name_operands(region,function_address,operation)
    operation = action_key_scan_tables_name_operands(region,function_address,operation)
    operation = action_near_zero_word_name_operands(region, function_address, operation)
    operation = action_panel_gauges_name_operands(region, function_address, operation)
    operation = action_preferred_byte_name_operands(region, function_address, operation)
    operation = action_gauge_wrapper_name_operands(region, function_address, operation)
    operation = controls_six_row_gauge_name_operands(region, function_address, operation)
    operation = controls_raster_returns_name_operands(region, function_address, operation)
    operation = controls_glyph_indicators_name_operands(region, function_address, operation)
    operation = controls_three_row_glyph_name_operands(region, function_address, operation)
    operation = controls_parameter_activation_name_operands(region, function_address, operation)
    operation = action_parameter_activation_name_operands(region, function_address, operation)
    operation = action_apply_parameters_name_operands(region, function_address, operation)
    operation = controls_parameter_tables_name_operands(region, function_address, operation)
    operation = controls_seeded_parameters_name_operands(region, function_address, operation)
    operation = action_region_type_name_operands(region, function_address, operation)
    operation = controls_word_random_name_operands(region, function_address, operation)
    operation = controls_circle_span_name_operands(region, function_address, operation)
    operation = controls_circle_setup_name_operands(region, function_address, operation)
    operation = controls_small_bodies_name_operands(region, function_address, operation)
    operation = controls_small_masks_name_operands(region, function_address, operation)
    operation = controls_component_compare_name_operands(region, function_address, operation)
    operation = controls_push_spans_name_operands(region, function_address, operation)
    operation = controls_raster_step_name_operands(region, function_address, operation)
    operation = controls_squares_name_operands(region, function_address, operation)
    operation = controls_interior_rows_name_operands(region, function_address, operation)
    operation = controls_even_span_name_operands(region, function_address, operation)
    operation = controls_point_motion_name_operands(region, function_address, operation)
    operation = controls_point_respawn_name_operands(region, function_address, operation)
    operation = controls_span_masks_name_operands(region, function_address, operation)
    operation = controls_division_name_operands(region, function_address, operation)
    operation = action_bitmap_name_operands(region, function_address, operation)
    operation = controls_buffer_points_name_operands(region, function_address, operation)
    operation = controls_buffer_copy_name_operands(region, function_address, operation)
    operation = controls_marker_name_operands(region, function_address, operation)
    operation = controls_bcd_counter_name_operands(region, function_address, operation)
    operation = controls_text_display_name_operands(region, function_address, operation)
    operation = action_text_queue_name_operands(region, function_address, operation)
    operation = controls_text_queue_name_operands(region, function_address, operation)
    operation = music_initialization_name_operands(region, function_address, operation)
    operation = musicadvancea_name_operands(region, function_address, operation)
    operation = music_pattern_name_operands(region, function_address, operation)
    operation = musicchannelarow_name_operands(region, function_address, operation)
    operation = music_synthesis_name_operands(region, function_address, operation)
    operation = music_effect_name_operands(region, function_address, operation)
    operation = music_ay_output_name_operands(region, function_address, operation)
    operation = music_gate_tick_name_operands(region, function_address, operation)
    operation = musicchannelbrow_name_operands(region, function_address, operation)
    operation = musicchannelbstaging_name_operands(region, function_address, operation)
    operation = musicchannelastaging_name_operands(region, function_address, operation)
    operation = music_envelope_command_name_operands(region, function_address, operation)
    operation = music_envelope_name_operands(region, function_address, operation)
    operation = mainloopexecution_name_operands(region, function_address, operation)
    operation = unpackresource_name_operands(region, function_address, operation)
    operation = statuspanelaction_name_operands(region, function_address, operation)
    operation = stopmusic_name_operands(region, function_address, operation)
    operation = panelopenadapters_name_operands(region, function_address, operation)
    operation = counterevent_name_operands(region, function_address, operation)
    operation = contractmap_name_operands(region, function_address, operation)
    operation = flightbutton_name_operands(region, function_address, operation)
    operation = tradebuttonactions_name_operands(region, function_address, operation)
    operation = deferredactionadapters_name_operands(region, function_address, operation)
    operation = listhoveradapters_name_operands(region, function_address, operation)
    operation = missionpanelactions_name_operands(region, function_address, operation)
    operation = equipmentlistaction_name_operands(region, function_address, operation)
    operation = shiptradeaction_name_operands(region, function_address, operation)
    operation = systemmapaction_name_operands(region, function_address, operation)
    operation = saveslotpanels_name_operands(region, function_address, operation)
    operation = saveslotprotocol_name_operands(region, function_address, operation)
    operation = equipmentlisthover_name_operands(region, function_address, operation)
    operation = equipmentlistpanels_name_operands(region, function_address, operation)
    operation = passivepanelactions_name_operands(region, function_address, operation)
    operation = welcomepanel_name_operands(region, function_address, operation)
    operation = mappanelopening_name_operands(region, function_address, operation)
    operation = equipmentlistsetup_name_operands(region, function_address, operation)
    operation = equipmenttrademode_name_operands(region, function_address, operation)
    operation = modeltrademode_name_operands(region, function_address, operation)
    operation = helpnewsopening_name_operands(region, function_address, operation)
    operation = passivepanelhovers_name_operands(region, function_address, operation)
    operation = packedwordandactionreturn_name_operands(region, function_address, operation)
    operation = settingspanelactions_name_operands(region, function_address, operation)
    operation = settingsrowpanels_name_operands(region, function_address, operation)
    operation = keylabel_name_operands(region, function_address, operation)
    operation = equipmentinfo_name_operands(region, function_address, operation)
    operation = helppanelactions_name_operands(region, function_address, operation)
    operation = helppaneldraws_name_operands(region, function_address, operation)
    operation = stationhelpcalls_name_operands(region, function_address, operation)
    operation = shipmodelactionsstation_name_operands(region, function_address, operation)
    operation = help_text_selector_name_operands(region, function_address, operation)
    operation = help_line_index_name_operands(region, function_address, operation)
    operation = help_text_output_name_operands(region, function_address, operation)
    operation = d3d_clip_name_operands(region, function_address, operation)
    operation = d3d_third_name_operands(region, function_address, operation)
    operation = sprite_line_table_name_operands(region, function_address, operation)
    operation = d3d_setup_name_operands(region, function_address, operation)
    operation = preview_face_fill_name_operands(region, function_address, operation)
    operation = d3d_description_name_operands(region, function_address, operation)
    operation = d3d_price_name_operands(region, function_address, operation)
    operation = model_availability_name_operands(region, function_address, operation)
    operation = model_list_panel_name_operands(region, function_address, operation)
    operation = description_bank_name_operands(region, function_address, operation)
    operation = description_panel_name_operands(region, function_address, operation)
    operation = description_action_name_operands(region, function_address, operation)
    operation = preview_hover_name_operands(region, function_address, operation)
    operation = preview_action_name_operands(region, function_address, operation)
    operation = preview_multiply_name_operands(region, function_address, operation)
    operation = preview_transform_name_operands(region, function_address, operation)
    operation = preview_queue_name_operands(region, function_address, operation)
    operation = preview_lookup_name_operands(region, function_address, operation)
    operation = preview_bounds_name_operands(region, function_address, operation)
    operation = preview_queue_build_name_operands(region, function_address, operation)
    operation = preview_model_matrix_name_operands(region, function_address, operation)
    operation = preview_matrix_compose_name_operands(region, function_address, operation)
    operation = preview_projection_scale_name_operands(region, function_address, operation)
    operation = preview_perspective_name_operands(region, function_address, operation)
    operation = preview_vertex_group_name_operands(region, function_address, operation)
    operation = previewsquareentry_name_operands(region, function_address, operation)
    operation = previewframe_name_operands(region, function_address, operation)
    operation = previewqueuerender_name_operands(region, function_address, operation)
    operation = previewclippedfacestream_name_operands(region, function_address, operation)
    operation = previewclippolygon_name_operands(region, function_address, operation)
    operation = previewclipdispatch_name_operands(region, function_address, operation)
    operation = previewclipcases_name_operands(region, function_address, operation)
    operation = previewclipintersections_name_operands(region, function_address, operation)
    operation = previewclipdivision_name_operands(region, function_address, operation)
    operation = previewclipproductbuilders_name_operands(region, function_address, operation)
    operation = previewclipproductdifferences_name_operands(region, function_address, operation)
    operation = previewcliptail_name_operands(region, function_address, operation)
    operation = previewclipunwind_name_operands(region, function_address, operation)
    operation = previewinsidefacestream_name_operands(region, function_address, operation)
    operation = previewpolygonpreparation_name_operands(region, function_address, operation)
    operation = previewpolygonedges_name_operands(region, function_address, operation)
    operation = previewpolygonrows_name_operands(region, function_address, operation)
    operation = previewslopedivision_name_operands(region, function_address, operation)
    operation = previewedgeraster_name_operands(region, function_address, operation)
    operation = previewfacecodes_name_operands(region, function_address, operation)
    operation = previewfacemath_name_operands(region, function_address, operation)
    operation = previewvertexclass_name_operands(region, function_address, operation)
    operation = previewmodelwalk_name_operands(region, function_address, operation)
    operation = previewvertexproducts_name_operands(region, function_address, operation)
    operation = map_point_chain_name_operands(region, function_address, operation)
    operation = map_line_name_operands(region, function_address, operation)
    operation = arc_closing_name_operands(region, function_address, operation)
    operation = arc_preparation_name_operands(region, function_address, operation)
    operation = clip_case_name_operands(region, function_address, operation)
    operation = clip_tail_name_operands(region, function_address, operation)
    operation = clip_intersection_name_operands(region, function_address, operation)
    operation = clip_product_name_operands(region, function_address, operation)
    operation = map_point_outcode_name_operands(region, function_address, operation)
    operation = raster_preparation_name_operands(region, function_address, operation)
    operation = secondary_point_order_name_operands(region, function_address, operation)
    operation = variant_resource_name_operands(region, function_address, operation)
    operation = map_point_marker_name_operands(region, function_address, operation)
    operation = map_screen_table_name_operands(region, function_address, operation)
    operation = map_sector_table_name_operands(region, function_address, operation)
    operation = variant_label_name_operands(region, function_address, operation)
    operation = map_view_center_name_operands(region, function_address, operation)
    operation = stored_map_point_name_operands(region, function_address, operation)
    operation = mission_action_name_operands(region, function_address, operation)
    operation = status_draw_name_operands(region, function_address, operation)
    operation = mission_completion_name_operands(region, function_address, operation)
    operation = mission_name_draw_name_operands(region, function_address, operation)
    operation = mission_hover_name_operands(region, function_address, operation)
    operation = system_name_name_operands(region, function_address, operation)
    operation = mission_offer_name_operands(region, function_address, operation)
    operation = player_rank_name_operands(region, function_address, operation)
    operation = coordinate_distance_name_operands(region, function_address, operation)
    operation = seeded_root_name_operands(region, function_address, operation)
    operation = counter_draw_name_operands(region, function_address, operation)
    operation = main_loop_control_name_operands(region, function_address, operation)
    operation = script_cursor_name_operands(region, function_address, operation)
    operation = station_exit_name_operands(region, function_address, operation)
    operation = transition_name_operands(region, function_address, operation)
    operation = script_control_name_operands(region, function_address, operation)
    operation = queued_text_name_operands(region, function_address, operation)
    operation = unary_mode_name_operands(region, function_address, operation)
    operation = assignment_pipeline_name_operands(region, function_address, operation)
    operation = indexed_writer_name_operands(region, function_address, operation)
    operation = scalar_writer_name_operands(region, function_address, operation)
    operation = record_field_selector_name_operands(region, function_address, operation)
    operation = key_field_selector_name_operands(region, function_address, operation)
    operation = bank4_index_name_operands(region, function_address, operation)
    operation = entry_threshold_name_operands(region, function_address, operation)
    operation = weight_field_name_operands(region, function_address, operation)
    operation = cargo_field_name_operands(region, function_address, operation)
    operation = threshold_set_name_operands(region, function_address, operation)
    operation = membership_flags_name_operands(region, function_address, operation)
    operation = expression_push_name_operands(region, function_address, operation)
    operation = key_choice_name_operands(region, function_address, operation)
    operation = signature_return_name_operands(region, function_address, operation)
    operation = delimited_record_name_operands(region, function_address, operation)
    operation = station_script_fields_name_operands(region, function_address, operation)
    operation = market_field_name_operands(region, function_address, operation)
    operation = weighted_load_name_operands(region, function_address, operation)
    operation = field_suffix_name_operands(region, function_address, operation)
    if region == "Station" and function_address in (0xBDA6, 0xBDCA, 0xAE8D):
        operation = operation.replace("LD D, #89", "LD D, @FontConst.WidthPage")
        operation = operation.replace("#8A00", "@FontConst.GlyphBase")
    if region == "Station" and function_address in (0xBDA6, 0xBDCA):
        operation = operation.replace("CP #0D", "CP @TextConst.CarriageReturn")
        operation = operation.replace("CP #0A", "CP @TextConst.LineFeed")
    if region == "Station" and function_address in (0xBFAD, 0xC000, 0xBEAE):
        operation = operation.replace("CP #21", "CP @ScreenConst.ColumnEndLimit")
        operation = operation.replace("CP #19", "CP @ScreenConst.RowEndLimit")
        operation = operation.replace("SUB #20", "SUB @ScreenConst.ByteColumns")
        operation = operation.replace("SUB #18", "SUB @ScreenConst.CharRows")
    if (region, function_address) == ("Station", 0xBFAD):
        operation = operation.replace("CALL #C039", "CALL @Station.SetupTextWindow.Entry")
        operation = operation.replace("JP #C626", "JP @Station.FillRectangle.Entry")
    if (region, function_address) == ("Station", 0xBEAE):
        operation = operation.replace("#84FF", "@StationState.ItemIndex - 1")
        operation = operation.replace("(#BF08)", "(@StationState.CellSpanSkip)")
        operation = operation.replace("LD A, #20", "LD A, @ScreenConst.ByteColumns")
    if (region, function_address) == ("Station", 0x9EC4):
        operation = operation.replace("#8601", "@StationState.DirtyCells + 1")
        operation = operation.replace("#02FF", "@StationTables.WorkspaceTail")
    if (region, function_address) == ("Station", 0x9ED7):
        operation = operation.replace("#8501", "@StationState.ItemIndex + 1")
        operation = operation.replace("#007F", "@StationTables.IndexInitTail")
        operation = operation.replace("LD (HL), #FF", "LD (HL), @ItemIndexConst.FreeHigh")
    if (region, function_address) == ("Station", 0x9D96):
        operation = operation.replace("(#6307)", "(@StationState.PointerXY)")
    if (region, function_address) == ("Station", 0x9DA6):
        operation = operation.replace("ADD A, #86", "ADD A, @StationTables.CellMapPage")
    if (region, function_address) == ("Station", 0xBE91):
        operation = operation.replace("LD (HL), #FF", "LD (HL), @ItemIndexConst.FreeHigh")
    if (region, function_address) == ("Station", 0x6396):
        operation = operation.replace("AND #F8", "AND @Hardware.PageUpperMask")
    if (region, function_address) == ("Station", 0x639F):
        operation = operation.replace("#7FFD", "@Hardware.PagingPort")
    if (region, function_address) == ("Station", 0xC233):
        operation = operation.replace("ADD A, #03", "ADD A, @TextWindowConst.OriginInset")
        operation = operation.replace("SUB #04", "SUB @TextWindowConst.WidthInset")
        operation = operation.replace("SUB #0B", "SUB @TextWindowConst.HeightInset")
    if region == "Station" and function_address in (0xC039, 0xC233, 0xA3FF, 0xA436):
        fields = {0x6320: "CursorX", 0x6321: "CursorY", 0xAEBB: "OriginXLow", 0xAEBF: "OriginXHigh",
                  0xAEC7: "OriginYLow", 0xAECB: "OriginYHigh", 0xAEB3: "Width", 0xAEAB: "Height", 0xBD26: "Style",
                  0xA437: "SavedXLow", 0xA43C: "SavedYLow", 0xA441: "SavedXHigh", 0xA446: "SavedYHigh",
                  0xA44B: "SavedWidth", 0xA450: "SavedHeight", 0xA455: "SavedStyle", 0xA45A: "SavedCursorX", 0xA45F: "SavedCursorY"}
        for address, name in fields.items():
            operation = operation.replace(f"(#{address:04X})", f"(@TextWindow.{name})")
    if (region, function_address) == ("Station", 0xC626):
        operation = operation.replace("(#99B4)", "(@StationRaster.FillMode)")
        operation = operation.replace("(#C656)", "(@StationRaster.RectangleByte)")
        operation = operation.replace("(#C658)", "(@StationRaster.RectangleSkip)")
        operation = operation.replace("LD H, #82", "LD H, @StationTables.RowHighPage")
        operation = operation.replace("LD A, #20", "LD A, @ScreenConst.ByteColumns")
        operation = operation.replace("ADD A, #20", "ADD A, @ScreenConst.ByteColumns")
        operation = operation.replace("LD C, #08", "LD C, @ScreenConst.PixelsPerChar")
        operation = operation.replace("SUB #08", "SUB @ScreenConst.PixelsPerChar")
    if (region, function_address) == ("Station", 0xC093):
        operation = operation.replace("#C1C0", "@Station.SetOutlinePattern.Entry")
        operation = operation.replace("#C1CF", "@Station.SetCutoutPattern.Entry")
        operation = operation.replace("(#C0CA)", "(@StationRaster.BandPattern)")
    if region == "Station":
        operation = operation.replace("(#C17F)", "(@StationRaster.SpanSkip)")
        operation = operation.replace("(#C17C)", "(@StationRaster.LeftCode)")
        operation = operation.replace("(#C17D)", "(@StationRaster.LeftCode + 1)")
        operation = operation.replace("(#C1BC)", "(@StationRaster.RightCode)")
    if (region, function_address) == ("Station", 0xBF4E):
        operation = operation.replace("#2C72", "@SpanOpcode.LeftPair")
        operation = operation.replace("LD A, #71", "LD A, @SpanOpcode.WriteRight")
        operation = operation.replace("CP #1F", "CP @ScreenConst.LastColumn")
        operation = operation.replace("SUB #1F", "SUB @ScreenConst.LastColumn")
        operation = operation.replace("LD H, #82", "LD H, @StationTables.RowHighPage")
    if (region, function_address) == ("Station", 0xC165):
        operation = operation.replace("CP #18", "CP @ScreenConst.CharRows")
    if (region, function_address) == ("Station", 0xC16F):
        operation = operation.replace("ADD A, #20", "ADD A, @ScreenConst.ByteColumns")
        operation = operation.replace("SUB #08", "SUB @ScreenConst.PixelsPerChar")
    patterns = {
        0xC1C0: ("OutlineLeft", "Empty", "OutlineRight"),
        0xC1CF: ("CutoutLeft", "Solid", "CutoutRight"),
        0xC1DE: ("SixBitEdge", "Solid", "SixBitEdge"),
        0xC1F2: ("InsetLeft", "Solid", "InsetRight"),
        0xC224: ("OutlineLeft", "Empty", "OutlineRight"),
    }
    if region == "Station" and function_address in patterns:
        values = {"OutlineLeft": 0x40, "Empty": 0, "OutlineRight": 2, "CutoutLeft": 0x5F,
                  "Solid": 255, "CutoutRight": 0xFA, "SixBitEdge": 0x7E, "InsetLeft": 0x3F, "InsetRight": 0xFC}
        for register, field in zip(("D", "E", "C"), patterns[function_address]):
            operation = operation.replace(f"LD {register}, #{values[field]:02X}", f"LD {register}, @SpanPattern.{field}")
    if (region, function_address) == ("Station", 0xC1ED):
        operation = operation.replace("LD DE, #0000", "LD DE, @SpanPattern.EmptyPair")
    if (region, function_address) == ("Station", 0xC21F):
        operation = operation.replace("LD DE, #FFFF", "LD DE, @SpanPattern.SolidPair")
    if (region, function_address) == ("Intro", 0x6A2C):
        operation = operation.replace("BIT 7, B", "BIT @IntroConst.PhaseSignBit, B")
    if (region, function_address) == ("Intro", 0x6A4B):
        operation = operation.replace("(#6A5E)", "(@Intro.RunTimedEffect.StepCall + 1)")
    if region == "Intro" and function_address in (0x6BF6, 0x6DB6, 0x6C9C):
        for address, name in ((0x6C8A, "TexturePhases.PhaseA"), (0x6C90, "TexturePhases.PhaseB"),
                              (0x6C96, "TexturePhases.PhaseC"), (0x6400, "IntroTables.PhaseSamples"),
                              (0x6BA2, "IntroState.LookupHL"), (0x6BA6, "IntroState.LookupBCAlt"),
                              (0x6BA9, "IntroState.LookupHLAlt"), (0x6BAC, "IntroState.LookupDEAlt"),
                              (0x6C12, "IntroState.SampleCursor"), (0x6D40, "IntroLookupState.PointerRowPhase")):
            operation = operation.replace(f"#{address:04X}", "@" + name)
    if (region, function_address) == ("Basic", 0x5D41):
        for literal, name in (("#5FFF", "@LoaderConst.StackTop"), ("#5C3A", "@LoaderConst.SystemIY"),
                              ("#6500", "@Intro.InitializeIntro.Entry"), ("#5CF4", "@LoaderState.NextIntroBlock")):
            operation = operation.replace(literal, name)
        operation = operation.replace("LD B, #2C", "LD B, @LoaderConst.IntroSectors")
        operation = operation.replace("LD C, #05", "LD C, @TrDos.ReadSectors")
    if region == "Map" and function_address in (0xE57E, 0xE5AC, 0xE666, 0xE674):
        for address, name in ((0xDFB4, "RasterStack"), (0xDFB9, "RasterDown"),
                              (0xDFBA, "UpperRow"), (0xDFBC, "LowerRow")):
            operation = operation.replace(f"(#{address:04X})", f"(@MapState.{name})")
    if (region, function_address) == ("Station", 0x9C77):
        operation = operation.replace("#F101", "@StationState.Items + FInterfaceItem.Flags")
        operation = operation.replace("AND #E0", "AND @InterfaceFlags.GroupMask")
        operation = operation.replace("CP #40", "CP @InterfaceFlags.FrontGroup")
    if (region, function_address) == ("Map", 0xE65D):
        operation = operation.replace("#E9", "@MapConst.SquareLowPage")
    if (region, function_address) == ("Map", 0xE554):
        operation = operation.replace("(#DFB6)", "(@MapState.SqrtTarget)")
    if (region, function_address) in (("Text", 0xC900), ("Text", 0xC918)):
        for address, name in ((0x7217, "EquipmentRow"), (0x71B9, "EquipmentBase"),
                              (0x7068, "CargoRow"), (0x7026, "CargoBase")):
            operation = operation.replace(f"(#{address:04X})", f"(@ScriptSelection.{name})")
    if (region, function_address) == ("Text", 0xC7E3):
        operation = operation.replace("#0003", "FScriptToken")
    if (region, function_address) == ("Text", 0xC79C):
        operation = operation.replace("#C95F", "@ScriptTables.OperatorAnchor")
        operation = operation.replace("#0B", "@ScriptConst.OperatorCount")
        operation = operation.replace("(IX + #00)", "(IX + @ScriptConst.Cursor)")
    # Привязка извлечения трёх слов к фактическому размеру записи выражения.
    if (region, function_address) == ("Text", 0xC825):
        operation = operation.replace("#C1B9", "@Text.PushExpressionWord.Entry")
        operation = operation.replace("#FFFA", "-FExpressionCall")
        operation = operation.replace("#FFFB", "1 - FExpressionCall")
    # Именование границ десятичных ASCII-цифр только в подтверждённом считывателе.
    if (region, function_address) == ("Text", 0xC6EA):
        operation = operation.replace("#30", "@ScriptConst.DecimalZero")
        operation = operation.replace("#3A", "@ScriptConst.DecimalLimit")
        operation = operation.replace("(IX + #00)", "(IX + @ScriptConst.Cursor)")
        for offset, name in ((1, "UnitsBack"), (2, "TensBack"), (3, "HundredsBack"),
                             (4, "ThousandsBack"), (5, "TenThousands")):
            operation = operation.replace(f"(IX - #{offset:02X})", f"(IX - @ScriptConst.{name})")
    # Именование только обращений к подтверждённым операндам канала C.
    if region == "Music":
        for address, name in MUSIC_VARIABLES.items():
            operation = operation.replace(f"(#{address:04X})", f"(@MusicState.{name})")
    # Преобразование только подтверждённого указателя записи в AllocateEffect.
    if (region, function_address) == ("Voxel", 0xEC33):
        operation = re.sub(
            r"\(IY \+ #([0-9A-F]{2})\)",
            lambda match: "(IY + FVisualEffect."
            + VISUAL_EFFECT_FIELDS[int(match[1], 16)] + ")", operation)
        if operation == "LD BC, #0012":
            operation = "LD BC, FVisualEffect"
    operation = market_access_name_operands(region, function_address, operation)
    operation = market_name_operands(region, function_address, operation)
    return signature_name_operands(region, function_address, random_state_name_operands(region, function_address, event_dispatch_name_operands(region, function_address, rebuild_name_operands(region, function_address, background_name_operands(region, function_address, menu_command_name_operands(region, function_address, context_menu_draw_name_operands(region, function_address, row_hover_name_operands(region, function_address, row_highlight_name_operands(region, function_address, selection_band_name_operands(region, function_address, row_selection_name_operands(region, function_address, popup_name_operands(region, function_address, settings_label_name_operands(region, function_address, matrix_key_name_operands(region, function_address, window_graphics_name_operands(region, function_address, station_irq_name_operands(region, function_address, pointer_input_name_operands(region, function_address, mouse_name_operands(region, function_address, repaint_name_operands(region, function_address, screen_update_name_operands(region, function_address, track_name_operands(region, function_address, remove_draw_name_operands(region, function_address, xor_outline_name_operands(region, function_address, bounds_toggle_name_operands(region, function_address, active_name_operands(region, function_address, close_name_operands(region, function_address, interface_state_name_operands(region, function_address, toggle_name_operands(region, function_address, pointer_name_operands(region, function_address, bounds_name_operands(region, function_address, move_draw_name_operands(region, function_address, draw_list_name_operands(region, function_address, band_mode_name_operands(region, function_address, rect_name_operands(region, function_address, adapter_name_operands(region, function_address, caption_name_operands(region, function_address, centered_name_operands(region, function_address, inner_name_operands(region, function_address, pagination_name_operands(region, function_address, select_name_operands(region, function_address, justify_name_operands(region, function_address, word_name_operands(region, function_address, stream_name_operands(region, function_address, number_name_operands(region, function_address, glyph_name_operands(region, function_address, operation)))))))))))))))))))))))))))))))))))))))))))))


from GlyphFacts import LABELS as GLYPH_LABELS, DOCUMENTS as GLYPH_DOCUMENTS, name_operands as glyph_name_operands
LABELS.update(GLYPH_LABELS)
DOCUMENTS.update(GLYPH_DOCUMENTS)

from NumberFacts import LABELS as NUMBER_LABELS, DOCUMENTS as NUMBER_DOCUMENTS, name_operands as number_name_operands
LABELS.update(NUMBER_LABELS)
DOCUMENTS.update(NUMBER_DOCUMENTS)

from TextStreamFacts import LABELS as STREAM_LABELS, DOCUMENTS as STREAM_DOCUMENTS, name_operands as stream_name_operands
LABELS.update(STREAM_LABELS)
DOCUMENTS.update(STREAM_DOCUMENTS)

from WordFacts import LABELS as WORD_LABELS, DOCUMENTS as WORD_DOCUMENTS, name_operands as word_name_operands
LABELS.update(WORD_LABELS)
DOCUMENTS.update(WORD_DOCUMENTS)

from JustifyFacts import LABELS as JUSTIFY_LABELS, DOCUMENTS as JUSTIFY_DOCUMENTS, name_operands as justify_name_operands
LABELS.update(JUSTIFY_LABELS)
DOCUMENTS.update(JUSTIFY_DOCUMENTS)

from TextSelectFacts import LABELS as SELECT_LABELS, DOCUMENTS as SELECT_DOCUMENTS, name_operands as select_name_operands
LABELS.update(SELECT_LABELS)
DOCUMENTS.update(SELECT_DOCUMENTS)

from PaginationFacts import LABELS as PAGINATION_LABELS, DOCUMENTS as PAGINATION_DOCUMENTS, name_operands as pagination_name_operands
LABELS.update(PAGINATION_LABELS)
DOCUMENTS.update(PAGINATION_DOCUMENTS)

from InnerFrameFacts import LABELS as INNER_LABELS, DOCUMENTS as INNER_DOCUMENTS, name_operands as inner_name_operands
LABELS.update(INNER_LABELS)
DOCUMENTS.update(INNER_DOCUMENTS)

from CenteredItemFacts import LABELS as CENTERED_LABELS, DOCUMENTS as CENTERED_DOCUMENTS, name_operands as centered_name_operands
LABELS.update(CENTERED_LABELS)
DOCUMENTS.update(CENTERED_DOCUMENTS)

from CaptionItemFacts import LABELS as CAPTION_LABELS, DOCUMENTS as CAPTION_DOCUMENTS, name_operands as caption_name_operands
LABELS.update(CAPTION_LABELS)
DOCUMENTS.update(CAPTION_DOCUMENTS)

from DrawAdapterFacts import DOCUMENTS as ADAPTER_DOCUMENTS, name_operands as adapter_name_operands
DOCUMENTS.update(ADAPTER_DOCUMENTS)

from ItemRectFacts import DOCUMENTS as RECT_DOCUMENTS, name_operands as rect_name_operands
DOCUMENTS.update(RECT_DOCUMENTS)

from BandModeFacts import DOCUMENTS as BAND_MODE_DOCUMENTS, name_operands as band_mode_name_operands
DOCUMENTS.update(BAND_MODE_DOCUMENTS)

from DrawListFacts import DOCUMENTS as DRAW_LIST_DOCUMENTS, name_operands as draw_list_name_operands
DOCUMENTS.update(DRAW_LIST_DOCUMENTS)

from MoveDrawFacts import LABELS as MOVE_DRAW_LABELS, DOCUMENTS as MOVE_DRAW_DOCUMENTS, name_operands as move_draw_name_operands
LABELS.update(MOVE_DRAW_LABELS)
DOCUMENTS.update(MOVE_DRAW_DOCUMENTS)

from BoundsFacts import LABELS as BOUNDS_LABELS, DOCUMENTS as BOUNDS_DOCUMENTS, name_operands as bounds_name_operands
LABELS.update(BOUNDS_LABELS)
DOCUMENTS.update(BOUNDS_DOCUMENTS)

from PointerFacts import LABELS as POINTER_LABELS, DOCUMENTS as POINTER_DOCUMENTS, name_operands as pointer_name_operands
LABELS.update(POINTER_LABELS)
DOCUMENTS.update(POINTER_DOCUMENTS)

from ToggleFacts import LABELS as TOGGLE_LABELS, DOCUMENTS as TOGGLE_DOCUMENTS, name_operands as toggle_name_operands
LABELS.update(TOGGLE_LABELS)
DOCUMENTS.update(TOGGLE_DOCUMENTS)

from InterfaceStateFacts import DOCUMENTS as INTERFACE_STATE_DOCUMENTS, name_operands as interface_state_name_operands
DOCUMENTS.update(INTERFACE_STATE_DOCUMENTS)

from CloseItemFacts import DOCUMENTS as CLOSE_DOCUMENTS, name_operands as close_name_operands
DOCUMENTS.update(CLOSE_DOCUMENTS)

from ActiveItemFacts import LABELS as ACTIVE_LABELS, DOCUMENTS as ACTIVE_DOCUMENTS, name_operands as active_name_operands
LABELS.update(ACTIVE_LABELS)
DOCUMENTS.update(ACTIVE_DOCUMENTS)

from BoundsToggleFacts import LABELS as BOUNDS_TOGGLE_LABELS, DOCUMENTS as BOUNDS_TOGGLE_DOCUMENTS, name_operands as bounds_toggle_name_operands
LABELS.update(BOUNDS_TOGGLE_LABELS)
DOCUMENTS.update(BOUNDS_TOGGLE_DOCUMENTS)

from XorOutlineFacts import LABELS as XOR_OUTLINE_LABELS, DOCUMENTS as XOR_OUTLINE_DOCUMENTS, name_operands as xor_outline_name_operands
LABELS.update(XOR_OUTLINE_LABELS)
DOCUMENTS.update(XOR_OUTLINE_DOCUMENTS)

from RemoveDrawFacts import LABELS as REMOVE_DRAW_LABELS, DOCUMENTS as REMOVE_DRAW_DOCUMENTS, name_operands as remove_draw_name_operands
LABELS.update(REMOVE_DRAW_LABELS)
DOCUMENTS.update(REMOVE_DRAW_DOCUMENTS)

from TrackGeometryFacts import LABELS as TRACK_LABELS, DOCUMENTS as TRACK_DOCUMENTS, name_operands as track_name_operands
LABELS.update(TRACK_LABELS)
DOCUMENTS.update(TRACK_DOCUMENTS)

from ScreenUpdateFacts import DOCUMENTS as SCREEN_UPDATE_DOCUMENTS
DOCUMENTS.update(SCREEN_UPDATE_DOCUMENTS)
from ScreenUpdateFacts import LABELS as SCREEN_UPDATE_LABELS, name_operands as screen_update_name_operands
LABELS.update(SCREEN_UPDATE_LABELS)

from InterfaceActionFacts import DOCUMENTS as INTERFACE_ACTION_DOCUMENTS
DOCUMENTS.update(INTERFACE_ACTION_DOCUMENTS)

from RepaintChainFacts import LABELS as REPAINT_LABELS, DOCUMENTS as REPAINT_DOCUMENTS, name_operands as repaint_name_operands
LABELS.update(REPAINT_LABELS)
DOCUMENTS.update(REPAINT_DOCUMENTS)

from MouseInputFacts import LABELS as MOUSE_LABELS, DOCUMENTS as MOUSE_DOCUMENTS, name_operands as mouse_name_operands
LABELS.update(MOUSE_LABELS)
DOCUMENTS.update(MOUSE_DOCUMENTS)

from PointerInputFacts import LABELS as POINTER_INPUT_LABELS, DOCUMENTS as POINTER_INPUT_DOCUMENTS, name_operands as pointer_input_name_operands
LABELS.update(POINTER_INPUT_LABELS)
DOCUMENTS.update(POINTER_INPUT_DOCUMENTS)

from StationInterruptFacts import LABELS as STATION_IRQ_LABELS, DOCUMENTS as STATION_IRQ_DOCUMENTS, name_operands as station_irq_name_operands
LABELS.update(STATION_IRQ_LABELS)
DOCUMENTS.update(STATION_IRQ_DOCUMENTS)

from WindowGraphicsFacts import LABELS as WINDOW_GRAPHICS_LABELS, DOCUMENTS as WINDOW_GRAPHICS_DOCUMENTS, name_operands as window_graphics_name_operands
LABELS.update(WINDOW_GRAPHICS_LABELS)
DOCUMENTS.update(WINDOW_GRAPHICS_DOCUMENTS)


from MatrixKeyFacts import LABELS as MATRIX_KEY_LABELS, DOCUMENTS as MATRIX_KEY_DOCUMENTS, name_operands as matrix_key_name_operands
LABELS.update(MATRIX_KEY_LABELS)
DOCUMENTS.update(MATRIX_KEY_DOCUMENTS)

from SettingsLabelFacts import LABELS as SETTINGS_LABEL_LABELS, DOCUMENTS as SETTINGS_LABEL_DOCUMENTS, name_operands as settings_label_name_operands
LABELS.update(SETTINGS_LABEL_LABELS)
DOCUMENTS.update(SETTINGS_LABEL_DOCUMENTS)

from PopupFacts import LABELS as POPUP_LABELS, DOCUMENTS as POPUP_DOCUMENTS, name_operands as popup_name_operands
LABELS.update(POPUP_LABELS)
DOCUMENTS.update(POPUP_DOCUMENTS)

from RowSelectionFacts import DOCUMENTS as ROW_SELECTION_DOCUMENTS, name_operands as row_selection_name_operands
DOCUMENTS.update(ROW_SELECTION_DOCUMENTS)

from SelectionBandFacts import LABELS as SELECTION_BAND_LABELS, DOCUMENTS as SELECTION_BAND_DOCUMENTS, name_operands as selection_band_name_operands
LABELS.update(SELECTION_BAND_LABELS)
DOCUMENTS.update(SELECTION_BAND_DOCUMENTS)

from RowHighlightFacts import LABELS as ROW_HIGHLIGHT_LABELS, DOCUMENTS as ROW_HIGHLIGHT_DOCUMENTS, name_operands as row_highlight_name_operands
LABELS.update(ROW_HIGHLIGHT_LABELS)
DOCUMENTS.update(ROW_HIGHLIGHT_DOCUMENTS)

from RowHoverFacts import LABELS as ROW_HOVER_LABELS, DOCUMENTS as ROW_HOVER_DOCUMENTS, name_operands as row_hover_name_operands
LABELS.update(ROW_HOVER_LABELS)
DOCUMENTS.update(ROW_HOVER_DOCUMENTS)

from ContextMenuDrawFacts import DOCUMENTS as CONTEXT_MENU_DRAW_DOCUMENTS, name_operands as context_menu_draw_name_operands
DOCUMENTS.update(CONTEXT_MENU_DRAW_DOCUMENTS)

from MenuCommandFacts import LABELS as MENU_COMMAND_LABELS, DOCUMENTS as MENU_COMMAND_DOCUMENTS, name_operands as menu_command_name_operands
LABELS.update(MENU_COMMAND_LABELS)
DOCUMENTS.update(MENU_COMMAND_DOCUMENTS)

from BackgroundFacts import LABELS as BACKGROUND_LABELS, DOCUMENTS as BACKGROUND_DOCUMENTS, name_operands as background_name_operands
LABELS.update(BACKGROUND_LABELS)
DOCUMENTS.update(BACKGROUND_DOCUMENTS)

from RebuildFacts import LABELS as REBUILD_LABELS, DOCUMENTS as REBUILD_DOCUMENTS, name_operands as rebuild_name_operands
LABELS.update(REBUILD_LABELS)
DOCUMENTS.update(REBUILD_DOCUMENTS)

from EventDispatchFacts import LABELS as EVENT_DISPATCH_LABELS, DOCUMENTS as EVENT_DISPATCH_DOCUMENTS, name_operands as event_dispatch_name_operands
LABELS.update(EVENT_DISPATCH_LABELS)
DOCUMENTS.update(EVENT_DISPATCH_DOCUMENTS)

from RandomStateFacts import DOCUMENTS as RANDOM_STATE_DOCUMENTS, name_operands as random_state_name_operands
DOCUMENTS.update(RANDOM_STATE_DOCUMENTS)

from WorldSignatureFacts import LABELS as SIGNATURE_LABELS, DOCUMENTS as SIGNATURE_DOCUMENTS, name_operands as signature_name_operands
LABELS.update(SIGNATURE_LABELS)
DOCUMENTS.update(SIGNATURE_DOCUMENTS)

from MarketFacts import LABELS as MARKET_LABELS, DOCUMENTS as MARKET_DOCUMENTS, name_operands as market_name_operands
LABELS.update(MARKET_LABELS)
DOCUMENTS.update(MARKET_DOCUMENTS)

from MarketAccessFacts import LABELS as MARKET_ACCESS_LABELS, DOCUMENTS as MARKET_ACCESS_DOCUMENTS, name_operands as market_access_name_operands
LABELS.update(MARKET_ACCESS_LABELS)
DOCUMENTS.update(MARKET_ACCESS_DOCUMENTS)

from FieldSuffixFacts import LABELS as FIELD_SUFFIX_LABELS, DOCUMENTS as FIELD_SUFFIX_DOCUMENTS, name_operands as field_suffix_name_operands
LABELS.update(FIELD_SUFFIX_LABELS)
DOCUMENTS.update(FIELD_SUFFIX_DOCUMENTS)

from WeightedLoadFacts import LABELS as WEIGHTED_LOAD_LABELS, DOCUMENTS as WEIGHTED_LOAD_DOCUMENTS, name_operands as weighted_load_name_operands
LABELS.update(WEIGHTED_LOAD_LABELS)
DOCUMENTS.update(WEIGHTED_LOAD_DOCUMENTS)

from MarketFieldFacts import LABELS as MARKET_FIELD_LABELS, DOCUMENTS as MARKET_FIELD_DOCUMENTS, name_operands as market_field_name_operands
LABELS.update(MARKET_FIELD_LABELS)
DOCUMENTS.update(MARKET_FIELD_DOCUMENTS)

from DelimitedRecordFacts import LABELS as DELIMITED_RECORD_LABELS, DOCUMENTS as DELIMITED_RECORD_DOCUMENTS, name_operands as delimited_record_name_operands
from StationScriptFields import name_operands as station_script_fields_name_operands
LABELS.update(DELIMITED_RECORD_LABELS)
DOCUMENTS.update(DELIMITED_RECORD_DOCUMENTS)

from SignatureReturnFacts import DOCUMENTS as SIGNATURE_RETURN_DOCUMENTS, name_operands as signature_return_name_operands
DOCUMENTS.update(SIGNATURE_RETURN_DOCUMENTS)

from KeyChoiceFacts import DOCUMENTS as KEY_CHOICE_DOCUMENTS, name_operands as key_choice_name_operands
DOCUMENTS.update(KEY_CHOICE_DOCUMENTS)

from StrideFiveFacts import LABELS as STRIDE_FIVE_LABELS, DOCUMENTS as STRIDE_FIVE_DOCUMENTS
LABELS.update(STRIDE_FIVE_LABELS)
DOCUMENTS.update(STRIDE_FIVE_DOCUMENTS)

from MembershipFlagsFacts import LABELS as MEMBERSHIP_FLAGS_LABELS, DOCUMENTS as MEMBERSHIP_FLAGS_DOCUMENTS, name_operands as membership_flags_name_operands
LABELS.update(MEMBERSHIP_FLAGS_LABELS)
DOCUMENTS.update(MEMBERSHIP_FLAGS_DOCUMENTS)

from ThresholdSetFacts import LABELS as THRESHOLD_SET_LABELS, DOCUMENTS as THRESHOLD_SET_DOCUMENTS, name_operands as threshold_set_name_operands
LABELS.update(THRESHOLD_SET_LABELS)
DOCUMENTS.update(THRESHOLD_SET_DOCUMENTS)

from ActiveNeighborFacts import LABELS as ACTIVE_NEIGHBOR_LABELS, DOCUMENTS as ACTIVE_NEIGHBOR_DOCUMENTS
LABELS.update(ACTIVE_NEIGHBOR_LABELS)
DOCUMENTS.update(ACTIVE_NEIGHBOR_DOCUMENTS)

from CargoFieldFacts import LABELS as CARGO_FIELD_LABELS, DOCUMENTS as CARGO_FIELD_DOCUMENTS, name_operands as cargo_field_name_operands
LABELS.update(CARGO_FIELD_LABELS)
DOCUMENTS.update(CARGO_FIELD_DOCUMENTS)

from WeightFieldFacts import LABELS as WEIGHT_FIELD_LABELS, DOCUMENTS as WEIGHT_FIELD_DOCUMENTS, name_operands as weight_field_name_operands
LABELS.update(WEIGHT_FIELD_LABELS)
DOCUMENTS.update(WEIGHT_FIELD_DOCUMENTS)

from EntryThresholdFacts import LABELS as ENTRY_THRESHOLD_LABELS, DOCUMENTS as ENTRY_THRESHOLD_DOCUMENTS, name_operands as entry_threshold_name_operands
LABELS.update(ENTRY_THRESHOLD_LABELS)
DOCUMENTS.update(ENTRY_THRESHOLD_DOCUMENTS)

from Bank4IndexFacts import DOCUMENTS as BANK4_INDEX_DOCUMENTS, name_operands as bank4_index_name_operands
DOCUMENTS.update(BANK4_INDEX_DOCUMENTS)

from KeyFieldSelectorFacts import LABELS as KEY_FIELD_SELECTOR_LABELS, DOCUMENTS as KEY_FIELD_SELECTOR_DOCUMENTS, name_operands as key_field_selector_name_operands
LABELS.update(KEY_FIELD_SELECTOR_LABELS)
DOCUMENTS.update(KEY_FIELD_SELECTOR_DOCUMENTS)

from RecordFieldSelectorFacts import LABELS as RECORD_FIELD_SELECTOR_LABELS, DOCUMENTS as RECORD_FIELD_SELECTOR_DOCUMENTS, name_operands as record_field_selector_name_operands
LABELS.update(RECORD_FIELD_SELECTOR_LABELS)
DOCUMENTS.update(RECORD_FIELD_SELECTOR_DOCUMENTS)

from ExpressionPushFacts import LABELS as EXPRESSION_PUSH_LABELS, DOCUMENTS as EXPRESSION_PUSH_DOCUMENTS, name_operands as expression_push_name_operands
LABELS.update(EXPRESSION_PUSH_LABELS)
DOCUMENTS.update(EXPRESSION_PUSH_DOCUMENTS)

from MultiplyFacts import LABELS as MULTIPLY_LABELS, DOCUMENTS as MULTIPLY_DOCUMENTS
LABELS.update(MULTIPLY_LABELS)
DOCUMENTS.update(MULTIPLY_DOCUMENTS)

from NumericFieldFacts import LABELS as NUMERIC_FIELD_LABELS, DOCUMENTS as NUMERIC_FIELD_DOCUMENTS
LABELS.update(NUMERIC_FIELD_LABELS)
DOCUMENTS.update(NUMERIC_FIELD_DOCUMENTS)

from ScalarWriterFacts import LABELS as SCALAR_WRITER_LABELS, DOCUMENTS as SCALAR_WRITER_DOCUMENTS, name_operands as scalar_writer_name_operands
LABELS.update(SCALAR_WRITER_LABELS)
DOCUMENTS.update(SCALAR_WRITER_DOCUMENTS)

from IndexedWriterFacts import LABELS as INDEXED_WRITER_LABELS, DOCUMENTS as INDEXED_WRITER_DOCUMENTS, name_operands as indexed_writer_name_operands
LABELS.update(INDEXED_WRITER_LABELS)
DOCUMENTS.update(INDEXED_WRITER_DOCUMENTS)

from AssignmentPipelineFacts import LABELS as ASSIGNMENT_PIPELINE_LABELS, DOCUMENTS as ASSIGNMENT_PIPELINE_DOCUMENTS, name_operands as assignment_pipeline_name_operands
LABELS.update(ASSIGNMENT_PIPELINE_LABELS)
DOCUMENTS.update(ASSIGNMENT_PIPELINE_DOCUMENTS)

from UnaryModeFacts import LABELS as UNARY_MODE_LABELS, DOCUMENTS as UNARY_MODE_DOCUMENTS, name_operands as unary_mode_name_operands
LABELS.update(UNARY_MODE_LABELS)
DOCUMENTS.update(UNARY_MODE_DOCUMENTS)

from QueuedTextFacts import LABELS as QUEUED_TEXT_LABELS, DOCUMENTS as QUEUED_TEXT_DOCUMENTS, name_operands as queued_text_name_operands
LABELS.update(QUEUED_TEXT_LABELS)
DOCUMENTS.update(QUEUED_TEXT_DOCUMENTS)

from ScriptControlFacts import LABELS as SCRIPT_CONTROL_LABELS, DOCUMENTS as SCRIPT_CONTROL_DOCUMENTS, name_operands as script_control_name_operands
LABELS.update(SCRIPT_CONTROL_LABELS)
DOCUMENTS.update(SCRIPT_CONTROL_DOCUMENTS)

from ExpressionControlFacts import LABELS as EXPRESSION_CONTROL_LABELS, DOCUMENTS as EXPRESSION_CONTROL_DOCUMENTS
LABELS.update(EXPRESSION_CONTROL_LABELS)
DOCUMENTS.update(EXPRESSION_CONTROL_DOCUMENTS)

from TonnageCommandFacts import DOCUMENTS as TONNAGE_COMMAND_DOCUMENTS
DOCUMENTS.update(TONNAGE_COMMAND_DOCUMENTS)

from StationTransitionFacts import LABELS as TRANSITION_LABELS, DOCUMENTS as TRANSITION_DOCUMENTS, name_operands as transition_name_operands
LABELS.update(TRANSITION_LABELS)
DOCUMENTS.update(TRANSITION_DOCUMENTS)

from StationExitFacts import LABELS as STATION_EXIT_LABELS, DOCUMENTS as STATION_EXIT_DOCUMENTS, name_operands as station_exit_name_operands
LABELS.update(STATION_EXIT_LABELS)
DOCUMENTS.update(STATION_EXIT_DOCUMENTS)

from ScriptCursorFacts import name_operands as script_cursor_name_operands

from MainLoopControlFacts import LABELS as MAIN_LOOP_CONTROL_LABELS, DOCUMENTS as MAIN_LOOP_CONTROL_DOCUMENTS, name_operands as main_loop_control_name_operands
LABELS.update(MAIN_LOOP_CONTROL_LABELS)
DOCUMENTS.update(MAIN_LOOP_CONTROL_DOCUMENTS)

from CounterDrawFacts import DOCUMENTS as COUNTER_DRAW_DOCUMENTS, name_operands as counter_draw_name_operands
DOCUMENTS.update(COUNTER_DRAW_DOCUMENTS)

from SignedMultiplyFacts import LABELS as SIGNED_MULTIPLY_LABELS, DOCUMENTS as SIGNED_MULTIPLY_DOCUMENTS
LABELS.update(SIGNED_MULTIPLY_LABELS)
DOCUMENTS.update(SIGNED_MULTIPLY_DOCUMENTS)

from SeededRootFacts import LABELS as SEEDED_ROOT_LABELS, DOCUMENTS as SEEDED_ROOT_DOCUMENTS, name_operands as seeded_root_name_operands
LABELS.update(SEEDED_ROOT_LABELS)
DOCUMENTS.update(SEEDED_ROOT_DOCUMENTS)

from SignedDivisionFacts import LABELS as SIGNED_DIVISION_LABELS, DOCUMENTS as SIGNED_DIVISION_DOCUMENTS
LABELS.update(SIGNED_DIVISION_LABELS)
DOCUMENTS.update(SIGNED_DIVISION_DOCUMENTS)

from CoordinateDistanceFacts import LABELS as COORDINATE_DISTANCE_LABELS, DOCUMENTS as COORDINATE_DISTANCE_DOCUMENTS, name_operands as coordinate_distance_name_operands
LABELS.update(COORDINATE_DISTANCE_LABELS)
DOCUMENTS.update(COORDINATE_DISTANCE_DOCUMENTS)

from PlayerRankFacts import LABELS as PLAYER_RANK_LABELS, DOCUMENTS as PLAYER_RANK_DOCUMENTS, name_operands as player_rank_name_operands
LABELS.update(PLAYER_RANK_LABELS)
DOCUMENTS.update(PLAYER_RANK_DOCUMENTS)

from MissionOfferFacts import LABELS as MISSION_OFFER_LABELS, DOCUMENTS as MISSION_OFFER_DOCUMENTS, name_operands as mission_offer_name_operands
LABELS.update(MISSION_OFFER_LABELS)
DOCUMENTS.update(MISSION_OFFER_DOCUMENTS)

from SystemNameFacts import LABELS as SYSTEM_NAME_LABELS, DOCUMENTS as SYSTEM_NAME_DOCUMENTS, name_operands as system_name_name_operands
LABELS.update(SYSTEM_NAME_LABELS)
DOCUMENTS.update(SYSTEM_NAME_DOCUMENTS)

from MissionHoverFacts import LABELS as MISSION_HOVER_LABELS, DOCUMENTS as MISSION_HOVER_DOCUMENTS, name_operands as mission_hover_name_operands
LABELS.update(MISSION_HOVER_LABELS)
DOCUMENTS.update(MISSION_HOVER_DOCUMENTS)

from MissionNameDrawFacts import LABELS as MISSION_NAME_DRAW_LABELS, DOCUMENTS as MISSION_NAME_DRAW_DOCUMENTS, name_operands as mission_name_draw_name_operands
LABELS.update(MISSION_NAME_DRAW_LABELS)
DOCUMENTS.update(MISSION_NAME_DRAW_DOCUMENTS)

from MissionCompletionFacts import LABELS as MISSION_COMPLETION_LABELS, DOCUMENTS as MISSION_COMPLETION_DOCUMENTS, name_operands as mission_completion_name_operands
LABELS.update(MISSION_COMPLETION_LABELS)
DOCUMENTS.update(MISSION_COMPLETION_DOCUMENTS)

from StatusDrawFacts import LABELS as STATUS_DRAW_LABELS, DOCUMENTS as STATUS_DRAW_DOCUMENTS, name_operands as status_draw_name_operands
LABELS.update(STATUS_DRAW_LABELS)
DOCUMENTS.update(STATUS_DRAW_DOCUMENTS)

from MissionActionFacts import LABELS as MISSION_ACTION_LABELS, DOCUMENTS as MISSION_ACTION_DOCUMENTS, name_operands as mission_action_name_operands
LABELS.update(MISSION_ACTION_LABELS)
DOCUMENTS.update(MISSION_ACTION_DOCUMENTS)

from StoredMapPointFacts import LABELS as STORED_MAP_POINT_LABELS, DOCUMENTS as STORED_MAP_POINT_DOCUMENTS, name_operands as stored_map_point_name_operands
LABELS.update(STORED_MAP_POINT_LABELS)
DOCUMENTS.update(STORED_MAP_POINT_DOCUMENTS)

from MapViewCenterFacts import LABELS as MAP_VIEW_CENTER_LABELS, DOCUMENTS as MAP_VIEW_CENTER_DOCUMENTS, name_operands as map_view_center_name_operands
LABELS.update(MAP_VIEW_CENTER_LABELS)
DOCUMENTS.update(MAP_VIEW_CENTER_DOCUMENTS)

from VariantLabelFacts import LABELS as VARIANT_LABEL_LABELS, DOCUMENTS as VARIANT_LABEL_DOCUMENTS, name_operands as variant_label_name_operands
LABELS.update(VARIANT_LABEL_LABELS)
DOCUMENTS.update(VARIANT_LABEL_DOCUMENTS)

from MapSectorTableFacts import LABELS as MAP_SECTOR_TABLE_LABELS, DOCUMENTS as MAP_SECTOR_TABLE_DOCUMENTS, name_operands as map_sector_table_name_operands
LABELS.update(MAP_SECTOR_TABLE_LABELS)
DOCUMENTS.update(MAP_SECTOR_TABLE_DOCUMENTS)

from MapScreenTableFacts import LABELS as MAP_SCREEN_TABLE_LABELS, DOCUMENTS as MAP_SCREEN_TABLE_DOCUMENTS, name_operands as map_screen_table_name_operands
LABELS.update(MAP_SCREEN_TABLE_LABELS)
DOCUMENTS.update(MAP_SCREEN_TABLE_DOCUMENTS)

from MapPointMarkerFacts import LABELS as MAP_POINT_MARKER_LABELS, DOCUMENTS as MAP_POINT_MARKER_DOCUMENTS, name_operands as map_point_marker_name_operands
LABELS.update(MAP_POINT_MARKER_LABELS)
DOCUMENTS.update(MAP_POINT_MARKER_DOCUMENTS)

from VariantResourceFacts import LABELS as VARIANT_RESOURCE_LABELS, DOCUMENTS as VARIANT_RESOURCE_DOCUMENTS, name_operands as variant_resource_name_operands
LABELS.update(VARIANT_RESOURCE_LABELS)
DOCUMENTS.update(VARIANT_RESOURCE_DOCUMENTS)

from SecondaryPointOrderFacts import LABELS as SECONDARY_POINT_ORDER_LABELS, DOCUMENTS as SECONDARY_POINT_ORDER_DOCUMENTS, name_operands as secondary_point_order_name_operands
LABELS.update(SECONDARY_POINT_ORDER_LABELS)
DOCUMENTS.update(SECONDARY_POINT_ORDER_DOCUMENTS)

from RasterPreparationFacts import LABELS as RASTER_PREPARATION_LABELS, DOCUMENTS as RASTER_PREPARATION_DOCUMENTS, name_operands as raster_preparation_name_operands
LABELS.update(RASTER_PREPARATION_LABELS)
DOCUMENTS.update(RASTER_PREPARATION_DOCUMENTS)

from MapPointOutcodeFacts import LABELS as MAP_POINT_OUTCODE_LABELS, DOCUMENTS as MAP_POINT_OUTCODE_DOCUMENTS, name_operands as map_point_outcode_name_operands
LABELS.update(MAP_POINT_OUTCODE_LABELS)
DOCUMENTS.update(MAP_POINT_OUTCODE_DOCUMENTS)

from ClipProductFacts import LABELS as CLIP_PRODUCT_LABELS, DOCUMENTS as CLIP_PRODUCT_DOCUMENTS, name_operands as clip_product_name_operands
LABELS.update(CLIP_PRODUCT_LABELS)
DOCUMENTS.update(CLIP_PRODUCT_DOCUMENTS)

from ClipIntersectionFacts import LABELS as CLIP_INTERSECTION_LABELS, DOCUMENTS as CLIP_INTERSECTION_DOCUMENTS, name_operands as clip_intersection_name_operands
LABELS.update(CLIP_INTERSECTION_LABELS)
DOCUMENTS.update(CLIP_INTERSECTION_DOCUMENTS)

from ClipTailFacts import LABELS as CLIP_TAIL_LABELS, DOCUMENTS as CLIP_TAIL_DOCUMENTS, name_operands as clip_tail_name_operands
LABELS.update(CLIP_TAIL_LABELS)
DOCUMENTS.update(CLIP_TAIL_DOCUMENTS)

from ClipCaseFacts import LABELS as CLIP_CASE_LABELS, DOCUMENTS as CLIP_CASE_DOCUMENTS, name_operands as clip_case_name_operands
LABELS.update(CLIP_CASE_LABELS)
DOCUMENTS.update(CLIP_CASE_DOCUMENTS)

from ArcPreparationFacts import LABELS as ARC_PREPARATION_LABELS, DOCUMENTS as ARC_PREPARATION_DOCUMENTS, name_operands as arc_preparation_name_operands
LABELS.update(ARC_PREPARATION_LABELS)
DOCUMENTS.update(ARC_PREPARATION_DOCUMENTS)

from ArcClosingFacts import LABELS as ARC_CLOSING_LABELS, DOCUMENTS as ARC_CLOSING_DOCUMENTS, name_operands as arc_closing_name_operands
LABELS.update(ARC_CLOSING_LABELS)
DOCUMENTS.update(ARC_CLOSING_DOCUMENTS)

from MapLineFacts import LABELS as MAP_LINE_LABELS, DOCUMENTS as MAP_LINE_DOCUMENTS, name_operands as map_line_name_operands
LABELS.update(MAP_LINE_LABELS)
DOCUMENTS.update(MAP_LINE_DOCUMENTS)

from MapPointChainFacts import LABELS as MAP_POINT_CHAIN_LABELS, DOCUMENTS as MAP_POINT_CHAIN_DOCUMENTS, name_operands as map_point_chain_name_operands
LABELS.update(MAP_POINT_CHAIN_LABELS)
DOCUMENTS.update(MAP_POINT_CHAIN_DOCUMENTS)

from SumSquares8Facts import LABELS as SUM_SQUARES8_LABELS, DOCUMENTS as SUM_SQUARES8_DOCUMENTS, name_operands as sum_squares8_name_operands
LABELS.update(SUM_SQUARES8_LABELS)
DOCUMENTS.update(SUM_SQUARES8_DOCUMENTS)

from MapRuntimeProfiles import DOCUMENTS as MAP_RUNTIME_PROFILE_DOCUMENTS
DOCUMENTS.update(MAP_RUNTIME_PROFILE_DOCUMENTS)

from MapRasterSetupFacts import LABELS as MAP_RASTER_SETUP_LABELS, DOCUMENTS as MAP_RASTER_SETUP_DOCUMENTS, name_operands as map_raster_setup_name_operands
LABELS.update(MAP_RASTER_SETUP_LABELS)
DOCUMENTS.update(MAP_RASTER_SETUP_DOCUMENTS)

from MapDistanceMinimumFacts import LABELS as MAP_DISTANCE_MINIMUM_LABELS, DOCUMENTS as MAP_DISTANCE_MINIMUM_DOCUMENTS, name_operands as map_distance_minimum_name_operands
LABELS.update(MAP_DISTANCE_MINIMUM_LABELS)
DOCUMENTS.update(MAP_DISTANCE_MINIMUM_DOCUMENTS)

from NearestMapVariantFacts import LABELS as NEAREST_MAP_VARIANT_LABELS, DOCUMENTS as NEAREST_MAP_VARIANT_DOCUMENTS, name_operands as nearest_map_variant_name_operands
LABELS.update(NEAREST_MAP_VARIANT_LABELS)
DOCUMENTS.update(NEAREST_MAP_VARIANT_DOCUMENTS)

from VisibleMapPointsFacts import LABELS as VISIBLE_MAP_POINTS_LABELS, DOCUMENTS as VISIBLE_MAP_POINTS_DOCUMENTS, name_operands as visible_map_points_name_operands
LABELS.update(VISIBLE_MAP_POINTS_LABELS)
DOCUMENTS.update(VISIBLE_MAP_POINTS_DOCUMENTS)

from NearestVisiblePointFacts import LABELS as NEAREST_VISIBLE_POINT_LABELS, DOCUMENTS as NEAREST_VISIBLE_POINT_DOCUMENTS, name_operands as nearest_visible_point_name_operands
LABELS.update(NEAREST_VISIBLE_POINT_LABELS)
DOCUMENTS.update(NEAREST_VISIBLE_POINT_DOCUMENTS)

from ArcRecurrenceFacts import LABELS as ARC_RECURRENCE_LABELS, DOCUMENTS as ARC_RECURRENCE_DOCUMENTS
LABELS.update(ARC_RECURRENCE_LABELS)
DOCUMENTS.update(ARC_RECURRENCE_DOCUMENTS)

from ArcKernelFacts import LABELS as ARC_KERNEL_LABELS, DOCUMENTS as ARC_KERNEL_DOCUMENTS, name_operands as arc_kernel_name_operands
LABELS.update(ARC_KERNEL_LABELS)
DOCUMENTS.update(ARC_KERNEL_DOCUMENTS)

from ArcGeometryFacts import LABELS as ARC_GEOMETRY_LABELS, name_operands as arc_geometry_name_operands
LABELS.update(ARC_GEOMETRY_LABELS)

from ArcDispatcherFacts import LABELS as ARC_DISPATCHER_LABELS, DOCUMENTS as ARC_DISPATCHER_DOCUMENTS, name_operands as arc_dispatcher_name_operands
LABELS.update(ARC_DISPATCHER_LABELS)
DOCUMENTS.update(ARC_DISPATCHER_DOCUMENTS)

from MapSceneFacts import LABELS as MAP_SCENE_LABELS, DOCUMENTS as MAP_SCENE_DOCUMENTS, name_operands as map_scene_name_operands
LABELS.update(MAP_SCENE_LABELS)
DOCUMENTS.update(MAP_SCENE_DOCUMENTS)

from MapClipCasesFacts import LABELS as MAP_CLIP_CASE_LABELS, DOCUMENTS as MAP_CLIP_CASE_DOCUMENTS
LABELS.update(MAP_CLIP_CASE_LABELS)
DOCUMENTS.update(MAP_CLIP_CASE_DOCUMENTS)

from AnimatedVariantFacts import LABELS as ANIMATED_VARIANT_LABELS, DOCUMENTS as ANIMATED_VARIANT_DOCUMENTS, name_operands as animated_variant_name_operands
LABELS.update(ANIMATED_VARIANT_LABELS)
DOCUMENTS.update(ANIMATED_VARIANT_DOCUMENTS)

from VariantCountFacts import DOCUMENTS as VARIANT_COUNT_DOCUMENTS, name_operands as variant_count_name_operands
DOCUMENTS.update(VARIANT_COUNT_DOCUMENTS)

from ItemContourSwitchFacts import DOCUMENTS as ITEM_CONTOUR_SWITCH_DOCUMENTS, name_operands as item_contour_switch_name_operands
DOCUMENTS.update(ITEM_CONTOUR_SWITCH_DOCUMENTS)

from PeriodicVariantFacts import LABELS as PERIODIC_VARIANT_LABELS, DOCUMENTS as PERIODIC_VARIANT_DOCUMENTS, name_operands as periodic_variant_name_operands
LABELS.update(PERIODIC_VARIANT_LABELS)
DOCUMENTS.update(PERIODIC_VARIANT_DOCUMENTS)

from MapPanelFacts import DOCUMENTS as MAP_PANEL_DOCUMENTS, name_operands as map_panel_name_operands
DOCUMENTS.update(MAP_PANEL_DOCUMENTS)

from ItemMoveGuardFacts import DOCUMENTS as ITEM_MOVE_GUARD_DOCUMENTS, name_operands as item_move_guard_name_operands
DOCUMENTS.update(ITEM_MOVE_GUARD_DOCUMENTS)

from MapPanFacts import LABELS as MAP_PAN_LABELS, DOCUMENTS as MAP_PAN_DOCUMENTS, name_operands as map_pan_name_operands
LABELS.update(MAP_PAN_LABELS)
DOCUMENTS.update(MAP_PAN_DOCUMENTS)

from SystemTraitsFacts import LABELS as SYSTEM_TRAITS_LABELS, DOCUMENTS as SYSTEM_TRAITS_DOCUMENTS, name_operands as system_traits_name_operands
LABELS.update(SYSTEM_TRAITS_LABELS)
DOCUMENTS.update(SYSTEM_TRAITS_DOCUMENTS)

from SystemInfoPanelFacts import LABELS as SYSTEM_INFO_PANEL_LABELS, DOCUMENTS as SYSTEM_INFO_PANEL_DOCUMENTS, name_operands as system_info_panel_name_operands
LABELS.update(SYSTEM_INFO_PANEL_LABELS)
DOCUMENTS.update(SYSTEM_INFO_PANEL_DOCUMENTS)

from MapSelectionPanelFacts import DOCUMENTS as MAP_SELECTION_PANEL_DOCUMENTS, name_operands as map_selection_panel_name_operands
DOCUMENTS.update(MAP_SELECTION_PANEL_DOCUMENTS)

from MapPanelEventFacts import DOCUMENTS as MAP_PANEL_EVENT_DOCUMENTS, name_operands as map_panel_event_name_operands
DOCUMENTS.update(MAP_PANEL_EVENT_DOCUMENTS)

from StoredPointEditFacts import LABELS as STORED_POINT_EDIT_LABELS, DOCUMENTS as STORED_POINT_EDIT_DOCUMENTS, name_operands as stored_point_edit_name_operands
LABELS.update(STORED_POINT_EDIT_LABELS)
DOCUMENTS.update(STORED_POINT_EDIT_DOCUMENTS)

from StoredPointControlFacts import LABELS as STORED_POINT_CONTROL_LABELS, DOCUMENTS as STORED_POINT_CONTROL_DOCUMENTS, name_operands as stored_point_control_name_operands
LABELS.update(STORED_POINT_CONTROL_LABELS)
DOCUMENTS.update(STORED_POINT_CONTROL_DOCUMENTS)

DOCUMENTS['Station',0x7CC6]=('AuxiliaryCycleReads','частичные доказательства двух абсолютных чтений, игровой договор остаётся Unknown')

from DecodedMessageFacts import DOCUMENTS as DECODED_MESSAGE_DOCUMENTS, name_operands as decoded_message_name_operands
DOCUMENTS.update(DECODED_MESSAGE_DOCUMENTS)

from FinalExitFacts import LABELS as FINAL_EXIT_LABELS, DOCUMENTS as FINAL_EXIT_DOCUMENTS, name_operands as final_exit_name_operands
LABELS.update(FINAL_EXIT_LABELS)
DOCUMENTS.update(FINAL_EXIT_DOCUMENTS)

from DecodedPanelFacts import LABELS as DECODED_PANEL_LABELS, DOCUMENTS as DECODED_PANEL_DOCUMENTS, name_operands as decoded_panel_name_operands
LABELS.update(DECODED_PANEL_LABELS)
DOCUMENTS.update(DECODED_PANEL_DOCUMENTS)

from MessagePanelFacts import LABELS as MESSAGE_PANEL_LABELS, DOCUMENTS as MESSAGE_PANEL_DOCUMENTS, name_operands as message_panel_name_operands
LABELS.update(MESSAGE_PANEL_LABELS)
DOCUMENTS.update(MESSAGE_PANEL_DOCUMENTS)

from MarketPanelHelperFacts import DOCUMENTS as MARKET_PANEL_HELPER_DOCUMENTS, name_operands as market_panel_helper_name_operands
DOCUMENTS.update(MARKET_PANEL_HELPER_DOCUMENTS)

from PanelHoverFacts import DOCUMENTS as PANEL_HOVER_DOCUMENTS, name_operands as panel_hover_name_operands
DOCUMENTS.update(PANEL_HOVER_DOCUMENTS)

from TradeNumericColumnFacts import LABELS as TRADE_NUMERIC_COLUMN_LABELS, DOCUMENTS as TRADE_NUMERIC_COLUMN_DOCUMENTS, name_operands as trade_numeric_column_name_operands
LABELS.update(TRADE_NUMERIC_COLUMN_LABELS)
DOCUMENTS.update(TRADE_NUMERIC_COLUMN_DOCUMENTS)

from SettingsParserFacts import LABELS as SETTINGS_PARSER_LABELS, DOCUMENTS as SETTINGS_PARSER_DOCUMENTS, name_operands as settings_parser_name_operands
LABELS.update(SETTINGS_PARSER_LABELS)
DOCUMENTS.update(SETTINGS_PARSER_DOCUMENTS)

from ScrollBodyClearFacts import LABELS as SCROLL_BODY_CLEAR_LABELS, DOCUMENTS as SCROLL_BODY_CLEAR_DOCUMENTS, name_operands as scroll_body_clear_name_operands
LABELS.update(SCROLL_BODY_CLEAR_LABELS)
DOCUMENTS.update(SCROLL_BODY_CLEAR_DOCUMENTS)

from ScrollWindowFacts import LABELS as SCROLL_WINDOW_LABELS, DOCUMENTS as SCROLL_WINDOW_DOCUMENTS, name_operands as scroll_window_name_operands
LABELS.update(SCROLL_WINDOW_LABELS)
DOCUMENTS.update(SCROLL_WINDOW_DOCUMENTS)

from TradePanelFacts import LABELS as TRADE_PANEL_LABELS, DOCUMENTS as TRADE_PANEL_DOCUMENTS, name_operands as trade_panel_name_operands
LABELS.update(TRADE_PANEL_LABELS)
DOCUMENTS.update(TRADE_PANEL_DOCUMENTS)

from ControlPanelGroupFacts import LABELS as CONTROL_PANEL_GROUP_LABELS, DOCUMENTS as CONTROL_PANEL_GROUP_DOCUMENTS, name_operands as control_panel_group_name_operands
LABELS.update(CONTROL_PANEL_GROUP_LABELS)
DOCUMENTS.update(CONTROL_PANEL_GROUP_DOCUMENTS)

from ShipPeriodicCodeFacts import DOCUMENTS as SHIP_PERIODIC_CODE_DOCUMENTS, name_operands as ship_periodic_code_name_operands
DOCUMENTS.update(SHIP_PERIODIC_CODE_DOCUMENTS)

from D3DClipFacts import LABELS as D3D_CLIP_LABELS, DOCUMENTS as D3D_CLIP_DOCUMENTS, name_operands as d3d_clip_name_operands
LABELS.update(D3D_CLIP_LABELS)
DOCUMENTS.update(D3D_CLIP_DOCUMENTS)

from D3DThirdFacts import LABELS as D3D_THIRD_LABELS, DOCUMENTS as D3D_THIRD_DOCUMENTS, name_operands as d3d_third_name_operands
LABELS.update(D3D_THIRD_LABELS)
DOCUMENTS.update(D3D_THIRD_DOCUMENTS)

from SpriteLineTableFacts import LABELS as SPRITE_LINE_TABLE_LABELS, DOCUMENTS as SPRITE_LINE_TABLE_DOCUMENTS, name_operands as sprite_line_table_name_operands
LABELS.update(SPRITE_LINE_TABLE_LABELS)
DOCUMENTS.update(SPRITE_LINE_TABLE_DOCUMENTS)

from D3DSetupFacts import LABELS as D3D_SETUP_LABELS, DOCUMENTS as D3D_SETUP_DOCUMENTS, name_operands as d3d_setup_name_operands
LABELS.update(D3D_SETUP_LABELS)
DOCUMENTS.update(D3D_SETUP_DOCUMENTS)

from PreviewFaceFillFacts import LABELS as PREVIEW_FACE_FILL_LABELS, DOCUMENTS as PREVIEW_FACE_FILL_DOCUMENTS, name_operands as preview_face_fill_name_operands
LABELS.update(PREVIEW_FACE_FILL_LABELS)
DOCUMENTS.update(PREVIEW_FACE_FILL_DOCUMENTS)

from D3DDescriptionFacts import LABELS as D3D_DESCRIPTION_LABELS, DOCUMENTS as D3D_DESCRIPTION_DOCUMENTS, name_operands as d3d_description_name_operands
LABELS.update(D3D_DESCRIPTION_LABELS)
DOCUMENTS.update(D3D_DESCRIPTION_DOCUMENTS)

from D3DPriceFacts import LABELS as D3D_PRICE_LABELS, DOCUMENTS as D3D_PRICE_DOCUMENTS, name_operands as d3d_price_name_operands
LABELS.update(D3D_PRICE_LABELS)
DOCUMENTS.update(D3D_PRICE_DOCUMENTS)

from ModelAvailabilityTable import name_operands as model_availability_name_operands

from ModelListPanelFacts import LABELS as MODEL_LIST_PANEL_LABELS, DOCUMENTS as MODEL_LIST_PANEL_DOCUMENTS, name_operands as model_list_panel_name_operands
LABELS.update(MODEL_LIST_PANEL_LABELS)
DOCUMENTS.update(MODEL_LIST_PANEL_DOCUMENTS)

from DescriptionBankFacts import LABELS as DESCRIPTION_BANK_LABELS, DOCUMENTS as DESCRIPTION_BANK_DOCUMENTS, name_operands as description_bank_name_operands
LABELS.update(DESCRIPTION_BANK_LABELS)
DOCUMENTS.update(DESCRIPTION_BANK_DOCUMENTS)

from DescriptionPanelFacts import LABELS as DESCRIPTION_PANEL_LABELS, DOCUMENTS as DESCRIPTION_PANEL_DOCUMENTS, name_operands as description_panel_name_operands
LABELS.update(DESCRIPTION_PANEL_LABELS)
DOCUMENTS.update(DESCRIPTION_PANEL_DOCUMENTS)

from DescriptionActionFacts import LABELS as DESCRIPTION_ACTION_LABELS, DOCUMENTS as DESCRIPTION_ACTION_DOCUMENTS, name_operands as description_action_name_operands
LABELS.update(DESCRIPTION_ACTION_LABELS)
DOCUMENTS.update(DESCRIPTION_ACTION_DOCUMENTS)

from PreviewHoverFacts import LABELS as PREVIEW_HOVER_LABELS, DOCUMENTS as PREVIEW_HOVER_DOCUMENTS, name_operands as preview_hover_name_operands
LABELS.update(PREVIEW_HOVER_LABELS)
DOCUMENTS.update(PREVIEW_HOVER_DOCUMENTS)

from PreviewActionFacts import LABELS as PREVIEW_ACTION_LABELS, DOCUMENTS as PREVIEW_ACTION_DOCUMENTS, name_operands as preview_action_name_operands
LABELS.update(PREVIEW_ACTION_LABELS)
DOCUMENTS.update(PREVIEW_ACTION_DOCUMENTS)

from PreviewMultiplyFacts import LABELS as PREVIEW_MULTIPLY_LABELS, DOCUMENTS as PREVIEW_MULTIPLY_DOCUMENTS, name_operands as preview_multiply_name_operands
LABELS.update(PREVIEW_MULTIPLY_LABELS)
DOCUMENTS.update(PREVIEW_MULTIPLY_DOCUMENTS)

from PreviewTransformFacts import LABELS as PREVIEW_TRANSFORM_LABELS, DOCUMENTS as PREVIEW_TRANSFORM_DOCUMENTS, name_operands as preview_transform_name_operands
LABELS.update(PREVIEW_TRANSFORM_LABELS)
DOCUMENTS.update(PREVIEW_TRANSFORM_DOCUMENTS)

from PreviewQueueFacts import LABELS as PREVIEW_QUEUE_LABELS, DOCUMENTS as PREVIEW_QUEUE_DOCUMENTS, name_operands as preview_queue_name_operands
LABELS.update(PREVIEW_QUEUE_LABELS)
DOCUMENTS.update(PREVIEW_QUEUE_DOCUMENTS)

from PreviewLookupProductFacts import LABELS as PREVIEW_LOOKUP_LABELS, DOCUMENTS as PREVIEW_LOOKUP_DOCUMENTS, name_operands as preview_lookup_name_operands
LABELS.update(PREVIEW_LOOKUP_LABELS)
DOCUMENTS.update(PREVIEW_LOOKUP_DOCUMENTS)

from PreviewBoundsFacts import LABELS as PREVIEW_BOUNDS_LABELS, DOCUMENTS as PREVIEW_BOUNDS_DOCUMENTS, name_operands as preview_bounds_name_operands
LABELS.update(PREVIEW_BOUNDS_LABELS)
DOCUMENTS.update(PREVIEW_BOUNDS_DOCUMENTS)

from PreviewQueueBuildFacts import LABELS as PREVIEW_QUEUE_BUILD_LABELS, DOCUMENTS as PREVIEW_QUEUE_BUILD_DOCUMENTS, name_operands as preview_queue_build_name_operands
LABELS.update(PREVIEW_QUEUE_BUILD_LABELS)
DOCUMENTS.update(PREVIEW_QUEUE_BUILD_DOCUMENTS)

from PreviewModelMatrixFacts import LABELS as PREVIEW_MODEL_MATRIX_LABELS, DOCUMENTS as PREVIEW_MODEL_MATRIX_DOCUMENTS, name_operands as preview_model_matrix_name_operands
LABELS.update(PREVIEW_MODEL_MATRIX_LABELS)
DOCUMENTS.update(PREVIEW_MODEL_MATRIX_DOCUMENTS)

from PreviewMatrixComposeFacts import LABELS as PREVIEW_MATRIX_COMPOSE_LABELS, DOCUMENTS as PREVIEW_MATRIX_COMPOSE_DOCUMENTS, name_operands as preview_matrix_compose_name_operands
LABELS.update(PREVIEW_MATRIX_COMPOSE_LABELS)
DOCUMENTS.update(PREVIEW_MATRIX_COMPOSE_DOCUMENTS)

from PreviewProjectionScaleFacts import LABELS as PREVIEW_PROJECTION_SCALE_LABELS, DOCUMENTS as PREVIEW_PROJECTION_SCALE_DOCUMENTS, name_operands as preview_projection_scale_name_operands
LABELS.update(PREVIEW_PROJECTION_SCALE_LABELS)
DOCUMENTS.update(PREVIEW_PROJECTION_SCALE_DOCUMENTS)

from PreviewPerspectiveFacts import LABELS as PREVIEW_PERSPECTIVE_LABELS, DOCUMENTS as PREVIEW_PERSPECTIVE_DOCUMENTS, name_operands as preview_perspective_name_operands
LABELS.update(PREVIEW_PERSPECTIVE_LABELS)
DOCUMENTS.update(PREVIEW_PERSPECTIVE_DOCUMENTS)

from PreviewVertexGroupFacts import LABELS as PREVIEW_VERTEX_GROUP_LABELS, DOCUMENTS as PREVIEW_VERTEX_GROUP_DOCUMENTS, name_operands as preview_vertex_group_name_operands
LABELS.update(PREVIEW_VERTEX_GROUP_LABELS)
DOCUMENTS.update(PREVIEW_VERTEX_GROUP_DOCUMENTS)

from PreviewVertexProductsFacts import LABELS as PREVIEW_VERTEX_PRODUCTS_LABELS, DOCUMENTS as PREVIEW_VERTEX_PRODUCTS_DOCUMENTS, name_operands as previewvertexproducts_name_operands
LABELS.update(PREVIEW_VERTEX_PRODUCTS_LABELS)
DOCUMENTS.update(PREVIEW_VERTEX_PRODUCTS_DOCUMENTS)

from PreviewModelWalkFacts import LABELS as PREVIEW_MODEL_WALK_LABELS, DOCUMENTS as PREVIEW_MODEL_WALK_DOCUMENTS, name_operands as previewmodelwalk_name_operands
LABELS.update(PREVIEW_MODEL_WALK_LABELS)
DOCUMENTS.update(PREVIEW_MODEL_WALK_DOCUMENTS)

from PreviewVertexClassFacts import LABELS as PREVIEW_VERTEX_CLASS_LABELS, DOCUMENTS as PREVIEW_VERTEX_CLASS_DOCUMENTS, name_operands as previewvertexclass_name_operands
LABELS.update(PREVIEW_VERTEX_CLASS_LABELS)
DOCUMENTS.update(PREVIEW_VERTEX_CLASS_DOCUMENTS)

from PreviewFaceMathFacts import LABELS as PREVIEW_FACE_MATH_LABELS, DOCUMENTS as PREVIEW_FACE_MATH_DOCUMENTS, name_operands as previewfacemath_name_operands
LABELS.update(PREVIEW_FACE_MATH_LABELS)
DOCUMENTS.update(PREVIEW_FACE_MATH_DOCUMENTS)

from PreviewFaceCodesFacts import LABELS as PREVIEW_FACE_CODES_LABELS, DOCUMENTS as PREVIEW_FACE_CODES_DOCUMENTS, name_operands as previewfacecodes_name_operands
LABELS.update(PREVIEW_FACE_CODES_LABELS)
DOCUMENTS.update(PREVIEW_FACE_CODES_DOCUMENTS)

from PreviewEdgeRasterFacts import LABELS as PREVIEW_EDGE_RASTER_LABELS, DOCUMENTS as PREVIEW_EDGE_RASTER_DOCUMENTS, name_operands as previewedgeraster_name_operands
LABELS.update(PREVIEW_EDGE_RASTER_LABELS)
DOCUMENTS.update(PREVIEW_EDGE_RASTER_DOCUMENTS)

from PreviewSlopeDivisionFacts import LABELS as PREVIEW_SLOPE_DIVISION_LABELS, DOCUMENTS as PREVIEW_SLOPE_DIVISION_DOCUMENTS, name_operands as previewslopedivision_name_operands
LABELS.update(PREVIEW_SLOPE_DIVISION_LABELS)
DOCUMENTS.update(PREVIEW_SLOPE_DIVISION_DOCUMENTS)

from PreviewPolygonRowsFacts import LABELS as PREVIEW_POLYGON_ROWS_LABELS, DOCUMENTS as PREVIEW_POLYGON_ROWS_DOCUMENTS, name_operands as previewpolygonrows_name_operands
LABELS.update(PREVIEW_POLYGON_ROWS_LABELS)
DOCUMENTS.update(PREVIEW_POLYGON_ROWS_DOCUMENTS)

from PreviewPolygonEdgesFacts import LABELS as PREVIEW_POLYGON_EDGES_LABELS, DOCUMENTS as PREVIEW_POLYGON_EDGES_DOCUMENTS, name_operands as previewpolygonedges_name_operands
LABELS.update(PREVIEW_POLYGON_EDGES_LABELS)
DOCUMENTS.update(PREVIEW_POLYGON_EDGES_DOCUMENTS)

from PreviewPolygonPreparationFacts import LABELS as PREVIEW_POLYGON_PREPARATION_LABELS, DOCUMENTS as PREVIEW_POLYGON_PREPARATION_DOCUMENTS, name_operands as previewpolygonpreparation_name_operands
LABELS.update(PREVIEW_POLYGON_PREPARATION_LABELS)
DOCUMENTS.update(PREVIEW_POLYGON_PREPARATION_DOCUMENTS)

from PreviewInsideFaceStreamFacts import LABELS as PREVIEW_INSIDE_FACE_STREAM_LABELS, DOCUMENTS as PREVIEW_INSIDE_FACE_STREAM_DOCUMENTS, name_operands as previewinsidefacestream_name_operands
LABELS.update(PREVIEW_INSIDE_FACE_STREAM_LABELS)
DOCUMENTS.update(PREVIEW_INSIDE_FACE_STREAM_DOCUMENTS)

from PreviewClipUnwindFacts import LABELS as PREVIEW_CLIP_UNWIND_LABELS, DOCUMENTS as PREVIEW_CLIP_UNWIND_DOCUMENTS, name_operands as previewclipunwind_name_operands
LABELS.update(PREVIEW_CLIP_UNWIND_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_UNWIND_DOCUMENTS)

from PreviewClipTailFacts import LABELS as PREVIEW_CLIP_TAIL_LABELS, DOCUMENTS as PREVIEW_CLIP_TAIL_DOCUMENTS, name_operands as previewcliptail_name_operands
LABELS.update(PREVIEW_CLIP_TAIL_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_TAIL_DOCUMENTS)

from PreviewClipProductDifferenceFacts import LABELS as PREVIEW_CLIP_PRODUCT_DIFFERENCES_LABELS, DOCUMENTS as PREVIEW_CLIP_PRODUCT_DIFFERENCES_DOCUMENTS, name_operands as previewclipproductdifferences_name_operands
LABELS.update(PREVIEW_CLIP_PRODUCT_DIFFERENCES_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_PRODUCT_DIFFERENCES_DOCUMENTS)

from PreviewClipProductBuilderFacts import LABELS as PREVIEW_CLIP_PRODUCT_BUILDERS_LABELS, DOCUMENTS as PREVIEW_CLIP_PRODUCT_BUILDERS_DOCUMENTS, name_operands as previewclipproductbuilders_name_operands
LABELS.update(PREVIEW_CLIP_PRODUCT_BUILDERS_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_PRODUCT_BUILDERS_DOCUMENTS)

from PreviewClipDivisionFacts import LABELS as PREVIEW_CLIP_DIVISION_LABELS, DOCUMENTS as PREVIEW_CLIP_DIVISION_DOCUMENTS, name_operands as previewclipdivision_name_operands
LABELS.update(PREVIEW_CLIP_DIVISION_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_DIVISION_DOCUMENTS)

from PreviewClipIntersectionFacts import LABELS as PREVIEW_CLIP_INTERSECTIONS_LABELS, DOCUMENTS as PREVIEW_CLIP_INTERSECTIONS_DOCUMENTS, name_operands as previewclipintersections_name_operands
LABELS.update(PREVIEW_CLIP_INTERSECTIONS_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_INTERSECTIONS_DOCUMENTS)

from PreviewClipCaseFacts import LABELS as PREVIEW_CLIP_CASES_LABELS, DOCUMENTS as PREVIEW_CLIP_CASES_DOCUMENTS, name_operands as previewclipcases_name_operands
LABELS.update(PREVIEW_CLIP_CASES_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_CASES_DOCUMENTS)

from PreviewClipDispatchFacts import LABELS as PREVIEW_CLIP_DISPATCH_LABELS, DOCUMENTS as PREVIEW_CLIP_DISPATCH_DOCUMENTS, name_operands as previewclipdispatch_name_operands
LABELS.update(PREVIEW_CLIP_DISPATCH_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_DISPATCH_DOCUMENTS)

from PreviewClipPolygonFacts import LABELS as PREVIEW_CLIP_POLYGON_LABELS, DOCUMENTS as PREVIEW_CLIP_POLYGON_DOCUMENTS, name_operands as previewclippolygon_name_operands
LABELS.update(PREVIEW_CLIP_POLYGON_LABELS)
DOCUMENTS.update(PREVIEW_CLIP_POLYGON_DOCUMENTS)

from PreviewClippedFaceStreamFacts import LABELS as PREVIEW_CLIPPED_FACE_STREAM_LABELS, DOCUMENTS as PREVIEW_CLIPPED_FACE_STREAM_DOCUMENTS, name_operands as previewclippedfacestream_name_operands
LABELS.update(PREVIEW_CLIPPED_FACE_STREAM_LABELS)
DOCUMENTS.update(PREVIEW_CLIPPED_FACE_STREAM_DOCUMENTS)

from PreviewQueueRenderFacts import LABELS as PREVIEW_QUEUE_RENDER_LABELS, DOCUMENTS as PREVIEW_QUEUE_RENDER_DOCUMENTS, name_operands as previewqueuerender_name_operands
LABELS.update(PREVIEW_QUEUE_RENDER_LABELS)
DOCUMENTS.update(PREVIEW_QUEUE_RENDER_DOCUMENTS)

from PreviewFrameFacts import LABELS as PREVIEW_FRAME_LABELS, DOCUMENTS as PREVIEW_FRAME_DOCUMENTS, name_operands as previewframe_name_operands
LABELS.update(PREVIEW_FRAME_LABELS)
DOCUMENTS.update(PREVIEW_FRAME_DOCUMENTS)

from ShipPreviewCallbackFacts import LABELS as SHIP_PREVIEW_CALLBACK_LABELS, DOCUMENTS as SHIP_PREVIEW_CALLBACK_DOCUMENTS, name_operands as ship_preview_callback_name_operands
LABELS.update(SHIP_PREVIEW_CALLBACK_LABELS)
DOCUMENTS.update(SHIP_PREVIEW_CALLBACK_DOCUMENTS)

from ShipModelActionFacts import LABELS as SHIPMODELACTIONSSTATION_LABELS, DOCUMENTS as SHIPMODELACTIONSSTATION_DOCUMENTS, name_operands as shipmodelactionsstation_name_operands
LABELS.update(SHIPMODELACTIONSSTATION_LABELS)
DOCUMENTS.update(SHIPMODELACTIONSSTATION_DOCUMENTS)

from HelpTextSelectorFacts import DOCUMENTS as HELP_TEXT_SELECTOR_DOCUMENTS, name_operands as help_text_selector_name_operands
DOCUMENTS.update(HELP_TEXT_SELECTOR_DOCUMENTS)

from HelpLineIndexFacts import DOCUMENTS as HELP_LINE_INDEX_DOCUMENTS, name_operands as help_line_index_name_operands
DOCUMENTS.update(HELP_LINE_INDEX_DOCUMENTS)

from HelpTextOutputFacts import DOCUMENTS as HELP_TEXT_OUTPUT_DOCUMENTS, name_operands as help_text_output_name_operands
DOCUMENTS.update(HELP_TEXT_OUTPUT_DOCUMENTS)

from StationHelpCallFacts import LABELS as STATIONHELPCALLS_LABELS, DOCUMENTS as STATIONHELPCALLS_DOCUMENTS, name_operands as stationhelpcalls_name_operands
LABELS.update(STATIONHELPCALLS_LABELS)
DOCUMENTS.update(STATIONHELPCALLS_DOCUMENTS)

from HelpPanelDrawFacts import LABELS as HELPPANELDRAWS_LABELS, DOCUMENTS as HELPPANELDRAWS_DOCUMENTS, name_operands as helppaneldraws_name_operands
LABELS.update(HELPPANELDRAWS_LABELS)
DOCUMENTS.update(HELPPANELDRAWS_DOCUMENTS)

from HelpPanelActionFacts import LABELS as HELPPANELACTIONS_LABELS, DOCUMENTS as HELPPANELACTIONS_DOCUMENTS, name_operands as helppanelactions_name_operands
LABELS.update(HELPPANELACTIONS_LABELS)
DOCUMENTS.update(HELPPANELACTIONS_DOCUMENTS)

from EquipmentInfoFacts import LABELS as EQUIPMENTINFO_LABELS, DOCUMENTS as EQUIPMENTINFO_DOCUMENTS, name_operands as equipmentinfo_name_operands
LABELS.update(EQUIPMENTINFO_LABELS)
DOCUMENTS.update(EQUIPMENTINFO_DOCUMENTS)

from KeyLabelFacts import LABELS as KEYLABEL_LABELS, DOCUMENTS as KEYLABEL_DOCUMENTS, name_operands as keylabel_name_operands
LABELS.update(KEYLABEL_LABELS)
DOCUMENTS.update(KEYLABEL_DOCUMENTS)

from SettingsRowPanelFacts import LABELS as SETTINGSROWPANELS_LABELS, DOCUMENTS as SETTINGSROWPANELS_DOCUMENTS, name_operands as settingsrowpanels_name_operands
LABELS.update(SETTINGSROWPANELS_LABELS)
DOCUMENTS.update(SETTINGSROWPANELS_DOCUMENTS)

from SettingsPanelActionFacts import LABELS as SETTINGSPANELACTIONS_LABELS, DOCUMENTS as SETTINGSPANELACTIONS_DOCUMENTS, name_operands as settingspanelactions_name_operands
LABELS.update(SETTINGSPANELACTIONS_LABELS)
DOCUMENTS.update(SETTINGSPANELACTIONS_DOCUMENTS)

from PackedWordAndActionReturnFacts import LABELS as PACKEDWORDANDACTIONRETURN_LABELS, DOCUMENTS as PACKEDWORDANDACTIONRETURN_DOCUMENTS, name_operands as packedwordandactionreturn_name_operands
LABELS.update(PACKEDWORDANDACTIONRETURN_LABELS)
DOCUMENTS.update(PACKEDWORDANDACTIONRETURN_DOCUMENTS)

from PassivePanelHoverFacts import LABELS as PASSIVEPANELHOVERS_LABELS, DOCUMENTS as PASSIVEPANELHOVERS_DOCUMENTS, name_operands as passivepanelhovers_name_operands
LABELS.update(PASSIVEPANELHOVERS_LABELS)
DOCUMENTS.update(PASSIVEPANELHOVERS_DOCUMENTS)

from HelpNewsOpeningFacts import LABELS as HELPNEWSOPENING_LABELS, DOCUMENTS as HELPNEWSOPENING_DOCUMENTS, name_operands as helpnewsopening_name_operands
LABELS.update(HELPNEWSOPENING_LABELS)
DOCUMENTS.update(HELPNEWSOPENING_DOCUMENTS)

from ModelTradeModeFacts import LABELS as MODELTRADEMODE_LABELS, DOCUMENTS as MODELTRADEMODE_DOCUMENTS, name_operands as modeltrademode_name_operands
LABELS.update(MODELTRADEMODE_LABELS)
DOCUMENTS.update(MODELTRADEMODE_DOCUMENTS)

from EquipmentTradeModeFacts import LABELS as EQUIPMENTTRADEMODE_LABELS, DOCUMENTS as EQUIPMENTTRADEMODE_DOCUMENTS, name_operands as equipmenttrademode_name_operands
LABELS.update(EQUIPMENTTRADEMODE_LABELS)
DOCUMENTS.update(EQUIPMENTTRADEMODE_DOCUMENTS)

from EquipmentListSetupFacts import LABELS as EQUIPMENTLISTSETUP_LABELS, DOCUMENTS as EQUIPMENTLISTSETUP_DOCUMENTS, name_operands as equipmentlistsetup_name_operands
LABELS.update(EQUIPMENTLISTSETUP_LABELS)
DOCUMENTS.update(EQUIPMENTLISTSETUP_DOCUMENTS)

from MapPanelOpeningFacts import LABELS as MAPPANELOPENING_LABELS, DOCUMENTS as MAPPANELOPENING_DOCUMENTS, name_operands as mappanelopening_name_operands
LABELS.update(MAPPANELOPENING_LABELS)
DOCUMENTS.update(MAPPANELOPENING_DOCUMENTS)

from WelcomePanelFacts import LABELS as WELCOMEPANEL_LABELS, DOCUMENTS as WELCOMEPANEL_DOCUMENTS, name_operands as welcomepanel_name_operands
LABELS.update(WELCOMEPANEL_LABELS)
DOCUMENTS.update(WELCOMEPANEL_DOCUMENTS)

from PassivePanelActionFacts import LABELS as PASSIVEPANELACTIONS_LABELS, DOCUMENTS as PASSIVEPANELACTIONS_DOCUMENTS, name_operands as passivepanelactions_name_operands
LABELS.update(PASSIVEPANELACTIONS_LABELS)
DOCUMENTS.update(PASSIVEPANELACTIONS_DOCUMENTS)

from EquipmentListPanelFacts import LABELS as EQUIPMENTLISTPANELS_LABELS, DOCUMENTS as EQUIPMENTLISTPANELS_DOCUMENTS, name_operands as equipmentlistpanels_name_operands
LABELS.update(EQUIPMENTLISTPANELS_LABELS)
DOCUMENTS.update(EQUIPMENTLISTPANELS_DOCUMENTS)

from EquipmentListHoverFacts import LABELS as EQUIPMENTLISTHOVER_LABELS, DOCUMENTS as EQUIPMENTLISTHOVER_DOCUMENTS, name_operands as equipmentlisthover_name_operands
LABELS.update(EQUIPMENTLISTHOVER_LABELS)
DOCUMENTS.update(EQUIPMENTLISTHOVER_DOCUMENTS)

from SaveSlotProtocolFacts import LABELS as SAVESLOTPROTOCOL_LABELS, DOCUMENTS as SAVESLOTPROTOCOL_DOCUMENTS, name_operands as saveslotprotocol_name_operands
LABELS.update(SAVESLOTPROTOCOL_LABELS)
DOCUMENTS.update(SAVESLOTPROTOCOL_DOCUMENTS)

from SaveSlotPanelFacts import LABELS as SAVESLOTPANELS_LABELS, DOCUMENTS as SAVESLOTPANELS_DOCUMENTS, name_operands as saveslotpanels_name_operands
LABELS.update(SAVESLOTPANELS_LABELS)
DOCUMENTS.update(SAVESLOTPANELS_DOCUMENTS)

from SystemMapActionFacts import LABELS as SYSTEMMAPACTION_LABELS, DOCUMENTS as SYSTEMMAPACTION_DOCUMENTS, name_operands as systemmapaction_name_operands
LABELS.update(SYSTEMMAPACTION_LABELS)
DOCUMENTS.update(SYSTEMMAPACTION_DOCUMENTS)

from ShipTradeActionFacts import LABELS as SHIPTRADEACTION_LABELS, DOCUMENTS as SHIPTRADEACTION_DOCUMENTS, name_operands as shiptradeaction_name_operands
LABELS.update(SHIPTRADEACTION_LABELS)
DOCUMENTS.update(SHIPTRADEACTION_DOCUMENTS)

from EquipmentListActionFacts import LABELS as EQUIPMENTLISTACTION_LABELS, DOCUMENTS as EQUIPMENTLISTACTION_DOCUMENTS, name_operands as equipmentlistaction_name_operands
LABELS.update(EQUIPMENTLISTACTION_LABELS)
DOCUMENTS.update(EQUIPMENTLISTACTION_DOCUMENTS)

from MissionPanelActionFacts import LABELS as MISSIONPANELACTIONS_LABELS, DOCUMENTS as MISSIONPANELACTIONS_DOCUMENTS, name_operands as missionpanelactions_name_operands
LABELS.update(MISSIONPANELACTIONS_LABELS)
DOCUMENTS.update(MISSIONPANELACTIONS_DOCUMENTS)

from ListHoverAdapterFacts import LABELS as LISTHOVERADAPTERS_LABELS, DOCUMENTS as LISTHOVERADAPTERS_DOCUMENTS, name_operands as listhoveradapters_name_operands
LABELS.update(LISTHOVERADAPTERS_LABELS)
DOCUMENTS.update(LISTHOVERADAPTERS_DOCUMENTS)

from DeferredActionAdapterFacts import LABELS as DEFERREDACTIONADAPTERS_LABELS, DOCUMENTS as DEFERREDACTIONADAPTERS_DOCUMENTS, name_operands as deferredactionadapters_name_operands
LABELS.update(DEFERREDACTIONADAPTERS_LABELS)
DOCUMENTS.update(DEFERREDACTIONADAPTERS_DOCUMENTS)

from TradeButtonActionFacts import LABELS as TRADEBUTTONACTIONS_LABELS, DOCUMENTS as TRADEBUTTONACTIONS_DOCUMENTS, name_operands as tradebuttonactions_name_operands
LABELS.update(TRADEBUTTONACTIONS_LABELS)
DOCUMENTS.update(TRADEBUTTONACTIONS_DOCUMENTS)

from FlightButtonFacts import LABELS as FLIGHTBUTTON_LABELS, DOCUMENTS as FLIGHTBUTTON_DOCUMENTS, name_operands as flightbutton_name_operands
LABELS.update(FLIGHTBUTTON_LABELS)
DOCUMENTS.update(FLIGHTBUTTON_DOCUMENTS)

from ContractMapFacts import LABELS as CONTRACTMAP_LABELS, DOCUMENTS as CONTRACTMAP_DOCUMENTS, name_operands as contractmap_name_operands
LABELS.update(CONTRACTMAP_LABELS)
DOCUMENTS.update(CONTRACTMAP_DOCUMENTS)

from CounterEventFacts import LABELS as COUNTEREVENT_LABELS, DOCUMENTS as COUNTEREVENT_DOCUMENTS, name_operands as counterevent_name_operands
LABELS.update(COUNTEREVENT_LABELS)
DOCUMENTS.update(COUNTEREVENT_DOCUMENTS)

from PanelOpenAdapterFacts import LABELS as PANELOPENADAPTERS_LABELS, DOCUMENTS as PANELOPENADAPTERS_DOCUMENTS, name_operands as panelopenadapters_name_operands
LABELS.update(PANELOPENADAPTERS_LABELS)
DOCUMENTS.update(PANELOPENADAPTERS_DOCUMENTS)

from StopMusicFacts import LABELS as STOPMUSIC_LABELS, DOCUMENTS as STOPMUSIC_DOCUMENTS, name_operands as stopmusic_name_operands
LABELS.update(STOPMUSIC_LABELS)
DOCUMENTS.update(STOPMUSIC_DOCUMENTS)

from StatusPanelActionFacts import LABELS as STATUSPANELACTION_LABELS, DOCUMENTS as STATUSPANELACTION_DOCUMENTS, name_operands as statuspanelaction_name_operands
LABELS.update(STATUSPANELACTION_LABELS)
DOCUMENTS.update(STATUSPANELACTION_DOCUMENTS)

from UnpackResourceFacts import LABELS as UNPACKRESOURCE_LABELS, DOCUMENTS as UNPACKRESOURCE_DOCUMENTS, name_operands as unpackresource_name_operands
LABELS.update(UNPACKRESOURCE_LABELS)
DOCUMENTS.update(UNPACKRESOURCE_DOCUMENTS)

from MainLoopExecutionFacts import LABELS as MAINLOOPEXECUTION_LABELS, DOCUMENTS as MAINLOOPEXECUTION_DOCUMENTS, name_operands as mainloopexecution_name_operands
LABELS.update(MAINLOOPEXECUTION_LABELS)
DOCUMENTS.update(MAINLOOPEXECUTION_DOCUMENTS)

from MusicEnvelopeStagingFacts import LABELS as MUSIC_ENVELOPE_LABELS, name_operands as music_envelope_name_operands
LABELS.update(MUSIC_ENVELOPE_LABELS)
DOCUMENTS.update({('Music',a):('MusicEnvelopeStaging','подготовка огибающей') for a in (0xDF47,0xDF70)})

from MusicEnvelopeCommandFacts import name_operands as music_envelope_command_name_operands
DOCUMENTS['Music',0xDB8C]=('MusicEnvelopeStaging','команда скольжения огибающей')

from MusicChannelAStagingFacts import LABELS as MUSICCHANNELASTAGING_LABELS, name_operands as musicchannelastaging_name_operands
LABELS.update(MUSICCHANNELASTAGING_LABELS)
DOCUMENTS.update({("Music",a):("MusicChannelStaging","отложенные состояния каналов") for a in (56976, 57006)})

from MusicChannelBStagingFacts import LABELS as MUSICCHANNELBSTAGING_LABELS, name_operands as musicchannelbstaging_name_operands
LABELS.update(MUSICCHANNELBSTAGING_LABELS)
DOCUMENTS.update({("Music",a):("MusicChannelStaging","отложенные состояния каналов") for a in (57118, 57137, 57148)})

from MusicChannelBRowFacts import LABELS as MUSICCHANNELBROW_LABELS, name_operands as musicchannelbrow_name_operands
LABELS.update(MUSICCHANNELBROW_LABELS)
DOCUMENTS.update({("Music",a):("MusicChannelStaging","отложенные состояния каналов") for a in (57017,)})

from MusicGateTickFacts import name_operands as music_gate_tick_name_operands

from MusicAyOutputFacts import name_operands as music_ay_output_name_operands
DOCUMENTS.update({("Music",a):("MusicAyOutput","огибающая и вывод AY") for a in (0xE2CB,0xE2EB,0xE37C)})
LABELS.update({('Music', 58061): 'StoreSlideDelay', ('Music', 58064): 'RestoreLevel', ('Music', 58065): 'UpdateGate', ('Music', 58088): 'StoreGateDelay', ('Music', 58122): 'StoreEnvDelay', ('Music', 58125): 'FlushAy', ('Music', 58275): 'PointE3A3', ('Music', 58281): 'PointE3A9', ('Music', 58298): 'PointE3BA', ('Music', 58332): 'PointE3DC', ('Music', 58340): 'PointE3E4', ('Music', 58351): 'PointE3EF', ('Music', 58353): 'PointE3F1', ('Music', 58360): 'PointE3F8', ('Music', 58372): 'PointE404', ('Music', 58387): 'PointE413', ('Music', 58395): 'PointE41B', ('Music', 58407): 'PointE427', ('Music', 58415): 'PointE42F'})

from MusicEffectFacts import name_operands as music_effect_name_operands
DOCUMENTS.update({("Music",a):("MusicEffects","отложенные музыкальные команды") for a in (58892, 58973, 58915, 58996, 59081, 58951, 58962, 59032, 59043, 59118, 59124, 56810, 56818, 59130)})

from MusicSynthesisFacts import LABELS as MUSIC_SYNTHESIS_LABELS, name_operands as music_synthesis_name_operands
LABELS.update(MUSIC_SYNTHESIS_LABELS)
DOCUMENTS.update({("Music",a):("MusicSynthesis","синтез трёх каналов") for a in (57315, 57549, 57581, 57805, 57837)})

from MusicChannelARowFacts import LABELS as MUSICCHANNELAROW_LABELS, name_operands as musicchannelarow_name_operands
LABELS.update(MUSICCHANNELAROW_LABELS)
DOCUMENTS.update({("Music",a):("MusicChannelStaging","отложенные состояния каналов") for a in (56863,)})

from MusicPatternFacts import name_operands as music_pattern_name_operands
DOCUMENTS.update({("Music", a): ("MusicPattern", "декодирование паттернов") for a in (58236, 58332, 58425, 58505, 58598, 58685, 58755)})
LABELS.update({('Music', 58275): 'SelectReset', ('Music', 58281): 'StoreReset', ('Music', 58298): 'AdvanceC', ('Music', 58340): 'SetVolume', ('Music', 58351): 'ReleaseNote', ('Music', 58353): 'StoreEnable', ('Music', 58360): 'EnvelopeOrDelay', ('Music', 58372): 'ReadEnvelope', ('Music', 58387): 'StoreEnvelope', ('Music', 58395): 'OrnamentSample', ('Music', 58407): 'EnvelopeSample', ('Music', 58415): 'StoreSample', ('Music', 58428): 'ReadCommand', ('Music', 58466): 'EnvelopeSample', ('Music', 58485): 'SampleOrEnd', ('Music', 58489): 'SetOrnament', ('Music', 58513): 'SetVolume', ('Music', 58524): 'ReleaseNote', ('Music', 58526): 'StoreEnable', ('Music', 58533): 'EnvelopeOrDelay', ('Music', 58545): 'ReadEnvelope', ('Music', 58560): 'StoreEnvelope', ('Music', 58568): 'OrnamentSample', ('Music', 58580): 'EnvelopeSample', ('Music', 58588): 'StoreSample', ('Music', 58601): 'ReadCommand', ('Music', 58641): 'SetNoise', ('Music', 58646): 'EnvelopeSample', ('Music', 58665): 'SampleOrEnd', ('Music', 58669): 'SetOrnament', ('Music', 58696): 'ReleaseNote', ('Music', 58704): 'ReadEnvelope', ('Music', 58719): 'StoreEnvelope', ('Music', 58724): 'OrnamentSample', ('Music', 58736): 'EnvelopeSample', ('Music', 58745): 'StoreSample', ('Music', 58758): 'ReadCommand', ('Music', 58802): 'EnvelopeOrDelay', ('Music', 58814): 'EnvelopeSample', ('Music', 58833): 'SampleOrEnd', ('Music', 58837): 'SetOrnament', ('Music', 58854): 'SetNote'})

from MusicAdvanceAFacts import LABELS as MUSICADVANCEA_LABELS, name_operands as musicadvancea_name_operands
LABELS.update(MUSICADVANCEA_LABELS)
DOCUMENTS.update({("Music",a):("MusicPattern","отложенные состояния каналов") for a in (57215,)})

from MusicInitializationFacts import LABELS as MUSIC_INITIALIZATION_LABELS, name_operands as music_initialization_name_operands
LABELS.update(MUSIC_INITIALIZATION_LABELS)
DOCUMENTS.update({("Music", a): ("MusicInitialization", "инициализация и глушение AY") for a in (0xDB00, 0xDB08, 0xDB0A, 0xDB7C)})

from ControlsTextQueueFacts import LABELS as CONTROLS_TEXT_QUEUE_LABELS, name_operands as controls_text_queue_name_operands
LABELS.update(CONTROLS_TEXT_QUEUE_LABELS)
DOCUMENTS.update({("Controls", a): ("TextQueueProducer", "производитель текстовой очереди") for a in (0xEC56, 0xEC59)})

from ActionTextQueueFacts import name_operands as action_text_queue_name_operands
DOCUMENTS.update({("Action", a): ("ActionTextQueueCalls", "межбанковые вызовы очереди") for a in (0x6000, 0x6040, 0x6054)})

from ControlsTextDisplayFacts import LABELS as CONTROLS_TEXT_DISPLAY_LABELS, name_operands as controls_text_display_name_operands
LABELS.update(CONTROLS_TEXT_DISPLAY_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsTextDisplay", "вывод текстового окна") for a in (0xEC0E, 0xECA2, 0xECF3, 0xED28, 0xEFC4, 0xEFF1)})

from ControlsBcdCounterFacts import LABELS as CONTROLS_BCD_COUNTER_LABELS, name_operands as controls_bcd_counter_name_operands
LABELS.update(CONTROLS_BCD_COUNTER_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsBcdCounter", "алгоритм и проверка") for a in (61709, 61762, 61832)})

from ControlsMarkerFacts import LABELS as CONTROLS_MARKER_LABELS, name_operands as controls_marker_name_operands
LABELS.update(CONTROLS_MARKER_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsMarker", "алгоритм и проверка") for a in (61588,)})

from ControlsBufferCopyFacts import LABELS as CONTROLS_BUFFER_COPY_LABELS, name_operands as controls_buffer_copy_name_operands
LABELS.update(CONTROLS_BUFFER_COPY_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsBufferCopy", "алгоритм и проверка") for a in (51312, 51330)})

from ControlsBufferPointsFacts import LABELS as CONTROLS_BUFFER_POINTS_LABELS, name_operands as controls_buffer_points_name_operands
LABELS.update(CONTROLS_BUFFER_POINTS_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsBufferPoints", "алгоритм и проверка") for a in (51853, 51891, 51939)})

from ActionBitmapTablesFacts import LABELS as ACTION_BITMAP_LABELS, name_operands as action_bitmap_name_operands
LABELS.update(ACTION_BITMAP_LABELS)
DOCUMENTS[("ActionBoot",0x43CF)] = ("ControlsBufferPoints","таблицы и XOR-точки")

from ControlsDivisionFacts import LABELS as CONTROLS_DIVISION_LABELS, name_operands as controls_division_name_operands
LABELS.update(CONTROLS_DIVISION_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsDivision", "алгоритм и проверка") for a in (53605, 53607)})

from ControlsSpanMasksFacts import LABELS as CONTROLS_SPAN_MASKS_LABELS, name_operands as controls_span_masks_name_operands
LABELS.update(CONTROLS_SPAN_MASKS_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsSpanMasks", "алгоритм и проверка") for a in (54549, 54588)})

from ControlsPointRespawnFacts import LABELS as CONTROLS_POINT_RESPAWN_LABELS, name_operands as controls_point_respawn_name_operands
LABELS.update(CONTROLS_POINT_RESPAWN_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsPointRespawn", "алгоритм и проверка") for a in (52758, 52829)})


ACTION_FIXED_OPERANDS = {
    0xF760: ('BIT 1,', 'BIT @ActionArrivalConst.RocketAttackBit,'),
    0x6B0D: ('#CEFA', '@Controls.ProjectAndDrawBody.Entry'),
    0x6C86: ('#CEFA', '@Controls.ProjectAndDrawBody.Entry'),
    0x6E1E: ('#FA3A', '@Voxel.DrawProjectedEffect.Entry'),
    **dict.fromkeys((0xE98D, 0xE9A1, 0xF729),
                    ('#A0C0', '@ActionObjectRecords.Record00 - @FActionRecord')),
    **dict.fromkeys((0x7246, 0x74AE, 0xEA77, 0xF4A9),
                    ('#A0C1', '@ActionObjectRecords.Record00.Components.Component0.High - @FActionRecord')),
}


def name_instruction(region, function_address, address, operation):
    """Уточнение одинаковых литералов с разным смыслом в конкретных инструкциях."""
    from ControlsPointMotionFacts import name_instruction as point_motion_instruction
    from ActionBank4Writes import name_instruction as action_material_instruction
    operation = confirmed_indexed_field_name_instruction(region, function_address, address, operation)
    operation = action_class3_link_count_name_operands_instruction(region, function_address, address, operation)
    operation = action_material_instruction(region, address, operation)
    if region == 'Action' and address in ACTION_FIXED_OPERANDS:
        operation = operation.replace(*ACTION_FIXED_OPERANDS[address])
    return point_motion_instruction(region, function_address, address, operation)

from ControlsPointMotionFacts import LABELS as CONTROLS_POINT_MOTION_LABELS, name_operands as controls_point_motion_name_operands
LABELS.update(CONTROLS_POINT_MOTION_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsPointMotion", "алгоритм и проверка") for a in (51968,)})

from ControlsEvenSpanFacts import LABELS as CONTROLS_EVEN_SPAN_LABELS, name_operands as controls_even_span_name_operands
LABELS.update(CONTROLS_EVEN_SPAN_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsEvenSpan", "алгоритм и проверка") for a in (52900, 52919, 52943)})

from ControlsInteriorRowsFacts import LABELS as CONTROLS_INTERIOR_ROWS_LABELS, name_operands as controls_interior_rows_name_operands
LABELS.update(CONTROLS_INTERIOR_ROWS_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsInteriorRows", "алгоритм и проверка") for a in (53768, 53777, 54651)})

from ControlsSquaresFacts import LABELS as CONTROLS_SQUARES_LABELS, name_operands as controls_squares_name_operands
LABELS.update(CONTROLS_SQUARES_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsSquares", "алгоритм и проверка") for a in (54027, 54793)})

from ControlsRasterStepFacts import LABELS as CONTROLS_RASTER_STEP_LABELS, name_operands as controls_raster_step_name_operands
LABELS.update(CONTROLS_RASTER_STEP_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsRasterStep", "алгоритм и проверка") for a in (55589, 55616)})

from ControlsPushSpansFacts import LABELS as CONTROLS_PUSH_SPANS_LABELS, name_operands as controls_push_spans_name_operands
LABELS.update(CONTROLS_PUSH_SPANS_LABELS)
DOCUMENTS.update({('Controls',a):('ControlsPushSpans','частичный разбор быстрой заливки') for a in (0xD633,0xD727,0xD833)})
DOCUMENTS['Controls',0xD314]=('ControlsCircleInterior','частичный разбор контура без горизонтального отсечения')

from ControlsComponentCompareFacts import LABELS as CONTROLS_COMPONENT_COMPARE_LABELS, name_operands as controls_component_compare_name_operands
LABELS.update(CONTROLS_COMPONENT_COMPARE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsComponentCompare", "алгоритм и проверка") for a in (55993,)})

from ControlsSmallMasksFacts import LABELS as CONTROLS_SMALL_MASKS_LABELS, name_operands as controls_small_masks_name_operands
LABELS.update(CONTROLS_SMALL_MASKS_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsSmallMasks", "алгоритм и проверка") for a in (55728,)})

from ControlsSmallBodiesFacts import LABELS as CONTROLS_SMALL_BODIES_LABELS, name_operands as controls_small_bodies_name_operands
LABELS.update(CONTROLS_SMALL_BODIES_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsSmallBodies", "алгоритм и проверка") for a in (55774,)})

from ControlsCircleSetupFacts import LABELS as CONTROLS_CIRCLE_SETUP_LABELS, name_operands as controls_circle_setup_name_operands
LABELS.update(CONTROLS_CIRCLE_SETUP_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsCircleSetup", "алгоритм и проверка") for a in (54532, 54636, 54475, 54500)})
DOCUMENTS[("Controls", 0xD501)] = ("ControlsCircleSetup", "вход UNFILLED")

from ControlsCircleSpanFacts import LABELS as CONTROLS_CIRCLE_SPAN_LABELS, name_operands as controls_circle_span_name_operands
LABELS.update(CONTROLS_CIRCLE_SPAN_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsCircleSpan", "алгоритм и проверка") for a in (54048,)})

from ControlsWordRandomFacts import LABELS as CONTROLS_WORD_RANDOM_LABELS, name_operands as controls_word_random_name_operands
LABELS.update(CONTROLS_WORD_RANDOM_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsWordRandom", "алгоритм и проверка") for a in (56669,)})

# Частичная нормализация N<=Q, имена и договоры остальных ветвей не объявляются доказанными.
DOCUMENTS.update({("Controls", a): ("ControlsRatioInside", "частичная нормализация отношения") for a in (0xCF0B, 0xD0CA, 0xD10A)})

from ActionRegionTypeFacts import LABELS as ACTION_REGION_TYPE_LABELS, name_operands as action_region_type_name_operands
LABELS.update(ACTION_REGION_TYPE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRegionType", "алгоритм и проверка") for a in (28203,)})

from ControlsSeededParametersFacts import LABELS as CONTROLS_SEEDED_PARAMETERS_LABELS, name_operands as controls_seeded_parameters_name_operands
LABELS.update(CONTROLS_SEEDED_PARAMETERS_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsSeededParameters", "алгоритм и проверка") for a in (56986,)})

from ControlsParameterTablesFacts import LABELS as CONTROLS_PARAMETER_TABLES_LABELS, name_operands as controls_parameter_tables_name_operands
LABELS.update(CONTROLS_PARAMETER_TABLES_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsParameterTables", "алгоритм и проверка") for a in (56848,)})

from ActionApplyParametersFacts import LABELS as ACTION_APPLY_PARAMETERS_LABELS, name_operands as action_apply_parameters_name_operands
LABELS.update(ACTION_APPLY_PARAMETERS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionApplyParameters", "алгоритм и проверка") for a in (44125,)})

from ActionParameterActivationFacts import LABELS as ACTION_PARAMETER_ACTIVATION_LABELS, name_operands as action_parameter_activation_name_operands
LABELS.update(ACTION_PARAMETER_ACTIVATION_LABELS)
DOCUMENTS.update({("Action", a): ("ActionParameterActivation", "алгоритм и проверка") for a in (44088, 44100)})

DOCUMENTS["Action", 0xAB1B] = ("ActionParameterActivation", "выбор страницы и активация параметров")

from ControlsParameterActivationFacts import LABELS as CONTROLS_PARAMETER_ACTIVATION_LABELS, name_operands as controls_parameter_activation_name_operands
LABELS.update(CONTROLS_PARAMETER_ACTIVATION_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsParameterActivation", "алгоритм и проверка") for a in (56842,)})

from ControlsThreeRowGlyphFacts import LABELS as CONTROLS_THREE_ROW_GLYPH_LABELS, name_operands as controls_three_row_glyph_name_operands
LABELS.update(CONTROLS_THREE_ROW_GLYPH_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsThreeRowGlyph", "алгоритм и проверка") for a in (57678,)})

from ControlsGlyphIndicatorsFacts import LABELS as CONTROLS_GLYPH_INDICATORS_LABELS, name_operands as controls_glyph_indicators_name_operands
LABELS.update(CONTROLS_GLYPH_INDICATORS_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsGlyphIndicators", "алгоритм и проверка") for a in (57377,)})

from ControlsRasterReturns import name_operands as controls_raster_returns_name_operands
LABELS["Controls", 0xE2BB] = "DispatchIndex"
DOCUMENTS["Controls", 0xE291] = ("ControlsRasterBackground", "частичный фон и выбор через RET")

from ControlsSixRowGaugeFacts import LABELS as CONTROLS_SIX_ROW_GAUGE_LABELS, name_operands as controls_six_row_gauge_name_operands
LABELS.update(CONTROLS_SIX_ROW_GAUGE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsSixRowGauge", "алгоритм и проверка") for a in (59645,)})

from ActionGaugeWrapperFacts import LABELS as ACTION_GAUGE_WRAPPER_LABELS, name_operands as action_gauge_wrapper_name_operands
LABELS.update(ACTION_GAUGE_WRAPPER_LABELS)
DOCUMENTS.update({("Action", a): ("ActionGaugeWrapper", "алгоритм и проверка") for a in (26169,)})

from ActionPreferredByteFacts import LABELS as ACTION_PREFERRED_BYTE_LABELS, name_operands as action_preferred_byte_name_operands
LABELS.update(ACTION_PREFERRED_BYTE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionPreferredByte", "алгоритм и проверка") for a in (29947,)})

from ActionPanelGaugesFacts import LABELS as ACTION_PANEL_GAUGES_LABELS, name_operands as action_panel_gauges_name_operands
LABELS.update(ACTION_PANEL_GAUGES_LABELS)
DOCUMENTS.update({("Action", a): ("ActionPanelGauges", "алгоритм и проверка") for a in (26185,)})

from ActionNearZeroWordFacts import LABELS as ACTION_NEAR_ZERO_WORD_LABELS, name_operands as action_near_zero_word_name_operands
LABELS.update(ACTION_NEAR_ZERO_WORD_LABELS)
DOCUMENTS.update({("Action", a): ("ActionNearZeroWord", "алгоритм и проверка") for a in (28332,)})

# Обработчики клавиш не доказаны, корневой фрагмент сохраняет Unknown.
DOCUMENTS['Action',0x6F1D]=('ActionKeyDispatchPrefix','частичный диспетчер и рамка')

DOCUMENTS['Action',0x6F4E]=('ActionKeyDispatchPrefix','рамка клавиатурного сканирования')

from ActionKeyScanTables import name_operands as action_key_scan_tables_name_operands
DOCUMENTS['Action',0x704B]=('ActionKeyDispatchPrefix','пустой обработчик клавиши')

from ActionMissileStockFacts import name_operands as action_missile_stock_name_operands
DOCUMENTS['Action',0x70ED]=('ActionMissileStock','выбор остатка ракет')

from ActionMissileLaunchFacts import name_operands as action_missile_launch_name_operands
DOCUMENTS.update({('Action',a):('ActionMissileLaunch','проверка перед пуском') for a in (0x709B,0x70A4)})

from ActionMissileConsumeFacts import name_operands as action_missile_consume_name_operands
DOCUMENTS['Action',0x70C6]=('ActionMissileConsume','списание ракет')

from ActionTypeDeltaFacts import name_operands as action_type_delta_name_operands
DOCUMENTS['Action',0x6380]=('ActionTypeDelta','табличная поправка')
LABELS.update({('Action', 25498): 'Action.ApplyIndexedDelta.ApplyDelta', ('Action', 25509): 'Action.ApplyIndexedDelta.ClampSign', ('Action', 25513): 'Action.ApplyIndexedDelta.CheckOld', ('Action', 25521): 'Action.ApplyIndexedDelta.StoreValue'})

from ActionRecordIndexFacts import name_operands as action_record_index_name_operands
DOCUMENTS.update({('Action',a):('ActionRecordIndex','коды и адреса записей') for a in (0xE6A7,0xE6B5,0xE6BE,0xE6C7)})

from ActionRecordSearchFacts import LABELS as ACTION_RECORD_SEARCH_LABELS, name_operands as action_record_search_name_operands
LABELS.update(ACTION_RECORD_SEARCH_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordSearch", "алгоритм и проверка") for a in (59809,)})

from ActionRecordIteratorFacts import LABELS as ACTION_RECORD_ITERATOR_LABELS, name_operands as action_record_iterator_name_operands
LABELS.update(ACTION_RECORD_ITERATOR_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordIterator", "алгоритм и проверка") for a in (59089, 59789)})

from ActionPatchSwapFacts import name_operands as action_patch_swap_name_operands
DOCUMENTS['Action',0xAD1D]=('ActionPatchSwap','обмен слов кода')

from ActionScaledMultiplyFacts import LABELS as ACTION_SCALED_MULTIPLY_LABELS, name_operands as action_scaled_multiply_name_operands
LABELS.update(ACTION_SCALED_MULTIPLY_LABELS)
DOCUMENTS.update({("Action", a): ("ActionScaledMultiply", "алгоритм и проверка") for a in (53548,)})

from ActionPatchedVectorFacts import name_operands as action_patched_vector_name_operands
DOCUMENTS['Action',0xAF43]=('ActionPatchedVector','три компоненты и арифметический SP')
LABELS.update({('Action', 44884): 'NextRow0Term', ('Action', 44898): 'SumRow0Part', ('Action', 44917): 'FinishRow0', ('Action', 44939): 'NextRow1Term', ('Action', 44954): 'SumRow1Part', ('Action', 44974): 'FinishRow1', ('Action', 44996): 'NextRow2Term', ('Action', 45011): 'SumRow2Part', ('Action', 45031): 'FinishRow2', ('Action', 45039): 'RestoreIX'})

from ActionVectorWrapperFacts import name_operands as action_vector_wrapper_name_operands
DOCUMENTS['Action',0xACEA]=('ActionVectorWrapper','транспонированная матрица и CPU-стек')
LABELS['Action',0xAD07]='Resume'

from ActionMissileCreationFacts import name_operands as action_missile_creation_name_operands
DOCUMENTS['Action',0x60AE]=('ActionMissileCreation','создание записи ракеты')
LABELS.update({('Action', 24760): 'LostTarget', ('Action', 24776): 'BuildComponents', ('Action', 24806): 'FindSlot', ('Action', 24817): 'InitializeSlot'})

from ActionMissileRequestsFacts import name_operands as action_missile_requests_name_operands
DOCUMENTS['Action',28748]=('ActionMissileRequests','запросы запуска ракет')
DOCUMENTS['Action',28765]=('ActionMissileRequests','запросы запуска ракет')
DOCUMENTS['Action',28789]=('ActionMissileRequests','запросы запуска ракет')
DOCUMENTS['Action',28808]=('ActionMissileRequests','запросы запуска ракет')

from ActionAyEffectsFacts import LABELS as ACTION_AY_EFFECTS_LABELS, name_operands as action_ay_effects_name_operands
LABELS.update(ACTION_AY_EFFECTS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionAyEffects", "алгоритм и проверка") for a in (60584,)})

from ActionRecordLinkEventFacts import LABELS as ACTION_RECORD_LINK_EVENT_LABELS, name_operands as action_record_link_event_name_operands
LABELS.update(ACTION_RECORD_LINK_EVENT_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordLinkEvent", "алгоритм и проверка") for a in (25435,)})

from ActionProjectedCaptureFacts import name_operands as action_projected_capture_name_operands
DOCUMENTS['Action',0xE30F]=('ActionProjectedCapture','локальная проверка допуска')
LABELS.update({('Action', 58147): 'TranslateY', ('Action', 58160): 'CheckY', ('Action', 58186): 'TranslateX', ('Action', 58199): 'CheckX'})

from ActionLogarithmTableFacts import name_operands as action_logarithm_table_name_operands
DOCUMENTS['ActionBoot',0x438F]=('ActionLogarithmTable','построение логарифма')
LABELS.update({('ActionBoot', 17307): 'NextEntry', ('ActionBoot', 17331): 'DivideBit', ('ActionBoot', 17341): 'QuotientBit'})

from ActionExponentialTableFacts import name_operands as action_exponential_table_name_operands
DOCUMENTS['ActionBoot',17237]=('ActionExponentialTable','формула таблицы')
LABELS.update({('ActionBoot', 17244): 'NextEntry', ('ActionBoot', 17250): 'StoreEntry', ('ActionBoot', 17265): 'MultiplyBit', ('ActionBoot', 17277): 'ShiftProduct'})

from ActionLogRatioFacts import LABELS as ACTION_LOG_RATIO_LABELS, name_operands as action_log_ratio_name_operands
LABELS.update(ACTION_LOG_RATIO_LABELS)
DOCUMENTS.update({("Action", a): ("ActionLogRatio", "алгоритм и проверка") for a in (44659,)})

from ActionObjectHeaderFacts import LABELS as ACTION_OBJECT_HEADER_LABELS, name_operands as action_object_header_name_operands
LABELS.update(ACTION_OBJECT_HEADER_LABELS)
DOCUMENTS.update({("Action", a): ("ActionObjectHeader", "алгоритм и проверка") for a in (43724,)})

from ActionScaleHeaderFacts import name_operands as action_scale_header_name_operands
DOCUMENTS['Action',0xE1B9]=('ActionScaleHeader','масштабирование заголовка')
LABELS['Action',0xE1C7]='SelectShifts'

from ActionProjectedBoundsFacts import name_operands as action_projected_bounds_name_operands
DOCUMENTS['Action',0xE299]=('ActionProjectedBounds','подготовка допуска и координат')
LABELS.update({('Action', 58018): 'CheckHighX', ('Action', 58032): 'CheckHighY', ('Action', 58095): 'StoreAbsX', ('Action', 58124): 'StoreAbsY'})

from ActionProjectionClipFacts import name_operands as action_projection_clip_name_operands
DOCUMENTS['Action',0xE213]=('ActionProjectionClip','граничный отбор')
LABELS.update({('Action', 57905): 'ScaleX', ('Action', 57962): 'ScaleY'})

from ActionVectorReverseFacts import name_operands as action_vector_reverse_name_operands
DOCUMENTS['Action',28382]=('ActionVectorReverse','алгоритм и проверка')
LABELS.update({})

from ActionStationTransferFacts import name_operands as action_station_transfer_name_operands
DOCUMENTS['Action',27876]=('ActionStationTransfer','алгоритм и проверка')
LABELS.update({})

from ActionCloseRecordFacts import name_operands as action_close_record_name_operands
DOCUMENTS['Action',58630]=('ActionCloseRecord','три входа обработки записи')
DOCUMENTS['Action',58655]=('ActionCloseRecord','три входа обработки записи')
DOCUMENTS['Action',58698]=('ActionCloseRecord','три входа обработки записи')
LABELS.update({('Action', 58669): 'CheckComp0', ('Action', 58681): 'CheckComp1', ('Action', 58693): 'CheckComp2'})

from ActionCloseBoundsFacts import LABELS as ACTION_CLOSE_BOUNDS_LABELS, name_operands as action_close_bounds_name_operands
LABELS.update(ACTION_CLOSE_BOUNDS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionCloseBounds", "алгоритм и проверка") for a in (57809,)})

from ActionAimFollowFacts import name_operands as action_aim_follow_name_operands
DOCUMENTS['Action',0xE36A]=('ActionAimFollow','сопровождение и цель')
LABELS.update({('Action', 58258): 'TranslateX', ('Action', 58271): 'TranslateY', ('Action', 58285): 'StepX', ('Action', 58297): 'StepY', ('Action', 58363): 'EncodeRecord'})

from ActionRenderQueueInsertFacts import LABELS as ACTION_RENDER_QUEUE_INSERT_LABELS, name_operands as action_render_queue_insert_name_operands
LABELS.update(ACTION_RENDER_QUEUE_INSERT_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRenderQueueInsert", "алгоритм и проверка") for a in (58383,)})

from ActionRenderContinuationFacts import name_operands as action_render_continuation_name_operands
DOCUMENTS['Action',58587]=('ActionRenderContinuation','алгоритм и проверка')
LABELS.update({('Action', 58618): 'PointE4FA', ('Action', 58621): 'PointE4FD'})

from ActionRenderQueueControlFacts import LABELS as ACTION_RENDER_QUEUE_CONTROL_LABELS, name_operands as action_render_queue_control_name_operands
LABELS.update(ACTION_RENDER_QUEUE_CONTROL_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRenderQueueControl", "алгоритм и проверка") for a in (58534, 58623)})

from ActionRenderCoefficientsFacts import name_operands as action_render_coefficients_name_operands
DOCUMENTS['Action',0xC99B]=('ActionRenderCoefficients','точные формулы коэффициентов')
LABELS.update({('Action', 51663): 'ThreePhases', ('Action', 51797): 'StoreCoeff12', ('Action', 51870): 'StoreCoeff22', ('Action', 51926): 'StoreCoeff13', ('Action', 51999): 'StoreCoeff23', ('Action', 51891): 'ScaleCoeff13', ('Action', 51939): 'ReadCoeff33Base'})

from ActionRenderMatrixFacts import LABELS as ACTION_RENDER_MATRIX_LABELS, name_operands as action_render_matrix_name_operands
LABELS.update(ACTION_RENDER_MATRIX_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRenderMatrix", "алгоритм и проверка") for a in (52003,)})

from ActionObjectCopyFacts import name_operands as action_object_copy_name_operands
DOCUMENTS['Action',43746]=('ActionObjectCopy','алгоритм и проверка')
LABELS.update({('Action', 43764): 'NextFixed', ('Action', 43779): 'FixedEnd', ('Action', 43781): 'NextVariable', ('Action', 43795): 'VariableEnd'})

from ActionPerspectiveFacts import name_operands as action_perspective_name_operands
DOCUMENTS['Action',55200]=('ActionPerspective','алгоритм и проверка')
LABELS.update({('Action', 55211): 'DepthShift', ('Action', 55238): 'FirstShift', ('Action', 55262): 'FirstMagnitude', ('Action', 55708): 'FirstQuotient', ('Action', 55721): 'FirstNegative', ('Action', 55736): 'SecondShift', ('Action', 55759): 'SecondMagnitude', ('Action', 56205): 'SecondQuotient', ('Action', 56223): 'SecondNegative', ('Action', 56232): 'RejectFirst', ('Action', 56243): 'RejectSecond', ('Action', 55371): 'FirstLead01', ('Action', 55377): 'FirstLead02', ('Action', 55383): 'FirstLead03', ('Action', 55389): 'FirstLead04', ('Action', 55395): 'FirstLead05', ('Action', 55401): 'FirstLead06', ('Action', 55407): 'FirstLead07', ('Action', 55413): 'FirstLead08', ('Action', 55419): 'FirstLead09', ('Action', 55426): 'FirstLead10', ('Action', 55432): 'FirstLead11', ('Action', 55438): 'FirstLead12', ('Action', 55444): 'FirstLead13', ('Action', 55450): 'FirstLead14', ('Action', 55456): 'FirstLead15', ('Action', 55462): 'FirstLead16', ('Action', 55470): 'FirstSplit01', ('Action', 55477): 'FirstSplit02', ('Action', 55484): 'FirstSplit03', ('Action', 55491): 'FirstSplit04', ('Action', 55498): 'FirstSplit05', ('Action', 55505): 'FirstSplit06', ('Action', 55512): 'FirstSplit07', ('Action', 55519): 'FirstSplit08', ('Action', 55526): 'FirstSplit09', ('Action', 55533): 'FirstSplit10', ('Action', 55540): 'FirstSplit11', ('Action', 55547): 'FirstSplit12', ('Action', 55554): 'FirstSplit13', ('Action', 55561): 'FirstSplit14', ('Action', 55568): 'FirstSplit15', ('Action', 55575): 'FirstLowDepth', ('Action', 55588): 'FirstRange15', ('Action', 55597): 'FirstBit14', ('Action', 55602): 'FirstKeep14', ('Action', 55605): 'FirstBit13', ('Action', 55610): 'FirstKeep13', ('Action', 55613): 'FirstBit12', ('Action', 55618): 'FirstKeep12', ('Action', 55621): 'FirstBit11', ('Action', 55626): 'FirstKeep11', ('Action', 55629): 'FirstBit10', ('Action', 55634): 'FirstKeep10', ('Action', 55637): 'FirstBit09', ('Action', 55642): 'FirstKeep09', ('Action', 55645): 'FirstBit08', ('Action', 55650): 'FirstKeep08', ('Action', 55653): 'FirstBit07', ('Action', 55658): 'FirstKeep07', ('Action', 55660): 'FirstBit06', ('Action', 55665): 'FirstKeep06', ('Action', 55667): 'FirstBit05', ('Action', 55672): 'FirstKeep05', ('Action', 55674): 'FirstBit04', ('Action', 55679): 'FirstKeep04', ('Action', 55681): 'FirstBit03', ('Action', 55686): 'FirstKeep03', ('Action', 55688): 'FirstBit02', ('Action', 55693): 'FirstKeep02', ('Action', 55695): 'FirstBit01', ('Action', 55700): 'FirstKeep01', ('Action', 55702): 'FirstBit00', ('Action', 55707): 'FirstKeep00', ('Action', 55868): 'SecondLead01', ('Action', 55874): 'SecondLead02', ('Action', 55880): 'SecondLead03', ('Action', 55886): 'SecondLead04', ('Action', 55892): 'SecondLead05', ('Action', 55898): 'SecondLead06', ('Action', 55904): 'SecondLead07', ('Action', 55910): 'SecondLead08', ('Action', 55916): 'SecondLead09', ('Action', 55923): 'SecondLead10', ('Action', 55929): 'SecondLead11', ('Action', 55935): 'SecondLead12', ('Action', 55941): 'SecondLead13', ('Action', 55947): 'SecondLead14', ('Action', 55953): 'SecondLead15', ('Action', 55959): 'SecondLead16', ('Action', 55967): 'SecondSplit01', ('Action', 55974): 'SecondSplit02', ('Action', 55981): 'SecondSplit03', ('Action', 55988): 'SecondSplit04', ('Action', 55995): 'SecondSplit05', ('Action', 56002): 'SecondSplit06', ('Action', 56009): 'SecondSplit07', ('Action', 56016): 'SecondSplit08', ('Action', 56023): 'SecondSplit09', ('Action', 56030): 'SecondSplit10', ('Action', 56037): 'SecondSplit11', ('Action', 56044): 'SecondSplit12', ('Action', 56051): 'SecondSplit13', ('Action', 56058): 'SecondSplit14', ('Action', 56065): 'SecondSplit15', ('Action', 56072): 'SecondLowDepth', ('Action', 56085): 'SecondRange15', ('Action', 56094): 'SecondBit14', ('Action', 56099): 'SecondKeep14', ('Action', 56102): 'SecondBit13', ('Action', 56107): 'SecondKeep13', ('Action', 56110): 'SecondBit12', ('Action', 56115): 'SecondKeep12', ('Action', 56118): 'SecondBit11', ('Action', 56123): 'SecondKeep11', ('Action', 56126): 'SecondBit10', ('Action', 56131): 'SecondKeep10', ('Action', 56134): 'SecondBit09', ('Action', 56139): 'SecondKeep09', ('Action', 56142): 'SecondBit08', ('Action', 56147): 'SecondKeep08', ('Action', 56150): 'SecondBit07', ('Action', 56155): 'SecondKeep07', ('Action', 56157): 'SecondBit06', ('Action', 56162): 'SecondKeep06', ('Action', 56164): 'SecondBit05', ('Action', 56169): 'SecondKeep05', ('Action', 56171): 'SecondBit04', ('Action', 56176): 'SecondKeep04', ('Action', 56178): 'SecondBit03', ('Action', 56183): 'SecondKeep03', ('Action', 56185): 'SecondBit02', ('Action', 56190): 'SecondKeep02', ('Action', 56192): 'SecondBit01', ('Action', 56197): 'SecondKeep01', ('Action', 56199): 'SecondBit00', ('Action', 56204): 'SecondKeep00'})

LABELS['Action',0xD9AA]='StoreFirst'

from ActionVertexGroupFacts import name_operands as action_vertex_group_name_operands
DOCUMENTS['Action',54932]=('ActionVertexGroup','алгоритм и проверка')
LABELS.update({('Action', 55065): 'NegatePair', ('Action', 55079): 'Single', ('Action', 55087): 'Masked', ('Action', 55097): 'Next1', ('Action', 55110): 'Next3', ('Action', 55123): 'Next2', ('Action', 55136): 'Next6', ('Action', 55149): 'Next7', ('Action', 55162): 'Next5', ('Action', 55175): 'Next4', ('Action', 55188): 'Finish'})

from ActionVertexProductsFacts import name_operands as action_vertex_products_name_operands
DOCUMENTS['Action',54777]=('ActionVertexProducts','алгоритм и проверка')
LABELS.update({})

from ActionObjectVerticesFacts import name_operands as action_object_vertices_name_operands
DOCUMENTS['Action',54729]=('ActionObjectVertices','алгоритм и проверка')
LABELS.update({('Action', 54757): 'NextGroup'})

from ActionVertexAbortFacts import name_operands as action_vertex_abort_name_operands
DOCUMENTS['Action',57072]=('ActionVertexAbort','алгоритм и проверка')
LABELS.update({})

from ActionVertexCodesFacts import name_operands as action_vertex_codes_name_operands
DOCUMENTS['Action',57075]=('ActionVertexCodes','алгоритм и проверка')
LABELS.update({('Action', 57087): 'NextPoint', ('Action', 57140): 'SecondNegative', ('Action', 57180): 'FirstHigh', ('Action', 57205): 'SecondHigh', ('Action', 57245): 'FirstNegative'})

from ActionListedCodesFacts import name_operands as action_listed_codes_name_operands
DOCUMENTS['Action',56785]=('ActionListedCodes','алгоритм и проверка')
LABELS.update({('Action', 56794): 'NextIndex', ('Action', 56811): 'ZeroCode'})

from ActionSignedMultiplyFacts import LABELS as ACTION_SIGNED_MULTIPLY_LABELS, name_operands as action_signed_multiply_name_operands
LABELS.update(ACTION_SIGNED_MULTIPLY_LABELS)
DOCUMENTS.update({("Action", a): ("ActionSignedMultiply", "алгоритм и проверка") for a in (50932,)})

from ActionFaceOrientationFacts import name_operands as action_face_orientation_name_operands
DOCUMENTS['Action',57270]=('ActionFaceOrientation','алгоритм и проверка')
LABELS.update({('Action', 57285): 'Alternate', ('Action', 57292): 'ReadPoints'})

from ActionSignedDivisionFacts import LABELS as ACTION_SIGNED_DIVISION_LABELS, name_operands as action_signed_division_name_operands
LABELS.update(ACTION_SIGNED_DIVISION_LABELS)
DOCUMENTS.update({("Action", a): ("ActionSignedDivision", "алгоритм и проверка") for a in (51340,)})

from ActionClipProductsFacts import LABELS as ACTION_CLIP_PRODUCTS_LABELS, name_operands as action_clip_products_name_operands
LABELS.update(ACTION_CLIP_PRODUCTS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClipProducts", "алгоритм и проверка") for a in (50295, 50326, 50357, 50388)})

from ActionClipIntersectionsFacts import LABELS as ACTION_CLIP_INTERSECTIONS_LABELS, name_operands as action_clip_intersections_name_operands
LABELS.update(ACTION_CLIP_INTERSECTIONS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClipIntersections", "алгоритм и проверка") for a in (50422, 50496, 50571, 50663)})

from ActionClipComparisonsFacts import LABELS as ACTION_CLIP_COMPARISONS_LABELS, name_operands as action_clip_comparisons_name_operands
LABELS.update(ACTION_CLIP_COMPARISONS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClipComparisons", "алгоритм и проверка") for a in (50797, 50817, 50837, 50857, 50877, 50888)})

from ActionClipPointWritersFacts import LABELS as ACTION_CLIP_POINT_WRITERS_LABELS, name_operands as action_clip_point_writers_name_operands
LABELS.update(ACTION_CLIP_POINT_WRITERS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClipPointWriters", "алгоритм и проверка") for a in (50753, 50764, 50775, 50786, 50899)})

from ActionClipCasesFacts import LABELS as ACTION_CLIP_CASES_LABELS, name_operands as action_clip_cases_name_operands
LABELS.update(ACTION_CLIP_CASES_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClipCases", "алгоритм и проверка") for a in (49274, 49275, 49290, 49301, 49316, 49327, 49342, 49353, 49368, 49379, 49385, 49391, 49409, 49433, 49451, 49458, 49476, 49482, 49488, 49506, 49524, 49531, 49549, 49573, 49579, 49597, 49615, 49622, 49628, 49649, 49676, 49704, 49711, 49742, 49753, 49759, 49780, 49805, 49833, 49854, 49865, 49872, 49903, 49928, 49934, 49940, 49958, 49976, 49982, 50009, 50030, 50037, 50065, 50076, 50097, 50128, 50134, 50159, 50166, 50194, 50225, 50232, 50253, 50278, 50289, 50419, 50493, 50568, 50660, 50922)})

from ActionPolygonFacts import LABELS as ACTION_POLYGON_LABELS, name_operands as action_polygon_name_operands
LABELS.update(ACTION_POLYGON_LABELS)
DOCUMENTS.update({("Action", a): ("ActionPolygon", "алгоритм и проверка") for a in (49152, 49265)})

from ActionSingleEdgeFacts import LABELS as ACTION_SINGLE_EDGE_LABELS, name_operands as action_single_edge_name_operands
LABELS.update(ACTION_SINGLE_EDGE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionSingleEdge", "алгоритм и проверка") for a in (51521,)})

from ActionLineRasterFacts import name_operands as action_line_raster_name_operands
DOCUMENTS['Action',56816]=('ActionLineRaster','алгоритм и проверка')
LABELS.update({('Action', 56842): 'OrderedY', ('Action', 56895): 'ApplyLeft', ('Action', 56898): 'LeftBoundary', ('Action', 56900): 'LeftError', ('Action', 56911): 'LeftByte', ('Action', 56917): 'LeftRow', ('Action', 56927): 'SteepLeft', ('Action', 56945): 'LeftDownPixel', ('Action', 56946): 'ApplyDownLeft', ('Action', 56956): 'LeftDownBound', ('Action', 56958): 'LeftDownNext', ('Action', 56964): 'LeftDownByte', ('Action', 56971): 'Rightward', ('Action', 56995): 'ApplyRight', ('Action', 56998): 'RightBoundary', ('Action', 57000): 'RightError', ('Action', 57011): 'RightByte', ('Action', 57017): 'RightRow', ('Action', 57027): 'SteepRight', ('Action', 57045): 'RightDownPixel', ('Action', 57046): 'ApplyDownRight', ('Action', 57056): 'RightDownBound', ('Action', 57058): 'RightDownNext', ('Action', 57064): 'RightDownByte', ('Action', 57068): 'RestoreStack'})

from ActionPolygonPreparationFacts import name_operands as action_polygon_preparation_name_operands
DOCUMENTS['Action',54545]=('ActionPolygonPreparation','алгоритм и проверка')
LABELS.update({('Action', 54563): 'ScanRows', ('Action', 54570): 'CheckMaximum', ('Action', 54575): 'NextVertex', ('Action', 54595): 'ScanLeftTop', ('Action', 54599): 'ReadLeftTop', ('Action', 54603): 'KeepLeftTop', ('Action', 54608): 'ScanRightTop', ('Action', 54613): 'NextRightTop', ('Action', 54615): 'ReadRightTop', ('Action', 54619): 'KeepRightTop'})

from ActionPolygonRowSelectionFacts import name_operands as action_polygon_row_selection_name_operands
DOCUMENTS['Action',54465]=('ActionPolygonRowSelection','алгоритм и проверка')
LABELS.update({('Action', 54479): 'FinishAtMax', ('Action', 54491): 'CompareEdges', ('Action', 54494): 'FinishAtLeft', ('Action', 54506): 'FinishAtRight'})

from ActionPolygonLeftEdgeFacts import name_operands as action_polygon_left_edge_name_operands
DOCUMENTS['Action',53874]=('ActionPolygonLeftEdge','алгоритм и проверка')
LABELS.update({('Action', 53882): 'PreviousRow', ('Action', 53886): 'ReadNextRow', ('Action', 54012): 'ExactPositive', ('Action', 54041): 'ShortPositive', ('Action', 54058): 'NegativeSlope', ('Action', 54150): 'CheckRightReady', ('Action', 54169): 'ShortNegative', ('Action', 53926): 'PositiveBit0', ('Action', 53933): 'PositiveBit1', ('Action', 53940): 'PositiveBit2', ('Action', 53947): 'PositiveBit3', ('Action', 53954): 'PositiveBit4', ('Action', 53961): 'PositiveBit5', ('Action', 53968): 'PositiveBit6', ('Action', 53975): 'PositiveBit7', ('Action', 54072): 'NegativeBit0', ('Action', 54079): 'NegativeBit1', ('Action', 54086): 'NegativeBit2', ('Action', 54093): 'NegativeBit3', ('Action', 54100): 'NegativeBit4', ('Action', 54107): 'NegativeBit5', ('Action', 54114): 'NegativeBit6', ('Action', 54121): 'NegativeBit7'})

from ActionPolygonRightShortStepFacts import name_operands as action_polygon_right_short_step_name_operands
DOCUMENTS['Action',54517]=('ActionPolygonRightShortStep','алгоритм и проверка')
LABELS.update({})

from ActionPolygonRightEdgeFacts import name_operands as action_polygon_right_edge_name_operands
DOCUMENTS['Action',54189]=('ActionPolygonRightEdge','алгоритм и проверка')
LABELS.update({('Action', 54197): 'NextRow', ('Action', 54204): 'ReadNextRow', ('Action', 54330): 'ExactPositive', ('Action', 54358): 'ShortPositive', ('Action', 54374): 'NegativeSlope', ('Action', 54245): 'PositiveBit0', ('Action', 54252): 'PositiveBit1', ('Action', 54259): 'PositiveBit2', ('Action', 54266): 'PositiveBit3', ('Action', 54273): 'PositiveBit4', ('Action', 54280): 'PositiveBit5', ('Action', 54287): 'PositiveBit6', ('Action', 54294): 'PositiveBit7', ('Action', 54389): 'NegativeBit0', ('Action', 54396): 'NegativeBit1', ('Action', 54403): 'NegativeBit2', ('Action', 54410): 'NegativeBit3', ('Action', 54417): 'NegativeBit4', ('Action', 54424): 'NegativeBit5', ('Action', 54431): 'NegativeBit6', ('Action', 54438): 'NegativeBit7'})

from ActionPolygonFillRowsFacts import name_operands as action_polygon_fill_rows_name_operands
DOCUMENTS['Action',53696]=('ActionPolygonFillRows','алгоритм и проверка')
LABELS.update({('Action', 53758): 'FinishWide', ('Action', 53769): 'AdvanceRow', ('Action', 53777): 'CorrectLeft', ('Action', 53786): 'KeepLeftError', ('Action', 53798): 'KeepRightError', ('Action', 53801): 'CheckRow', ('Action', 53805): 'DrawRow', ('Action', 53830): 'SameByte', ('Action', 53846): 'FlipNarrow', ('Action', 53853): 'CarryRow', ('Action', 53859): 'RestoreStack', ('Action', 53698): 'Span30', ('Action', 53700): 'Span29', ('Action', 53702): 'Span28', ('Action', 53704): 'Span27', ('Action', 53706): 'Span26', ('Action', 53708): 'Span25', ('Action', 53710): 'Span24', ('Action', 53712): 'Span23', ('Action', 53714): 'Span22', ('Action', 53716): 'Span21', ('Action', 53718): 'Span20', ('Action', 53720): 'Span19', ('Action', 53722): 'Span18', ('Action', 53724): 'Span17', ('Action', 53726): 'Span16', ('Action', 53728): 'Span15', ('Action', 53730): 'Span14', ('Action', 53732): 'Span13', ('Action', 53734): 'Span12', ('Action', 53736): 'Span11', ('Action', 53738): 'Span10', ('Action', 53740): 'Span9', ('Action', 53742): 'Span8', ('Action', 53744): 'Span7', ('Action', 53746): 'Span6', ('Action', 53748): 'Span5', ('Action', 53750): 'Span4', ('Action', 53752): 'Span3', ('Action', 53754): 'Span2', ('Action', 53756): 'Span1'})

from ActionPolygonSelectRightFacts import name_operands as action_polygon_select_right_name_operands
DOCUMENTS['Action',53864]=('ActionPolygonSelectRight','алгоритм и проверка')
LABELS.update({})

from ActionPolygonWrapLeftFacts import name_operands as action_polygon_wrap_left_name_operands
DOCUMENTS['Action',53867]=('ActionPolygonWrapLeft','алгоритм и проверка')
LABELS.update({})

from ActionPolygonWrapRightFacts import name_operands as action_polygon_wrap_right_name_operands
DOCUMENTS['Action',54184]=('ActionPolygonWrapRight','алгоритм и проверка')
LABELS.update({})

from ActionPolygonWrapLeftTopFacts import name_operands as action_polygon_wrap_left_top_name_operands
DOCUMENTS['Action',54531]=('ActionPolygonWrapLeftTop','алгоритм и проверка')
LABELS.update({})

from ActionPolygonWrapRightTopFacts import name_operands as action_polygon_wrap_right_top_name_operands
DOCUMENTS['Action',54538]=('ActionPolygonWrapRightTop','алгоритм и проверка')
LABELS.update({})

from ActionPolygonReturnFacts import name_operands as action_polygon_return_name_operands
DOCUMENTS['Action',54543]=('ActionPolygonReturn','алгоритм и проверка')
LABELS.update({})

from ActionPolygonFlowNames import name_operands as action_polygon_flow_names

from ActionPacketRendererFacts import name_operands as action_packet_renderer_name_operands
DOCUMENTS['Action',56611]=('ActionPacketRenderer','алгоритм и проверка')
LABELS.update({('Action', 56652): 'NextFacePoint', ('Action', 56674): 'RejectFace', ('Action', 56679): 'SkipRecord', ('Action', 56687): 'LineRecord', ('Action', 56700): 'PrepareLineMode', ('Action', 56719): 'SetClearMode', ('Action', 56727): 'SetOrMode', ('Action', 56732): 'StoreLineMode', ('Action', 56753): 'NextLinePoint'})

from ActionClippedPacketRendererFacts import name_operands as action_clipped_packet_renderer_name_operands
DOCUMENTS['Action',56253]=('ActionClippedPacketRenderer','алгоритм и проверка')
LABELS.update({('Action', 56309): 'NextFacePoint', ('Action', 56331): 'ClipFace', ('Action', 56340): 'RejectFace', ('Action', 56345): 'SkipRecord', ('Action', 56353): 'LineRecord', ('Action', 56366): 'PrepareLineMode', ('Action', 56385): 'SetClearMode', ('Action', 56393): 'SetOrMode', ('Action', 56398): 'StoreLineMode', ('Action', 56438): 'NextLinePoint', ('Action', 56531): 'DrawSegment', ('Action', 56534): 'NextSegment', ('Action', 56541): 'ClipSegment', ('Action', 56586): 'CopyClippedPair'})

from ActionQueuedObjectFacts import LABELS as ACTION_QUEUED_OBJECT_LABELS, name_operands as action_queued_object_name_operands
LABELS.update(ACTION_QUEUED_OBJECT_LABELS)
DOCUMENTS.update({("Action", a): ("ActionQueuedObject", "алгоритм и проверка") for a in (58587,)})

from ActionWorkBufferFacts import LABELS as ACTION_WORK_BUFFER_LABELS, name_operands as action_work_buffer_name_operands
LABELS.update(ACTION_WORK_BUFFER_LABELS)
DOCUMENTS.update({("Action", a): ("ActionWorkBuffer", "алгоритм и проверка") for a in (53514,)})

from ThreeDOverlayMirrorFacts import LABELS as THREED_OVERLAY_LABELS,name_operands as three_d_overlay_names
LABELS.update(THREED_OVERLAY_LABELS)
DOCUMENTS.update({("ThreeD",a):("ThreeDOverlayMirror","копия и границы доказательства") for a in (49152, 49265, 49274, 49275, 49290, 49301, 49316, 49327, 49342, 49353, 49368, 49379, 49385, 49391, 49409, 49433, 49451, 49458, 49476, 49482, 49488, 49506, 49524, 49531, 49549, 49573, 49579, 49597, 49615, 49622, 49628, 49649, 49676, 49704, 49711, 49742, 49753, 49759, 49780, 49805, 49833, 49854, 49865, 49872, 49903, 49928, 49934, 49940, 49958, 49976, 49982, 50009, 50030, 50037, 50065, 50076, 50097, 50128, 50134, 50159, 50166, 50194, 50225, 50232, 50253, 50278, 50289, 50295, 50326, 50357, 50388, 50419, 50422, 50493, 50496, 50568, 50571, 50660, 50663, 50753, 50764, 50775, 50786, 50797, 50817, 50837, 50857, 50877, 50888, 50899, 50922, 50932, 51340, 51521, 51611, 52003, 53000, 53514, 53548, 53696, 53864, 53867, 53874, 54184, 54189, 54465, 54517, 54531, 54538, 54543, 54545, 54729, 54777, 54932, 55200, 56253, 56611, 56785, 56816, 57072, 57075, 57270)})

DOCUMENTS["Intro", 0x692D] = ("IntroAttributeWriter", "писатель атрибутов")

from IntroTextureScaleFacts import LABELS as INTRO_TEXTURE_SCALE_LABELS, name_operands as intro_texture_scale_name_operands
LABELS.update(INTRO_TEXTURE_SCALE_LABELS)
DOCUMENTS["Intro", 0x6C21] = ("IntroTextureScale", "масштаб текстуры")

DOCUMENTS["Intro", 0x6827] = ("IntroScatter", "экранный перенос")
DOCUMENTS["Intro", 0x67F1] = ("IntroScatter", "экранный перенос")

from IntroPointerSamplerFacts import name_operands as intro_pointer_sampler_name_operands
from IntroPointerSamplerFacts import LABELS as INTRO_POINTER_SAMPLER_LABELS
LABELS.update(INTRO_POINTER_SAMPLER_LABELS)
DOCUMENTS['Intro', 27619] = ('IntroPointerSampler', "алгоритм и проверка")
DOCUMENTS['Intro', 27629] = ('IntroPointerSampler', "алгоритм и проверка")

from IntroScrolledSamplerFacts import name_operands as intro_scrolled_sampler_name_operands
from IntroScrolledSamplerFacts import LABELS as INTRO_SCROLLED_SAMPLER_LABELS
LABELS.update(INTRO_SCROLLED_SAMPLER_LABELS)
DOCUMENTS['Intro', 26338] = ('IntroScrolledSampler', "алгоритм и проверка")
DOCUMENTS['Intro', 26355] = ('IntroScrolledSampler', "алгоритм и проверка")

DOCUMENTS['Final', 24904] = ('FinalHalt', "алгоритм и проверка")

from ActionUnpackFacts import LABELS as ACTION_UNPACK_LABELS, name_operands as action_unpack_name_operands
LABELS.update(ACTION_UNPACK_LABELS)
DOCUMENTS.update({("Action", a): ("ActionUnpack", "алгоритм и проверка") for a in (43811,)})

from BootstrapRelocationFacts import name_operands as bootstrap_relocation_name_operands
DOCUMENTS['StationBoot', 25344] = ('BootstrapRelocation', "алгоритм и проверка")
DOCUMENTS['ActionBoot', 24576] = ('BootstrapRelocation', "алгоритм и проверка")

from IntroScreenFacts import name_operands as intro_screen_name_operands
from IntroScreenFacts import LABELS as INTRO_SCREEN_LABELS
LABELS.update(INTRO_SCREEN_LABELS)
DOCUMENTS['IntroUnpack', 28209] = ('IntroScreen', "алгоритм и проверка")

from IntroLookupTransferFacts import name_operands as intro_lookup_transfer_name_operands
DOCUMENTS['Intro', 27548] = ('IntroLookupTransfer', "алгоритм и проверка")

DOCUMENTS['Intro', 27155] = ('IntroWaitInterrupt', "алгоритм и проверка")

from IntroPresentAttributesFacts import name_operands as intro_present_attributes_name_operands
from IntroPresentAttributesFacts import LABELS as INTRO_PRESENT_ATTRIBUTES_LABELS
LABELS.update(INTRO_PRESENT_ATTRIBUTES_LABELS)
DOCUMENTS['Intro', 26788] = ('IntroPresentAttributes', "алгоритм и проверка")
DOCUMENTS['Intro', 27011] = ('IntroPresentAttributes', "алгоритм и проверка")

from IntroInterlacedFrameFacts import name_operands as intro_interlaced_frame_name_operands
from IntroInterlacedFrameFacts import LABELS as INTRO_INTERLACED_FRAME_LABELS
LABELS.update(INTRO_INTERLACED_FRAME_LABELS)
DOCUMENTS['Intro', 26609] = ('IntroInterlacedFrame', "алгоритм и проверка")
DOCUMENTS['Intro', 26663] = ('IntroInterlacedFrame', "алгоритм и проверка")

from IntroLookupContinuationFacts import name_operands as intro_lookup_continuation_name_operands
DOCUMENTS['Intro', 27580] = ('IntroLookupContinuation', "алгоритм и проверка")

from ActionFoldedRandomFacts import LABELS as ACTION_FOLDED_RANDOM_LABELS, name_operands as action_folded_random_name_operands
LABELS.update(ACTION_FOLDED_RANDOM_LABELS)
DOCUMENTS.update({("Action", a): ("ActionFoldedRandom", "алгоритм и проверка") for a in (60424, 60274, 60295, 60344)})

from ActionRandomClusterFacts import name_operands as action_random_cluster_name_operands
DOCUMENTS.update({("Action",a): ("ActionFoldedRandom", "генератор и все потоки") for a in (60281, 60288, 60302, 60309, 60316, 60323, 60330, 60337, 60351, 60358, 60365, 60372)})

from ActionRecordReuseFacts import LABELS as ACTION_RECORD_REUSE_LABELS, name_operands as action_record_reuse_name_operands
LABELS.update(ACTION_RECORD_REUSE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordReuse", "алгоритм и проверка") for a in (62356,)})

from ActionOffsetRestoreFacts import LABELS as ACTION_OFFSET_RESTORE_LABELS, name_operands as action_offset_restore_name_operands
LABELS.update(ACTION_OFFSET_RESTORE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionOffsetRestore", "алгоритм и проверка") for a in (59013,)})

from ActionRecordSelectionFacts import name_operands as action_record_selection_name_operands
DOCUMENTS['Action',59038]=('ActionRecordSelection','алгоритм и проверка')
LABELS.update({})

from ActionRecordScaleFacts import LABELS as ACTION_RECORD_SCALE_LABELS, name_operands as action_record_scale_name_operands
LABELS.update(ACTION_RECORD_SCALE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordScale", "алгоритм и проверка") for a in (58716,)})

from ActionIYRecordReuseFacts import name_operands as actioniy_record_reuse_name_operands
DOCUMENTS['Action',61501]=('ActionIYRecordReuse','алгоритм и проверка')
LABELS.update({})

from ActionClassReuseFacts import name_operands as action_class_reuse_name_operands
DOCUMENTS['Action',58975]=('ActionClassReuse','алгоритм и проверка')
LABELS.update({('Action', 58996): 'ScanNext'})

from ActionRejectRecordFacts import LABELS as ACTION_REJECT_RECORD_LABELS, name_operands as action_reject_record_name_operands
LABELS.update(ACTION_REJECT_RECORD_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRejectRecord", "алгоритм и проверка") for a in (58968,)})

from ActionRecordWarningReturnFacts import name_operands as action_record_warning_return_name_operands
DOCUMENTS['Action',58965]=('ActionRecordWarningReturn','алгоритм и проверка')
LABELS.update({})

from ActionRecordUpdateFacts import LABELS as ACTION_RECORD_UPDATE_LABELS, name_operands as action_record_update_name_operands
LABELS.update(ACTION_RECORD_UPDATE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordUpdate", "алгоритм и проверка") for a in (58784,)})

from ActionRecordBaseResetFacts import LABELS as ACTION_RECORD_BASE_RESET_LABELS, name_operands as action_record_base_reset_name_operands
LABELS.update(ACTION_RECORD_BASE_RESET_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordBaseReset", "алгоритм и проверка") for a in (62834,)})

from ActionClass14ReuseFacts import LABELS as ACTION_CLASS14_REUSE_LABELS, name_operands as action_class14_reuse_name_operands
LABELS.update(ACTION_CLASS14_REUSE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClass14Reuse", "алгоритм и проверка") for a in (24946,)})

from ActionBankedBufferInitFacts import LABELS as ACTION_BANKED_BUFFER_INIT_LABELS, name_operands as action_banked_buffer_init_name_operands
LABELS.update(ACTION_BANKED_BUFFER_INIT_LABELS)
DOCUMENTS.update({("Action", a): ("ActionBankedBufferInit", "алгоритм и проверка") for a in (27862,)})

from ActionThirdGlyphPublishFacts import LABELS as ACTION_THIRD_GLYPH_PUBLISH_LABELS, name_operands as action_third_glyph_publish_name_operands
LABELS.update(ACTION_THIRD_GLYPH_PUBLISH_LABELS)
DOCUMENTS.update({("Action", a): ("ActionThirdGlyphPublish", "алгоритм и проверка") for a in (27828,)})

from ActionThirdGlyphStackFacts import name_operands as action_third_glyph_stack_name_operands
DOCUMENTS['Action',27825]=('ActionThirdGlyphStack','алгоритм и проверка')
LABELS.update({})

from ActionThirdGlyphVectorFacts import LABELS as ACTION_THIRD_GLYPH_VECTOR_LABELS, name_operands as action_third_glyph_vector_name_operands
LABELS.update(ACTION_THIRD_GLYPH_VECTOR_LABELS)
DOCUMENTS.update({("Action", a): ("ActionThirdGlyphVector", "алгоритм и проверка") for a in (27791,)})

from ActionCachedRootFacts import LABELS as ACTION_CACHED_ROOT_LABELS, name_operands as action_cached_root_name_operands
LABELS.update(ACTION_CACHED_ROOT_LABELS)
DOCUMENTS.update({("Action", a): ("ActionCachedRoot", "алгоритм и проверка") for a in (44360, 45289)})

from ActionComponentEncodingFacts import LABELS as ACTION_COMPONENT_ENCODING_LABELS, name_operands as action_component_encoding_name_operands
LABELS.update(ACTION_COMPONENT_ENCODING_LABELS)
DOCUMENTS.update({("Action", a): ("ActionComponentEncoding", "алгоритм и проверка") for a in (27715,)})

from ActionComponentStackFacts import name_operands as action_component_stack_name_operands
DOCUMENTS['Action',27712]=('ActionComponentStack','алгоритм и проверка')
LABELS.update({})

from ActionComponentTransformFacts import LABELS as ACTION_COMPONENT_TRANSFORM_LABELS, name_operands as action_component_transform_name_operands
LABELS.update(ACTION_COMPONENT_TRANSFORM_LABELS)
DOCUMENTS.update({("Action", a): ("ActionComponentTransform", "алгоритм и проверка") for a in (27647, 27673)})

from ControlsProjectionAlgorithmFacts import LABELS as CONTROLS_PROJECTION_ALGORITHM_LABELS, name_operands as controls_projection_algorithm_name_operands
LABELS.update(CONTROLS_PROJECTION_ALGORITHM_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsBodyProjection", "алгоритм и проверка") for a in (53003, 53450, 53514)})

from ControlsProjectionGateFacts import LABELS as CONTROLS_PROJECTION_GATE_LABELS, name_operands as controls_projection_gate_name_operands
LABELS.update(CONTROLS_PROJECTION_GATE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsProjectionGate", "алгоритм и проверка") for a in (55647,)})

from ActionClassDispatchFacts import LABELS as ACTION_CLASS_DISPATCH_LABELS, name_operands as action_class_dispatch_name_operands
LABELS.update(ACTION_CLASS_DISPATCH_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClassDispatch", "алгоритм и проверка") for a in (25823,)})

from ActionLinkOverrideFacts import name_operands as action_link_override_name_operands
DOCUMENTS['Action',26155]=('ActionLinkOverride','алгоритм и проверка')
LABELS.update({})

from ActionRecordsExcept6And7Facts import name_operands as action_records_except6_and7_name_operands
DOCUMENTS['Action',59149]=('ActionRecordsExcept6And7','алгоритм и проверка')
LABELS.update({('Action', 59156): 'ScanNext', ('Action', 59172): 'IndexRecord'})

from ActionRecords6Or7Facts import name_operands as action_records6_or7_name_operands
DOCUMENTS['Action',59177]=('ActionRecords6Or7','алгоритм и проверка')
LABELS.update({('Action', 59184): 'ScanNext', ('Action', 59200): 'IndexRecord'})

from ActionRecords5Or14Facts import name_operands as action_records5_or14_name_operands
DOCUMENTS['Action',59205]=('ActionRecords5Or14','алгоритм и проверка')
LABELS.update({('Action', 59212): 'ScanNext', ('Action', 59228): 'IndexRecord'})

from ActionRandomFilteredRecordFacts import name_operands as action_random_filtered_record_name_operands
DOCUMENTS['Action',59106]=('ActionRandomFilteredRecord','алгоритм и проверка')
LABELS.update({('Action', 59124): 'ScanNext', ('Action', 59144): 'IndexRecord'})

from ActionClass9LinkFacts import name_operands as action_class9_link_name_operands
DOCUMENTS['Action',26054]=('ActionClass9Link','алгоритм и проверка')
LABELS.update({('Action', 26065): 'ResetLink'})

from ActionIgnoredClassesFacts import name_operands as action_ignored_classes_name_operands
DOCUMENTS['Action',25892]=('ActionIgnoredClasses','алгоритм и проверка')
LABELS.update({})

from ActionClass0LinkFacts import name_operands as action_class0_link_name_operands
DOCUMENTS['Action',26126]=('ActionClass0Link','алгоритм и проверка')
LABELS.update({('Action', 26138): 'SelectLink'})

from ActionPreferredApplyFacts import name_operands as action_preferred_apply_name_operands
DOCUMENTS['Action',62807]=('ActionPreferredApply','алгоритм и проверка')
LABELS.update({})

from ActionPreferredChanceFacts import name_operands as action_preferred_chance_name_operands
DOCUMENTS['Action',62759]=('ActionPreferredChance','алгоритм и проверка')
LABELS.update({})

from ActionPreferredZeroBridgeFacts import name_operands as action_preferred_zero_bridge_name_operands
DOCUMENTS['Action',62783]=('ActionPreferredZeroBridge','алгоритм и проверка')
LABELS.update({})

from ActionPreferredSevenBridgeFacts import name_operands as action_preferred_seven_bridge_name_operands
DOCUMENTS['Action',62795]=('ActionPreferredSevenBridge','алгоритм и проверка')
LABELS.update({})

from ActionPreferredDispatchFacts import LABELS as ACTION_PREFERRED_DISPATCH_LABELS, name_operands as action_preferred_dispatch_name_operands
LABELS.update(ACTION_PREFERRED_DISPATCH_LABELS)
DOCUMENTS.update({("Action", a): ("ActionPreferredRecord", "алгоритм и проверка") for a in (62750, 62773, 62785, 62797)})

from ActionAbsSigned32Facts import LABELS as ACTION_ABS_SIGNED32_LABELS, name_operands as action_abs_signed32_name_operands
LABELS.update(ACTION_ABS_SIGNED32_LABELS)
DOCUMENTS.update({("Action", a): ("ActionAbsSigned32", "алгоритм и проверка") for a in (32630,)})

from ActionContextWordPairsFacts import LABELS as ACTION_CONTEXT_WORD_PAIRS_LABELS, name_operands as action_context_word_pairs_name_operands
LABELS.update(ACTION_CONTEXT_WORD_PAIRS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionContextWordPairs", "алгоритм и проверка") for a in (27014,)})

from ActionVectorHighMaximumFacts import LABELS as ACTION_VECTOR_HIGH_MAXIMUM_LABELS, name_operands as action_vector_high_maximum_name_operands
LABELS.update(ACTION_VECTOR_HIGH_MAXIMUM_LABELS)
DOCUMENTS.update({("Action", a): ("ActionVectorHighMaximum", "алгоритм и проверка") for a in (27036,)})

from ActionSignedRatioCodeFacts import LABELS as ACTION_SIGNED_RATIO_CODE_LABELS, name_operands as action_signed_ratio_code_name_operands
LABELS.update(ACTION_SIGNED_RATIO_CODE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionSignedRatioCode", "алгоритм и проверка") for a in (44580,)})

from ActionHalfDeltaCodesFacts import LABELS as ACTION_HALF_DELTA_CODES_LABELS, name_operands as action_half_delta_codes_name_operands
LABELS.update(ACTION_HALF_DELTA_CODES_LABELS)
DOCUMENTS.update({("Action", a): ("ActionHalfDeltaCodes", "алгоритм и проверка") for a in (44378,)})

from ActionRecordCodeStepFacts import LABELS as ACTION_RECORD_CODE_STEP_LABELS, name_operands as action_record_code_step_name_operands
LABELS.update(ACTION_RECORD_CODE_STEP_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordCodeStep", "алгоритм и проверка") for a in (25189,)})

from ActionClass3LinkCountFacts import LABELS as ACTION_CLASS3_LINK_COUNT_LABELS, name_operands as action_class3_link_count_name_operands
LABELS.update(ACTION_CLASS3_LINK_COUNT_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClass3LinkCount", "алгоритм и проверка") for a in (25295,)})

from ActionClass3LinkCountFacts import name_instruction as action_class3_link_count_name_operands_instruction

from ActionFoldedNearWordsFacts import LABELS as ACTION_FOLDED_NEAR_WORDS_LABELS, name_operands as action_folded_near_words_name_operands
LABELS.update(ACTION_FOLDED_NEAR_WORDS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionFoldedNearWords", "алгоритм и проверка") for a in (27177,)})

from ActionClampVectorWordsFacts import LABELS as ACTION_CLAMP_VECTOR_WORDS_LABELS, name_operands as action_clamp_vector_words_name_operands
LABELS.update(ACTION_CLAMP_VECTOR_WORDS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionClampVectorWords", "алгоритм и проверка") for a in (32526,)})

from ActionWideTargetStepFacts import LABELS as ACTION_WIDE_TARGET_STEP_LABELS, name_operands as action_wide_target_step_name_operands
LABELS.update(ACTION_WIDE_TARGET_STEP_LABELS)
DOCUMENTS.update({("Action", a): ("ActionWideTargetStep", "алгоритм и проверка") for a in (32439,)})

from ActionNearVectorSearchFacts import LABELS as ACTION_NEAR_VECTOR_SEARCH_LABELS, name_operands as action_near_vector_search_name_operands
LABELS.update(ACTION_NEAR_VECTOR_SEARCH_LABELS)
DOCUMENTS.update({("Action", a): ("ActionNearVectorSearch", "алгоритм и проверка") for a in (27070,)})

from ActionSelectWideTargetFacts import LABELS as ACTION_SELECT_WIDE_TARGET_LABELS, name_operands as action_select_wide_target_name_operands
LABELS.update(ACTION_SELECT_WIDE_TARGET_LABELS)
DOCUMENTS.update({("Action", a): ("ActionSelectWideTarget", "алгоритм и проверка") for a in (32413,)})

from ActionControlDecayFacts import LABELS as ACTION_CONTROL_DECAY_LABELS, name_operands as action_control_decay_name_operands
LABELS.update(ACTION_CONTROL_DECAY_LABELS)
DOCUMENTS.update({("Action", a): ("ActionControlDecay", "алгоритм и проверка") for a in (28501,)})

from ActionKeyTurnNegativeFacts import name_operands as action_key_turn_negative_name_operands
DOCUMENTS['Action',30407]=('ActionKeyTurnNegative','алгоритм и проверка')
LABELS.update({('Action', 30435): 'CheckLimit'})

from ActionKeyTurnPositiveFacts import name_operands as action_key_turn_positive_name_operands
DOCUMENTS['Action',30442]=('ActionKeyTurnPositive','алгоритм и проверка')
LABELS.update({('Action', 30470): 'CheckLimit'})

from ActionKeyXNegativeFacts import name_operands as action_keyx_negative_name_operands
DOCUMENTS['Action',30477]=('ActionKeyXNegative','алгоритм и проверка')
LABELS.update({('Action', 30505): 'CheckLimit'})

from ActionKeyXPositiveFacts import name_operands as action_keyx_positive_name_operands
DOCUMENTS['Action',30512]=('ActionKeyXPositive','алгоритм и проверка')
LABELS.update({('Action', 30540): 'CheckLimit'})

from ActionKeyYNegativeFacts import name_operands as action_keyy_negative_name_operands
DOCUMENTS['Action',30547]=('ActionKeyYNegative','алгоритм и проверка')
LABELS.update({('Action', 30575): 'CheckLimit'})

from ActionKeyYPositiveFacts import name_operands as action_keyy_positive_name_operands
DOCUMENTS['Action',30582]=('ActionKeyYPositive','алгоритм и проверка')
LABELS.update({('Action', 30610): 'CheckLimit'})

from ActionKeyGaugeIncreaseFacts import name_operands as action_key_gauge_increase_name_operands
DOCUMENTS['Action',30336]=('ActionKeyGaugeIncrease','алгоритм и проверка')
LABELS.update({})

from ActionKeyGaugeDecreaseFacts import name_operands as action_key_gauge_decrease_name_operands
DOCUMENTS['Action',30371]=('ActionKeyGaugeDecrease','алгоритм и проверка')
LABELS.update({('Action', 30395): 'SubtractStep'})

from ActionBankedCallbackReturnFacts import name_operands as action_banked_callback_return_name_operands
DOCUMENTS['Action',27904]=('ActionBankedCallbackReturn','алгоритм и проверка')
LABELS.update({})

from ActionBankedCallbackFacts import LABELS as ACTION_BANKED_CALLBACK_LABELS, name_operands as action_banked_callback_name_operands
LABELS.update(ACTION_BANKED_CALLBACK_LABELS)
DOCUMENTS.update({("Action", a): ("ActionBankedCallback", "алгоритм и проверка") for a in (27887,)})

from ControlsCircleInteriorFullFacts import LABELS as CONTROLS_CIRCLE_INTERIOR_FULL_LABELS, name_operands as controls_circle_interior_full_name_operands
LABELS.update(CONTROLS_CIRCLE_INTERIOR_FULL_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsCircleInteriorFull", "алгоритм и проверка") for a in (54036,)})

from ControlsCircleHalfFacts import LABELS as CONTROLS_CIRCLE_HALF_LABELS, name_operands as controls_circle_half_name_operands
LABELS.update(CONTROLS_CIRCLE_HALF_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsCircleHalf", "алгоритм и проверка") for a in (53727, 53748)})

from ControlsStationRelocationFacts import LABELS as CONTROLS_STATION_RELOCATION_LABELS, name_operands as controls_station_relocation_name_operands
LABELS.update(CONTROLS_STATION_RELOCATION_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsStationRelocation", "алгоритм и проверка") for a in (56475,)})

from ControlsStationPrepareFacts import LABELS as CONTROLS_STATION_PREPARE_LABELS, name_operands as controls_station_prepare_name_operands
LABELS.update(CONTROLS_STATION_PREPARE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsStationPrepare", "алгоритм и проверка") for a in (56547,)})

from ControlsClippedCircleHalfFacts import LABELS as CONTROLS_CLIPPED_CIRCLE_HALF_LABELS, name_operands as controls_clipped_circle_half_name_operands
LABELS.update(CONTROLS_CLIPPED_CIRCLE_HALF_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsClippedCircleHalf", "алгоритм и проверка") for a in (53645, 53666, 53686, 53707)})

from ControlsCircleKernelsFacts import LABELS as CONTROLS_CIRCLE_KERNELS_LABELS, name_operands as controls_circle_kernels_name_operands
LABELS.update(CONTROLS_CIRCLE_KERNELS_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsCircleKernels", "алгоритм и проверка") for a in (54835, 55079, 55099, 55347)})

from ActionSubtractWorkVectorFacts import LABELS as ACTION_SUBTRACT_WORK_VECTOR_LABELS, name_operands as action_subtract_work_vector_name_operands
LABELS.update(ACTION_SUBTRACT_WORK_VECTOR_LABELS)
DOCUMENTS.update({("Action", a): ("ActionSubtractWorkVector", "алгоритм и проверка") for a in (26322,)})

from ActionRefreshPanelFacts import LABELS as ACTION_REFRESH_PANEL_LABELS, name_operands as action_refresh_panel_name_operands
LABELS.update(ACTION_REFRESH_PANEL_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRefreshPanel", "алгоритм и проверка") for a in (24901,)})

from ControlsVerticalCircleSliceFacts import LABELS as CONTROLS_VERTICAL_CIRCLE_SLICE_LABELS, name_operands as controls_vertical_circle_slice_name_operands
LABELS.update(CONTROLS_VERTICAL_CIRCLE_SLICE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsVerticalCircleSlice", "алгоритм и проверка") for a in (54405,)})

from ControlsHorizontalCircleFacts import LABELS as CONTROLS_HORIZONTAL_CIRCLE_LABELS, name_operands as controls_horizontal_circle_name_operands
LABELS.update(CONTROLS_HORIZONTAL_CIRCLE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsHorizontalCircle", "алгоритм и проверка") for a in (54234,)})

from ControlsCornerCircleSliceFacts import LABELS as CONTROLS_CORNER_CIRCLE_SLICE_LABELS, name_operands as controls_corner_circle_slice_name_operands
LABELS.update(CONTROLS_CORNER_CIRCLE_SLICE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsCornerCircleSlice", "алгоритм и проверка") for a in (54276,)})

from ControlsFullWidthCircleFacts import LABELS as CONTROLS_FULL_WIDTH_CIRCLE_LABELS, name_operands as controls_full_width_circle_name_operands
LABELS.update(CONTROLS_FULL_WIDTH_CIRCLE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsFullWidthCircle", "алгоритм и проверка") for a in (54080, 54156)})

from ControlsLargeCircleFacts import LABELS as CONTROLS_LARGE_CIRCLE_LABELS, name_operands as controls_large_circle_name_operands
LABELS.update(CONTROLS_LARGE_CIRCLE_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsCircleDispatch", "алгоритм и проверка") for a in (53814,)})

from ControlsBodyDrawFacts import LABELS as CONTROLS_BODY_DRAW_LABELS, name_operands as controls_body_draw_name_operands
LABELS.update(CONTROLS_BODY_DRAW_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsBodyDraw", "алгоритм и проверка") for a in (53786, 53810)})

from ControlsProjectDrawBodyFacts import LABELS as CONTROLS_PROJECT_DRAW_BODY_LABELS, name_operands as controls_project_draw_body_name_operands
LABELS.update(CONTROLS_PROJECT_DRAW_BODY_LABELS)
DOCUMENTS.update({("Controls", a): ("ProjectedBodyEntry", "алгоритм и проверка") for a in (52986,)})

from ActionDrawBankedBodyFacts import LABELS as ACTION_DRAW_BANKED_BODY_LABELS, name_operands as action_draw_banked_body_name_operands
LABELS.update(ACTION_DRAW_BANKED_BODY_LABELS)
DOCUMENTS.update({("Action", a): ("ProjectedBodyEntry", "алгоритм и проверка") for a in (27774,)})

from ActionRestoreBodyStackFacts import name_operands as action_restore_body_stack_name_operands
DOCUMENTS['Action',27309]=('ActionRestoreBodyStack','алгоритм и проверка')
LABELS.update({})

from ActionBodyTransformFacts import LABELS as ACTION_BODY_TRANSFORM_LABELS, name_operands as action_body_transform_name_operands
LABELS.update(ACTION_BODY_TRANSFORM_LABELS)
DOCUMENTS.update({("Action", a): ("ActionPrepareBodyTransform", "алгоритм и проверка") for a in (27246, 27312)})

from ActionObjectOffsetRiseFacts import name_operands as action_object_offset_rise_name_operands
DOCUMENTS['Action',61309]=('ActionObjectOffsetRise','алгоритм и проверка')
LABELS.update({})

from ActionObjectOffsetFallFacts import name_operands as action_object_offset_fall_name_operands
DOCUMENTS['Action',61338]=('ActionObjectOffsetFall','алгоритм и проверка')
LABELS.update({})

from ActionObjectPhaseWaitFacts import name_operands as action_object_phase_wait_name_operands
DOCUMENTS['Action',61365]=('ActionObjectPhaseWait','алгоритм и проверка')
LABELS.update({('Action', 61391): 'FoldX', ('Action', 61399): 'SaveX', ('Action', 61408): 'SaveY', ('Action', 61417): 'CompareY', ('Action', 61421): 'CompareX', ('Action', 61425): 'CheckLimit', ('Action', 61430): 'ResumeState'})

from ActionObjectOffsetTransferFacts import name_operands as action_object_offset_transfer_name_operands
DOCUMENTS['Action',61688]=('ActionObjectOffsetTransfer','алгоритм и проверка')
LABELS.update({('Action', 61725): 'StoreCounter', ('Action', 61746): 'LoadPhase'})

from ActionObjectOffsetVectorFacts import name_operands as action_object_offset_vector_name_operands
DOCUMENTS['Action',27910]=('ActionObjectOffsetVector','алгоритм и проверка')
LABELS.update({('Action', 27927): 'Store0', ('Action', 27941): 'Store1', ('Action', 27954): 'Store2'})

from ActionObjectOffsetCoefficientsFacts import name_operands as action_object_offset_coefficients_name_operands
DOCUMENTS['Action',45124]=('ActionObjectOffsetCoefficients','алгоритм и проверка')
LABELS.update({('Action', 45229): 'StoreSecond', ('Action', 45285): 'StoreThird'})

from ActionClass18StateFacts import LABELS as ACTION_CLASS18_STATE_LABELS, name_operands as action_class18_state_name_operands
LABELS.update(ACTION_CLASS18_STATE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionObjectStateDispatch", "алгоритм и проверка") for a in (61557,)})

from ActionVisualEffectResumeFacts import name_operands as action_visual_effect_resume_name_operands
DOCUMENTS['Action',28113]=('ActionVisualEffectResume','алгоритм и проверка')
LABELS.update({})

from ActionWideProjectionLoopFacts import LABELS as ACTION_WIDE_PROJECTION_LOOP_LABELS, name_operands as action_wide_projection_loop_name_operands
LABELS.update(ACTION_WIDE_PROJECTION_LOOP_LABELS)
DOCUMENTS.update({("Action", a): ("ActionWideProjectionInput", "алгоритм и проверка") for a in (27414,)})

from ActionBankedBasisRotationFacts import LABELS as ACTION_BANKED_BASIS_ROTATION_LABELS, name_operands as action_banked_basis_rotation_name_operands
LABELS.update(ACTION_BANKED_BASIS_ROTATION_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRenderFrameSetup", "алгоритм и проверка") for a in (44471,)})

from ActionNonemptyRenderFrameFacts import LABELS as ACTION_NONEMPTY_RENDER_FRAME_LABELS, name_operands as action_nonempty_render_frame_name_operands
LABELS.update(ACTION_NONEMPTY_RENDER_FRAME_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRenderFrameSetup", "алгоритм и проверка") for a in (57376,)})

from ActionLargeEffectContinuationFacts import name_operands as action_large_effect_continuation_name_operands
DOCUMENTS['Action',59965]=('ActionLargeEffectContinuation','алгоритм и проверка')
LABELS.update({('Action', 60015): 'CheckClass', ('Action', 60032): 'SaveCount', ('Action', 60036): 'FindSlot', ('Action', 60128): 'ReleaseObject'})

from ActionLargeEffectEntryFacts import LABELS as ACTION_LARGE_EFFECT_ENTRY_LABELS, name_operands as action_large_effect_entry_name_operands
LABELS.update(ACTION_LARGE_EFFECT_ENTRY_LABELS)
DOCUMENTS.update({("Action", a): ("ActionLargeEffectEntry", "алгоритм и проверка") for a in (59945,)})

from ActionRecordEffectResumeFacts import name_operands as action_record_effect_resume_name_operands
DOCUMENTS['Action',63423]=('ActionRecordEffectResume','алгоритм и проверка')
LABELS.update({})

from ActionRecordEffectThresholdFacts import LABELS as ACTION_RECORD_EFFECT_THRESHOLD_LABELS, name_operands as action_record_effect_threshold_name_operands
LABELS.update(ACTION_RECORD_EFFECT_THRESHOLD_LABELS)
DOCUMENTS.update({("Action", a): ("ActionRecordEffectResume", "алгоритм и проверка") for a in (63378,)})

from ActionObjectStateReturnFacts import LABELS as ACTION_OBJECT_STATE_RETURN_LABELS, name_operands as action_object_state_return_name_operands
LABELS.update(ACTION_OBJECT_STATE_RETURN_LABELS)
DOCUMENTS.update({("Action", a): ("ActionObjectStateDispatch", "алгоритм и проверка") for a in (63430,)})

from ActionNoiseExitFacts import LABELS as ACTION_NOISE_EXIT_LABELS, name_operands as action_noise_exit_name_operands
LABELS.update(ACTION_NOISE_EXIT_LABELS)
DOCUMENTS.update({("Action", a): ("ActionNoiseExit", "алгоритм и проверка") for a in (24660,)})

from ActionBodyModeTransitionFacts import LABELS as ACTION_BODY_MODE_TRANSITION_LABELS, name_operands as action_body_mode_transition_name_operands
LABELS.update(ACTION_BODY_MODE_TRANSITION_LABELS)
DOCUMENTS.update({("Action", a): ("ActionBodyModeTransition", "алгоритм и проверка") for a in (26407,)})

from ActionBodyMotionFacts import LABELS as ACTION_BODY_MOTION_LABELS, name_operands as action_body_motion_name_operands
LABELS.update(ACTION_BODY_MOTION_LABELS)
DOCUMENTS.update({("Action", a): ("ActionWideMotionPrefix", "алгоритм и проверка") for a in (26496,)})

from ControlsTargetOverlayFacts import LABELS as CONTROLS_TARGET_OVERLAY_LABELS, name_operands as controls_target_overlay_name_operands
LABELS.update(CONTROLS_TARGET_OVERLAY_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsTargetOverlay", "алгоритм и проверка") for a in (59770,)})

from ActionMotionWithoutKeysFacts import LABELS as ACTION_MOTION_WITHOUT_KEYS_LABELS, name_operands as action_motion_without_keys_name_operands
LABELS.update(ACTION_MOTION_WITHOUT_KEYS_LABELS)
DOCUMENTS.update({("Action", a): ("ActionMotionVectorTail", "алгоритм и проверка") for a in (28268, 28445)})

from ControlsRadarLoopFacts import LABELS as CONTROLS_RADAR_LOOP_LABELS, name_operands as controls_radar_loop_name_operands
LABELS.update(CONTROLS_RADAR_LOOP_LABELS)
DOCUMENTS.update({("Controls", a): ("ControlsRasterBackground", "алгоритм и проверка") for a in (58001,)})

from ActionVisualEffectListFacts import LABELS as ACTION_VISUAL_EFFECT_LIST_LABELS, name_operands as action_visual_effect_list_name_operands
LABELS.update(ACTION_VISUAL_EFFECT_LIST_LABELS)
DOCUMENTS.update({("Action", a): ("ActionVisualEffectWalk", "алгоритм и проверка") for a in (27960, 28113)})

from ActionSpawnRecordFinishFacts import LABELS as ACTION_SPAWN_RECORD_FINISH_LABELS, name_operands as action_spawn_record_finish_name_operands
LABELS.update(ACTION_SPAWN_RECORD_FINISH_LABELS)
DOCUMENTS.update({("Action", a): ("ActionSpawnRecordFinish", "алгоритм и проверка") for a in (32212,)})

from ActionSpawnScheduleFacts import LABELS as ACTION_SPAWN_SCHEDULE_LABELS, name_operands as action_spawn_schedule_name_operands
LABELS.update(ACTION_SPAWN_SCHEDULE_LABELS)
DOCUMENTS.update({("Action", a): ("ActionSpawnSchedule", "алгоритм и проверка") for a in (30809, 31576)})

from ActionOverlayProjectionFacts import name_operands as action_overlay_projection_name_operands
DOCUMENTS['Action',44485]=('ActionOverlayProjection','алгоритм и проверка')
LABELS.update({('Action', 44498): 'DivideVertical', ('Action', 44516): 'CenterVertical', ('Action', 44536): 'DivideHoriz', ('Action', 44554): 'CenterHoriz', ('Action', 44561): 'Reject'})

from ConfirmedCallTargets import name_operands as confirmed_call_target_name_operands
from InternalLabelNames import LABELS as VERIFIED_INTERNAL_LABELS
LABELS.update(VERIFIED_INTERNAL_LABELS)

from ConfirmedIndexedFields import name_instruction as confirmed_indexed_field_name_instruction

from ActionDiagnosticQueueFacts import name_operands as action_diagnostic_queue_name_operands
DOCUMENTS['Action',44203]=('ActionDiagnosticQueue','алгоритм и проверка')
LABELS.update({})

from ActionDeltaRatioFacts import name_operands as action_delta_ratio_name_operands
DOCUMENTS['Action',44565]=('ActionDeltaRatio','алгоритм и проверка')
LABELS.update({})

from IntroPhysicalParameters import name_operands as intro_physical_parameter_name_operands

from ActionBootFileKeys import name_operands as action_boot_file_key_name_operands

from ActionDirectDecimalScrollFacts import name_operands as action_direct_decimal_scroll_name_operands
DOCUMENTS['Action',24592]=('ActionDirectDecimalScroll','алгоритм и проверка')
LABELS.update({})

from ActionDirectDecimalPlainFacts import name_operands as action_direct_decimal_plain_name_operands
DOCUMENTS['Action',24617]=('ActionDirectDecimalPlain','алгоритм и проверка')
LABELS.update({})

from ActionApproachWordFacts import name_operands as action_approach_word_name_operands
DOCUMENTS['Action',25361]=('ActionApproachWord','алгоритм и проверка')
LABELS.update({('Action', 25376): 'SelectStep', ('Action', 25392): 'SetDirection', ('Action', 25406): 'ApplyStep', ('Action', 25414): 'Accumulate'})

from ActionRecordDistanceFacts import name_operands as action_record_distance_name_operands
DOCUMENTS['Action',60137]=('ActionRecordDistance','алгоритм и проверка')
LABELS.update({('Action', 60162): 'SaveFirst', ('Action', 60188): 'SaveSecond', ('Action', 60214): 'CompareThird', ('Action', 60220): 'ReadFirst'})

from ActionSelectedRecordStepFacts import name_operands as action_selected_record_step_name_operands
DOCUMENTS['Action',62315]=('ActionSelectedRecordStep','алгоритм и проверка')
LABELS.update({})

from ActionClass18ProximityFacts import name_operands as action_class18_proximity_name_operands
DOCUMENTS['Action',62294]=('ActionClass18Proximity','алгоритм и проверка')
LABELS.update({})

from ActionSelectClass8Facts import name_operands as action_select_class8_name_operands
DOCUMENTS['Action',59772]=('ActionSelectClass8','алгоритм и проверка')
LABELS.update({})

from ActionSelectedRecordProximityFacts import name_operands as action_selected_record_proximity_name_operands
DOCUMENTS['Action',61514]=('ActionSelectedRecordProximity','алгоритм и проверка')
LABELS.update({('Action', 61551): 'StepFar'})

from ActionClass2LinkFacts import name_operands as action_class2_link_name_operands
DOCUMENTS['Action',25929]=('ActionClass2Link','алгоритм и проверка')
LABELS.update({('Action', 25946): 'SelectSixSeven'})

from ActionClass5LinkFacts import name_operands as action_class5_link_name_operands
DOCUMENTS['Action',25893]=('ActionClass5Link','алгоритм и проверка')
LABELS.update({})

from ActionClass8LinkFacts import name_operands as action_class8_link_name_operands
DOCUMENTS['Action',25910]=('ActionClass8Link','алгоритм и проверка')
LABELS.update({})

from ActionClass7LinkFacts import name_operands as action_class7_link_name_operands
DOCUMENTS['Action',25958]=('ActionClass7Link','алгоритм и проверка')
LABELS.update({})

from ActionClass6LinkFacts import name_operands as action_class6_link_name_operands
DOCUMENTS['Action',25983]=('ActionClass6Link','алгоритм и проверка')
LABELS.update({})

from ActionClass1LinkFacts import name_operands as action_class1_link_name_operands
DOCUMENTS['Action',26004]=('ActionClass1Link','алгоритм и проверка')
LABELS.update({})

from ActionClass4LinkFacts import name_operands as action_class4_link_name_operands
DOCUMENTS['Action',26029]=('ActionClass4Link','алгоритм и проверка')
LABELS.update({})

from ActionClass3LinkFacts import name_operands as action_class3_link_name_operands
DOCUMENTS['Action',26078]=('ActionClass3Link','алгоритм и проверка')
LABELS.update({('Action', 26104): 'TryCode26'})

from ActionPhaseTransitionFacts import name_operands as action_phase_transition_name_operands
DOCUMENTS['Action',59701]=('ActionPhaseTransition','алгоритм и проверка')
LABELS.update({('Action', 59724): 'CheckFirst', ('Action', 59732): 'FoldFirst', ('Action', 59743): 'FoldSecond', ('Action', 59754): 'FoldThird'})

from ActionCandidateClassFacts import name_operands as action_candidate_class_name_operands
DOCUMENTS['Action',59904]=('ActionCandidateClass','алгоритм и проверка')
LABELS.update({})

from ActionCandidateGateFacts import name_operands as action_candidate_gate_name_operands
DOCUMENTS['Action',59925]=('ActionCandidateGate','алгоритм и проверка')
LABELS.update({('Action', 59932): 'StartList', ('Action', 59935): 'NextItem'})

from ActionNearestCandidateFacts import name_operands as action_nearest_candidate_name_operands
DOCUMENTS['Action',59842]=('ActionNearestCandidate','алгоритм и проверка')
LABELS.update({('Action', 59850): 'NextItem', ('Action', 59891): 'NextLoop', ('Action', 59895): 'DropStale', ('Action', 59901): 'ReadResult'})

from ActionTargetTransitionFacts import name_operands as action_target_transition_name_operands
DOCUMENTS['Action',59678]=('ActionTargetTransition','алгоритм и проверка')
LABELS.update({})

from ActionNearPhaseFacts import name_operands as action_near_phase_name_operands
DOCUMENTS['Action',61575]=('ActionNearPhase','алгоритм и проверка')
LABELS.update({('Action', 61612): 'CheckGlobal'})

from ActionPhaseNearStateFacts import name_operands as action_phase_near_state_name_operands
DOCUMENTS['Action',61564]=('ActionPhaseNearState','алгоритм и проверка')
LABELS.update({})

from ActionLinkedNearStateFacts import name_operands as action_linked_near_state_name_operands
DOCUMENTS['Action',61569]=('ActionLinkedNearState','алгоритм и проверка')
LABELS.update({})

from ActionTimedDecayStateFacts import name_operands as action_timed_decay_state_name_operands
DOCUMENTS['Action',63082]=('ActionTimedDecayState','алгоритм и проверка')
LABELS.update({})

from ActionIdleBaseResetFacts import name_operands as action_idle_base_reset_name_operands
DOCUMENTS['Action',63121]=('ActionIdleBaseReset','алгоритм и проверка')
LABELS.update({})

from ActionIdleStateFacts import name_operands as action_idle_state_name_operands
DOCUMENTS['Action',63103]=('ActionIdleState','алгоритм и проверка')
LABELS.update({})

from ActionLocalOffsetsFacts import name_operands as action_local_offsets_name_operands
DOCUMENTS['Action',63181]=('ActionLocalOffsets','алгоритм и проверка')
LABELS.update({})

from ActionFastPhaseStateFacts import name_operands as action_fast_phase_state_name_operands
DOCUMENTS['Action',63147]=('ActionFastPhaseState','алгоритм и проверка')
LABELS.update({})

from ActionTimedPhaseStateFacts import name_operands as action_timed_phase_state_name_operands
DOCUMENTS['Action',62369]=('ActionTimedPhaseState','алгоритм и проверка')
LABELS.update({})

from ActionLinkedContextFacts import name_operands as action_linked_context_name_operands
DOCUMENTS['Action',59233]=('ActionLinkedContext','алгоритм и проверка')
LABELS.update({('Action', 59244): 'UseIndex', ('Action', 59248): 'StorePointer'})

from ActionLinkedVectorsFacts import name_operands as action_linked_vectors_name_operands
DOCUMENTS['Action',59284]=('ActionLinkedVectors','алгоритм и проверка')
LABELS.update({('Action', 59333): 'ReadRecord'})

from ActionChildSpawnFacts import name_operands as action_child_spawn_name_operands
DOCUMENTS['Action',59499]=('ActionChildSpawn','алгоритм и проверка')
LABELS.update({('Action', 59524): 'NextChild', ('Action', 59601): 'StoreModel'})

from ActionAcquireLocalStateFacts import name_operands as action_acquire_local_state_name_operands
DOCUMENTS['Action',63165]=('ActionAcquireLocalState','алгоритм и проверка')
LABELS.update({})

from ActionPeriodicClass3StateFacts import name_operands as action_periodic_class3_state_name_operands
DOCUMENTS['Action',62448]=('ActionPeriodicClass3State','алгоритм и проверка')
LABELS.update({('Action', 62484): 'CreateChild', ('Action', 62617): 'ResetBases'})

from ActionClass8SpawnGateFacts import name_operands as action_class8_spawn_gate_name_operands
DOCUMENTS['Action',59491]=('ActionClass8SpawnGate','алгоритм и проверка')
LABELS.update({})

from ActionClassRefreshFacts import name_operands as action_class_refresh_name_operands
DOCUMENTS['Action',61443]=('ActionClassRefresh','алгоритм и проверка')
LABELS.update({})

from ActionLinkedProximityFacts import name_operands as action_linked_proximity_name_operands
DOCUMENTS['Action',61449]=('ActionLinkedProximity','алгоритм и проверка')
LABELS.update({})

LABELS['Action',0xF365]='StepFar'

from ActionSmallEffectStateFacts import name_operands as action_small_effect_state_name_operands
DOCUMENTS['Action',63212]=('ActionSmallEffectState','алгоритм и проверка')
LABELS.update({('Action', 63264): 'SetDecay'})

from ActionClass17SweepFacts import name_operands as action_class17_sweep_name_operands
DOCUMENTS['Action',62620]=('ActionClass17Sweep','алгоритм и проверка')
LABELS.update({('Action', 62642): 'CheckMarker', ('Action', 62649): 'NextRecord', ('Action', 62719): 'CheckClass3'})

from ActionClass19SpawnFacts import name_operands as action_class19_spawn_name_operands
DOCUMENTS['Action',25623]=('ActionClass19Spawn','алгоритм и проверка')
LABELS.update({('Action', 25650): 'StoreKind', ('Action', 25657): 'BuildControl', ('Action', 25756): 'ClampHigh', ('Action', 25762): 'StoreScale', ('Action', 25785): 'StoreTag', ('Action', 25800): 'NextItem', ('Action', 25809): 'CheckOld'})

from ActionWideVectorStateFacts import name_operands as action_wide_vector_state_name_operands
DOCUMENTS['Action',61630]=('ActionWideVectorState','алгоритм и проверка')
LABELS.update({('Action', 61641): 'SelectVector'})

from ActionProjectedPairCodesFacts import name_operands as action_projected_pair_codes_name_operands
DOCUMENTS['Action',60500]=('ActionProjectedPairCodes','алгоритм и проверка')
LABELS.update({('Action', 60507): 'NextPoint', ('Action', 60525): 'SecondNegative', ('Action', 60530): 'SecondHigh', ('Action', 60532): 'CheckFirst', ('Action', 60550): 'FirstNegative', ('Action', 60555): 'FirstHigh', ('Action', 60557): 'StoreCode', ('Action', 60570): 'CheckEnd', ('Action', 60579): 'StoreRejected'})

from ActionOverlayPairFacts import name_operands as action_overlay_pair_name_operands
DOCUMENTS['Action',60225]=('ActionOverlayPair','алгоритм и проверка')
LABELS.update({})

from ActionLinkedOverlayFacts import name_operands as action_linked_overlay_name_operands
DOCUMENTS['Action',59396]=('ActionLinkedOverlay','алгоритм и проверка')
LABELS.update({('Action', 59445): 'CheckDepthSigns'})

from ActionClass17SpawnFacts import name_operands as class17_spawn_name_operands
DOCUMENTS['Action',0x60E8]=('ActionClass17Spawn','алгоритм и проверка')
LABELS['Action',0x60F1]='InitializeSlot'

from ActionSpawnCurrentLinkFacts import name_operands as action_spawn_current_link_name_operands
DOCUMENTS['Action',62037]=('ActionSpawnCurrentLink','алгоритм и проверка')
LABELS.update({('Action', 62077): 'CreateLinked'})

from ActionSpawnWindowFacts import name_operands as action_spawn_window_name_operands
DOCUMENTS['Action',61986]=('ActionSpawnWindow','алгоритм и проверка')
LABELS.update({})

from ActionTimedLinkedStateFacts import name_operands as action_timed_linked_state_name_operands
DOCUMENTS['Action',62408]=('ActionTimedLinkedState','алгоритм и проверка')
LABELS.update({('Action', 62426): 'CheckLinked'})

from ActionEnterTimedStateFacts import name_operands as action_enter_timed_state_name_operands
DOCUMENTS['Action',25269]=('ActionEnterTimedState','алгоритм и проверка')
LABELS.update({})

from ActionLinkedMotionGateFacts import name_operands as action_linked_motion_gate_name_operands
DOCUMENTS['Action',25163]=('ActionLinkedMotionGate','алгоритм и проверка')
LABELS.update({('Action', 25186): 'RestoreArgs'})

from ActionRandomPhaseStepFacts import name_operands as action_random_phase_step_name_operands
DOCUMENTS['Action',25089]=('ActionRandomPhaseStep','алгоритм и проверка')
LABELS.update({('Action', 25116): 'CheckCount', ('Action', 25139): 'IncreasePhase', ('Action', 25142): 'CheckAmplitude', ('Action', 25151): 'CheckLimit'})

from ActionSpawnContinueFacts import name_operands as action_spawn_continue_name_operands
DOCUMENTS['Action',62031]=('ActionSpawnContinue','алгоритм и проверка')
LABELS.update({})

from ActionLinkedTargetStateFacts import name_operands as action_linked_target_state_name_operands
DOCUMENTS['Action',61752]=('ActionLinkedTargetState','алгоритм и проверка')
LABELS.update({('Action', 61762): 'CheckListGate', ('Action', 61782): 'RefreshClass', ('Action', 61800): 'SelectSaved', ('Action', 61814): 'CheckLinked', ('Action', 61857): 'CheckSpawn', ('Action', 61883): 'SpawnClass19', ('Action', 61901): 'PrepareLinked', ('Action', 61913): 'LoadLinked', ('Action', 61932): 'LoadMotion', ('Action', 61953): 'CheckMotion', ('Action', 61961): 'CheckDelta', ('Action', 61980): 'DispatchClass', ('Action', 61983): 'Finish'})

from ActionLinkedPhaseStateFacts import name_operands as action_linked_phase_state_name_operands
DOCUMENTS['Action',62089]=('ActionLinkedPhaseState','алгоритм и проверка')
LABELS.update({('Action', 62099): 'CheckList', ('Action', 62119): 'RefreshClass', ('Action', 62137): 'SelectSaved', ('Action', 62151): 'CheckLinked', ('Action', 62184): 'CheckSpawn', ('Action', 62210): 'SpawnClass19', ('Action', 62228): 'PrepareLinked', ('Action', 62240): 'CheckCounter', ('Action', 62253): 'SpawnClass9', ('Action', 62267): 'LoadMotion'})

from ActionArrivalStateFacts import name_operands as action_arrival_state_name_operands
DOCUMENTS['Action',62847]=('ActionArrivalState','алгоритм и проверка')
LABELS.update({('Action', 62893): 'EffectCurrent', ('Action', 62900): 'Approach', ('Action', 63003): 'Reached', ('Action', 63020): 'MarkArrival', ('Action', 63061): 'ScoreTarget', ('Action', 63070): 'EffectTarget'})

LABELS['Action',0xDDFC]='DrawPacked'

from ActionPairedAimLinesFacts import name_operands as action_paired_aim_lines_name_operands
DOCUMENTS['Action',25526]=('ActionPairedAimLines','алгоритм и проверка')
LABELS.update({('Action', 25582): 'SetX', ('Action', 25601): 'SetY'})

from ActionClass20SpawnFacts import name_operands as action_class20_spawn_name_operands
DOCUMENTS['Action',24957]=('ActionClass20Spawn','алгоритм и проверка')
LABELS.update({('Action', 24993): 'PositiveX', ('Action', 24995): 'SelectYSign', ('Action', 25003): 'PositiveY', ('Action', 25005): 'SelectDepth', ('Action', 25017): 'Transform'})

from ActionRandomClassGateFacts import name_operands as action_random_class_gate_name_operands
DOCUMENTS['Action',63134]=('ActionRandomClassGate','алгоритм и проверка')
LABELS.update({})

from ActionBankedParameterBuildFacts import name_operands as action_banked_parameter_build_name_operands
DOCUMENTS['Action',27006]=('ActionBankedParameterBuild','алгоритм и проверка')
LABELS.update({('Action', 27011): 'Build'})

from ActionRenderBasisData import name_operands as action_render_basis_name_operands

from ActionEquipmentData import name_operands as action_equipment_name_operands

from IntroStationRuntimeNames import name_operands as intro_station_runtime_name_operands

from ActionTargetCommandsFacts import name_operands as action_target_commands_name_operands
DOCUMENTS['Action',29374]=('ActionTargetCommands','команды захватов и наведения')
DOCUMENTS['Action',29410]=('ActionTargetCommands','команды захватов и наведения')
LABELS['Action',29426]='ToggleRequest'
LABELS['Action',29446]='QueueEnabled'
LABELS['Action',29454]='QueueModeName'

from ActionOverlayModeCommandFacts import name_operands as actionoverlaymodecommand_name_operands
DOCUMENTS['Action',29824]=('ActionOverlayModeCommand','смена режима отображения целей')
LABELS['Action',29849]='StoreMode'
LABELS['Action',0xAA99]='OverlayMode'

from ActionTractorModeCommandFacts import name_operands as actiontractormodecommand_name_operands
DOCUMENTS['Action',29753]=('ActionTractorModeCommand','команда силового луча')
LABELS['Action',29805]='QueueDisabled'
LABELS['Action',29813]='QueueBeamName'

from ActionFreeFlightCommandFacts import name_operands as actionfreeflightcommand_name_operands
DOCUMENTS['Action',30028]=('ActionFreeFlightCommand','команда свободного полёта')
LABELS['Action',30078]='QueueEnabled'
LABELS['Action',30088]='StoreOpcode'

from ActionStationReturnCommandFacts import name_operands as actionstationreturncommand_name_operands
DOCUMENTS['Action',30214]=('ActionStationReturnCommand','команда возврата к станции')

LABELS['Action',0x6441]='SpawnPrepared'

from ActionEjectCommandsFacts import name_operands as actionejectcommands_name_operands
DOCUMENTS['Action',30100]=('ActionEjectCommands','выброс груза и мины')
DOCUMENTS['Action',30159]=('ActionEjectCommands','выброс груза и мины')
LABELS['Action',30121]='NextByte'
LABELS['Action',30137]='DropByte'
LABELS['Action',30205]='NoMines'

from ActionReverseViewBasisFacts import name_operands as actionreverseviewbasis_name_operands
DOCUMENTS['Action',45045]=('ActionReverseViewBasis','отрицание внешних строк базиса')

from ActionViewDirectionCommandFacts import name_operands as actionviewdirectioncommand_name_operands
DOCUMENTS['Action',30250]=('ActionViewDirectionCommand','переключение переднего и заднего вида')
LABELS['Action',30307]='SelectRear'
LABELS['Action',28277]='NegateFirst'
LABELS['Action',28296]='NegateSecond'
LABELS['Action',28315]='NegateThird'

from ActionTractorCollectFacts import name_operands as actiontractorcollect_name_operands
DOCUMENTS['Action',29463]=('ActionTractorCollect','прицельный запрос и сбор захваченного объекта')
LABELS['Action',29492]='DropTarget'
LABELS['Action',29498]='PullTarget'
LABELS['Action',29525]='CheckFirst'
LABELS['Action',29532]='StepFirst'
LABELS['Action',29540]='AddFirst'
LABELS['Action',29542]='StoreFirst'
LABELS['Action',29555]='CheckSecond'
LABELS['Action',29562]='StepSecond'
LABELS['Action',29570]='AddSecond'
LABELS['Action',29572]='StoreSecond'
LABELS['Action',29585]='CheckThird'
LABELS['Action',29592]='StepThird'
LABELS['Action',29600]='AddThird'
LABELS['Action',29602]='StoreThird'
LABELS['Action',29603]='RestoreStack'
LABELS['Action',29634]='RandomAmount'
LABELS['Action',29641]='ReadPayload'
LABELS['Action',29650]='ApplyRule'
LABELS['Action',29675]='CheckByte'
LABELS['Action',29710]='QueuePickup'

from ActionAntimissileCommandFacts import name_operands as actionantimissilecommand_name_operands
DOCUMENTS['Action',29230]=('ActionAntimissileCommand','поиск ракеты противоракетной командой и общий вход вывода')
LABELS['Action',29263]='CheckEndMarker'
LABELS['Action',29269]='NextRecord'
LABELS['Action',29371]='RestoreIndex'

from ActionBoostCommandFacts import name_operands as actionboostcommand_name_operands
DOCUMENTS['Action',29859]=('ActionBoostCommand','проверка пространства перед ускорением')
LABELS['Action',29878]='CheckMarker'
LABELS['Action',29885]='NextRecord'
LABELS['Action',29896]='FirstFolded'
LABELS['Action',29914]='CheckOtherAxes'
LABELS['Action',29922]='SecondFolded'
LABELS['Action',29932]='ThirdFolded'

from ActionBoostAdvanceFacts import name_operands as actionboostadvance_name_operands
DOCUMENTS['Action',29956]=('ActionBoostAdvance','общий хвост ускорения, расход и шестнадцать шагов шкалы')
LABELS['Action',29964]='StepFastPhase'
LABELS['Action',29972]='StepSlowPhase'
LABELS['Action',29995]='RotateFirst'
LABELS['Action',30003]='RotateSecond'
LABELS['Action',30012]='SetBoostLimit'
LABELS['Action',30020]='IncreaseLoop'

LABELS['Action',0x7685]='MotionGate'

from ActionHyperJumpFacts import name_operands as actionhyperjump_name_operands
from FinalSyncAndPreviewRecord import name_operands as final_sync_name_operands
from InterfaceEventAndSpecialRecord import name_operands as interface_special_name_operands
from MapDistanceAndRenderState import name_operands as map_distance_render_name_operands
from StationBootResourceTables import name_operands as station_boot_resource_name_operands
DOCUMENTS['Action',28918]=('ActionHyperJump','запрос гиперперехода и расход до сравнения контекстов')
LABELS['Action',28960]='SpendPreferred'
LABELS['Action',28967]='TryFallback'
LABELS['Action',28986]='SpendFallback'
LABELS['Action',28990]='CompareContexts'
LABELS['Action',29028]='CopyContext'

from ActionHyperJumpPreparationFacts import name_operands as actionhyperjumppreparation_name_operands
DOCUMENTS['Action',29046]=('ActionHyperJumpPreparation','подготовка копируемого загрузчика гиперперехода')
LABELS['Action',29061]='ConsumeLoop'
LABELS['Action',29080]='LongDelay'
LABELS['Action',29082]='DelayOuter'
LABELS['Action',29085]='DelayMiddle'
LABELS['Action',29087]='DelayInner'

from ActionHyperReloadFacts import name_operands as actionhyperreload_name_operands
DOCUMENTS['Action',16896]=('ActionHyperReload','перенесённый загрузчик ACTION после гиперперехода')
LABELS['Action',16948]='AfterLoad'

from ActionFlightMessageNames import name_operands as flight_message_name_operands

from ControlsDirectStationRelayFacts import name_operands as controlsdirectstationrelay_name_operands
DOCUMENTS['Controls',16384]=('ControlsDirectStationRelay','прямая перенесённая загрузка STATIONF')

from ControlsStateStationRelayFacts import name_operands as controlsstatestationrelay_name_operands
DOCUMENTS['Controls',16896]=('ControlsStateStationRelay','перенесённая загрузка STATIONF с восстановлением состояния')
LABELS['Controls',16927]='AfterLoad'

from ConfirmedControlTargetNames import name_operands as confirmed_control_target_name_operands

from ControlsResetFlightContextFacts import name_operands as controlsresetflightcontext_name_operands
DOCUMENTS['Controls',56711]=('ControlsResetFlightContext','сброс полётного контекста и активация параметров')
LABELS['Controls',56722]='StoreVector'
LABELS['Controls',56743]='CopyVectors'
LABELS['Controls',56758]='NextObject'
LABELS['Controls',56772]='ClearObject'
LABELS['Controls',56786]='BeginEffects'
LABELS['Controls',56793]='NextEffect'
LABELS['Controls',56808]='CopyContext'
LABELS['Controls',56838]='StoreOpcode'

LABELS['Action',0x7B60]='OpcodeGate'

from ControlsLegacyLoadChainFacts import name_operands as controlslegacyloadchain_name_operands
LABELS['Controls',0x5E22]='SectorCount'
DOCUMENTS['Controls',24095]=('ControlsLegacyLoadChain','старое чтение секторов, распаковка и восстановление полётного контекста')
DOCUMENTS['Controls',24141]=('ControlsLegacyLoadChain','старое чтение секторов, распаковка и восстановление полётного контекста')
DOCUMENTS['Controls',24274]=('ControlsLegacyLoadChain','старое чтение секторов, распаковка и восстановление полётного контекста')
DOCUMENTS['Controls',24278]=('ControlsLegacyLoadChain','старое чтение секторов, распаковка и восстановление полётного контекста')
LABELS['Controls',24114]='RestoreStack'
LABELS['Controls',24161]='NextSector'
LABELS['Controls',24174]='SelectSide'
LABELS['Controls',24195]='ReadAttempt'
LABELS['Controls',24269]='CountDown'

from SecondaryEquipmentRowsFacts import name_operands as secondaryequipmentrows_name_operands
DOCUMENTS['Station',29535]=('SecondaryEquipmentRows','второй список, общая печать, выбор и события LANG')
DOCUMENTS['Station',29574]=('SecondaryEquipmentRows','второй список, общая печать, выбор и события LANG')
DOCUMENTS['Station',29655]=('SecondaryEquipmentRows','второй список, общая печать, выбор и события LANG')
DOCUMENTS['Station',29662]=('SecondaryEquipmentRows','второй список, общая печать, выбор и события LANG')
DOCUMENTS['Station',29699]=('SecondaryEquipmentRows','второй список, общая печать, выбор и события LANG')
LABELS['Station',29564]='ReadTop'
LABELS['Station',29617]='RepeatChoice'
LABELS['Station',29626]='RunEvent'
LABELS['Station',29691]='RenderRows'
LABELS['Station',29694]='SaveRowCount'

from ControlsBodyPrimaryMaskFacts import name_operands as controlsbodyprimarymask_name_operands
DOCUMENTS['Controls',53799]=('ControlsBodyPrimaryMask','основная затравка малого тела и режим 1 большого растра')

from DrawCenteredWithoutOwnerFacts import name_operands as drawcenteredwithoutowner_name_operands
DOCUMENTS['Station',49867]=('DrawCenteredWithoutOwner','центрируемый элемент без записи в карту владельцев')
LABELS['Station',49886]='Return'
LABELS['Station',0xC2F8]='RegisterCall'

from ArcHalfLimitInputsFacts import name_operands as archalflimitinputs_name_operands
DOCUMENTS['Map',57993]=('ArcHalfLimitInputs','подготовка альтернативных счётчиков дуги от полуширины окна')

LABELS['Controls',0xED2C]='FirstSource'
LABELS['Controls',0xED36]='FirstTarget'
LABELS['Controls',0xED40]='SecondSource'

from IntroDetachedTailFacts import name_operands as introdetachedtail_name_operands
DOCUMENTS['IntroUnpack',29901]=('IntroDetachedTail','условные входы за концом экранного потока')
DOCUMENTS['IntroUnpack',29912]=('IntroDetachedTail','условные входы за концом экранного потока')
DOCUMENTS['IntroUnpack',29924]=('IntroDetachedTail','условные входы за концом экранного потока')
LABELS['IntroUnpack',29905]='PollKey'
LABELS['IntroUnpack',29918]='CopyBlock'

from StationAllFilledBandFacts import name_operands as stationallfilledband_name_operands
DOCUMENTS['Station',52394]=('StationAllFilledBand','заполненная одиннадцатая строка полосовой рамки')
LABELS['Station',0xCCB2]='ReadFillMode'

from ActionRandomClassGateEntryFacts import name_operands as actionrandomclassgateentry_name_operands
DOCUMENTS['Action',63118]=('ActionRandomClassGateEntry','хвостовой вход в случайный допуск класса')

from IntroAttributeCountTailFacts import name_operands as introattributecounttail_name_operands
DOCUMENTS['IntroUnpack',29847]=('IntroAttributeCountTail','условный подсчёт атрибутов и вывод смещения')
LABELS['IntroUnpack',29864]='ReadPaper'
LABELS['IntroUnpack',29883]='CompareCount'
LABELS['IntroUnpack',29889]='NextCount'

from PreviewSquareEntryFacts import LABELS as PREVIEW_SQUARE_ENTRY_LABELS, DOCUMENTS as PREVIEW_SQUARE_ENTRY_DOCUMENTS, name_operands as previewsquareentry_name_operands
LABELS.update(PREVIEW_SQUARE_ENTRY_LABELS)
DOCUMENTS.update(PREVIEW_SQUARE_ENTRY_DOCUMENTS)
LABELS['Intro',0x6A5D]='StepCall'

from ActionRecordScaleExtraEntryFacts import name_operands as action_record_scale_extra_entry_name_operands
DOCUMENTS['Action',58783]=('ActionRecordScaleExtraEntry','алгоритм и проверка')
LABELS.update({})

from ControlsEvenSpanPrefixFacts import name_operands as controlsevenspanprefix_name_operands
DOCUMENTS['Controls',52917]=('ControlsEvenSpanPrefix','условное заполнение 31 байта')

from IntroDetachedUnpackGateFacts import name_operands as introdetachedunpackgate_name_operands
DOCUMENTS['IntroUnpack',29932]=('IntroDetachedUnpackGate','условный вход и переходы за экранным потоком')
LABELS['IntroUnpack',29943]='ProbeByte'

from IntroAttributeScanPrefixFacts import name_operands as introattributescanprefix_name_operands
DOCUMENTS['IntroUnpack',29844]=('IntroAttributeCountTail','фиксированный приёмник условного обхода атрибутов')

DOCUMENTS['Action',61308]=('ActionObjectStateReturnOnly','алгоритм и проверка')
