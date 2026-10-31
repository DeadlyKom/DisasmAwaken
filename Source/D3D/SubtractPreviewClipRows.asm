                module D3D
                module SubtractPreviewClipRows
                ; Документация [точные флаги, оборачивание страницы, физические точки и углы после настоящей настройки](../../Docs/PreviewClipTail.md)
                ; -----------------------------------------
                ; Разность знаковых слов строк второго и первого конца с точными флагами SBC
                ; исходная запись 6, банк 4, файловые смещения #283B..#2845
                ; In:
                ;   HL и DE не являются входами, BC сохраняется, AF - A сохраняется, входной Carry сбрасывается
                ;   PreviewClipFirst.Value.FirstAxis и PreviewClipSecond.Value.FirstAxis содержат два 16-битных слова
                ; Out:
                ;   HL=(второй FirstAxis-первый FirstAxis) AND FFFF, DE содержит первый FirstAxis
                ;   BC сохранён, AF - A сохранён, F принадлежит SBC HL, DE с нулевым входным Carry
                ;   HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2, записей в память нет
                ; Corrupt:
                ;   HL, DE, AF - только F
                ; Note:
                ;   это обёрнутая словная разность строк, S не корректируется через P/V для математического знакового сравнения
                ; -----------------------------------------
                ; чтение слов строк второго и первого конца
Entry:          LD HL, (@PreviewClipSecond.Value.FirstAxis)
                LD DE, (@PreviewClipFirst.Value.FirstAxis)
                ; сброс входного Carry перед разностью строк
                OR A
                ; расчёт обёрнутой 16-битной разности строк
                SBC HL, DE
                RET

                endmodule
                endmodule
