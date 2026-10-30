"""Три физические записи фаз вступления из исходного AWAKEN.B."""

PATH = "Source/Intro/Data/TexturePhases.asm"
BEGIN = 0x98A
END = 0x99C
LABELS = ("PhaseA", "PhaseB", "PhaseC")


def render(data):
    lines = [" " * 16 + "module TexturePhases",
             "; Документация [фазы вступления](../../../Docs/Intro.md)",
             "; PhaseA управляет младшим байтом HL, PhaseB альтернативным BC, PhaseC альтернативным HL",
             " " * 16 + "assert $ == #6C8A"]
    symbols = {}
    for index, label in enumerate(LABELS):
        offset = BEGIN + index * 6
        symbols["TexturePhases." + label] = 0x6300 + offset
        values = [int.from_bytes(data[offset + field:offset + field + 2], "little") for field in (0, 2, 4)]
        lines.append((label + ":").ljust(16) + "FTexturePhase {")
        for field, value in zip(("Phase", "Step", "StepDelta"), values):
            code = " " * 20 + f"#{value:04X}" + ("," if field != "StepDelta" else "")
            lines.append(code.ljust(80) + "; FTexturePhase." + field)
        lines.append(" " * 16 + "}")
    lines += [" " * 16 + "assert $ == #6C9C", " " * 16 + "endmodule"]
    return "\n".join(lines) + "\n", symbols
