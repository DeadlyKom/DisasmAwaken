                module Controls
                module CircleRasterCore
                ; Документация [алгоритм и проверка](../../Docs/ControlsCircleKernels.md)
                ; -----------------------------------------
                ; Двухфазное сужение кругового сечения с двумя криволинейными краями
                ; исходная запись 22, банк 1, смещения #1633..#1726
                ; In:
                ;   HL задаёт правую границу строки растра 8000..8BFF, DE задаёт младший адрес левой границы E, D произвольный
                ;   BC содержит маски открытого интервала, обе границы канонического сечения находятся в 0..255
                ;   HL'=0, D'=0, B'=FF, C'=(-X) AND FF, E'=Y0, допустимые начальные X/Y0 заданы в документации внешних входов
                ;   AF' сохраняется при обычном входе, при продолжении отсечённого ядра F' уже может содержать результат CP
                ;   IX задаёт IXL как рисунок и IXH как чередование, IY сохраняется
                ;   на CPU-стеке SavedAF и внешний возврат, Direction по D18B равен 0 для движения вверх либо 1 для движения вниз
                ;   банк 1 выбран, растр и стек не пересекают код, IRQ не вмешиваются, отдельные внутренние входы требуют состояния соответствующей фазы
                ; Out:
                ;   HL, DE, BC содержат конечные края и маски либо арифметическое состояние при исходном выходе с активным EXX
                ;   AF восстановлен из SavedAF, альтернативные HL, DE, BC содержат состояние ошибки, Y и X либо переставленные края
                ;   AF' сохраняется
                ;   IXH и IY сохраняются, IXL переключается после каждой нарисованной строки, SP после внешнего RET равен входному SP+4
                ;   I, IM, IFF и страница сохраняются, порты не записываются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IXL, R, растр, SavedSP, условно изменяемые операнды и четыре временных байта CPU-стека
                ; Note:
                ;   это внутреннее ядро после PUSH AF и подготовки альтернативных пар, настоящий CALL к Entry без такой рамки не соответствует договору
                ;   FinishSlowX и FinishFastX обычного ядра принимают активный EXX, первое прибавление по X и INC C уже выполнены
                ;   сохранённый AF восстанавливается даже при выходе с активным EXX, переставленные HL/DE/BC принудительно не исправляются
                ;   при пустом обычном сечении SavedSP не меняется, при начале рисования он равен входному SP, Direction читается, но не записывается
                ;   быстрый PUSH-хвост временно заменяет SP правой границей, новая RAM не выделяется, рамка FSingleCircleHalfFrame учитывает внешний инициализатор
                ;   модели подтверждают достижимые состояния из описанных внешних входов и цепочки PUSH, произвольные входные ошибки и отдельные внутренние адреса не объявляются исчерпывающе проверенными
                ;   полное произведение геометрии и рисунков, R целого ядра, кратность пиксельных записей, IRQ, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Проверка исходной геометрии перед первым заполнением, SavedAF уже лежит на CPU-стеке.
Entry:          LD A, E
                SUB L
                JR NC, @Controls.CircleRasterCore.EmptyReturn                   ; переход, если младший левый адрес не меньше правого, завершить пустое сечение

                ; Чтение Direction, нулевое значение выбирает движение вверх, единица движение вниз.
                LD A, (@ControlsCircleWork.Value.Direction)
                AND A
                JR NZ, @Controls.CircleRasterCore.CheckDown                     ; переход, если Direction ненулевой, проверить нижний предел страницы

                LD A, #7F
                ; Проверка допуска верхнего прохода, старшая страница правого адреса должна быть больше 7F.
                CP H
                JR C, @Controls.CircleRasterCore.SaveStack                      ; переход, если правый адрес выше страницы 7F, начать заполнение

                JR @Controls.CircleRasterCore.EmptyReturn

CheckDown:      LD A, #8B
                ; Проверка допуска нижнего прохода, старшая страница правого адреса должна быть не больше 8B.
                CP H
                JR NC, @Controls.CircleRasterCore.SaveStack                     ; переход, если правый адрес не выше страницы 8B, начать заполнение

                ; Восстановление SavedAF и внешнего возврата без записи SavedSP и без рисования.
