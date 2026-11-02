                module Controls
                module UnknownD633
                ; Документация [быстрая заливка через SP](../../Docs/ControlsPushSpans.md)
; Документация [Controls](../../Docs/FunctionDetails/Controls.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 22, файловые смещения #1633..#1726
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
                SUB L
                JR NC, @Controls.UnknownD633.PointD649                          ; переход, если флаг Carry сброшен


                LD A, (@ControlsEvenSpanState.Mode)
                AND A
                JR NZ, @Controls.UnknownD633.PointD644                          ; переход, если флаг Z сброшен


                LD A, #7F
                CP H
                JR C, @Controls.UnknownD633.PointD64B                           ; переход, если флаг Carry установлен


                JR @Controls.UnknownD633.PointD649


PointD644:      LD A, #8B
                CP H
                JR NC, @Controls.UnknownD633.PointD64B                          ; переход, если флаг Carry сброшен


PointD649:      POP AF
                RET


PointD64B:      LD (@ControlsRasterStepState.SavedSP), SP
PointD64F:      LD A, C
                AND (HL)
                LD D, A
                LD A, C
                CPL
                AND IXL
                OR D
                LD (HL), A
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
                JR NC, @Controls.UnknownD633.PointD673                          ; переход, если флаг Carry сброшен


                INC L
                LD (#D672), A
                LD A, IXL
                LD (HL), A
                LD A, #00
PointD673:      CALL @Controls.FillEvenSpan.Entry
                JR NZ, @Controls.UnknownD633.PointD67E                          ; переход, если флаг Z сброшен


                CALL @Controls.AdvanceRasterUp.Entry
                JP @Controls.UnknownD633.PointD681


PointD67E:      CALL @Controls.AdvanceRasterDown.Entry
PointD681:      EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                BIT 7, H
                EXX
                JR NZ, @Controls.UnknownD633.PointD69A                          ; переход, если флаг Z сброшен


                SCF
                RR B
                JR C, @Controls.UnknownD633.PointD69F                           ; переход, если флаг Carry установлен


PointD68F:      SLL C
                JR C, @Controls.UnknownD633.PointD6A8                           ; переход, если флаг Carry установлен


PointD693:      EXX
                ADD HL, BC
                INC C
PointD696:      ADD HL, BC
                BIT 7, H
                EXX
PointD69A:      JP NZ, @Controls.UnknownD633.PointD64F                          ; переход, если флаг Z сброшен


                JR @Controls.UnknownD633.PointD6C9


PointD69F:      INC E
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD633.PointD6B1                           ; переход, если флаг Z установлен


                LD B, #80
                JR @Controls.UnknownD633.PointD68F


PointD6A8:      DEC L
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD633.PointD6B1                           ; переход, если флаг Z установлен


                LD C, #01
                JR @Controls.UnknownD633.PointD693


PointD6B1:      LD SP, (@ControlsRasterStepState.SavedSP)
                POP AF
                RET


PointD6B7:      INC E
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD633.PointD6B1                           ; переход, если флаг Z установлен


                LD B, #80
                JR @Controls.UnknownD633.PointD6CE


PointD6C0:      DEC L
                LD A, L
                SUB E
                JR Z, @Controls.UnknownD633.PointD6B1                           ; переход, если флаг Z установлен


                LD C, #01
                JR @Controls.UnknownD633.PointD6D2


PointD6C9:      SCF
                RR B
                JR C, @Controls.UnknownD633.PointD6B7                           ; переход, если флаг Carry установлен


PointD6CE:      SLL C
                JR C, @Controls.UnknownD633.PointD6C0                           ; переход, если флаг Carry установлен


PointD6D2:      EXX
                ADD HL, BC
                INC C
                JR Z, @Controls.UnknownD633.PointD6B1                           ; переход, если флаг Z установлен


PointD6D7:      ADD HL, BC
                BIT 7, H
                EXX
                JR Z, @Controls.UnknownD633.PointD6C9                           ; переход, если флаг Z установлен


                EXX
                ADD HL, DE
                INC E
                ADD HL, DE
                EXX
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
                JR NC, @Controls.UnknownD633.PointD706                          ; переход, если флаг Carry сброшен


                INC L
                LD (#D705), A
                LD A, IXL
                LD (HL), A
                LD A, #00
                ; (0) порядок перед UnknownD727.asm обязателен для продолжения после последнего PUSH
                ; вычисление изменяемого смещения JR как 16-A для выбора A операций PUSH AF
                ; после подготовки AF оба его байта равны IXL, затем SP заменяется адресом правой границы растра
PointD706:      LD L, D
                SUB #11
                CPL
                LD (#D716), A
                PUSH DE
                LD E, IXL
                LD D, E
                PUSH DE
                POP AF
                POP DE
                LD SP, HL
                JR @Controls.UnknownD727.Entry


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
                ; JP @Controls.UnknownD727.Entry, продолжение в UnknownD727.asm

                ; -----------------------------------------

                endmodule
                endmodule
