                module ArchiveEngine
                module ExtendLeftMeter
                ; Документация [экранные индикаторы](../../Docs/ArchiveEngineMeters.md)
                ; -----------------------------------------
                ; заполнение следующего столбца левой полосы при росте заданного размера
                ; In:
                ;   страница 7 выбрана, поля LeftTarget, LeftShown, LeftCursor и LeftMask согласованы
                ; Out:
                ;   при LeftShown < LeftTarget счётчик увеличен, восемь пикселей изменены через XOR
                ;   после переноса бита 0 в разряд 7 адрес увеличен на один
                ; Corrupt:
                ;   HL, BC, AF
                ; -----------------------------------------
                ; сравнение уже показанного размера и целевого значения
Entry:          LD A, (@ArchiveEngineMeters.Value.LeftShown)
                LD HL, @ArchiveEngineMeters.Value.LeftTarget
                CP (HL)
                RET Z                                                           ; выход, если показанный размер равен целевому

                JR C, @ArchiveEngine.ExtendLeftMeter.AddColumn                  ; переход, если показанный размер меньше целевого, добавить столбец

                RET

                ; добавление одного столбца высотой восемь пикселей
AddColumn:      INC A
                LD (@ArchiveEngineMeters.Value.LeftShown), A
                LD HL, (@ArchiveEngineMeters.Value.LeftCursor)
                LD A, (@ArchiveEngineMeters.Value.LeftMask)
                LD C, A
                LD B, @ArchiveEngineConst.MeterHeight
DrawPixel:      LD A, C
                XOR (HL)
                LD (HL), A
                INC H
                DJNZ @ArchiveEngine.ExtendLeftMeter.DrawPixel

                ; переход к соседнему биту и проверка окончания текущего байта
                LD A, (@ArchiveEngineMeters.Value.LeftMask)
                RRC A
                LD (@ArchiveEngineMeters.Value.LeftMask), A
                RET NC                                                          ; выход, если следующий бит остаётся в текущем байте

                LD HL, (@ArchiveEngineMeters.Value.LeftCursor)
                INC HL
                LD (@ArchiveEngineMeters.Value.LeftCursor), HL
                RET

                endmodule
                endmodule
