                module Station
                module ToggleSecondaryMapPoint
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [физические пятибайтовые записи, точные диапазоны сдвигов и общие хвосты](../../Docs/StoredPointEdits.md)
; -----------------------------------------
; Удаление найденной точки B либо вставка относительно курсора с исходной особенностью сдвига
; исходная запись 4, файловые смещения #1E6C..#1EC9
; In:
;   MapSelection задаёт выбранные два слова и Variant, Cursor у доступной записи B, доступен конец по шагу пять
;   для обычного B занятые первые байты 00..7E, пустые FF, исходный ограничитель 80, доступны данные кадра вставки и договор нормализатора
;   действуют договоры BeginScreenUpdate, TryDrawSystemInfo, DrawMapPanel и EndScreenUpdate, две записи панелей и данные карты готовы
;   paging доступен, указатель согласован с фоном, адресные и индексные таблицы готовы, все фактические HALT пробуждаются окружением
;   стек вне экранных областей и переключаемого окна, банк станции 0 доступен
; Out:
;   Pending=1 до поиска, существующий четырёхбайтовый ключ удаляется через RemoveFoundSecondaryPoint независимо от Variant
;   если ключ отсутствует и Cursor у FF, новая запись заменяет именно текущую пустоту
;   иначе при следующей FF новая запись помещается сразу после Cursor и Cursor переходит к ней
;   если следующая запись занята, ищется более дальняя FF, исходный LDDR сдвигает Cursor..Hole-1 на пять байтов вправо, новый ключ записан на старом Cursor
;   Cursor в последнем случае не продвигается, это исходное отличие от пути немедленной пустоты
;   после записи новых пяти байтов выполняется RefreshSecondaryListPanels, нормализатор может дополнительно изменить Cursor
;   при достижении первого байта 7F..FE во время поиска места возврат выполнен до изменения B и общего рисунка, Pending остаётся 1
;   на ранней ветви сразу следующего конца HL у этого конца, DE=FStoredMapPoint, F от INC маркера, при дальнем конце HL восстановлен к позиции сразу после входного Cursor
;   IX,IY и альтернативные общие пары сохраняются на ранних выходах, AF' содержит страницу возврата и флаги её OR
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, bitmap и рабочие данные общего рисунка, физический блок B, Cursor, порядок и Pending
; Note:
;   FSecondaryInsertFrame.SavedAddress сначала хранит Insert=Cursor+5, затем после POP DE тот же слот хранит Hole
;   длина LDDR равна Hole+5-Insert, его источник Cursor..Hole-1, приёмник Insert..Hole+4, прежние поля пустоты перезаписываются сдвигом
;   RET M и JP M после INC трактуют 7F как конец места, хотя FindSecondaryMapPoint ещё может искать ключ 7F, эта неодинаковость сохранена
;   проверены все 1024 схемы пустот и каждый из десяти курсоров, в том числе 1793 сдвига
; -----------------------------------------
                ; запрос обновления панели планет до поиска и возможного раннего отказа
Entry:          LD A, #01
                LD (@VariantPanelState.RefreshPending), A
                ; выбор KARTA для поиска выбранного ключа в B
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                CALL @Map.FindSecondaryMapPoint.Entry
                ; сохранение точного AF поиска вокруг возврата станционного банка
                EX AF, AF'
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                EX AF, AF'
                JP P, @Station.RemoveFoundSecondaryPoint.Entry                  ; переход, если выбранный ключ найден в B, удалить физическую запись

                ; проверка пустоты текущей записи B, при FF новая запись заменит её на месте
                LD HL, (@SecondaryPointState.Cursor)
                LD A, (HL)
                INC A
                JR Z, @Station.ToggleSecondaryMapPoint.StoreSelected            ; переход, если текущая запись пуста, записать выбранные пять байтов здесь

                ; расчёт адреса следующей записи для проверки немедленного свободного места
                LD DE, FStoredMapPoint
                ADD HL, DE
                ; проверка первого байта следующей записи через INC, 7F..FE заканчивают поиск места
                LD A, (HL)
                INC A
                RET M                                                           ; выход, если следующая запись содержит первый байт 7F..FE, места для вставки нет

                JR Z, @Station.ToggleSecondaryMapPoint.StoreSelected            ; переход, если следующая запись пуста, записать новый ключ сразу после Cursor

                ; подготовка шага и сохранение Insert=Cursor+5 в FSecondaryInsertFrame.SavedAddress
                LD BC, FStoredMapPoint
                PUSH HL
                ; расчёт адреса следующей проверяемой записи при поиске более дальней пустоты
FindHole:       ADD HL, BC
                ; проверка конца и пустоты после INC первого байта дальней записи
                LD A, (HL)
                INC A
                JP M, @Station.ToggleSecondaryMapPoint.NoHole                   ; переход, если достигнут первый байт 7F..FE, восстановить сохранённый адрес и вернуть отказ

                JR NZ, @Station.ToggleSecondaryMapPoint.FindHole                ; переход, если запись не пуста, продолжить поиск более дальней FF

                ; восстановление Insert в DE и повторное использование стекового слота для адреса Hole
                POP DE
                PUSH HL
                ; расчёт длины исходного сдвига Hole+5-Insert, включающей запись Cursor перед Insert
                ADD HL, BC
                OR A
                SBC HL, DE
                LD B, H
                LD C, L
                ; расчёт конца приёмника Hole+4 перед перекрывающимся обратным переносом
                ADD HL, DE
                DEC HL
                EX DE, HL
                ; восстановление Hole и расчёт конца источника Hole-1
                POP HL
                DEC HL
                ; перенос Cursor..Hole-1 вправо на одну запись, исходная асимметрия вставки сохранена
                LDDR
                ; возврат HL к старому Cursor после LDDR, именно сюда будет записан новый ключ
                INC HL
                ; чтение FirstWord нового ключа и сохранение фактической позиции вставки в Cursor
StoreSelected:  LD DE, (@MapSelection.FirstWord)
                LD (@SecondaryPointState.Cursor), HL
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                ; запись SecondWord в физическое второе поле
                LD DE, (@MapSelection.SecondWord)
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                ; запись Variant и переход к нормализации B и общему рисунку
                LD A, (@MapSelection.Variant)
                LD (HL), A
                JR @Station.RefreshSecondaryListPanels.Entry

                ; снятие FSecondaryInsertFrame без изменения списка при отсутствии дальней пустоты
NoHole:         POP HL
                RET

                endmodule
                endmodule
