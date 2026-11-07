                module Action
                module ApplyRecordLocalOffsets
                ; Документация [алгоритм и проверка](../../Docs/ActionLocalOffsets.md)
                ; -----------------------------------------
                ; Увеличение фазового индекса и расчёт баз по отдельным фазам из байтов 0D..0F записи
                ; исходная запись 17, адреса F6CD..F6EB
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает доступную FActionRecord
                ;   читаются Unknown0D, Unknown0E, TargetIndex и Unknown10, OffsetPhase0 доступен для записи
                ;   действуют договоры BuildObjectOffsetCoefficients и ApplyObjectOffsetVector, исходные фазовые таблицы доступны
                ;   ACTION банка 0 выбран, шесть дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены
                ; Out:
                ;   OffsetPhase0 увеличен на один по модулю 256, это значение не используется как первая фаза данного вызова
                ;   операнды Offset0, Offset1 и Offset2 получают Unknown0D, wrap8(Unknown0E+80) и TargetIndex соответственно
                ;   DE перед вычислителем содержит D=00 и E=Unknown10, значение без знака 0..255, Unknown10 не изменяется
                ;   ApplyObjectOffsetVector записывает Base0..2, HL, DE, BC, AF, AF' и IYL определяются настоящим вычислителем и последним произведением
                ;   HL', DE', BC', IX, IYH, I/IM/IFF и paging сохраняются, SP после внешнего RET увеличен на два
                ;   нет проверки Component0.High и обновления Unknown24, в отличие от общего подготовителя F0F8
                ;   R добавляет 16 M1 к стоимости ApplyObjectOffsetVector, максимальная дополнительная рамка равна шести байтам
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IYL, R, OffsetPhase0, три фазовых операнда, три коэффициента, Base0..2 и шесть временных байтов CPU-стека, SP внешним RET
                ; Note:
                ;   TargetIndex является физическим именем байта 0F по ранее доказанному применению, здесь тот же байт используется как фазовый индекс
                ;   Unknown0D и Unknown0E не переименовываются глобально по одному контексту, общего назначения всех их писателей пока нет
                ;   65536 сценариев этого входа входят в общий набор из 131072, реальные коэффициенты и все три умножителя исполняются до полного RET
                ;   точные регистры, флаги, R, восемь банков и записи проверены, полное произведение входов, IRQ, сборка и нативный запуск не выполнялись
                ; -----------------------------------------
                ; Обновление OffsetPhase0 по модулю 256, фазы текущего расчёта читаются отдельно из 0D..0F.
Entry:          INC (IX + @FActionRecord.OffsetPhase0)
                ; Подготовка первой фазы из Unknown0D, увеличенный OffsetPhase0 здесь не читается.
                LD A, (IX + @FActionRecord.Unknown0D)
                LD (@ActionObjectOffsetTransferState.Offset0), A
                ; Расчёт второй фазы из Unknown0E с полупериодом 128 по модулю байта.
                LD A, (IX + @FActionRecord.Unknown0E)
                ADD A, #80
                LD (@ActionObjectOffsetTransferState.Offset1), A
                ; Подготовка третьей фазы из физического байта TargetIndex, в этом состоянии он не разыменовывается как индекс записи.
                LD A, (IX + @FActionRecord.TargetIndex)
                LD (@ActionObjectOffsetTransferState.Offset2), A
                ; Подготовка неотрицательного масштаба с D=00 и E=Unknown10 без изменения исходного байта.
                LD E, (IX + @FActionRecord.Unknown10)
                LD D, #00
                ; Расчёт коэффициентов и трёх базовых слов с исходным внешним возвратом.
                JP @Action.ApplyObjectOffsetVector.Entry

                endmodule
                endmodule
