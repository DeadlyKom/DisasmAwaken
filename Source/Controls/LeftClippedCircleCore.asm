                module Controls
                module LeftClippedCircleCore
                ; Документация [алгоритм и проверка](../../Docs/ControlsCircleKernels.md)
                ; -----------------------------------------
                ; Двухфазное сужение с неподвижным левым краем до совпадения порога Aprime
                ; исходная запись 22, банк 1, смещения #173B..#1832
                ; In:
                ;   HL задаёт правую границу строки растра 8000..8BFF, DE задаёт младший адрес левой границы E, D произвольный
                ;   BC и неподвижная граница соответствуют договору DrawLeftClippedHalf либо DrawRightClippedHalf, CurveX=8..247
                ;   HL'=0, D'=0, B'=FF, C'=(-X) AND FF, E'=Y0, допустимые начальные X/Y0 заданы в документации внешних входов
                ;   A' задаёт порог снятия отсечения, F' может быть произвольным
                ;   IX задаёт IXL как рисунок и IXH как чередование, IY сохраняется
                ;   на CPU-стеке SavedAF и внешний возврат, Direction по D18B равен 0 для движения вверх либо 1 для движения вниз
                ;   банк 1 выбран, растр и стек не пересекают код, IRQ не вмешиваются, отдельные внутренние входы требуют состояния соответствующей фазы
                ; Out:
                ;   HL, DE, BC содержат конечные края и маски либо арифметическое состояние при исходном выходе с активным EXX
                ;   AF восстановлен из SavedAF, альтернативные HL, DE, BC содержат состояние ошибки, Y и X либо переставленные края
                ;   A' сохраняется, F' содержит результат последнего сравнения с Cprime либо входное значение, если сравнения не было
                ;   IXH и IY сохраняются, IXL переключается после каждой нарисованной строки, SP после внешнего RET равен входному SP+4
                ;   I, IM, IFF и страница сохраняются, порты не записываются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', F', IXL, R, растр, SavedSP, условно изменяемые операнды и четыре временных байта CPU-стека
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
Entry:          LD A, L
                AND #1F
                CP #20
                JR NC, @Controls.LeftClippedCircleCore.EmptyReturn              ; переход, если остаток адреса по модулю 32 не меньше 32, исходная недостижимая ветвь завершения сохранена

                ; Чтение Direction, нулевое значение выбирает движение вверх, единица движение вниз.
                LD A, (@ControlsCircleWork.Value.Direction)
                AND A
                JR NZ, @Controls.LeftClippedCircleCore.CheckDown                ; переход, если Direction ненулевой, проверить нижний предел страницы

                LD A, #7F
                ; Проверка допуска верхнего прохода, старшая страница правого адреса должна быть больше 7F.
                CP H
                JR C, @Controls.LeftClippedCircleCore.SaveStack                 ; переход, если правый адрес выше страницы 7F, начать заполнение

                JR @Controls.LeftClippedCircleCore.EmptyReturn

CheckDown:      LD A, #8B
                ; Проверка допуска нижнего прохода, старшая страница правого адреса должна быть не больше 8B.
                CP H
                JR NC, @Controls.LeftClippedCircleCore.SaveStack                ; переход, если правый адрес не выше страницы 8B, начать заполнение

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
                ; Расчёт полных байтов от неподвижной левой границы, её байт включён в заполнение и не вычитается.
                LD A, D
                SUB E
                SRL A
                JR NC, @Controls.LeftClippedCircleCore.FillPairs                ; переход, если число полных байтов чётное, перейти к заполнению парами без одиночного байта

                LD (@ControlsCircleKernelsState.LeftOdd), A
                LD A, IXL
                LD (HL), A
                LD A, #00
FillPairs:      CALL @Controls.FillEvenSpan.Entry
                JR NZ, @Controls.LeftClippedCircleCore.SlowDown                 ; переход, если Direction ненулевой, вызвать шаг вниз вместо шага вверх

                CALL @Controls.AdvanceRasterUp.Entry
                JR @Controls.LeftClippedCircleCore.SlowY

SlowDown:       CALL @Controls.AdvanceRasterDown.Entry
                ; Расчёт новой вертикальной разности, два прибавления DEprime разделены увеличением только Eprime без переноса в Dprime.
SlowY:          EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JR NZ, @Controls.LeftClippedCircleCore.ChoosePhase              ; переход, если вертикальная ошибка отрицательна, сохранить ширину и нарисовать следующую строку

                ; Сужение правого криволинейного края на один пиксель, перенос маски требует предыдущего байта L.
                SLL C
                JR C, @Controls.LeftClippedCircleCore.SlowRightByte             ; переход, если маска правого края перенесена за байт, уменьшить адрес L

                ; Расчёт первого приращения по X в альтернативных парах, код отрицательного X увеличивается по модулю байта.
SlowX:          EXX
                ADD HL, BC
                INC C
                EX AF, AF'
                ; Проверка порога Aprime по новому коду Cprime, совпадение снимает отсечение и передаёт второе приращение обычному ядру.
                CP C
                JR Z, @Controls.LeftClippedCircleCore.ReleaseSlow               ; переход, если Aprime совпал с новым Cprime, снять отсечение в соответствующей фазе

                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
