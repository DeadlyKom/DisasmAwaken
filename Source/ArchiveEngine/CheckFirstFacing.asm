                module ArchiveEngine
                module CheckFirstFacing
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; запрос разворота первого бойца при несоответствии стороны взаимному X
                ; In:
                ;   обе записи бойцов содержат базовый X и сторону
                ; Out:
                ;   может измениться Request или TurnPending первой записи
                ; Corrupt:
                ;   BC, AF, IX
                ; -----------------------------------------
                ; проверка текущей стороны первого бойца
Entry:          LD A, (@ArchiveFighters.First)
                OR A
                JR Z, @ArchiveEngine.CheckFirstFacing.Direct                    ; переход, если сторона прямая, проверить противоположное условие

                ; сравнение X первого и второго бойцов для зеркальной стороны
                LD A, (@ArchiveFighters.Second.PositionX)
                LD B, A
                LD A, (@ArchiveFighters.First.PositionX)
                CP B
                JR NC, @ArchiveEngine.CheckFirstFacing.Done                     ; переход, если первый боец справа или на том же X, оставить сторону

                LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.RequestFighterTurn.Entry
Done:           RET

                ; сравнение тех же X для прямой стороны
Direct:         LD A, (@ArchiveFighters.Second.PositionX)
                LD B, A
                LD A, (@ArchiveFighters.First.PositionX)
                CP B
                JR C, @ArchiveEngine.CheckFirstFacing.Done                      ; переход, если первый боец левее второго, оставить сторону

                LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.RequestFighterTurn.Entry
                JR @ArchiveEngine.CheckFirstFacing.Done

                endmodule
                endmodule
