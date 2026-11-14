                module Station
                module ProcessMissionAction
                ; Документация [Station](../../Docs/FunctionDetails/Station.md)
                ; Подробный разбор [условия принятия, старшие байты отмены и общий стековый хвост](../../Docs/MissionAction.md)
                ; -----------------------------------------
                ; Проверка селектора и строки, принятие либо расторжение миссии с общей перерисовкой
                ; исходная запись 4, файловые смещения #1148..#11ED
                ; In:
                ;   HL - запасная обёртка, DE - выбранный индекс, BC - контекст по RepaintAndFlag
                ;   AF - A исходный селектор, действуют договоры RepaintAndFlag, callback и интерактивной геометрии
                ;   для собственного действия выполнены договоры DrawItem31, DrawItem32, DrawItem00 и экранного обновления
                ;   Row хранится в исходном операнде 6F54, текущий ключ и MissionOffer доступны
                ;   для предупреждения и отмены GenerateMissionOffer завершает поиск ненулевого ROM-тоннажа, LANG доступен в банке 6
                ;   стек вне экранов и банкового окна, HALT пробуждается с сохранением контекста
                ; Out:
                ;   при Carry после RepaintAndFlag немедленный возврат с его регистровыми результатами
                ;   при возвращённом A не равном 1 только DEC A и CloseMenuOnRow, результат по его договору
                ;   при возвращённом A=1 сохраняет шесть пар в FMissionActionFrame, дальнейшее восстановление относится к этому моменту
                ;   при Row не равном 1 или совпавших ключах пропускает собственное принятие и отмену, но выполняет общий хвост
                ;   при Row=1 и разных ключах ActiveCode=1 ведёт в CancelMission на этом же кадре
                ;   при прочих кодах ActiveCode сравнивает вместимость с младшим байтом суммы используемого и требуемого тоннажа
                ;   успех пишет ActiveCode=1, CompletionCode=0, байтовые суммы в Row00.QuantityAndMark и UsedTonnage, значение 0A в Row00.Price
                ;   отказ печатает предупреждение, ждёт два HALT, заменяет предложение генератором и выполняет общий хвост
                ;   HL и DE восстановлены из FMissionActionFrame, BC - B восстановлен из кадра, C=PointerY SHR 3
                ;   AF - A=#FF, F от CP TextWindow.OriginYLow SHR 3 и PointerY SHR 3 при разных строках, иначе от DropItemDraw
                ;   HL', DE', BC', AF' не восстанавливаются общим кадром и соответствуют вложенным игровым и графическим вызовам
                ;   IX и IY восстановлены из FMissionActionFrame перед CloseMenuOnRow
                ;   общий хвост вызывает BeginScreenUpdate, DrawItem31, DrawItem32, DrawItem00 и EndScreenUpdate
                ;   MissionHoverState.Row=#FF, при совпадении строк CloseMenuOnRow удаляет выбранный элемент через DropItemDraw, иначе список не меняется этим вызовом
                ;   конечная страница 10, блокировка указателя снята EndScreenUpdate, I и IFF собственным кодом не меняются
                ;   SP обычного возврата равен входному SP+2 при выполнении договоров вызываемых обработчиков
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по RepaintAndFlag, R, собственный кадр сохраняет шесть пар
                ;   MissionHoverState.Row, временные слова CPU-стека и побочные записи RepaintAndFlag, BeginScreenUpdate, DrawItem31, DrawItem32, DrawItem00, EndScreenUpdate и CloseMenuOnRow
                ;   на собственных ветвях изменяются MissionState, Row00.QuantityAndMark, Row00.Price, UsedTonnage, при генерации и отмене действуют договоры GenerateMissionOffer и LANG
                ; Note:
                ;   собственный FinishAction требует кадр от SaveContext, обычный CALL к этому хвосту недопустим
                ;   на ветви принятия сравнивается обёрнутая байтовая сумма, перенос выше 255 не вызывает отдельного отказа
                ;   пропуск собственного изменения не запрещает завершение миссии в DrawItem32 при уже достигнутой цели
                ;   результаты дочернего DrawItem32 могут включать деньги, новое предложение и сценарий, это часть общего хвоста
                ;   полная модель включает RepaintAndFlag при последнем обработчике списка и без интерактивного действия
                ;   модель не исполняет IRQ и не подтверждает аппаратный ввод, ROM Unreal или нативное прохождение
                ; -----------------------------------------
                ; обработка селектора через RepaintAndFlag до собственного действия элемента
Entry:          CALL @Station.RepaintAndFlag.Entry
                RET C                                                           ; выход, если RepaintAndFlag вернул Carry, действие миссии не выполнять

                ; проверка исходного возвращённого кода 1 через уменьшение на один
                DEC A
                JP Z, @Station.ProcessMissionAction.SaveContext                 ; переход, если возвращённый код равнялся 1, проверить выбранную строку

                ; попытка закрытия элемента по строке указателя для прочих кодов
                CALL @Station.CloseMenuOnRow.Entry
                RET Z                                                           ; выход, если CloseMenuOnRow закрыл элемент по совпадению строки

                RET

                ; создание FMissionActionFrame в исходном порядке DE, HL, BC, AF, IX, IY
