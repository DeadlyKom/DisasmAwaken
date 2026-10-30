                module Map
                module PrepareRightRasterPoint
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [табличные координаты краёв и ограниченный поиск без замены SP](../../Docs/RasterPreparation.md)
; -----------------------------------------
; Адрес правой растровой точки и маска C с сохранением левой B
; исходная запись 7, файловые смещения #252E..#2553
; In:
;   BC - B левая маска, C относительный Y, AF - A относительный X правой точки
;   MapScreenTables построены, KARTA выбран, перенос младшего адресного сложения не должен требовать исправления старшего байта для обычного bitmap
; Out:
;   HL - адрес правой точки с тем же байтовым сложением RowLow[Y] и ColumnByte[X]
;   DE сохранён, BC - B восстановленная левая маска, C=80 SHR (X AND 7)
;   A равен входному B, F=43 при X AND 7=7, иначе 42, MapState.LeftMask получает входной B
;   все альтернативные и индексные регистры, I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, BC только C, AF
; Note:
;   входной AF временно сохраняется вокруг копирования B в существующий рабочий байт DFB8
;   правая маска получается RLC из C=80 за 8-(X AND 7) шагов, это тот же одноразрядный результат с иным Carry
; -----------------------------------------
                ; сохранение входного X и F вокруг копирования левой маски B в рабочий байт
Entry:          PUSH AF
                LD A, B
                LD (@MapState.LeftMask), A
                POP AF
                ; выбор Y из C и X из A для адреса правого края
                LD L, C
                LD C, A
                LD H, @MapMarkerConst.RowHighPage
                LD B, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, C
                ADD A, (HL)
                INC H
                LD L, A
                LD H, B
                ; расчёт числа вращений правой маски как 8-(X AND 7)
                LD A, C
                AND #07
                SUB #08
                NEG
                LD C, #80
                ; вращение маски правого края в C
RotateMask:     RLC C
                DEC A
                JR NZ, @Map.PrepareRightRasterPoint.RotateMask                  ; переход, если остаются сдвиги правой маски, продолжить вращение C

                ; восстановление левой маски в B без изменения флагов последнего DEC
                LD A, (@MapState.LeftMask)
                LD B, A
                RET

                endmodule
                endmodule
