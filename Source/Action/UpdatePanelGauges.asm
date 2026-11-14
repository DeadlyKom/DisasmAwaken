                module Action
                module UpdatePanelGauges
                ; Физическое состояние [панель и счётчик](../../Docs/ActionPanelPhysicalData.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionPanelGauges.md)
                ; -----------------------------------------
                ; Условное обновление шести шкал, сброс пяти запросов и насыщение шестого значения
                ; исходная запись 17, банк 5, перенесённое ядро ACTION #6000..#7F8E, смещения #0886..#090E
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IY сохраняется
                ;   шесть изменяемых операндов Request задают запросы, любой ненулевой байт допускает соответствующую шкалу
                ;   FirstValue, ThirdValue, FourthValue и FifthValue задают четыре прямых байтовых входа
                ;   ActionPreferredByteState.Value задаёт пару выбора второй шкалы, SpeedWord задаёт знаковое слово шестой
                ;   действуют договоры DrawBankedGauge и SelectFuelStock, банк 1 содержит CONTROL, 7FFD доступен для записи
                ;   код, внешняя рамка и шесть дополнительных байтов CPU-стека находятся в общей RAM, IRQ не вмешиваются
                ; Out:
                ;   при отсутствии запросов HL, DE и BC сохраняются, AF=0054, альтернативный AF сохраняется
                ;   при наличии запросов HL, DE, BC и альтернативный AF соответствуют последней обновлённой шкале
                ;   если шестой запрос нулевой, AF=0054, иначе A=10 и F соответствует последнему DrawSixRowGauge
                ;   HL', DE', BC', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2
                ;   FirstRequest, ThirdRequest, FourthRequest, FifthRequest и SixthRequest обнуляются при их ненулевом входе, SecondRequest сохраняется
                ;   исходные значения и пара Preferred/Fallback не изменяются, значение шестой шкалы равно min(abs(signed16 SpeedWord)/4, 46) с целой частью
                ;   при хотя бы одном запросе 7FFD последовательно получает 11 и 10 для каждой обновлённой шкалы, на выходе 10
                ;   без запросов OUT отсутствуют и исходный 7FFD сохраняется, R учитывает весь выбранный маршрут и дочерние вызовы
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', R, пять операндов запросов, записанные шкалы, шесть байтов CPU-стека, аппаратный регистр 7FFD
                ; Note:
                ;   Request является целым кодом допуска, ноль запрещает ветвь, все ненулевые значения допускают, отдельные биты не проверяются
                ;   вторая шкала получает выбранный байт, делённый на два через RRA с гарантированно сброшенным Carry читателя
                ;   первая, третья, четвёртая и пятая шкалы передают весь исходный байт, исходный рисователь не ограничивает эти аргументы диапазоном 0..48
                ;   пять запросов являются изменяемыми операндами существующих инструкций, дополнительная RAM не выделяется
                ;   проверка родительского маршрута композиционная, полный совместный перебор всех входных полей не выполнялся
                ;   FirstValue является уровнем защиты SHILD, SpeedWord знаковой скоростью, игровой смысл ThirdValue и физическая единица скорости остаются открытыми
                ; -----------------------------------------
                ; -----------------------------------------
                ; Первая шкала
                ; Проверка запроса первой шкалы, запрос хранится в операнде этой инструкции.
Entry:          LD A, #00
                AND A
                JR Z, @Action.UpdatePanelGauges.SecondGauge                     ; переход, если FirstRequest равен нулю, первая шкала не обновляется

                ; Обновление первой шкалы исходным байтом FirstValue.
                LD A, (@ActionPanelGaugesState.FirstValue)
                LD HL, @ActionPanelGaugesConst.FirstTarget
                CALL @Action.DrawBankedGauge.Entry
                ; Сброс одноразового запроса первой шкалы после завершённого вывода.
                XOR A
                LD (@ActionPanelGaugesState.FirstRequest), A
                ; -----------------------------------------
                ; Вторая шкала
                ; Проверка запроса второй шкалы, этот запрос сохраняется после вывода.