EmptyReturn:    POP AF
                RET

                ; Сохранение адреса SavedAF перед заполнением, этот стек нужен для обычного и нелокального выхода.
SaveStack:      LD (@ControlsRasterStepState.SavedSP), SP
                ; Обновление правого крайнего байта, включающая маска C сохраняет границу, остальные биты получают рисунок IXL.
SlowRow:        LD A, C
                AND (HL)
                LD D, A
                LD A, C
                CPL
                AND IXL
                OR D
                LD (HL), A
                LD D, L
                LD L, E
                ; Обновление левого крайнего байта, включающая маска B сохраняет границу, остальные биты получают рисунок IXL.
                LD A, B
                AND (HL)
                LD (HL), A
                LD A, B
                CPL
                AND IXL
                OR (HL)
                LD (HL), A
                ; Расчёт числа полных байтов между исключёнными крайними байтами, остаток по модулю два заполняется отдельно.
                LD A, D
                SUB E
                DEC A
                SRL A
                JR NC, @Controls.CircleRasterCore.FillPairs                     ; переход, если число полных байтов чётное, перейти к заполнению парами без одиночного байта

                INC L
                LD (@ControlsCircleKernelsState.NormalOdd), A
                LD A, IXL
                LD (HL), A
                LD A, #00
FillPairs:      CALL @Controls.FillEvenSpan.Entry
                JR NZ, @Controls.CircleRasterCore.SlowDown                      ; переход, если Direction ненулевой, вызвать шаг вниз вместо шага вверх

                CALL @Controls.AdvanceRasterUp.Entry
                JP @Controls.CircleRasterCore.SlowY

SlowDown:       CALL @Controls.AdvanceRasterDown.Entry
                ; Расчёт новой вертикальной разности, два прибавления DEprime разделены увеличением только Eprime без переноса в Dprime.
SlowY:          EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JR NZ, @Controls.CircleRasterCore.ChoosePhase                   ; переход, если вертикальная ошибка отрицательна, сохранить ширину и нарисовать следующую строку

                ; Сужение левого криволинейного края на один пиксель, перенос маски требует следующего байта E.
                SCF
                RR B
                JR C, @Controls.CircleRasterCore.SlowLeftByte                   ; переход, если маска левого края перенесена за байт, увеличить адрес E

                ; Сужение правого криволинейного края на один пиксель, перенос маски требует предыдущего байта L.
SlowRight:      SLL C
                JR C, @Controls.CircleRasterCore.SlowRightByte                  ; переход, если маска правого края перенесена за байт, уменьшить адрес L

                ; Расчёт первого приращения по X в альтернативных парах, код отрицательного X увеличивается по модулю байта.
SlowX:          EXX
                ADD HL, BC
                INC C
                ; Продолжение с активным EXX, первое прибавление по X и INC C уже выполнены, осталось второе прибавление.
FinishSlowX:    ADD HL, BC
                BIT 7, H
                EXX
ChoosePhase:    JP NZ, @Controls.CircleRasterCore.SlowRow                       ; переход, если ошибка отрицательна, продолжить медленное заполнение текущей ширины

                JR @Controls.CircleRasterCore.FastX

SlowLeftByte:   INC E
                LD A, L
                SUB E
                JR Z, @Controls.CircleRasterCore.Finish                         ; переход, если байтовые адреса краёв совпали, восстановить стек и завершить сечение

                LD B, #80
                JR @Controls.CircleRasterCore.SlowRight

SlowRightByte:  DEC L
                LD A, L
                SUB E
                JR Z, @Controls.CircleRasterCore.Finish                         ; переход, если байтовые адреса краёв совпали, восстановить стек и завершить сечение

                LD C, #01
                JR @Controls.CircleRasterCore.SlowX

                ; Восстановление CPU-стека и SavedAF, активное состояние EXX намеренно не меняется.
Finish:         LD SP, (@ControlsRasterStepState.SavedSP)
                POP AF
                RET

