                module ArchiveEngine
                module MoveFirstApartLeft
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; разведение бойцов, смещение первого на один столбец
                ; In:
                ;   BC - C, сохранённый X первого бойца
                ; Out:
                ;   X первого бойца уменьшен на единицу по модулю байта
                ; Corrupt:
                ;   AF
                ; -----------------------------------------
Entry:          LD A, C
                DEC A
                LD (@ArchiveFighters.First.PositionX), A
                RET

                endmodule
                endmodule
