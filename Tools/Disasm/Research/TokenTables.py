"""Физические записи известных таблиц токенов LANG.C, без интерпретации неизвестных полей."""

from collections import Counter

BEGIN = 0x935
END = 0xA67
PATH = "Source/Text/Data/TokenBindings.asm"
GROUPS = ((0x935, 0x962, "Commands"), (0x962, 0x983, "Operators"),
          (0x983, 0x9EF, "Fields"), (0x9EF, 0xA67, "Suffixes"))
PUNCTUATION = {"?": "Question", ":": "Colon", "{": "OpenBrace", "}": "CloseBrace",
               "@": "At", "+": "Plus", "-": "Minus", "=": "Equal", ",": "Comma",
               "^": "Caret", "#": "Hash", "*": "Multiply", "<": "Less", ">": "Greater",
               "[": "NotGreater", "]": "NotLess", "&": "And", "!": "Or", "(": "OpenParen"}


def render(data, names):
    lines = [" " * 16 + "module ScriptTokens",
             "; Документация [торговый язык](../../../Docs/ScriptLanguage.md)",
             "; физические записи FScriptToken, исходный диапазон #C935..#CA66",
             "; имена экземпляров обозначают символы, смысл неизвестных свойств ещё разбирается",
             " " * 16 + "assert $ == #C935"]
    records = []
    for begin, end, group in GROUPS:
        lines += ["", " " * 16 + "module " + group]
        counts = Counter()
        for offset in range(begin, end, 3):
            token = data[offset]
            target = int.from_bytes(data[offset + 1:offset + 3], "little")
            handler = names["Text", target]
            char = chr(token)
            label = ("Digit" + char if char.isdigit() else "Upper" + char if char.isupper()
                     else "Lower" + char.upper() if char.islower() else PUNCTUATION[char])
            counts[label] += 1
            if counts[label] > 1:
                label += str(counts[label])
            if len(label) > 14:
                raise ValueError("Длинная метка токена")
            lines += [(label + ":").ljust(16) + "FScriptToken {",
                      (" " * 20 + f"#{token:02X},").ljust(80) + "; Symbol, исходный ASCII-код",
                      (" " * 20 + "@" + handler).ljust(80) + "; Handler, адрес из исходной записи",
                      " " * 16 + "}"]
            records.append({"offset": offset, "symbol": token, "handler": target,
                            "symbol_name": "ScriptTokens." + group + "." + label})
        lines.append(" " * 16 + "endmodule")
    lines += [" " * 16 + "assert $ == #CA67", " " * 16 + "endmodule"]
    return "\n".join(lines) + "\n", records
