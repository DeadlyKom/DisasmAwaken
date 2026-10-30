"""128 физических записей переходов глифа, подтверждённых пиксельной моделью."""

from GlyphFacts import product_routes, verify_table

PATH = "Source/Station/Data/GlyphRoutes.asm"


def render(data, names):
    verify_table(data)
    lines = ["                module GlyphRoutes",
             "; Документация [рисование глифа](../../../Docs/GlyphRendering.md)",
             "; порядок записи, сдвиг X, признак крайней колонки, младшие три бита Y",
             "                assert $ == #9200"]
    records = []
    symbols = {}
    for shift, edge, y in product_routes():
        index = (2*shift + int(edge))*8 + y
        offset = 0x3200 + 4*index
        first, after = (int.from_bytes(data[offset + field:offset + field + 2], "little") for field in (0, 2))
        label = f"{'Edge' if edge else 'Shift'}{shift}Y{y}"
        symbols["GlyphRoutes."+label] = offset + 0x6000
        lines.append((label+":").ljust(16) + "FGlyphRoute {")
        first_name = "@" + names["Station", first]
        after_name = "@" + names["Station", after] if after else "#0000"
        lines.append(("                    " + first_name + ",").ljust(80) + "; FGlyphRoute.First, участок до границы знакоместа")
        lines.append(("                    " + after_name).ljust(80) + "; FGlyphRoute.AfterWrap, остаток после перехода, ноль при Y кратном восьми")
        lines.append("                }")
        records.append(dict(shift=shift, right_edge=edge, y_modulo=y, first=first, after_wrap=after,
                            address=offset+0x6000, label="GlyphRoutes."+label))
    lines += ["                assert $ == #9400", "                endmodule"]
    return "\n".join(lines)+"\n", symbols, records
