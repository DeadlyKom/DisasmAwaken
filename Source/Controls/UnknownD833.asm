                module Controls
                module UnknownD833
                ; Документация [быстрая заливка через SP](../../Docs/ControlsPushSpans.md)
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1833..#1924
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          LD A, E
                AND #1F
                CP #20
                JR NC, @Controls.UnknownD833.PointD84C                          ; переход, если флаг Carry сброшен


                LD A, (@ControlsEvenSpanState.Mode)
                AND A
                JR NZ, @Controls.UnknownD833.PointD847                          ; переход, если флаг Z сброшен


                LD A, #7F
                CP H
                JR C, @Controls.UnknownD833.PointD84E                           ; переход, если флаг Carry установлен


                JR @Controls.UnknownD833.PointD84C


PointD847:      LD A, #8B
                CP H
                JR NC, @Controls.UnknownD833.PointD84E                          ; переход, если флаг Carry сброшен


PointD84C:      POP AF
                RET


PointD84E:      LD (@ControlsRasterStepState.SavedSP), SP
PointD852:      LD D, L
                LD L, E
                LD A, B
                AND (HL)
                LD (HL), A
                LD A, B
                CPL
                AND IXL
                OR (HL)
                LD (HL), A
                LD A, D
                SUB E
                DEC A
                SRL A
                JR NC, @Controls.UnknownD833.PointD86D                          ; переход, если флаг Carry сброшен


                INC L
                LD (#D86C), A
                LD A, IXL
                LD (HL), A
                LD A, #00
PointD86D:      CALL @Controls.FillEvenSpan.Entry
                JR @Controls.UnknownD833.PointD872


PointD872:      JR NZ, @Controls.UnknownD833.PointD879                          ; переход, если флаг Z сброшен


                CALL @Controls.AdvanceRasterUp.Entry
                JR @Controls.UnknownD833.PointD87C


PointD879:      CALL @Controls.AdvanceRasterDown.Entry
PointD87C:      EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JR NZ, @Controls.UnknownD833.PointD896                          ; переход, если флаг Z сброшен


                SCF
                RR B
                JR C, @Controls.UnknownD833.PointD89B                           ; переход, если флаг Carry установлен


PointD88A:      EXX
                ADD HL, BC
                INC C
                EX AF, AF'
                CP C
                JR Z, @Controls.UnknownD833.PointD8A4                           ; переход, если флаг Z установлен


                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
PointD896:      JP NZ, @Controls.UnknownD833.PointD852                          ; переход, если флаг Z сброшен


                JR @Controls.UnknownD833.PointD8BB


PointD89B:      INC E
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD833.PointD8AC                           ; переход, если флаг Z установлен


                LD B, #80
                JR @Controls.UnknownD833.PointD88A


PointD8A4:      EX AF, AF'
                JP @Controls.UnknownD633.PointD696


PointD8A8:      EX AF, AF'
                JP @Controls.UnknownD633.PointD6D7


PointD8AC:      LD SP, (@ControlsRasterStepState.SavedSP)
                POP AF
                RET


PointD8B2:      INC E
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD833.PointD8AC                           ; переход, если флаг Z установлен


                LD B, #80
                JR @Controls.UnknownD833.PointD8C0


PointD8BB:      SCF
                RR B
                JR C, @Controls.UnknownD833.PointD8B2                           ; переход, если флаг Carry установлен


PointD8C0:      EXX
                ADD HL, BC
                INC C
                JR Z, @Controls.UnknownD833.PointD8AC                           ; переход, если флаг Z установлен


                EX AF, AF'
                CP C
                JR Z, @Controls.UnknownD833.PointD8A8                           ; переход, если флаг Z установлен


                EX AF, AF'
                ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Controls.UnknownD833.PointD8BB                           ; переход, если флаг Z установлен


                EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                EXX
                LD D, L
                LD L, E
                LD A, B
                AND (HL)
                LD (HL), A
                LD A, B
                CPL
                AND IXL
                OR (HL)
                LD (HL), A
                LD A, D
                SUB E
                DEC A
                SRL A
                JR NC, @Controls.UnknownD833.PointD8F0                          ; переход, если флаг Carry сброшен


                INC L
                LD (#D8EF), A
                LD A, IXL
                LD (HL), A
                LD A, #00
                ; вычисление изменяемого смещения JR как 16-A для выбора A операций PUSH AF
                ; после подготовки AF оба его байта равны IXL, затем SP заменяется адресом правой границы растра
PointD8F0:      LD L, D
                SUB #11
                CPL
                LD (#D900), A
                PUSH DE
                LD E, IXL
                LD D, E
                PUSH DE
                POP AF
                POP DE
                LD SP, HL
PointD8FF:      JR @Controls.UnknownD833.PointD8FF


                ; -----------------------------------------
                ; Динамический хвост, SP направлен в растр и AF содержит два байта рисунка
                ; Каждый вход PushN записывает N пар справа налево, прежний CPU-стек восстанавливается после цепочки
                ; IRQ во время этого участка не входят в доказанный договор
                ; -----------------------------------------
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
                ; чтение Mode после заполнения, нуль выбирает движение вверх, ненулевой байт вниз
ResumeRows:     LD A, (@ControlsEvenSpanState.Mode)
                ; проверка направления следующей строки по нулевому состоянию Mode
                AND A
                ; восстановление CPU-стека из SavedSP перед настоящим CALL помощника строки
                LD SP, (@ControlsRasterStepState.SavedSP)
                JR NZ, @Controls.UnknownD833.ResumeDown                         ; переход, если Mode ненулевой, выполнить AdvanceRasterDown через ResumeDown

                ; шаг вверх, помощник может завершить весь рисователь через сохранённую рамку
                CALL @Controls.AdvanceRasterUp.Entry
                JR @Controls.UnknownD833.PointD8BB

                ; шаг вниз с тем же возможным нелокальным завершением рисователя
ResumeDown:     CALL @Controls.AdvanceRasterDown.Entry
                JR @Controls.UnknownD833.PointD8BB

                ; -----------------------------------------

                endmodule
                endmodule
