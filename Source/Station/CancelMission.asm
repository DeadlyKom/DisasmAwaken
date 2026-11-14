                module Station
                module CancelMission
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [условия принятия, старшие байты отмены и общий стековый хвост](../../Docs/MissionAction.md)
                ; -----------------------------------------
                ; Расторжение миссии на сохранённом кадре, пересчёт загрузки и денежный штраф
                ; исходная запись 4, файловые смещения #1209..#1260
                ; In:
                ;   HL - H старший байт разности слов ключей, DE - D старший байт слова предлагаемого ключа
                ;   OwnedCargoRows.Row00.QuantityAndMark содержит сырое количество, RequiredTonnage байтовое требование, их запись заменит только L и E
                ;   SP у SavedIY готового FMissionActionFrame, ниже сохранены IX, AF, BC, HL, DE и исходный возврат
                ;   действуют договоры LANG, GenerateMissionOffer, DrawItem00 и общего FinishAction родительской процедуры
                ; Out:
                ;   ActiveCode=0, Row00.QuantityAndMark обнулено при полном займе изменённых HL-DE, иначе получает младший байт разности
                ;   выполнен исходный LANG с событием 11, оба T пересчитали PlayerSaveHeader.Entry.UsedTonnage
                ;   PlayerSaveHeader.Entry.Money получает max(прежние деньги-1000,0)
                ;   выведено сообщение отмены, выполнены два HALT, новое предложение и дополнительный DrawItem00
                ;   HL и DE восстановлены из FMissionActionFrame, BC - B восстановлен из кадра, C=PointerY SHR 3
                ;   AF - A=#FF, F от CP TextWindow.OriginYLow SHR 3 и PointerY SHR 3 при разных строках, иначе от DropItemDraw
                ;   HL', DE', BC', AF' не восстанавливаются общим кадром и соответствуют вложенным игровым и графическим вызовам
                ;   IX и IY восстановлены из FMissionActionFrame перед CloseMenuOnRow
                ;   общий хвост вызывает BeginScreenUpdate, DrawItem31, DrawItem32, DrawItem00 и EndScreenUpdate
                ;   MissionHoverState.Row=#FF, при совпадении строк CloseMenuOnRow удаляет выбранный элемент через DropItemDraw, иначе список не меняется этим вызовом
                ;   конечная страница 10, блокировка указателя снята EndScreenUpdate, I и IFF собственным кодом не меняются
                ;   SP после исходного возврата равен входному SP+14, двенадцать байтов сохранений и два байта PC сняты
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY до восстановления из FMissionActionFrame, R
                ;   MissionState.ActiveCode, Row00.QuantityAndMark, PlayerSaveHeader.Entry.Money и UsedTonnage, MissionHoverState.Row, временные слова CPU-стека
                ;   побочные записи LANG, GenerateMissionOffer, DrawItem00 и общего хвоста BeginScreenUpdate, DrawItem31, DrawItem32, EndScreenUpdate и CloseMenuOnRow
                ; Note:
                ;   это продолжение через JP, собственного кадра CALL и собственных POP до FinishAction нет
                ;   снятие количества не является насыщенным байтовым вычитанием, H и D участвуют в проверке полного займа
                ;   при H больше D младший заём может дать обёрнутый результат, при H меньше D возможно обнуление достаточного количества
                ;   CompletionCode сама ветвь не меняет, генератор изменяет только свои доказанные поля состояния предложения
                ;   смысл старших байтов требования не выдумывается, только младший участвует в замене E
                ;   модель полного действия проверяет настоящий LANG, рисователи и обе ветви CloseMenuOnRow
                ; -----------------------------------------
                ; сброс MissionState.ActiveCode перед изменением Row00.QuantityAndMark в ветви расторжения
Entry:          XOR A
                LD (@MissionState.ActiveCode), A
                ; замена только L и E байтами количества и требования, H и D остаются от сравнения ключей
                LD A, (@OwnedCargoRows.Row00 + FOwnedCargoRow.QuantityAndMark)
                LD L, A
                LD A, (@MissionOffer.Entry.RequiredTonnage)
                LD E, A
                ; вычитание полных HL и DE с нулевым Carry, это не изолированное сравнение двух байтов
                XOR A
                SBC HL, DE
                JP C, @Station.CancelMission.ClearQuantity                      ; переход, если полное вычитание HL-DE дало заём, обнулить Row00.QuantityAndMark

                ; запись младшего байта результата без отдельной проверки байтового заёма
                LD A, L
                LD (@OwnedCargoRows.Row00 + FOwnedCargoRow.QuantityAndMark), A
                ; выбор LANG в банке 6 и кода события 11 перед исходным сценарием
RecomputeLoad:  LD A, #16
                CALL @Station.SelectRamBank.Entry
                LD A, #11
                LD (@ScriptCallState.EventCode), A
                CALL @Text.RunMarketScript.Entry
                ; возврат банка станции после сценария, если интерпретатор вернулся
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                ; расчёт денежного остатка после вычета исходного штрафа 1000
                LD HL, (@PlayerSaveHeader.Entry + FPlayerSaveHeader.Money)
                LD DE, @MissionOfferConst.CancelPenalty
                XOR A
                SBC HL, DE
                JP C, @Station.CancelMission.ClearCredits                       ; переход, если денежное слово меньше 1000, сохранить нулевой остаток

                LD (@PlayerSaveHeader.Entry + FPlayerSaveHeader.Money), HL
                ; вывод исходного сообщения расторжения и два ожидания HALT
PrintCancelled: LD HL, @MissionCancelMessage.Entry
                CALL @Station.PrintText.Entry
                HALT
                HALT
                ; генерация нового предложения после расторжения и обновление общего статусного элемента
                CALL @Station.GenerateMissionOffer.Entry
                CALL @Station.DrawItem00.Entry
                JP @Station.ProcessMissionAction.FinishAction

                ; обнуление количества при полном заёме исходного вычитания
ClearQuantity:  XOR A
                LD (@OwnedCargoRows.Row00 + FOwnedCargoRow.QuantityAndMark), A
                JP @Station.CancelMission.RecomputeLoad

                ; насыщение денежного остатка нулём при недостатке для штрафа
ClearCredits:   LD HL, #0000
                LD (@PlayerSaveHeader.Entry + FPlayerSaveHeader.Money), HL
                JP @Station.CancelMission.PrintCancelled

                endmodule
                endmodule