ChoosePhase:    JP NZ, @Controls.LeftClippedCircleCore.SlowRow                  ; переход, если ошибка отрицательна, продолжить медленное заполнение текущей ширины

                JR @Controls.LeftClippedCircleCore.FastX

SlowRightByte:  DEC L
                LD A, L
                SUB E
                INC A
                JR Z, @Controls.LeftClippedCircleCore.Finish                    ; переход, если правый байт стал меньше неподвижного левого на один, завершить сечение

                LD C, #01
                JR @Controls.LeftClippedCircleCore.SlowX

ReleaseSlow:    EX AF, AF'
                EXX
                ; Проверка совпадения байтов перед снятием левого отсечения, последующий EXX возвращает арифметические пары в основной набор.
                LD A, L
                SUB E
                EXX
                JR Z, @Controls.LeftClippedCircleCore.Finish                    ; переход, если байтовые адреса совпали при снятии отсечения, выйти с активным EXX

                JP @Controls.CircleRasterCore.FinishSlowX

ReleaseFast:    EX AF, AF'
                EXX
                ; Проверка совпадения байтов перед снятием левого отсечения, последующий EXX возвращает арифметические пары в основной набор.
                LD A, L
                SUB E
                EXX
                JR Z, @Controls.LeftClippedCircleCore.Finish                    ; переход, если байтовые адреса совпали при снятии отсечения, выйти с активным EXX

                JP @Controls.CircleRasterCore.FinishFastX

                ; Восстановление CPU-стека и SavedAF, активное состояние EXX намеренно не меняется.
Finish:         LD SP, (@ControlsRasterStepState.SavedSP)
                POP AF
                RET

FastRightByte:  DEC L
                LD A, L
                SUB E
                INC A
                JR Z, @Controls.LeftClippedCircleCore.Finish                    ; переход, если правый байт стал меньше неподвижного левого на один, завершить сечение

                LD C, #01
                JR @Controls.LeftClippedCircleCore.FastDifference

                ; Сужение правого криволинейного края на один пиксель, перенос маски требует предыдущего байта L.
FastX:          SLL C
                JR C, @Controls.LeftClippedCircleCore.FastRightByte             ; переход, если маска правого края перенесена за байт, уменьшить адрес L

                ; Расчёт первого приращения по X в альтернативных парах, код отрицательного X увеличивается по модулю байта.
FastDifference: EXX
                ADD HL, BC
                INC C
                JR Z, @Controls.LeftClippedCircleCore.Finish                    ; переход, если код Cprime обернулся в ноль, выйти до второго прибавления и обратного EXX

                EX AF, AF'
                ; Проверка порога Aprime по новому коду Cprime, совпадение снимает отсечение и передаёт второе приращение обычному ядру.
                CP C
                JR Z, @Controls.LeftClippedCircleCore.ReleaseFast               ; переход, если Aprime совпал с новым Cprime, снять отсечение в соответствующей фазе

                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Controls.LeftClippedCircleCore.FastX                     ; переход, если ошибка неотрицательна, продолжить горизонтальное сужение до следующей строки

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
                ; Расчёт полных байтов от неподвижной левой границы, её байт включён в заполнение и не вычитается.
                LD A, D
                SUB E
                SRL A
                JR NC, @Controls.LeftClippedCircleCore.PushSpan                 ; переход, если число полных байтов чётное, перейти к заполнению парами без одиночного байта

                LD (@ControlsCircleKernelsState.LeftFastOdd), A
                LD A, IXL
                LD (HL), A
                LD A, #00
                ; Расчёт смещения 16-A для выбора числа PUSH, сохранение краёв и создание пары одинаковых байтов рисунка в AF.
PushSpan:       LD L, D
                SUB #11
                CPL
                LD (@ControlsCircleKernelsState.LeftPushJump), A
                PUSH DE
                LD E, IXL
                LD D, E
                PUSH DE
                POP AF
                POP DE
                ; Замена CPU-стека адресом растра, изменённый JR направит исполнение в нужный хвост из шестнадцати PUSH.
                LD SP, HL
PushJump:       JR @Controls.LeftClippedCircleCore.PushJump

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
                ; Чтение Direction, нулевое значение выбирает движение вверх, единица движение вниз.
ResumeRows:     LD A, (@ControlsCircleWork.Value.Direction)
                AND A
                ; Восстановление CPU-стека перед настоящим CALL шага строки, помощник может завершить весь рисователь.
                LD SP, (@ControlsRasterStepState.SavedSP)
                JR NZ, @Controls.LeftClippedCircleCore.ResumeDown               ; переход, если Direction ненулевой, вызвать шаг вниз вместо шага вверх

                CALL @Controls.AdvanceRasterUp.Entry
                JR @Controls.LeftClippedCircleCore.FastX

ResumeDown:     CALL @Controls.AdvanceRasterDown.Entry
                JR @Controls.LeftClippedCircleCore.FastX

                endmodule
                endmodule
