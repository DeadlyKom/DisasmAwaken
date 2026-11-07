                module Action
                module StepRecordTowardWideVector
                ; Документация [алгоритм и проверка](../../Docs/ActionWideTargetStep.md)
                ; -----------------------------------------
                ; Обновление двух кодов записи по трём широким компонентам выбранной цели
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #20F4..#214A
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают
                ;   IX указывает FActionRecord с тремя словами Components, текущими OffsetPhase1/OffsetPhase2 и стабильным TargetCodeStep
                ;   IY указывает три читаемые четырёхбайтовые компоненты в порядке little-endian
                ;   таблицы LOG, EXP и SignedRatioCodes подготовлены как для EncodeHalfCoordinateDeltas, корень банка 1 доступен
                ;   7FFD имеет одно из значений 00, 08, 10, 18, код и операнды доступны, CPU-стек допускает 16 дополнительных байтов
                ;   IRQ не вмешиваются, исходные компоненты, таблицы и код не перекрывают рабочие записи и рамку стека
                ; Out:
                ;   HL, DE, BC, AF и два поля OffsetPhase1/OffsetPhase2 определены цепочкой ClampPatchedVectorWords и StepRecordTargetCodes
                ;   Left0, Left1, Left2 равны насыщенным словам выбранного IY в исходном знаковом правиле бита 23
                ;   Right0, Right1, Right2 равны исходным трём словам Components записи IX
                ;   OffsetPhase1/OffsetPhase2 изменяются по разным исходным правилам шага TargetCodeStep, точные формулы в документации
                ;   HL', DE', BC', AF' определены дочерней геометрией, IX, IY сохранены, SP=входной SP+2
                ;   шесть операндов ClampPatchedVectorWords содержат копию исходных 12 байтов IY, финальный 7FFD=10
                ;   I, IM, IFF сохраняются, две реальные записи порта 7FFD равны 11 и 10
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', R, 16 временных байтов CPU-стека, шесть операндов координат и операнды дочерней геометрии, OffsetPhase1/OffsetPhase2, 7FFD
                ; Note:
                ;   между чтением цели и геометрией исходные LD/PUSH/POP/EXX только размещают шесть аргументов без изменения координат
                ;   конечный JP не создаёт нового возврата, StepRecordTargetCodes возвращает непосредственно внешнему вызывающему
                ;   предел входа банкового корня 7FFE и недостижимость его плохой верхней области наследуются от EncodeHalfCoordinateDeltas
                ;   338616 сценариев проверили реальные дочерние процедуры, все слова Components каждой позиции и граничные dword
                ;   сопоставлены регистры кроме R, кратность записей, остаток CPU-стека, все банки RAM и реальные переключения страниц
                ;   R, полное произведение входов, игровые единицы, IRQ, точные T, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Чтение первой широкой компоненты выбранной цели, порядок байтов little-endian.
Entry:          LD L, (IY + @FActionWideVector.Component0.Byte0)
                LD H, (IY + @FActionWideVector.Component0.Byte1)
                LD E, (IY + @FActionWideVector.Component0.Byte2)
                LD D, (IY + @FActionWideVector.Component0.Byte3)
                ; Обновление пары исходных операндов первой компоненты ClampPatchedVectorWords.
                LD (@ActionClampVectorWordsState.FirstHigh), DE
                LD (@ActionClampVectorWordsState.FirstLow), HL
                ; Чтение второй широкой компоненты выбранной цели.
                LD L, (IY + @FActionWideVector.Component1.Byte0)
                LD H, (IY + @FActionWideVector.Component1.Byte1)
                LD E, (IY + @FActionWideVector.Component1.Byte2)
                LD D, (IY + @FActionWideVector.Component1.Byte3)
                ; Обновление пары исходных операндов второй компоненты.
                LD (@ActionClampVectorWordsState.SecondHigh), DE
                LD (@ActionClampVectorWordsState.SecondLow), HL
                ; Чтение третьей широкой компоненты выбранной цели.
                LD L, (IY + @FActionWideVector.Component2.Byte0)
                LD H, (IY + @FActionWideVector.Component2.Byte1)
                LD E, (IY + @FActionWideVector.Component2.Byte2)
                LD D, (IY + @FActionWideVector.Component2.Byte3)
                ; Обновление пары исходных операндов третьей компоненты.
                LD (@ActionClampVectorWordsState.ThirdHigh), DE
                LD (@ActionClampVectorWordsState.ThirdLow), HL
                ; Преобразование трёх signed32 к словам с насыщением 7F00 и исходным знаком по биту 23.
                CALL @Action.ClampPatchedVectorWords.Entry
                ; Сохранение второй и третьей левых координат для переноса в альтернативные регистры.
                PUSH BC
                PUSH DE
                ; Чтение первых двух правых координат из текущей записи IX.
                LD E, (IX + @FActionRecord.Components.Component0.Low)
                LD D, (IX + @FActionRecord.Components.Component0.High)
                LD C, (IX + @FActionRecord.Components.Component1.Low)
                LD B, (IX + @FActionRecord.Components.Component1.High)
                ; Преобразование раскладки аргументов, основные HL/DE/BC временно уходят в альтернативный набор.
                EXX
                POP HL
                POP DE
                ; Чтение третьей правой координаты в будущий альтернативный BC.
                LD C, (IX + @FActionRecord.Components.Component2.Low)
                LD B, (IX + @FActionRecord.Components.Component2.High)
                ; Восстановление основных Left0/Right0/Right1, альтернативные HL/DE/BC содержат Left1/Left2/Right2.
                EXX
                ; Обновление двух кодов направления, хвостовой JP сохраняет внешний адрес возврата.
                JP @Action.StepRecordTargetCodes.Entry

                endmodule
                endmodule
