                module ArchiveEngine
                module ExtendRightMeter
                ; Документация [экранные индикаторы](../../Docs/ArchiveEngineMeters.md)
                ; -----------------------------------------
                ; заполнение следующего столбца правой полосы справа налево
                ; In:
                ;   страница 7 выбрана, поля RightTarget, RightShown, RightCursor и RightMask согласованы
                ; Out:
                ;   при RightShown < RightTarget счётчик увеличен, восемь пикселей изменены через XOR
                ;   после переноса бита 7 в разряд 0 адрес уменьшен на один
                ; Corrupt:
                ;   HL, BC, AF
                ; -----------------------------------------
                ; сравнение уже показанного размера и целевого значения
Entry:          LD A, (@ArchiveEngineMeters.Value.RightShown)
                LD HL, @ArchiveEngineMeters.Value.RightTarget
                CP (HL)
                RET Z                                                           ; выход, если показанный размер равен целевому

                JR C, @ArchiveEngine.ExtendRightMeter.AddColumn                 ; переход, если показанный размер меньше целевого, добавить столбец

                RET

                ; добавление одного столбца высотой восемь пикселей
AddColumn:      INC A
                LD (@ArchiveEngineMeters.Value.RightShown), A
                LD HL, (@ArchiveEngineMeters.Value.RightCursor)
                LD B, @ArchiveEngineConst.MeterHeight
                LD A, (@ArchiveEngineMeters.Value.RightMask)
                LD C, A
DrawPixel:      LD A, C
                XOR (HL)
                LD (HL), A
                INC H
                DJNZ @ArchiveEngine.ExtendRightMeter.DrawPixel

                ; переход к соседнему биту и проверка окончания текущего байта
                LD A, (@ArchiveEngineMeters.Value.RightMask)
                RLC A
                LD (@ArchiveEngineMeters.Value.RightMask), A
                RET NC                                                          ; выход, если следующий бит остаётся в текущем байте

                LD HL, (@ArchiveEngineMeters.Value.RightCursor)
                DEC HL
                LD (@ArchiveEngineMeters.Value.RightCursor), HL
                RET

                endmodule
                endmodule
