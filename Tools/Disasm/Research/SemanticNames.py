"""Подтверждённые имена внутренних входов и полей, не меняющие исходные команды."""

import re

DOCUMENTS = {
    **{("Station", address): "StationSpans.md" for address in
       (0xBF4E, 0xC093, 0xC0C9, 0xC436, 0xC626, 0xC165, 0xC16F, 0xC17B, 0xC1C0, 0xC1CF, 0xC1DE, 0xC1ED, 0xC1F2, 0xC21F, 0xC224)},
    ("Intro", 0x6BF6): "Intro.md", ("Intro", 0x6A2C): "Intro.md",
    ("Basic", 0x5CD1): "Loader.md",
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
    0x08: "Source", 0x09: "Source + 1",
    0x0A: "Cursor", 0x0B: "Cursor + 1",
    0x0C: "Unknown0C", 0x0D: "Unknown0D",
    0x0E: "Unknown0E", 0x0F: "Unknown0E + 1",
    0x10: "Unknown10", 0x11: "Unknown11",
}


def name_operands(region, function_address, operation):
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
    operation = d3d_clip_name_operands(region, function_address, operation)
    operation = d3d_third_name_operands(region, function_address, operation)
    operation = sprite_line_table_name_operands(region, function_address, operation)
    operation = d3d_setup_name_operands(region, function_address, operation)
    operation = preview_face_fill_name_operands(region, function_address, operation)
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
    operation = key_choice_name_operands(region, function_address, operation)
    operation = signature_return_name_operands(region, function_address, operation)
    operation = delimited_record_name_operands(region, function_address, operation)
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
    if (region, function_address) == ("Intro", 0x6BF6):
        for address, name in ((0x6C8A, "TexturePhases.PhaseA"), (0x6C90, "TexturePhases.PhaseB"),
                              (0x6C96, "TexturePhases.PhaseC"), (0x6400, "IntroTables.PhaseSamples"),
                              (0x6BA2, "IntroState.LookupHL"), (0x6BA6, "IntroState.LookupBCAlt"),
                              (0x6BA9, "IntroState.LookupHLAlt"), (0x6BAC, "IntroState.LookupDEAlt"),
                              (0x6C12, "IntroState.SampleCursor")):
            operation = operation.replace(f"#{address:04X}", "@" + name)
    if (region, function_address) == ("Basic", 0x5CD1):
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
LABELS.update(DELIMITED_RECORD_LABELS)
DOCUMENTS.update(DELIMITED_RECORD_DOCUMENTS)

from SignatureReturnFacts import DOCUMENTS as SIGNATURE_RETURN_DOCUMENTS, name_operands as signature_return_name_operands
DOCUMENTS.update(SIGNATURE_RETURN_DOCUMENTS)

from KeyChoiceFacts import DOCUMENTS as KEY_CHOICE_DOCUMENTS, name_operands as key_choice_name_operands
DOCUMENTS.update(KEY_CHOICE_DOCUMENTS)

from StrideFiveFacts import LABELS as STRIDE_FIVE_LABELS, DOCUMENTS as STRIDE_FIVE_DOCUMENTS
LABELS.update(STRIDE_FIVE_LABELS)
DOCUMENTS.update(STRIDE_FIVE_DOCUMENTS)

from MembershipFlagsFacts import LABELS as MEMBERSHIP_FLAGS_LABELS, DOCUMENTS as MEMBERSHIP_FLAGS_DOCUMENTS
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

from ExpressionPushFacts import LABELS as EXPRESSION_PUSH_LABELS, DOCUMENTS as EXPRESSION_PUSH_DOCUMENTS
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
