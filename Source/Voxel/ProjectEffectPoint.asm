                module Voxel
                module ProjectEffectPoint
                ; Документация [две проекции эффекта](../../Docs/ActionVisualEffectWalk.md)
                ; -----------------------------------------
                ; Проекция точки эффекта с двумя знаковыми поправками
                ;   банк 3, исходная запись 21
                ; In:
                ;   HL, DE, BC задают горизонталь, глубину и вертикаль, HL' задаёт горизонтальную поправку в L' и вертикальную в H'
                ;   смещения обоих переходов заданы вызывающим как 6 минус режим, режим 0..6
                ;   доступны код банка 3, таблицы делителя и шесть байтов под SP, IRQ не вмешиваются
                ; Out:
                ;   HL, DE возвращают горизонтальную и вертикальную проекции при выполнении обоих делений
                ;   BC=#0080, AF содержит A второго деления и флаги прибавления #0080, P/V может быть установлен этим сложением
                ;   при отказе AF=#0304, HL восстанавливается из текущего слова стека, точные случаи приведены в документации
                ;   HL', DE', BC', IX, IY, I, IFF и IM сохраняются, после RET SP равен входному SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', R, рабочие операнды делителя и до шести байтов под SP
                ; Note:
                ;   при отрицательной глубине R меняется за восемь M1, остальные пути учитывают режим и M1 одного либо двух делений, бит 7 R сохраняется
                ;   точные ветви, масштабирование и границы проверки приведены в документации
                ; -----------------------------------------
                ; Проверка знака глубины до логарифмического деления.
Entry:          PUSH HL
                BIT 7, D
                JP NZ, @Voxel.ProjectEffectPoint.Reject                         ; переход, если глубина отрицательна, восстановить входной HL

                ; Расчёт вертикального числителя со знаковой поправкой из H'.
                EXX
                LD A, H
                EXX
                LD L, A
                RLCA
                AND #01
                NEG
                LD H, A
ShiftVertical:  JR @Voxel.ProjectEffectPoint.ShiftVertical                      ; исходный переход на себя, смещение задаёт DrawProjectedEffect

                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, BC
                PUSH DE
                CALL @Action.DivideScaledLogarithmic.Entry
                POP DE
                JR C, @Voxel.ProjectEffectPoint.Reject                          ; переход, если первая проекция выставила Carry

                ; Смещение первой проекции на 48 и сохранение для второй половины.
                LD BC, #0030
                ADD HL, BC
                POP BC
                PUSH HL
                ; Расчёт горизонтального числителя со знаковой поправкой из L'.
                EXX
                LD A, L
                EXX
                LD L, A
                RLCA
                AND #01
                NEG
                LD H, A
ShiftHorizontal:JR @Voxel.ProjectEffectPoint.ShiftHorizontal                    ; исходный переход на себя, смещение задаёт DrawProjectedEffect

                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, BC
                CALL @Action.DivideScaledLogarithmic.Entry
                JR C, @Voxel.ProjectEffectPoint.Reject                          ; переход, если вторая проекция выставила Carry

                ; Смещение второй проекции на 128, флаг переполнения сохраняется.
                OR A
                LD BC, #0080
                ADC HL, BC
                POP DE
                RET

Reject:         POP HL
                LD A, #03
                OR A
                RET

                endmodule
                endmodule
