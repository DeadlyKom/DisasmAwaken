                module Action
                module Unknown6054
                ; Документация [межбанковые вызовы очереди](../../Docs/ActionTextQueueCalls.md)
                ; -----------------------------------------
                ; Unknown, отдельная цепочка после обёртки очереди ещё не разобрана полностью
                ; исходная запись 17, файловые смещения #0291..#02EA
                ; In:
                ;   Unknown, алгоритм и полный входной договор цепочки ещё не доказаны
                ; Out:
                ;   Unknown, эта цепочка не является продолжением завершившейся обёртки 6040
                ; Corrupt:
                ;   Unknown, включая HL, DE, BC, AF, HL', DE', BC', AF', IX, IY и состояние отображения памяти
                ; Note:
                ;   выделение соседней проверенной обёртки не доказывает смысл оставшихся вызовов и аппаратных ожиданий
                ; -----------------------------------------
Entry:          PUSH DE
                LD DE, #F2A5
                CALL @Action.QueueTextItemBank1.Entry
                POP DE
                LD HL, #EE4D
                LD (#ECF6), HL
                LD A, #3F
                LD I, A
                LD IY, #5C3A
                LD B, #64
Point606C:      PUSH BC
                LD DE, #8000
                LD A, R
                LD L, A
                LD H, #05
                LD BC, #0C00
                LDIR
                EI
                HALT
                DI
                LD A, #11
                CALL @Action.SelectMemoryPage.Entry
                CALL @Controls.CopyViewportToScreen.Entry
                CALL #ECA2
                LD A, #10
                CALL @Action.SelectMemoryPage.Entry
                CALL @Action.UnknownECA8.Entry
                POP BC
                DEC B
                JP NZ, @Action.Unknown6054.Point60A3                            ; переход, если флаг Z сброшен


                LD B, #01
                XOR A
                IN A, (#FE)
                AND #1F
                CP #1F
                JR Z, @Action.Unknown6054.Point606C                             ; переход, если флаг Z установлен


                JP @Action.UpdateFrame.PointAAC4


Point60A3:      LD A, #01
                XOR A
                IN A, (#FE)
                AND #1F
                CP #1F
                JR @Action.Unknown6054.Point606C


                endmodule
                endmodule
