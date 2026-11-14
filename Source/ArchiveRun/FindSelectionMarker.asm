                module ArchiveRun
                module FindSelectionMarker
                ; Документация [архивное меню](../../Docs/StartArchiveMenu.md)
                ; -----------------------------------------
                ; расчёт адреса первого байта стрелки текущего пункта
                ; In:
                ;   индекс выбранного пункта установлен
                ; Out:
                ;   HL - адрес растра в окне #C000 для Y = 112 + 8 × индекс и X = 105
                ; Corrupt:
                ;   HL, DE, AF
                ; -----------------------------------------
                ; расчёт координат строки и перевод адреса в банковое окно
Entry:          LD A, (@ArchiveRunState.Menu.Selected)
                SLA A
                SLA A
                SLA A
                ADD A, @ArchiveRunConst.MarkerBaseY
                LD D, A
                LD E, @ArchiveRunConst.MarkerPixelX
                CALL @ArchiveRun.PixelAddress.Entry
                LD A, H
                OR #80
                LD H, A
                RET

                endmodule
                endmodule
