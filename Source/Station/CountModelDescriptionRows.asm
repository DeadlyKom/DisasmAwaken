                module Station
                module CountModelDescriptionRows
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [реальные страницы, выходной AF выбора банка и сохранённая граница прокрутки](../../Docs/DescriptionBankCalls.md)
                ; -----------------------------------------
                ; Банковый подсчёт описания модели с записью полного слова границы прокрутки
                ; исходная запись 4, файловые смещения #0C0F..#0C23
                ; In:
                ;   ShipPanelState.Selector, RowOperand, BaseOperand и окно подготовлены по договору D3D.CountPreviewTextRows
                ;   порт и CurrentPage согласованы, станционный банк 0, paging не заблокирован, CPU-стек вне сменяемого окна
                ; Out:
                ;   HL, DE, BC - результат настоящего D3D.CountPreviewTextRows, DE полное 16-битное число сухих проходов
                ;   ModelDescriptionState.RowCount получает DE после возврата в банк 0, это операнд будущего LD HL,nn перед ScrollState.EndLimit
                ;   AF - A=(исходная CurrentPage AND F8) OR 10, F от логического OR страницы, флаги подсчёта не возвращаются
                ;   все альтернативные и индексные регистры, I, IFF и IM сохраняются, SP обычного возврата равен входному SP+2
                ;   порт и CurrentPage посещают банк 4 и возвращаются в банк 0, экран в сухом подсчёте не рисуется
                ; Corrupt:
                ;   HL, DE, BC, AF
                ; Note:
                ;   сохраняется всё слово DE, хотя печататель при прокрутке использует только младший E, исходное различие не исправляется
                ;   обёртка не меняет ModelDescriptionState.TopRow, сохранение нового начала выполняет вызывающий обработчик
                ;   при незавершении общего подсчёта возврата и записи границы не будет, дополнительные ограничения оригиналом не введены
                ; -----------------------------------------
                ; выбор банка 4 для подсчёта исходного описания
Entry:          LD A, #14
                CALL @Station.SelectRamBank.Entry
                ; чтение того же полного селектора, что использует печататель
                LD A, (@ShipPanelState.Selector)
                ; подсчёт реальных выровненных строк через D3D
                CALL @D3D.CountPreviewTextRows.Entry
                ; возврат в станционный банк до изменения его операнда прокрутки
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                ; сохранение полного DE в существующем слове границы прокрутки
                LD (@ModelDescriptionState.RowCount), DE
                RET

                endmodule
                endmodule
