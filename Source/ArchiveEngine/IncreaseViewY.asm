                module ArchiveEngine
                module IncreaseViewY
                ; Документация [границы окна](../../Docs/Scene1PixelPairs.md#полный-фон-кадра)
                ; -----------------------------------------
                ; увеличение номера исходной строки начала окна до предельного смещения
                ; In:
                ;   VerticalOffset и MaxVertical заданы в строках рабочего растра
                ; Out:
                ;   при смещении меньше предела VerticalOffset увеличен на единицу
                ; Corrupt:
                ;   HL, AF
                ; Note:
                ;   штатный переход на этот вход не установлен
                ; -----------------------------------------
                ; сравнение текущего смещения с младшим байтом предела
Entry:          LD A, (@ArchiveEngineScene.View.VerticalOffset)
                LD HL, @ArchiveEngineScene.View.MaxVertical
                CP (HL)
                RET NC                                                          ; выход, если достигнут предельный номер строки или значение уже больше него

                INC A
                LD (@ArchiveEngineScene.View.VerticalOffset), A
                RET

                endmodule
                endmodule
