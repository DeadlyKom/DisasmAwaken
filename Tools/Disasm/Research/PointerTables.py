"""Физические записи масок и сохранённого фона исходного указателя."""

SPRITES = "Source/Station/Data/PointerSprites.asm"
BACKGROUND = "Source/Station/Data/PointerBackground.asm"


def render(data):
    outputs, symbols, records = {}, {}, []
    lines = ["                module PointerSprites",
             "; Документация [указатель](../../../Docs/Pointer.md)",
             "; исходные фазы сдвига, MaskLeft, XorLeft, MaskRight, XorRight",
             "                assert $ == #6000"]
    for page, shape in enumerate(("Normal", "Top", "Bottom")):
        lines.append("                module "+shape)
        for shift in range(8):
            for row in range(8):
                offset = 256*page+32*shift+4*row
                label = f"Shift{shift}Row{row}"
                values = data[offset:offset+4]
                lines.append((label+":").ljust(16)+"FPointerRasterRow {")
                for i, (value, field) in enumerate(zip(values, ("MaskLeft", "XorLeft", "MaskRight", "XorRight"))):
                    lines.append((f"                    #{value:02X}"+("," if i < 3 else "")).ljust(80)+"; FPointerRasterRow."+field)
                lines.append("                }")
                full = "PointerSprites."+shape+"."+label
                symbols[full] = 0x6000+offset
                records.append(dict(address=0x6000+offset, offset=offset, label=full, shift=shift, row=row, values=list(values)))
        lines.append("                endmodule")
    lines += ["                assert $ == #6300", "                endmodule"]
    outputs[SPRITES] = "\n".join(lines)+"\n"
    lines = ["                module PointerBackground",
             "; Документация [указатель](../../../Docs/Pointer.md)",
             "; исходные значения, во время работы каждая запись хранит два экранных байта",
             "                assert $ == #6575"]
    for row in range(8):
        values = data[0x821+2*row:0x823+2*row]
        lines.append((f"Row{row}:").ljust(16)+"FPointerSavedRow {")
        for i, (value, field) in enumerate(zip(values, ("Left", "Right"))):
            lines.append((f"                    #{value:02X}"+("," if i == 0 else "")).ljust(80)+"; FPointerSavedRow."+field)
        lines.append("                }")
        symbols[f"PointerBackground.Row{row}"] = 0x6575+2*row
    lines += ["                assert $ == #6585", "                endmodule"]
    outputs[BACKGROUND] = "\n".join(lines)+"\n"
    return outputs, symbols, records
