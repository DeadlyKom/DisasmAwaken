                module Station
                module AnimateShipPreview
                ; Документация [станционная цепочка, геометрия и настоящее IM2-пробуждение](../../Docs/ShipPreviewCallbacks.md)
                ; -----------------------------------------
                ; Периодическое рисование кадра последней корабельной панели либо переход к её отложенному обновлению
                ; исходная запись 4, файловые смещения #0B96..#0BBE
                ; In:
                ;   HL, DE, BC исходный контекст быстрых ветвей, AF не является параметром
                ;   PendingRedraw ненулевой выбирает RefreshShipPanels, при нуле проверяется последний точный указатель списка
                ;   для кадра уже настроены окно и D3D предыдущим DrawShipPreview, действуют договоры FillWindowBody и экранного обновления
                ;   Selector читается из собственного изменяемого операнда, HALT требует подходящего IRQ, аппаратная блокировка банка снята
                ; Out:
                ;   при PendingRedraw!=0 действует выходной договор RefreshShipPanels без дополнительного слова CPU-возврата
                ;   при другом последнем обработчике HL=(LastDraw-DrawShipPreview) AND FFFF, DE=DrawShipPreview, BC сохранён
                ;   A быстрого отказа равен старшему байту LastDraw, F от SBC HL,DE с предварительно сброшенным Carry
                ;   при таком отказе HL', DE', BC', AF', IX, IY, I и IFF сохранены, память кроме служебного CALL не меняется
                ;   кадр сохраняет снимок в банке 7, заполняет тело окна и рисует RenderPreviewFrame с исходным Selector
                ;   HL, DE и BC кадра принадлежат RenderPreviewFrame, A=10, F=0C после выбора страницы 18 перед EndScreenUpdate
                ;   HL', DE', BC', IX, IY кадра сохраняются после RenderPreviewFrame, AF' также зависит от ResumePointer
                ;   рабочий выход даёт CurrentPage=10, UpdateBlocked=0, IFF=1, SP входному+2, периодический callback здесь не меняется
                ; Corrupt:
                ;   HL, DE, AF при несовпадении, остальные регистры и память по RefreshShipPanels либо полному кадру
                ; Note:
                ;   сравнивается адрес последнего рисователя, а не индекс его элемента и не текущее состояние opcode C9 этого адреса
                ;   BeginScreenUpdate и EndScreenUpdate окружают FillWindowBody, HALT, выбор банка 4 и весь D3D
                ;   после кадра выбирается банк 0 с сохранённым скрытым экраном, только затем EndScreenUpdate показывает базовый экран
                ;   проверены 11 исходных моделей и оба результата классификации последнего адреса, IRQ только в HALT, музыка выключена
                ; -----------------------------------------
                ; чтение изменяемого запроса отложенной перерисовки
Entry:          LD A, #00
                ; проверка полного байта запроса до поиска последнего обработчика
                OR A
                JR NZ, @Station.RefreshShipPanels.Entry                         ; переход, если PendingRedraw ненулевой, выполнить отложенное обновление

                ; поиск последнего обработчика текущего списка, пустой список имеет отдельный договор GetLastDraw
                CALL @Station.GetLastDraw.Entry
                LD DE, @Station.DrawShipPreview.Entry
                ; сброс Carry перед сравнением полного адреса с рисователем просмотра
                OR A
                SBC HL, DE
                RET NZ                                                          ; выход, если последний обработчик не равен DrawShipPreview.Entry

                ; снимок старого экрана и переключение на скрытое рисование
                CALL @Station.BeginScreenUpdate.Entry
                ; заполнение тела настроенного окна по текущему FillMode
                CALL @Station.FillWindowBody.Entry
                ; ожидание IRQ после заполнения тела, банк станции пока остаётся выбранным
                HALT
                ; выбор банка 4 для полного кадра
                LD A, @ShipPreviewConst.PreviewPage
                CALL @Station.SelectRamBank.Entry
                ; чтение полного селектора из собственного изменяемого операнда
                LD A, #00
                ; полный кадр D3D, включая восстановление настоящего CPU-SP и EI
                CALL @D3D.RenderPreviewFrame.Entry
                ; выбор окна банка 0 при ещё показанном снимке банка 7
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; возобновление указателя и показ обновлённого базового экрана
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
