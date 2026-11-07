                module Action
                module MaxRecordDeltaHigh
                ; Документация [алгоритм и проверка](../../Docs/ActionRecordDistance.md)
                ; -----------------------------------------
                ; Максимальный старший байт модулей трёх обёрнутых разностей записей
                ; исходная запись 17, адреса EAE9..EB40
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX и IY указывают две читаемые FActionRecord
                ;   читаются три слова Components каждой записи, разности имеют направление IY минус IX
                ;   выбран исходный банк 0 с кодом ACTION, четыре байта ниже внешнего возврата доступны и не пересекают записи, IRQ не вмешиваются
                ; Out:
                ;   HL=модуль третьей обёрнутой разности, DE=модуль первой, BC сохраняется
                ;   A=max(magnitude0>>8, magnitude1>>8, magnitude2>>8), диапазон A равен 0..128
                ;   magnitudeI равен deltaI при сброшенном бите 15, иначе wrap16(−deltaI), deltaI=wrap16(IY.ComponentI−IX.ComponentI)
                ;   F соответствует CP(max(magnitude1>>8, magnitude2>>8), magnitude0>>8), флаги не пересчитываются после выбора большего первого байта
                ;   HL', DE', BC', AF', IX и IY, I/IM/IFF и paging сохраняются, SP после RET равен входному SP+2
                ;   четыре байта ниже исходного SP содержат сначала magnitude1, затем magnitude0, внешний возврат сохранён
                ;   R получает 45 M1 плюс семь на каждую отрицательную delta, плюс один при третьем старшем байте меньше второго, плюс два при первом больше их максимума
                ; Corrupt:
                ;   HL, DE, AF, R, четыре временных байта CPU-стека, SP только внешним RET
                ; Note:
                ;   это квантованный максимум покомпонентных расстояний, а не евклидова длина и не вычисление корня
                ;   JP P после SBC проверяет бит 15 обёрнутого результата, математическое переполнение отдельно не учитывается
                ;   модуль кода 8000 остаётся 8000 и трактуется как беззнаковое 32768, поэтому A может быть 128
                ;   197337 сценариев покрыли полный диапазон каждой разности и 729 совместных граничных троек, всего 32 профиля ветвей
                ;   точно проверены регистры, флаги, R, SP и все четыре записи со значениями, порядок шинных циклов этим не доказывается
                ;   полное произведение шести исходных слов не исчерпано, реальные игровые вызовы, IRQ, точные T, сборка и нативный запуск не выполнялись
                ; -----------------------------------------
                ; Чтение первой компоненты исходной записи IX и соответствующей компоненты выбранной записи IY.
Entry:          LD E, (IX + @FActionRecord.Components.Component0.Low)
                LD D, (IX + @FActionRecord.Components.Component0.High)
                LD L, (IY + @FActionRecord.Components.Component0.Low)
                LD H, (IY + @FActionRecord.Components.Component0.High)
                ; Расчёт первой разности IY минус IX с очищенным Carry и оборачиванием слова.
                OR A
                SBC HL, DE
                JP P, @Action.MaxRecordDeltaHigh.SaveFirst                      ; переход, если бит 15 первой разности сброшен, сохранить её без отрицания

                ; Расчёт модуля первой отрицательной разности по модулю 65536, код 8000 сохраняется.
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; Сохранение первого модуля в CPU-стеке перед обработкой следующей компоненты.
SaveFirst:      PUSH HL
                ; Чтение вторых компонент обеих записей.
                LD E, (IX + @FActionRecord.Components.Component1.Low)
                LD D, (IX + @FActionRecord.Components.Component1.High)
                LD L, (IY + @FActionRecord.Components.Component1.Low)
                LD H, (IY + @FActionRecord.Components.Component1.High)
                ; Расчёт второй обёрнутой разности без входного Carry.
                OR A
                SBC HL, DE
                JP P, @Action.MaxRecordDeltaHigh.SaveSecond                     ; переход, если бит 15 второй разности сброшен, сохранить её без отрицания

                ; Расчёт модуля второй отрицательной разности без изменения исходных записей.
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; Сохранение второго модуля в следующих двух байтах временного CPU-стека.
SaveSecond:     PUSH HL
                ; Чтение третьих компонент обеих записей.
                LD E, (IX + @FActionRecord.Components.Component2.Low)
                LD D, (IX + @FActionRecord.Components.Component2.High)
                LD L, (IY + @FActionRecord.Components.Component2.Low)
                LD H, (IY + @FActionRecord.Components.Component2.High)
                ; Расчёт третьей обёрнутой разности с очищенным Carry.
                OR A
                SBC HL, DE
                JP P, @Action.MaxRecordDeltaHigh.CompareThird                   ; переход, если бит 15 третьей разности сброшен, использовать её без отрицания

                ; Расчёт третьего модуля, он остаётся в выходном HL.
                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
                ; Поиск максимума старших байтов второго и третьего модулей, младшие байты не участвуют.
CompareThird:   POP DE
                LD A, H
                CP D
                JR NC, @Action.MaxRecordDeltaHigh.ReadFirst                     ; переход, если старший байт третьего модуля не меньше второго, сохранить его в A

                LD A, D
                ; Восстановление первого модуля в выходной DE и сравнение его старшего байта с уже выбранным максимумом.
ReadFirst:      POP DE
                CP D
                RET NC                                                          ; выход, если максимум второго и третьего старших байтов не меньше первого

                ; Выбор большего первого старшего байта, флаги предыдущего CP сохраняются.
                LD A, D
                RET

                endmodule
                endmodule