FastLeftByte:   INC E
                LD A, L
                SUB E
                JR Z, @Controls.CircleRasterCore.Finish                         ; переход, если байтовые адреса краёв совпали, восстановить стек и завершить сечение

                LD B, #80
                JR @Controls.CircleRasterCore.FastRight

FastRightByte:  DEC L
                LD A, L
                SUB E
                JR Z, @Controls.CircleRasterCore.Finish                         ; переход, если байтовые адреса краёв совпали, восстановить стек и завершить сечение

                LD C, #01
                JR @Controls.CircleRasterCore.FastDifference

                ; Сужение левого криволинейного края на один пиксель, перенос маски требует следующего байта E.
FastX:          SCF
                RR B
                JR C, @Controls.CircleRasterCore.FastLeftByte                   ; переход, если маска левого края перенесена за байт, увеличить адрес E

                ; Сужение правого криволинейного края на один пиксель, перенос маски требует предыдущего байта L.
FastRight:      SLL C
                JR C, @Controls.CircleRasterCore.FastRightByte                  ; переход, если маска правого края перенесена за байт, уменьшить адрес L

                ; Расчёт первого приращения по X в альтернативных парах, код отрицательного X увеличивается по модулю байта.
FastDifference: EXX
                ADD HL, BC
                INC C
                JR Z, @Controls.CircleRasterCore.Finish                         ; переход, если код Cprime обернулся в ноль, выйти до второго прибавления и обратного EXX

                ; Продолжение с активным EXX, первое прибавление по X и INC C уже выполнены, осталось второе прибавление.
FinishFastX:    ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Controls.CircleRasterCore.FastX                          ; переход, если ошибка неотрицательна, продолжить горизонтальное сужение до следующей строки

                ; Подготовка вертикальной разности для следующей PUSH-строки, увеличение Eprime остаётся байтовым.
                EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                EXX
                ; Обновление правого крайнего байта, включающая маска C сохраняет границу, остальные биты получают рисунок IXL.
                LD A, C
                AND (HL)
                LD D, A
                LD A, C
                CPL
                AND IXL
                OR D
                LD (HL), A
                LD D, L
                LD L, E
                ; Обновление левого крайнего байта, включающая маска B сохраняет границу, остальные биты получают рисунок IXL.
                LD A, B
                AND (HL)
                LD (HL), A
                LD A, B
                CPL
                AND IXL
                OR (HL)
                LD (HL), A
                ; Расчёт числа полных байтов между исключёнными крайними байтами, остаток по модулю два заполняется отдельно.
                LD A, D
                SUB E
                DEC A
                SRL A
                JR NC, @Controls.CircleRasterCore.PushSpan                      ; переход, если число полных байтов чётное, перейти к заполнению парами без одиночного байта

                INC L
                LD (@ControlsCircleKernelsState.NormalFastOdd), A
                LD A, IXL
                LD (HL), A
                LD A, #00
                ; Расчёт смещения 16-A для выбора числа PUSH, сохранение краёв и создание пары одинаковых байтов рисунка в AF.
PushSpan:       LD L, D
                SUB #11
                CPL
                LD (@ControlsCircleKernelsState.NormalPushJump), A
                PUSH DE
                LD E, IXL
                LD D, E
                PUSH DE
                POP AF
                POP DE
                ; Замена CPU-стека адресом растра, изменённый JR направит исполнение в нужный хвост из шестнадцати PUSH.
                LD SP, HL
                JR @Controls.ResumeCirclePushSpan.Entry

                ; Динамическая цепочка, каждый PUSH записывает пару байтов рисунка справа налево, настоящий стек восстановит продолжение.
Push16:         PUSH AF
Push15:         PUSH AF
Push14:         PUSH AF
Push13:         PUSH AF
Push12:         PUSH AF
Push11:         PUSH AF
Push10:         PUSH AF
Push9:          PUSH AF
Push8:          PUSH AF
Push7:          PUSH AF
Push6:          PUSH AF
Push5:          PUSH AF
Push4:          PUSH AF
Push3:          PUSH AF
Push2:          PUSH AF
Push1:          PUSH AF
                ; JP @Controls.ResumeCirclePushSpan.Entry, продолжение в ResumeCirclePushSpan.asm

                endmodule
                endmodule
