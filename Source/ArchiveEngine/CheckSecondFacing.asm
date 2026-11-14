                module ArchiveEngine
                module CheckSecondFacing
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; запрос разворота второго бойца при несоответствии стороны взаимному X
                ; In:
                ;   обе записи бойцов содержат базовый X и сторону
                ; Out:
                ;   может измениться Request или TurnPending второй записи
                ; Corrupt:
                ;   BC, AF, IX
                ; -----------------------------------------
                ; проверка текущей стороны второго бойца
Entry:          LD A, (@ArchiveFighters.Second)
                OR A
                JR Z, @ArchiveEngine.CheckSecondFacing.Direct                   ; переход, если сторона прямая, проверить противоположное условие

                ; сравнение X второго и первого бойцов для зеркальной стороны
                LD A, (@ArchiveFighters.First.PositionX)
                LD B, A
                LD A, (@ArchiveFighters.Second.PositionX)
                CP B
                JR NC, @ArchiveEngine.CheckSecondFacing.Done                    ; переход, если второй боец справа или на том же X, оставить сторону

                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.RequestFighterTurn.Entry
Done:           RET

                ; сравнение тех же X для прямой стороны
Direct:         LD A, (@ArchiveFighters.First.PositionX)
                LD B, A
                LD A, (@ArchiveFighters.Second.PositionX)
                CP B
                JR C, @ArchiveEngine.CheckSecondFacing.Done                     ; переход, если второй боец левее первого, оставить сторону

                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.RequestFighterTurn.Entry
                JR @ArchiveEngine.CheckSecondFacing.Done

                endmodule
                endmodule