SecondGauge:    LD A, #00
                AND A
                JR Z, @Action.UpdatePanelGauges.ThirdGauge                      ; переход, если SecondRequest равен нулю, вторая шкала не обновляется

                ; Выбор приоритетного байта второй шкалы, Carry читателя всегда сброшен.
                CALL @Action.SelectFuelStock.Entry
                ; Расчёт целой половины выбранного байта с нулевым входным Carry.
                RRA
                LD HL, @ActionPanelGaugesConst.SecondTarget
                CALL @Action.DrawBankedGauge.Entry
                ; -----------------------------------------
                ; Третья шкала
                ; Проверка запроса третьей шкалы.
ThirdGauge:     LD A, #00
                AND A
                JR Z, @Action.UpdatePanelGauges.FourthGauge                     ; переход, если ThirdRequest равен нулю, третья шкала не обновляется

                ; Обновление третьей шкалы текущим операндом ThirdValue из UpdateFrame.
                LD A, (@ActionPanelGaugesState.ThirdValue)
                LD HL, @ActionPanelGaugesConst.ThirdTarget
                CALL @Action.DrawBankedGauge.Entry
                ; Сброс одноразового запроса третьей шкалы.
                XOR A
                LD (@ActionPanelGaugesState.ThirdRequest), A
                ; -----------------------------------------
                ; Четвёртая шкала
                ; Проверка запроса четвёртой шкалы.
FourthGauge:    LD A, #00
                AND A
                JR Z, @Action.UpdatePanelGauges.FifthGauge                      ; переход, если FourthRequest равен нулю, четвёртая шкала не обновляется

                ; Чтение готового значения четвёртой шкалы из изменяемого операнда.
                LD A, #00
                LD HL, @ActionPanelGaugesConst.FourthTarget
                CALL @Action.DrawBankedGauge.Entry
                ; Сброс одноразового запроса четвёртой шкалы.
                XOR A
                LD (@ActionPanelGaugesState.FourthRequest), A
                ; -----------------------------------------
                ; Пятая шкала
                ; Проверка запроса пятой шкалы.
FifthGauge:     LD A, #00
                AND A
                JR Z, @Action.UpdatePanelGauges.SixthGauge                      ; переход, если FifthRequest равен нулю, пятая шкала не обновляется

                ; Чтение готового значения пятой шкалы из изменяемого операнда.
                LD A, #00
                LD HL, @ActionPanelGaugesConst.FifthTarget
                CALL @Action.DrawBankedGauge.Entry
                ; Сброс одноразового запроса пятой шкалы.
                XOR A
                LD (@ActionPanelGaugesState.FifthRequest), A
                ; -----------------------------------------
                ; Шестая шкала
                ; Проверка запроса шестой шкалы.
SixthGauge:     LD A, #00
                AND A
                JR Z, @Action.UpdatePanelGauges.Done                            ; переход, если SixthRequest равен нулю, обновление панели завершено

                ; Сброс запроса шестой шкалы перед расчётом её значения.
                XOR A
                LD (@ActionPanelGaugesState.SixthRequest), A
                ; Проверка знака исходного слова шестой шкалы.
                LD HL, (@ActionPanelGaugesState.SpeedWord)
                BIT 7, H
                JR Z, @Action.UpdatePanelGauges.ScaleMagnitude                  ; переход, если SpeedWord неотрицательно, преобразование к модулю не требуется

                ; Расчёт модуля отрицательного слова по модулю 65536, 8000 сохраняет величину 32768.
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; Деление беззнакового модуля слова на четыре с переносом старших разрядов в младший байт.
ScaleMagnitude: LD A, H
                SRL A
                RR L
                SRL A
                RR L
                ; Проверка старшего байта результата деления, ненулевой результат требует насыщения.
                AND A
                JR Z, @Action.UpdatePanelGauges.ClampValue                      ; переход, если старший байт частного нулевой, достаточно сравнения младшего байта

                LD L, @ActionPanelGaugesConst.MaxSixthValue
                ; Проверка младшего байта относительно первого недопустимого значения 47.
ClampValue:     LD A, L
                CP @ActionPanelGaugesConst.SixthEndValue
                JR C, @Action.UpdatePanelGauges.DrawSixth                       ; переход, если значение меньше 47, насыщение не требуется

                LD L, @ActionPanelGaugesConst.MaxSixthValue
                ; Обновление шестой шкалы значением из диапазона 0..46.
DrawSixth:      LD A, L
                LD HL, @ActionPanelGaugesConst.SixthTarget
                CALL @Action.DrawBankedGauge.Entry
Done:           RET

                ; -----------------------------------------
                endmodule
                endmodule
