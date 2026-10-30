                module Final
                module BuildDisplayChain
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
Point61E2:      PUSH BC
                LD B, #08
Point61E5:      PUSH BC
                CALL @Final.EmitBitmapLine.Entry
                POP BC
                DJNZ @Final.BuildDisplayChain.Point61E5

                CALL @Final.EmitAttributeRow.Entry
                POP BC
                LD A, B
                CP #07
                JP NZ, @Final.BuildDisplayChain.Point61FE                       ; переход, если флаг Z сброшен


                LD (#62A5), DE
                INC DE
                INC DE
                INC DE
                INC DE
Point61FE:      CP #0F
                JP NZ, @Final.BuildDisplayChain.Point620B                       ; переход, если флаг Z сброшен


                LD (#62A7), DE
                INC DE
                INC DE
                INC DE
                INC DE
Point620B:      DJNZ @Final.BuildDisplayChain.Point61E2

                RET


                endmodule
                endmodule
