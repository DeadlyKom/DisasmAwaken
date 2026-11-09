                module Station
                module SelectSecondaryRow
                ; Документация [второй список, общая печать, выбор и события LANG](../../Docs/SecondaryEquipmentRows.md)
                ; -----------------------------------------
                ; Выбор описания либо отправка события 7 или 8 для второго списка
                ; исходная запись 4, перенос STATIONF с 05CE в 6322, адреса 7386..73D6
                ; In:
                ;   Row и TopRow читаются из существующих операндов, EquipmentInfoState.TextIndex доступен
                ;   договоры BeginScreenUpdate, DrawItem00, обоих рисователей и EndScreenUpdate соблюдены
                ;   для повторного выбора LANG загружен в банк 6, выбран станционный банк 0
                ; Out:
                ;   при Row=FF A=0 и F=50 OR входной Carry, прочие регистры и состояние сохранены
                ;   индекс описания равен (Row+TopRow.low+30) AND FF
                ;   при новом индексе TextIndex обновлён, TopRow описания обнулён, выполнена условная перерисовка
                ;   при том же индексе EventCode=7 при нулевом режиме либо 8 иначе, LANG исполнен, банк 0 возвращён
                ;   на обоих путях перерисовки конечные регистры по последнему EndScreenUpdate, обычный SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX по LANG, рисунок и рабочие операнды детей
                ; Note:
                ;   первые 30 индексов относятся к основной таблице описаний, дополнительный набор начинается с 30
                ;   при смене индекса вызывается TryDrawSecondaryList, при повторении прямой DrawSecondaryList
                ;   256 режимов проверены до входа LANG, три профиля исполнили LANG и настоящий полный хвост
                ; -----------------------------------------
                ; проверка FF отсутствующей выбранной строки
Entry:          LD A, (@SecondaryEquipmentState.Row)
                INC A
                RET Z                                                           ; выход, если строка отсутствует, сохранить контекст списка

                ; расчёт общего индекса описания из строки, базы и смещения 30
                DEC A
                LD L, A
                LD A, (@SecondaryEquipmentState.TopRow)
                ADD A, L
                ADD A, #1E
                LD L, A
                ; проверка повторения прежнего индекса описания
                LD A, (@EquipmentInfoState.TextIndex)
                CP L
                JR Z, @Station.SelectSecondaryRow.RepeatChoice                  ; переход, если индекс уже выбран, вызвать событие LANG

                ; обновление индекса описания и обнуление его прокрутки
                LD A, L
                LD (@EquipmentInfoState.TextIndex), A
                LD HL, #0000
                LD (@EquipmentInfoState.TopRow), HL
                ; скрытое обновление описания и второго списка по наличию рисователей
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.TryDrawEquipmentInfo.Entry
                CALL @Station.TryDrawSecondaryList.Entry
                ; показ подготовленного экрана и возврат указателя
                CALL @Station.EndScreenUpdate.Entry
                RET

                ; проверка общего режима перед выбором события 7 или 8
RepeatChoice:   LD A, (@EquipmentTradeState.OwnedMode)
                OR A
                LD A, #07
                JR Z, @Station.SelectSecondaryRow.RunEvent                      ; переход, если режим нулевой, оставить событие 7

                INC A
                ; обновление номера события и выбор банка LANG
RunEvent:       LD (@ScriptCallState.EventCode), A
                LD A, #16
                CALL @Station.SelectRamBank.Entry
                CALL @Text.RunMarketScript.Entry
                ; возврат банка станции после сценария
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                ; скрытое обновление статуса и второго списка после сценария
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem00.Entry
                CALL @Station.DrawSecondaryList.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
