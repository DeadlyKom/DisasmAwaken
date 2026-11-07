                module Action
                module CreateClass17LinkedRecord
                ; Документация [алгоритм и проверка](../../Docs/ActionClass17Spawn.md)
                ; -----------------------------------------
                ; Создание записи класса 17 из альтернативных компонент и обновление связи целевой записи
                ; исходная запись 17, перенесённый код банка 5, адреса 60E8..6144
                ; In:
                ;   HL и DE числовых аргументов не задают, B задаёт копируемый индекс в Unknown0D, C обычный индекс целевой записи
                ;   A задаёт начальный Unknown13, HL', DE', BC' задают три копируемых Components, A' начальный Unknown11
                ;   доступны исходный список FActionRecord до маркера 8080 и запись по A100+64*C, ограничение индекса не добавляется
                ;   перенесённый общий код банка 5, ACTION банка 0 и изменяемый InitialParam доступны, шесть дополнительных байтов CPU-стека доступны, IRQ исключены
                ; Out:
                ;   InitialParam получает входной A даже при отсутствии свободной записи, поиск может очистить и пропустить ReuseByte=FF
                ;   при отсутствии слота A=80/F=42, HL сохраняется, DE=0040, BC сохраняется, IY указывает маркер, остальные поля не заполняются
                ;   при успехе IY указывает выделенную запись, её Components получают входные альтернативные HL, DE и BC
                ;   ModelOffset=90, OffsetPhase0/1/2=0, StateCode=8, LinkedIndex=0, LinkFlags=0, Unknown0D=B, TargetIndex=C
                ;   Unknown11 получает входной A', ClassCode=11, Unknown13 получает входной A, TargetCodeStep=2, прочие поля сохраняются после действий поиска
                ;   у целевой записи устанавливается бит 1 LinkFlags, её LinkedIndex получает обычный индекс созданной IY
                ;   после успеха HL=0040, DE=A100+64*C+0B, BC сохраняется, A равен индексу ребёнка, Carry=1, остальные F от преобразования IY
                ;   HL', DE', BC', IX, I/IM/IFF и paging сохраняются, AF'=0044 только при успехе, при отказе исходный AF' сохраняется
                ;   SP после внешнего RET равен входному SP+2, R добавляет стоимость FindReusableRecord и ещё 88 M1 при успехе либо 5 при отказе
                ; Corrupt:
                ;   HL, DE, AF, AF', IY, R, InitialParam, выделенная запись, обратная связь цели, шесть временных байтов CPU-стека, SP внешним RET
                ; Note:
                ;   полный ноль Z не служит признаком неудачи после успеха, индекс ребёнка 0 сохраняет Z от преобразования, успех явно задаётся Carry
                ;   C=FF здесь обычный индекс и не выбирает специальную запись A780, диапазон и побочные записи исходной адресной формулы сохранены
                ;   Unknown10, Unknown14, ReuseByte после очистки поиска и остальные неинициализируемые поля не зануляются дополнительно
                ;   66560 сценариев проверили все 65536 пар B/C, все начальные параметры, занятые слоты, однократный FF-пропуск и отсутствие свободного слота
                ;   сверены точные регистры, флаги, R, восемь банков, кратность записей и настоящие поисковые и индексные дети
                ;   полное произведение входов, аппаратные IRQ, время, сборка и нативная игра не проверялись
                ; -----------------------------------------
                ; Сохранение начального Unknown13 в исходном операнде до поиска свободной записи.
Entry:          LD (@ActionClass17SpawnState.InitialParam), A
                ; Поиск свободного слота с сохранением обеих входных частей BC.
                PUSH BC
                CALL @Action.FindReusableRecord.Entry
                POP BC
                RET Z                                                           ; выход, если поиск достиг маркера без свободного слота, начальный параметр уже сохранён

                ; Копирование трёх Components из альтернативного набора в реальную выделенную запись.
InitializeSlot: EXX
                LD (IY + @FActionRecord.Components.Component0.Low), L
                LD (IY + @FActionRecord.Components.Component0.High), H
                LD (IY + @FActionRecord.Components.Component1.Low), E
                LD (IY + @FActionRecord.Components.Component1.High), D
                LD (IY + @FActionRecord.Components.Component2.Low), C
                LD (IY + @FActionRecord.Components.Component2.High), B
                EXX
                ; Обновление исходных нулевых фаз, полей связи, модели и состояния дочерней записи.
                XOR A
                LD (IY + @FActionRecord.ModelOffset), #90
                LD (IY + @FActionRecord.OffsetPhase0), A
                LD (IY + @FActionRecord.OffsetPhase1), A
                LD (IY + @FActionRecord.OffsetPhase2), A
                LD (IY + @FActionRecord.StateCode), #08
                LD (IY + @FActionRecord.LinkedIndex), A
                LD (IY + @FActionRecord.LinkFlags), A
                ; Сохранение входных индексов B и C в разных физических полях ребёнка.
                LD (IY + @FActionRecord.Unknown0D), B
                LD (IY + @FActionRecord.TargetIndex), C
                ; Преобразование альтернативного A в начальный Unknown11, альтернативный AF получает 0044 от XOR.
                EX AF, AF'
                LD (IY + @FActionRecord.Unknown11), A
                ; Обновление полного класса 17, изменяемого начального параметра и шага кодов движения.
                LD (IY + @FActionRecord.ClassCode), #11
                LD (IY + @FActionRecord.Unknown13), #00
                LD (IY + @FActionRecord.TargetCodeStep), #02
                ; Расчёт адреса обычной целевой записи по входному C без особой обработки FF.
                LD A, C
                CALL @Action.RecordIndexToAddress.Entry
                ; Расчёт адреса LinkFlags цели и установка бита 1 до обновления её LinkedIndex.
                LD A, L
                ADD A, #0C
                LD L, A
                SET 1, (HL)
                ; Преобразование созданного адреса IY в обычный индекс и запись обратной ссылки у цели.
                DEC L
                EX DE, HL
                CALL @Action.RecordIYToIndex.Entry
                LD (DE), A
                ; Установка Carry как результата успешного создания, остальные флаги преобразования индекса сохраняются.
                SCF
                RET

                endmodule
                endmodule
