                module D3D
                module SubtractPreviewClipColumns
                ; Документация [точные флаги, оборачивание страницы, физические точки и углы после настоящей настройки](../../Docs/PreviewClipTail.md)
                ; -----------------------------------------
                ; Разность знаковых слов колонок второго и первого конца с точными флагами SBC
                ; исходная запись 6, банк 4, файловые смещения #2830..#283A
                ; In:
                ;   HL и DE не являются входами, BC сохраняется, AF - A сохраняется, входной Carry сбрасывается
                ;   PreviewClipFirst.Value.SecondAxis и PreviewClipSecond.Value.SecondAxis содержат два 16-битных слова
                ; Out:
                ;   HL=(второй SecondAxis-первый SecondAxis) AND FFFF, DE содержит первый SecondAxis
                ;   BC сохранён, AF - A сохранён, F принадлежит SBC HL, DE с нулевым входным Carry
                ;   HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2, записей в память нет
                ; Corrupt:
                ;   HL, DE, AF - только F
                ; Note:
                ;   это обёрнутая словная разность колонок, S не корректируется через P/V для математического знакового сравнения
                ; -----------------------------------------
                ; чтение слов колонок второго и первого конца
Entry:          LD HL, (@PreviewClipSecond.Value.SecondAxis)
                LD DE, (@PreviewClipFirst.Value.SecondAxis)
                ; сброс входного Carry перед точной разностью без изменения A
                OR A
                ; расчёт обёрнутой 16-битной разности колонок
                SBC HL, DE
                RET

                endmodule
                endmodule
