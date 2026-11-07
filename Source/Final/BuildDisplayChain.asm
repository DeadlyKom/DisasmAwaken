                module Final
                module BuildDisplayChain
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
; Документация [Final](../../Docs/FunctionDetails/Final.md)
; -----------------------------------------
; Создание 24 групп по восемь bitmap-строк и полосе атрибутов с двумя местами вставки синхронизации
; исходная запись 29, файловые смещения #01DF..#020D
; In:
;   HL - начало приёмника, образцы #6247 и #627D уже настроены PrepareFrame
; Out:
;   DE - адрес за 24 группами экранных строк и атрибутов, включая два пропуска по четыре байта
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   каждая группа содержит восемь образцов по 52 байта и один по 23 байта
;   после десятой и восемнадцатой групп пропускаются места синхронизации, адреса сохраняются в #62A7 и #62A5
; -----------------------------------------
                ; создание 24 знакоместных рядов, по восемь строк bitmap в каждом
Entry:          LD B, #18
                EX DE, HL
CharacterRow:   PUSH BC
                LD B, #08
BitmapLine:     PUSH BC
                CALL @Final.EmitBitmapLine.Entry
                POP BC
                DJNZ @Final.BuildDisplayChain.BitmapLine

                CALL @Final.EmitAttributeRow.Entry
                POP BC
                LD A, B
                CP #07
                JP NZ, @Final.BuildDisplayChain.CheckFirstSync                  ; переход, если осталось не семь рядов, пропустить место синхронизации после восемнадцатого


                LD (#62A5), DE
                INC DE
                INC DE
                INC DE
                INC DE
CheckFirstSync: CP #0F
                JP NZ, @Final.BuildDisplayChain.CountRows                       ; переход, если осталось не пятнадцать рядов, пропустить место синхронизации после десятого


                LD (#62A7), DE
                INC DE
                INC DE
                INC DE
                INC DE
CountRows:      DJNZ @Final.BuildDisplayChain.CharacterRow

                RET


                endmodule
                endmodule
