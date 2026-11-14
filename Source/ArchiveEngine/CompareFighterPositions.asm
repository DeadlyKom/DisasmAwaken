                module ArchiveEngine
                module CompareFighterPositions
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; разведение близких бойцов по X при равных базовых Y
                ; In:
                ;   обе рабочие записи содержат позицию и MoveX
                ; Out:
                ;   при разных Y проверена ориентация, при одинаковом Y близкие движущиеся бойцы раздвинуты
                ; Corrupt:
                ;   BC, AF, IX
                ; Note:
                ;   признак движения берётся из младшего байта MoveX, равные X направляют первого вправо, второго влево
                ; -----------------------------------------
                ; сравнение базовых вертикальных координат
Entry:          LD A, (@ArchiveFighters.First.PositionY)
                LD B, A
                LD A, (@ArchiveFighters.Second.PositionY)
                CP B
                JP NZ, @ArchiveEngine.ReconcileFacing.Entry                     ; переход, если базовые Y различаются, проверить стороны бойцов

                ; выбор порядка бойцов по X
                LD A, (@ArchiveFighters.Second.PositionX)
                LD B, A
                LD A, (@ArchiveFighters.First.PositionX)
                LD C, A
                CP B
                JR C, @ArchiveEngine.CompareFighterPositions.FirstAtLeft        ; переход, если первый боец левее второго

                ; расчёт расстояния, первый боец справа или на том же X
                LD A, C
                SUB B
                CP #05
                RET NC                                                          ; выход, если расстояние не меньше пяти

                ; проверка движения первого и второго бойцов перед раздвижением
                LD A, (@ArchiveFighters.First.MoveX.Low)
                OR A
                CALL NZ, @ArchiveEngine.MoveFirstApartRight.Entry               ; вызов, если первый боец движется, сдвинуть его вправо
                LD A, (@ArchiveFighters.Second.MoveX.Low)
                OR A
                CALL NZ, @ArchiveEngine.MoveSecondApartLeft.Entry               ; вызов, если второй боец движется, сдвинуть его влево
                RET

                ; расчёт расстояния, первый боец слева
FirstAtLeft:    LD A, B
                SUB C
                CP #05
                RET NC                                                          ; выход, если расстояние не меньше пяти

                ; проверка движения обоих бойцов для обратного порядка
                LD A, (@ArchiveFighters.First.MoveX.Low)
                OR A
                CALL NZ, @ArchiveEngine.MoveFirstApartLeft.Entry                ; вызов, если первый боец движется, сдвинуть его влево
                LD A, (@ArchiveFighters.Second.MoveX.Low)
                OR A
                CALL NZ, @ArchiveEngine.MoveSecondApartRight.Entry              ; вызов, если второй боец движется, сдвинуть его вправо
                RET

                endmodule
                endmodule
