                module Voxel
                module DrawProjectedEffect
                ; Документация [две проекции эффекта](../../Docs/ActionVisualEffectWalk.md)
                ; -----------------------------------------
                ; Проекция двух углов эффекта и передача прямоугольника на отсечение
                ;   банк 3, исходная запись 21
                ; In:
                ;   HL, DE, BC задают горизонталь, вертикаль и глубину центра, A задаёт режим 0..6, HL' задаёт полуразмеры, DE' указывает ресурс
                ;   доступны код банка 3, таблицы делителя и двенадцать байтов под SP, IRQ не вмешиваются
                ; Out:
                ;   при отказе SP снимает внешний возврат, при передаче в ClipSprite стек сохраняет его на вершине
                ;   при передаче в ClipSprite HL и DE содержат знаковые первые координаты, делённые на четыре, B=dy>>2 и C=dx>>2 для разностей 1..1023
                ;   до входа в ClipSprite либо собственного RET сохраняются DE', BC', IX, IY, I, IM и IFF, HL' изменяется
                ;   при передаче HL' содержит половины удвоенного входного слова, логически сдвинутые вправо отдельно, перенос между половинами при удвоении сохраняет исходный смысл
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', AF', R, операнды проекции и стек, после перехода действует договор ClipSprite
                ; Note:
                ;   при передаче в ClipSprite собственный код требует 113 M1 плюс M1 двух ProjectEffectPoint, при отказах действуют отдельные формулы, бит 7 R сохраняется
                ;   точные ветви, масштабирование и границы проверки приведены в документации
                ; -----------------------------------------
                ; Настройка числа удвоений в обеих половинах проектора.
Entry:          SUB #06
                NEG
                LD (@VoxelProjectionState.VerticalSkip), A
                LD (@VoxelProjectionState.HorizontalSkip), A
                LD A, C
                LD C, E
                LD E, A
                LD A, B
                LD B, D
                LD D, A
                ; Сохранение исходных компонент в операндах второго вызова.
                LD (@VoxelProjectionState.Horizontal), HL
                LD (@VoxelProjectionState.Vertical), BC
                LD (@VoxelProjectionState.Depth), DE
                ; Подготовка знаковых поправок для первого угла.
                EXX
                ADD HL, HL
                LD A, L
                NEG
                LD L, A
                LD A, H
                NEG
                LD H, A
                EXX
                CALL @Voxel.ProjectEffectPoint.Entry
                RET PE                                                          ; выход, если первая проекция выставила P/V

                PUSH DE
                PUSH HL
                LD HL, #0000
                LD DE, #0000
                LD BC, #0000
                ; Подготовка противоположных поправок для второго угла.
                EXX
                LD A, L
                NEG
                LD L, A
                LD A, H
                NEG
                LD H, A
                EXX
                CALL @Voxel.ProjectEffectPoint.Entry
                POP BC
                JP PO, @Voxel.DrawProjectedEffect.CheckWidth                    ; переход, если вторая проекция сбросила P/V, проверить размеры

DiscardCorner:  POP BC
                RET

                ; Расчёт горизонтальной разности и проверка диапазона.
CheckWidth:     OR A
                SBC HL, BC
                JR Z, @Voxel.DrawProjectedEffect.DiscardCorner                  ; переход, если горизонтальная разность равна нулю

                SRL H
                RR L
                SRL H
                JR NZ, @Voxel.DrawProjectedEffect.DiscardCorner                 ; переход, если горизонтальная разность не меньше 1024

                RR L
                LD H, B
                LD A, C
                LD C, L
                LD L, A
                LD A, C
                EX AF, AF'
                EX DE, HL
                POP BC
                ; Расчёт вертикальной разности и проверка диапазона.
                OR A
                SBC HL, BC
                RET Z                                                           ; выход, если вертикальная разность равна нулю

                SRL H
                RR L
                SRL H
                RET NZ                                                          ; выход, если вертикальная разность не меньше 1024

                RR L
                LD A, H
                OR A
                RET NZ                                                          ; выход, если старший байт уменьшенной вертикальной разности ненулевой

                ; Подготовка координат, размеров и шагов ресурса для отсечения.
                EX AF, AF'
                LD H, B
                LD B, L
                LD L, C
                LD C, A
                EX DE, HL
                SRA H
                RR L
                SRA D
                RR E
                SRA H
                RR L
                SRA D
                RR E
                EXX
                SRL H
                SRL L
                EXX
                JP @Voxel.ClipSprite.Entry

                endmodule
                endmodule
