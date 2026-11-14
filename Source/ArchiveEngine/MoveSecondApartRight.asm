                module ArchiveEngine
                module MoveSecondApartRight
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; разведение бойцов, смещение второго на один столбец
                ; In:
                ;   BC - B, сохранённый X второго бойца
                ; Out:
                ;   X второго бойца увеличен на единицу по модулю байта
                ; Corrupt:
                ;   AF
                ; -----------------------------------------
Entry:          LD A, B
                INC A
                LD (@ArchiveFighters.Second.PositionX), A
                RET

                endmodule
                endmodule
