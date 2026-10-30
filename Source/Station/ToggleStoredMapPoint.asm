                module Station
                module ToggleStoredMapPoint
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [физические пятибайтовые записи, точные диапазоны сдвигов и общие хвосты](../../Docs/StoredPointEdits.md)
; -----------------------------------------
; Удаление выбранного ключа из первого списка либо запись в его первую пустую запись
; исходная запись 4, файловые смещения #1E0D..#1E46
; In:
;   MapSelection задаёт выбранный ключ и Variant, A имеет достижимый отрицательный не-FF ограничитель и доступен по шагу FStoredMapPoint
;   действуют договоры BeginScreenUpdate, TryDrawSystemInfo, DrawMapPanel и EndScreenUpdate, две записи панелей и данные карты готовы
;   paging доступен, указатель согласован с фоном, адресные и индексные таблицы готовы, все фактические HALT пробуждаются окружением
;   стек вне экранных областей и переключаемого окна, банк станции 0 доступен
; Out:
;   VariantPanelState.RefreshPending=1 устанавливается до поиска, даже если полный A не будет изменён
;   при совпадении первых четырёх байтов удаляется первая совпавшая запись через RemoveFoundStoredPoint, пятый байт в ключ поиска не входит
;   при отсутствии совпадения ищется первая запись с первым байтом FF, в неё записаны оба слова и Variant выбранного ключа
;   порядок остальных записей и ограничитель сохраняются, после изменения выполняется общий рисунок
;   если свободной записи нет, возврат до рисунка с A=отрицательный маркер конца, F от DEC этого маркера с сохранённым Carry
;   на раннем выходе HL у маркера конца, BC=FStoredMapPoint, DE от FindStoredMapPoint, AF' от возврата SelectRamBank, остальные альтернативные пары и IX,IY сохранены
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, bitmap и рабочие данные общего рисунка, первый список и Pending
; Note:
;   два слова ищутся настоящим банковым FindStoredMapPoint, его AF сохранён через EX AF,AF' вокруг возврата страницы
;   A принимает 7F как занятую положительную запись, а FF как пустую, эти случаи не объединены с отрицательным не-FF концом
;   после записи Variant исполнение последовательно продолжается в отдельном файле общего рисунка
; -----------------------------------------
                ; запрос отложенного обновления панели планет до возможного изменения первого списка
Entry:          LD A, #01
                LD (@VariantPanelState.RefreshPending), A
                ; выбор KARTA для проверки наличия выбранного четырёхбайтового ключа в A
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                CALL @Map.FindStoredMapPoint.Entry
                ; сохранение результата поиска в AF альтернативного набора на время возврата банка
                EX AF, AF'
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                EX AF, AF'
                JP P, @Station.RemoveFoundStoredPoint.Entry                     ; переход, если ключ найден в A, удалить его первую совпавшую запись

                ; поиск первой физической пустоты FF с шагом FStoredMapPoint
                LD HL, @StoredMapPointsA.Point00
                LD BC, FStoredMapPoint
                ; проверка первого байта следующей записи A, остальные поля пока не читаются
FindEmpty:      LD A, (HL)
                INC A
                JR Z, @Station.ToggleStoredMapPoint.StoreSelected               ; переход, если первый байт равен FF, записать выбранный ключ в эту пустоту

                ; проверка отрицательного не-FF конца после исключения пустоты
                DEC A
                RET M                                                           ; выход, если достигнут отрицательный не-FF конец A без свободной записи

                ; расчёт адреса следующей пятибайтовой записи A
                ADD HL, BC
                JR @Station.ToggleStoredMapPoint.FindEmpty

                ; запись физического FirstWord выбранного ключа в найденную пустоту
StoreSelected:  LD DE, (@MapSelection.FirstWord)
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                ; запись физического SecondWord сразу после первого слова
                LD DE, (@MapSelection.SecondWord)
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                ; запись пятого поля Variant, затем последовательное продолжение общего рисунка
                LD A, (@MapSelection.Variant)
                LD (HL), A
                ; JP @Station.RefreshStoredMapPanels.Entry, продолжение в RefreshStoredMapPanels.asm

                endmodule
                endmodule
