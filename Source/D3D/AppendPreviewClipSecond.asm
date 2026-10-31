                module D3D
                module AppendPreviewClipSecond
                ; Документация [точные флаги, оборачивание страницы, физические точки и углы после настоящей настройки](../../Docs/PreviewClipTail.md)
                ; -----------------------------------------
                ; Упаковка младших байтов второго конца и последовательный вход в запись точки
                ; исходная запись 6, банк 4, файловые смещения #2846..#284D
                ; In:
                ;   HL и DE не являются параметрами, BC сохраняемый контекст, AF - только Carry участвует в результате
                ;   PreviewClipSecond.Value содержит координатные слова, ByteCount задаёт байтовый курсор C8
                ; Out:
                ;   HL=C800+((N+2) AND FF), DE содержит младший FirstAxis в D и младший SecondAxis в E
                ;   BC сохранён, AF содержит новый курсор и F второго INC L с входным Carry
                ;   HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после общего RET равен входному+2
                ;   в страницу C8 последовательно записаны колонка и строка второго конца, ByteCount увеличен по модулю 256
                ; Corrupt:
                ;   HL, DE, AF, два байта C8 и ByteCount
                ; Note:
                ;   старшие байты слов не читаются, это упаковка младших байтов, а не насыщение или дополнительное отсечение
                ;   фрагмент без RET продолжается в AppendPreviewClipPoint, физический порядок двух файлов обязателен
                ; -----------------------------------------
                ; чтение младшего SecondAxis как колонки второго конца
Entry:          LD A, (@PreviewClipSecond.Value.SecondAxis)
                LD E, A
                ; чтение младшего FirstAxis как строки, старшие байты координат не используются
                LD A, (@PreviewClipSecond.Value.FirstAxis)
                LD D, A
                ; JP @D3D.AppendPreviewClipPoint.Entry, продолжение в AppendPreviewClipPoint.asm

                endmodule
                endmodule
