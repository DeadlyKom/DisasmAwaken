                module InterfaceDrawList
                ; Список рисователей с ограничителем #0101, соответствует архивному Sur1 по формату
                ; Документация [список и граница хвоста](../../../Docs/Rendering.md#список-рисователей)
                DW @Station.DrawItem00.Entry
                DW @Station.DrawItem02.Entry
                DW @Station.DrawItem03.Entry
                DW @Station.DrawItem04.Entry
                DW @Station.DrawItem05.Entry
                DW @Station.DrawItem06.Entry
                DW @Station.DrawShipControl.Entry
                DW @Station.DrawItem08.Entry
                DW @Station.DrawItem09.Entry
                DW @Station.DrawWelcomePanel.Entry
End:            DW #0101                                                        ; ограничитель списка обработчиков
                endmodule
