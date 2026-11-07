"""Три физических текста диагностического входа, CR и LF сохранены буквально."""
import ast
import re

PATH = 'Source/Action/Data/DiagnosticMessages.asm'
DATA = b'Status: \n\rDeads: \n\r\n'
LABELS = {'StatusText': 0xACD6, 'DeadsText': 0xACDF, 'NewLine': 0xACE8}
SOURCE = '''                module ActionDiagnosticMessages
                ; Документация [диагностическая очередь](../../../Docs/ActionDiagnosticQueue.md)
                assert $ == #ACD6
StatusText:     db "Status: ", #0A                                              ; заголовок первого числа и LF, строка не завершается нулём
DeadsText:      db #0D, "Deads: ", #0A                                         ; CR, заголовок двух следующих чисел и LF
NewLine:        db #0D, #0A                                                     ; отдельные CR и LF
                assert $ == #ACEA
                endmodule
'''


def parse(text):
    raw, labels = bytearray(), {}
    for line in text.splitlines():
        code = line.partition(';')[0]
        match = re.match(r'(\w+):\s+db\s+(.+?)\s*$', code)
        if not match:
            continue
        labels[match[1]] = 0xACD6 + len(raw)
        for token in re.findall(r'"[^"\n]*"|#[0-9A-Fa-f]+', match[2]):
            if token.startswith('"'):
                raw.extend(ast.literal_eval(token).encode('ascii'))
            else:
                raw.append(int(token[1:], 16))
    return bytes(raw), labels
