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
;   успех пишет ActiveCode=1, CompletionCode=0, байтовые суммы в 9852 и 9850, значение 0A в 9853
;   отказ печатает предупреждение, ждёт два HALT, заменяет предложение генератором и выполняет общий хвост
;   общий хвост вызывает BeginScreenUpdate, DrawItem31, DrawItem32, DrawItem00 и EndScreenUpdate
;   HL, DE, B, IX и IY восстановлены из FMissionActionFrame перед CloseMenuOnRow
;   C равен PointerY SHR 3, A=FF, F от CloseMenuOnRow, MissionHoverState.Row=FF
;   при совпадении строк CloseMenuOnRow удаляет выбранный элемент через DropItemDraw, иначе список не меняется этим вызовом
;   HL', DE', BC', AF' не восстанавливаются общим кадром и соответствуют вложенным игровым и графическим вызовам
;   конечная страница 10, блокировка указателя снята EndScreenUpdate, I и IFF собственным кодом не меняются
;   SP обычного возврата равен входному SP+2 при выполнении договоров вызываемых обработчиков
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по RepaintAndFlag, собственный кадр сохраняет шесть пар
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

                ; проверка целого байта 99A3 на код активного предложения 1
TestActive:     LD A, (@MissionState.ActiveCode)
                CP #01
                JP Z, @Station.CancelMission.Entry                              ; переход, если байт 99A3 равен 1, выполнить ветвь расторжения

                ; расчёт суммы текущего младшего тоннажа и требуемого, старшие байты тоже участвуют в ADD
                LD HL, (#9850)
                LD DE, (@MissionOffer.Entry.RequiredTonnage)
                ADD HL, DE
                ; проверка вместимости 9851 относительно младшего байта рассчитанной суммы
                LD A, (#9851)
                LD H, L
                CP H
                JP C, @Station.ProcessMissionAction.WarnTonnage                 ; переход, если вместимость меньше младшего байта суммы, вывести предупреждение

                ; запись кода 1 в 99A3 и сброс 99A4 после прохождения проверки
                LD A, #01
                LD (@MissionState.ActiveCode), A
                XOR A
                LD (@MissionState.CompletionCode), A
                ; расчёт нового количества по 9852 с сохранением только младшего байта
                LD HL, (#9852)
                LD DE, (@MissionOffer.Entry.RequiredTonnage)
                ADD HL, DE
                LD A, L
                LD (#9852), A
                ; расчёт нового используемого тоннажа по 9850 с сохранением только младшего байта
                LD HL, (#9850)
                LD DE, (@MissionOffer.Entry.RequiredTonnage)
                ADD HL, DE
                LD A, L
                LD (#9850), A
                ; запись исходного кода 0A в соседний байт 9853
                LD A, #0A
                LD (#9853), A
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
