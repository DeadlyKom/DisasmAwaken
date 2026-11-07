                module Action
                module StepCodesTowardRecord
                ; Документация [алгоритм и проверка](../../Docs/ActionSelectedRecordStep.md)
                ; -----------------------------------------
                ; Подвод фазовых кодов текущей записи по трём компонентам выбранной записи
                ; исходная запись 17, адреса F36B..F393
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX текущая FActionRecord, IY выбранная FActionRecord
                ;   по IX доступны три Components, OffsetPhase1, OffsetPhase2 и стабильный числовой TargetCodeStep, по IY читаются три Components
                ;   действуют условия StepRecordTargetCodes и EncodeHalfCoordinateDeltas, подготовлены таблицы и банк 1 корня, выбран банк 0
                ;   7FFD не заблокирован, CPU-стек не пересекает записи, код и таблицы, доступны 16 дополнительных байтов, IRQ не вмешиваются
                ; Out:
                ;   исполнен настоящий StepRecordTargetCodes, левыми координатами становятся компоненты IY, правыми компоненты IX
                ;   BC содержит два целевых кода EncodeHalfCoordinateDeltas для трёх разностей арифметических половин координат
                ;   H=модуль обёрнутой разности исходного OffsetPhase2-C, L=модуль обёрнутой разности исходного OffsetPhase1-B
                ;   D=исходный OffsetPhase2, E=wrap8(исходный OffsetPhase2-C), A и F следуют точным двум выходам StepRecordTargetCodes
                ;   OffsetPhase1 и OffsetPhase2 обновлены по различным правилам TargetCodeStep, остальные поля записей сохраняются
                ;   HL', DE', BC', AF' равны результату геометрии, IX и IY, I/IM/IFF сохраняются, SP после внешнего RET равен входному SP+2
                ;   OUT 7FFD получает 11 и 10, конечная конфигурация 10, прежняя конфигурация не восстанавливается
                ;   собственный перенос аргументов не пишет RAM и добавляет 27 M1, точный R всей геометрической композиции не доказан
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', R, OffsetPhase1 и OffsetPhase2 по условиям дочернего шага, операнды делителя, 7FFD и до 16 байтов CPU-стека
                ; Note:
                ;   перед JP основной HL=IY.Component0, DE=IX.Component0, BC=IX.Component1, альтернативные HL'=IY.Component1, DE'=IY.Component2, BC'=IX.Component2
                ;   две инструкции EXX оставляют аргументы в нужных наборах, между чтением и JP арифметики и новых CALL нет
                ;   393216 сценариев проверили все значения каждого из шести слов на границе JP, точные регистры, флаги, R и отсутствие записей
                ;   512 дополнительных сценариев исполнили реальную геометрию, корень, оба кодировщика и шаг с независимыми моделями детей
                ;   в композиции сверены регистры кроме R, все восемь банков, значения и кратность записей и оба OUT, это не новый независимый алгоритм всех детей
                ;   полное произведение шести слов, аппаратные IRQ, точные T, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Подготовка альтернативных аргументов трёхмерной геометрии, исходные альтернативные пары будут заменены.
Entry:          EXX
                ; Чтение второй координаты выбранной записи как будущего левого слова второй разности.
                LD L, (IY + @FActionRecord.Components.Component1.Low)
                LD H, (IY + @FActionRecord.Components.Component1.High)
                ; Чтение третьей координаты выбранной записи как будущего левого слова третьей разности.
                LD E, (IY + @FActionRecord.Components.Component2.Low)
                LD D, (IY + @FActionRecord.Components.Component2.High)
                ; Чтение третьей координаты текущей записи как правого слова третьей разности.
                LD C, (IX + @FActionRecord.Components.Component2.Low)
                LD B, (IX + @FActionRecord.Components.Component2.High)
                ; Возврат к основному набору для первой пары координат и правого слова второй разности.
                EXX
                ; Чтение первой координаты текущей записи как правого слова первой разности.
                LD E, (IX + @FActionRecord.Components.Component0.Low)
                LD D, (IX + @FActionRecord.Components.Component0.High)
                ; Чтение первой координаты выбранной записи как левого слова первой разности.
                LD L, (IY + @FActionRecord.Components.Component0.Low)
                LD H, (IY + @FActionRecord.Components.Component0.High)
                ; Чтение второй координаты текущей записи и передача всех шести слов настоящему кодировщику.
                LD C, (IX + @FActionRecord.Components.Component1.Low)
                LD B, (IX + @FActionRecord.Components.Component1.High)
                ; Хвостовая передача не создаёт нового возврата, дочерняя цепочка вернётся внешнему вызывающему.
                JP @Action.StepRecordTargetCodes.Entry

                endmodule
                endmodule
