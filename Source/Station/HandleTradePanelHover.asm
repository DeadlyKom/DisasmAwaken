                module Station
                module HandleTradePanelHover
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [зависимость подсветки от рисунка, событие колонки, банковый запуск и дополнительные входы рисователя](../../Docs/TradePanel.md)
                ; -----------------------------------------
                ; Хвостовой вход обновления торговой строки наведения
                ; исходная запись 4, файловые смещения #129A..#129C
                ; In:
                ;   тот же контекст и условия, что у UpdateTradeRowHover
                ; Out:
                ;   хвостовой JP передаёт исходный возврат UpdateTradeRowHover, все выходы по его договору
                ; Corrupt:
                ;   HL, DE, BC, AF, AF' на обновлении по UpdateTradeRowHover
                ; Note:
                ;   это Event вход наведения, Event+3 начинается в HandleTradePanelClick, нового CALL этот вход не создаёт
                ; -----------------------------------------
                ; передача наведения торговой строке, соседнее действие начинается по Event+3
Entry:          JP @Station.UpdateTradeRowHover.Entry

                endmodule
                endmodule
