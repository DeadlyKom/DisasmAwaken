                module Controls
                module ContinueProjectionRatio
                ; Документация [алгоритм и проверка](../../Docs/ControlsBodyProjection.md)
                ; -----------------------------------------
                ; Продолжение сравнения, кодирование отношения и снятие внутреннего возврата
                ; исходная запись 22, банк 1, смещения #110A..#1164
                ; In:
                ;   внутренний вход после сравнения равных старших слов, HL=0, DE=общее старшее слово
                ;   BC на вершине стека восстанавливает младшие байты, затем лежат сохранённый HL и два возврата
                ;   AF содержит результат C-B, C' уже уменьшен, другие входы и их рамки перечислены в документации
                ; Out:
                ;   результат отношения совпадает с договором EncodeProjectionRatio
                ;   от физического Entry обычный выход увеличивает SP на 6, отказ на 8
                ;   RejectProject принимает внешний возврат прямо на вершине, возвращает A=0, F=44
                ;   HL', DE', AF', IX, IY сохраняются, I, IM, IFF и страница не меняются
                ;   R и значения временных байтов CPU-стека моделью не доказаны, прерывания не исполнялись
                ; Corrupt:
                ;   HL, DE, BC, AF, BC', R и временная рамка отношения
                ; Note:
                ;   это продолжение нескольких ветвей, не самостоятельная процедура с обычным CALL-контрактом
                ;   DivideCode физически продолжается в DivideByteFraction, порядок include обязателен
                ; -----------------------------------------
Entry:          POP BC
                JR C, @Controls.ContinueProjectionRatio.NormalizeInside         ; переход, если младший байт N меньше младшего байта Q, отношение находится внутри

                JR Z, @Controls.ContinueProjectionRatio.NormalizeInside         ; переход, если младшие байты равны, N равно Q

                JP @Controls.EncodeProjectionRatio.PrepareOutside

MarkFirstInside:SET @ControlsProjectConst.XWithinBit, B
                JP @Controls.ContinueProjectionRatio.StartInside

                ; Обновление признака N<=Q, разряд 2 для первой координаты либо 3 для второй.
NormalizeInside:EXX
                DEC C
                JR NZ, @Controls.ContinueProjectionRatio.MarkFirstInside        ; переход, если уменьшенный C' ненулевой, помечается первая координата

                SET @ControlsProjectConst.YWithinBit, B
StartInside:    INC C
                EXX
                POP HL
                LD A, @ControlsProjectConst.FullShiftMax
                ; Расчёт нормализации по делителю, не более 23 исходных сдвигов.
ShiftInside:    SLA C
                ADC HL, HL
                PUSH AF
                SLA B
                RL E
                RL D
                JR C, @Controls.ContinueProjectionRatio.InsideCarry             ; переход, если делитель вышел за 24 разряда, восстанавливаются коэффициенты

                POP AF
                DEC A
                JR NZ, @Controls.ContinueProjectionRatio.ShiftInside            ; переход, если остались сдвиги нормализации внутреннего отношения

                RET

                ; Расчёт внешней ветви с исходными побитовыми усечениями, точным N/Q она не является.
OutsideCarry:   SLA B
                RL E
                RL D
                PUSH AF
                SCF
                RR H
                RR L
                POP AF
                JR C, @Controls.ContinueProjectionRatio.SubtractBase            ; переход, если сдвиг делителя дал Carry, сравнение усечённых слов пропускается

                PUSH HL
                OR A
                SBC HL, DE
                JR NC, @Controls.ContinueProjectionRatio.DiscardCaller          ; переход, если нормализованный числитель не меньше делителя, снимается внутренний возврат

                POP HL
                ; Расчёт скорректированного числителя, SCF/RR меняет только D, байт E не вращается.
SubtractBase:   SCF
                RR D
                OR A
                SBC HL, DE
                JR @Controls.ContinueProjectionRatio.DivideCode

                ; Удаление внутреннего возврата отношения, следующий RET возвращает вызывающему проекции.
DiscardCaller:  POP HL
                POP AF
                ; Отказ проекции с внешним возвратом на вершине CPU-стека.
RejectProject:  XOR A
                RET

RestoreNumHigh: SCF
                RR H
                JR @Controls.ContinueProjectionRatio.RestoreDenHigh

InsideCarry:    POP AF
                JR C, @Controls.ContinueProjectionRatio.RestoreNumHigh          ; переход, если сдвиг числителя дал Carry, восстанавливается его старший разряд

                RR H
RestoreDenHigh: SCF
                RR D
                ; Подготовка коэффициентов для физического продолжения в байтовом делителе.
DivideCode:     LD A, H
                LD B, D
                ; JP @Controls.DivideByteFraction.Entry, продолжение в DivideByteFraction.asm

                endmodule
                endmodule