SaveContext:    PUSH DE
                PUSH HL
                PUSH BC
                PUSH AF
                PUSH IX
                PUSH IY
                ; проверка номера строки, сохранённого обновлением наведения
                LD A, (@MissionHoverState.Row)
                CP #01
                JP NZ, @Station.ProcessMissionAction.FinishAction               ; переход, если выбранная строка не равна 1, выполнить только общий проход перерисовки

                ; сравнение первых слов текущего и предлагаемого ключа с очисткой Carry
                LD HL, (@SignatureInput.Entry.FirstWord)
                LD DE, (@MissionOffer.Entry.FirstWord)
                XOR A
                SBC HL, DE
                JP NZ, @Station.ProcessMissionAction.TestActive                 ; переход, если первые слова ключей различаются, проверить состояние миссии

                ; сравнение вторых слов ключей при совпавших первых
                LD HL, (@SignatureInput.Entry.SecondWord)
                LD DE, (@MissionOffer.Entry.SecondWord)
                XOR A
                SBC HL, DE
                JP NZ, @Station.ProcessMissionAction.TestActive                 ; переход, если вторые слова различаются, проверить состояние миссии

                ; совпавшие оба слова пропускают принятие и расторжение, остаётся общий проход
                JP @Station.ProcessMissionAction.FinishAction

                ; проверка MissionState.ActiveCode на код активного предложения 1
TestActive:     LD A, (@MissionState.ActiveCode)
                CP #01
                JP Z, @Station.CancelMission.Entry                              ; переход, если MissionState.ActiveCode равен 1, выполнить ветвь расторжения

                ; расчёт суммы текущего младшего тоннажа и требуемого, старшие байты тоже участвуют в ADD
                LD HL, (@PlayerSaveHeader.Entry + FPlayerSaveHeader.UsedTonnage)
                LD DE, (@MissionOffer.Entry.RequiredTonnage)
                ADD HL, DE
                ; проверка PlayerSaveHeader.Entry.Capacity относительно младшего байта рассчитанной суммы
                LD A, (@PlayerSaveHeader.Entry + FPlayerSaveHeader.Capacity)
                LD H, L
                CP H
                JP C, @Station.ProcessMissionAction.WarnTonnage                 ; переход, если вместимость меньше младшего байта суммы, вывести предупреждение

                ; обновление MissionState.ActiveCode кодом 1 и сброс CompletionCode после прохождения проверки
                LD A, #01
                LD (@MissionState.ActiveCode), A
                XOR A
                LD (@MissionState.CompletionCode), A
                ; расчёт нового OwnedCargoRows.Row00.QuantityAndMark с сохранением только младшего байта
                LD HL, (@OwnedCargoRows.Row00 + FOwnedCargoRow.QuantityAndMark)
                LD DE, (@MissionOffer.Entry.RequiredTonnage)
                ADD HL, DE
                LD A, L
                LD (@OwnedCargoRows.Row00 + FOwnedCargoRow.QuantityAndMark), A
                ; расчёт нового PlayerSaveHeader.Entry.UsedTonnage с сохранением только младшего байта
                LD HL, (@PlayerSaveHeader.Entry + FPlayerSaveHeader.UsedTonnage)
                LD DE, (@MissionOffer.Entry.RequiredTonnage)
                ADD HL, DE
                LD A, L
                LD (@PlayerSaveHeader.Entry + FPlayerSaveHeader.UsedTonnage), A
                ; обновление соседнего OwnedCargoRows.Row00.Price исходным кодом 0A
                LD A, #0A
                LD (@OwnedCargoRows.Row00 + FOwnedCargoRow.Price), A
                ; общий экранный проход, стек обязан содержать FMissionActionFrame
FinishAction:   CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem31.Entry
                CALL @Station.DrawItem32.Entry
                CALL @Station.DrawItem00.Entry
                CALL @Station.EndScreenUpdate.Entry
                ; восстановление IY, IX, AF, BC, HL и DE из исходного кадра после вложенных рисователей
                POP IY
                POP IX
                POP AF
                POP BC
                POP HL
                POP DE
                ; попытка закрытия элемента по строке указателя уже с восстановленным контекстом
                CALL @Station.CloseMenuOnRow.Entry
                ; сброс сохранённого наведения в FF после завершения собственного действия
                LD A, #FF
                LD (@MissionHoverState.Row), A
                RET

                ; вывод исходного предупреждения о тоннаже и два ожидания HALT перед новым предложением
WarnTonnage:    LD HL, @MissionTonnageMessage.Entry
                CALL @Station.PrintText.Entry
                HALT
                HALT
                ; генерация нового предложения после предупреждения, прежний кандидат заменяется
                CALL @Station.GenerateMissionOffer.Entry
                JP @Station.ProcessMissionAction.FinishAction

                endmodule
                endmodule
