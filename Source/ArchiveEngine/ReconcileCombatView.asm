                module ArchiveEngine
                module ReconcileCombatView
                ; Документация [кадры и действия](../../Docs/ArchiveEngineAnimation.md)
                ; -----------------------------------------
                ; согласование вертикального смещения окна и взаимного положения бойцов
                ; In:
                ;   рабочие записи содержат базовые и рисуемые координаты
                ; Out:
                ;   вертикальное смещение выбрано по наибольшему выступающему кадру
                ;   при нулевом кандидате проверено взаимное положение бойцов
                ; Corrupt:
                ;   HL, BC, AF, IX
                ; -----------------------------------------
                ; расчёт максимального вертикального смещения по двум записям
Entry:          LD B, #00
                LD IX, @ArchiveFighters.First
                CALL @ArchiveEngine.AccumulateVerticalOffset.Entry
                LD IX, @ArchiveFighters.Second
                CALL @ArchiveEngine.AccumulateVerticalOffset.Entry

                ; проверка, потребовался ли вертикальный сдвиг окна
                LD A, B
                OR A
                RET NZ                                                          ; выход, если требуется ненулевое вертикальное смещение

                XOR A
                LD (@ArchiveEngineScene.View.VerticalOffset), A
                CALL @ArchiveEngine.CompareFighterPositions.Entry
                RET

                endmodule
                endmodule
