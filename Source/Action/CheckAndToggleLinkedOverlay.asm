                module Action
                module CheckAndToggleLinkedOverlay
                ; Документация [алгоритм и проверка](../../Docs/ActionLinkedOverlay.md)
                ; -----------------------------------------
                ; Проверка связанных векторов, обновление обратной связи и XOR-вывод сегмента
                ; исходная запись 17, адреса E804..E862
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, альтернативные пары учитываются ранними отказами
                ;   IX указывает FActionRecord с доступными словами 1A, 1C, 1E и LinkedIndex
                ;   RecordPointer подготовлен через PrepareLinkedRecordContext либо явно указывает допустимую запись, особый LinkedIndex=1A его игнорирует
                ;   действуют договоры LoadLinkedRecordVectors, RecordAddressToIndex и ToggleTargetOverlay, LinkRLimit доступен
                ;   ACTION банка 0, таблицы проекции, экран и CPU-стек детей доступны, IRQ и повторный вход исключены
                ; Out:
                ;   при полном Unknown1B=80 возвращается Carry=1 до обмена наборов, остальные данные сохраняются
                ;   иначе BC/HL/DE получают слова текущей записи 1A/1C/1E и EXX сохраняет их, LoadLinkedRecordVectors подготавливает выбранную запись
                ;   при Carry дочернего чтения возвращается Carry=1 с неотменённым EXX, созданные ранее контексты не нормализуются
                ;   при прочитанном R>=LinkRLimit у выбранной IY устанавливается бит 0 LinkFlags и LinkedIndex получает индекс текущего IX
                ;   обратная связь записывается до проверки знаков и переполнений, последующий отказ её не отменяет
                ;   если оба старших байта глубины отрицательны, возвращается Carry=0 без проекции
                ;   затем по очереди проверяются signed16-разности Output0-BC, Output2-DE и HL-Output1, при любом overflow возвращается Carry=1
                ;   при трёх допусках вызывается ToggleTargetOverlay, IX восстанавливается, окончательный AND A очищает Carry независимо от результата вывода
                ;   HL, DE, BC, AF, HL', DE', BC', AF' и IY определяются достигнутым путём, IX, I/IM/IFF и paging сохраняются
                ;   SP после внешнего RET равен входному SP+2, для полного вывода требуется стек дочерних процедур
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, обратная связь выбранной записи, векторные операнды, экран, буферы и CPU-стек детей, SP внешним RET
                ; Note:
                ;   Carry означает локальный отказ подготовки либо signed overflow, сброшенный Carry не доказывает фактического изменения пикселя
                ;   оба отрицательных старших байта проверяются AND D после EXX, это не сравнение модулей и не отбрасывание любого отрицательного конца
                ;   порядок трёх разностей и SCF перед RET PE сохраняется, Signed overflow использует P/V от SBC, а не чётность A
                ;   462848 сценариев включают все пары R и порога, шесть полных словарных срезов, особую связь, маркер и ссылку на себя
                ;   проверены настоящие дети до внешнего RET, регистры кроме R на путях растеризатора, все восемь банков и кратность записей
                ;   на остальных путях R сверяется точно, R/T растеризатора, полное произведение входов, IRQ, сборка и нативный вывод не проверялись
                ; -----------------------------------------
                ; Проверка полного старшего байта первого слова контекста текущей записи до любых обменов регистров.
Entry:          LD A, (IX + @FActionRecord.Unknown1B)
                CP @ActionReuseConst.ReusableHigh
                SCF
                RET Z                                                           ; выход, если Unknown1B равен 80, вернуть Carry без изменения векторных контекстов

                ; Подготовка BC, HL и DE из трёх слов текущей записи с сохранением в альтернативном наборе.
                LD B, A
                LD C, (IX + @FActionRecord.Unknown1A)
                LD L, (IX + @FActionRecord.Unknown1C)
                LD H, (IX + @FActionRecord.Unknown1D)
                LD E, (IX + @FActionRecord.Unknown1E)
                LD D, (IX + @FActionRecord.Unknown1F)
                EXX
                ; Чтение выбранного контекста либо фиксированного контекста особой связи 1A.
                CALL @Action.LoadLinkedRecordVectors.Entry
                RET C                                                           ; выход, если выбранный контекст вернул Carry, сохранить выполненный EXX

                ; Проверка аппаратного R перед обновлением обратной связи выбранной записи.
                LD A, R
                CP #4A
                JR C, @Action.CheckAndToggleLinkedOverlay.CheckDepthSigns       ; переход, если прочитанный R меньше LinkRLimit, сохранить прежнюю обратную связь

                ; Обновление бита обратной связи и LinkedIndex выбранной IY индексом текущего IX.
                SET 0, (IY + @FActionRecord.LinkFlags)
                PUSH HL
                PUSH IX
                POP HL
                CALL @Action.RecordAddressToIndex.Entry
                POP HL
                LD (IY + @FActionRecord.LinkedIndex), A
                ; Проверка совместного знака двух глубин, один отрицательный конец сам по себе не завершает обработку.
CheckDepthSigns:LD A, D
                EXX
                AND D
                RET M                                                           ; выход, если обе глубины отрицательны, вернуть Carry=0 без проекции

                ; Проверка signed16-переполнения первой разности Output0-BC с сохранением HL.
                PUSH HL
                LD HL, (@ActionPatchedVectorState.Output0)
                OR A
                SBC HL, BC
                POP HL
                SCF
                RET PE                                                          ; выход, если первая signed16-разность переполнилась, вернуть Carry=1

                ; Проверка signed16-переполнения разности Output2-DE без изменения рабочих векторов.
                PUSH HL
                LD HL, (@ActionPatchedVectorState.Output2)
                OR A
                SBC HL, DE
                POP HL
                SCF
                RET PE                                                          ; выход, если разность глубин signed16 переполнилась, вернуть Carry=1

                ; Проверка signed16-переполнения разности HL-Output1 с сохранением HL и DE.
                PUSH HL
                PUSH DE
                LD DE, (@ActionPatchedVectorState.Output1)
                OR A
                SBC HL, DE
                POP DE
                POP HL
                SCF
                RET PE                                                          ; выход, если третья signed16-разность переполнилась, вернуть Carry=1

                ; Сохранение IX вокруг полного XOR-вывода сегмента между подготовленными векторами.
                PUSH IX
                CALL @Action.ToggleTargetOverlay.Entry
                POP IX
                ; Обновление итоговых флагов A, Carry очищается даже при раннем отказе экранного вывода.
                AND A
                RET

                endmodule
                endmodule
