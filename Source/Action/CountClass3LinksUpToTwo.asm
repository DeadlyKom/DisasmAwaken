                module Action
                module CountClass3LinksUpToTwo
                ; Документация [алгоритм и проверка](../../Docs/ActionClass3LinkCount.md)
                ; -----------------------------------------
                ; Подсчёт до двух активных записей класса 3 с кодом 02 и совпадающей ссылкой
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #050C..#054D
                ; In:
                ;   HL, DE и AF входных аргументов не задают, BC задаёт сохраняемый начальный C до первой активной строки
                ;   IX указывает запись с доступным Unknown0D, сравниваемый байт может иметь любое значение 0..FF
                ;   список от Record00 имеет шаг FActionRecord, достижимы два совпадения либо маркер 80,80
                ;   читаемые записи и перенесённый код доступны, CPU-стек содержит внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   A=B=число совпадений с насыщением до двух, F=93 для нуля либо одного, F=42 для двух
                ;   HL указывает байт 0 маркера при завершении списка либо байт 1 второй подходящей записи
                ;   DE=FActionRecord, C содержит младший адрес байта 1 последней активной строки либо входной C, если активных строк не было
                ;   HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и страница сохраняются
                ;   RAM и CPU-стек не записываются, точная формула R приведена в документации, бит 7 R сохраняется
                ; Corrupt:
                ;   HL, DE, BC, AF, R
                ; Note:
                ;   совпадение требует полного ClassCode=3, полного StateCode=02 и LinkedIndex=Unknown0D указанной IX записи
                ;   неактивна строка с первым High=80, полный Low=80 при таком High является маркером и прекращает поиск
                ;   байт FF в LinkedIndex не является особым отказом, он считается совпадением при Unknown0D=FF
                ;   предел массива числом записей не зашит, насыщение прекращает просмотр сразу после второго совпадения
                ;   202350 сценариев проверили полные пары классов и кодов, ссылок и целей, двух байтов заголовка и позиции завершения
                ;   проверены регистры включая R, отсутствие всех записей и восемь банков RAM, полный набор списков, игровая ёмкость, IRQ, точные T, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; Создание нулевого счётчика и позиции байта High перед первой записью.
Entry:          LD B, #00
                LD HL, @ActionClass3CountConst.BeforeHigh
                LD DE, @FActionRecord
                JP @Action.CountClass3LinksUpToTwo.ScanNext

                ; Проверка полного Low после найденного High=80, это различает пропуск и маркер конца.
CheckEnd:       DEC L
                LD A, (HL)
                CP @ActionClass3CountConst.EndLow
                JR Z, @Action.CountClass3LinksUpToTwo.FinishCount               ; переход, если Low также равен 80, закончить подсчёт на маркере

                INC L
                ; Поиск следующей записи с исходным шагом FActionRecord.
ScanNext:       ADD HL, DE
                LD A, (HL)
                ; Проверка активности по полному High, значение 80 не трактуется как отдельный бит.
                CP @ActionReuseConst.ReusableHigh
                JR Z, @Action.CountClass3LinksUpToTwo.CheckEnd                  ; переход, если High равен 80, проверить Low на маркер конца

                ; Сохранение младшего адреса активного High и переход к полному ClassCode в той же странице.
                LD A, L
                LD C, A
                ADD A, @FActionRecord.ClassCode-@FActionWord.High
                LD L, A
                LD A, (HL)
                ; Проверка класса 3, нулевой и другие классы не учитываются.
                CP @ActionPreferredRecordConst.Class3
                LD L, C
                JR NZ, @Action.CountClass3LinksUpToTwo.ScanNext                 ; переход, если ClassCode отличается от 3, продолжить просмотр

                ; Поиск StateCode от адреса High с последующим восстановлением исходного L.
                LD A, L
                ADD A, @FActionRecord.StateCode-@FActionWord.High
                LD L, A
                LD A, (HL)
                ; Проверка полного числового кода 02 в StateCode.
                CP @ActionClass0Const.RecordCode
                LD L, C
                JR NZ, @Action.CountClass3LinksUpToTwo.ScanNext                 ; переход, если StateCode отличается от 02, продолжить просмотр

                ; Поиск LinkedIndex для точного сравнения с Unknown0D указанной IX записи.
                LD A, L
                ADD A, @FActionRecord.LinkedIndex-@FActionWord.High
                LD L, A
                LD A, (HL)
                ; Проверка совпадения полных байтов, FF допускается так же, как любой другой код.
                CP (IX + @FActionRecord.Unknown0D)
                LD L, C
                JR NZ, @Action.CountClass3LinksUpToTwo.ScanNext                 ; переход, если LinkedIndex не равен Unknown0D владельца, продолжить просмотр

                ; Обновление счётчика и проверка насыщения на втором совпадении.
                INC B
                LD A, B
                CP @ActionClass3CountConst.MaxCount
                JR C, @Action.CountClass3LinksUpToTwo.ScanNext                  ; переход, если найдено меньше двух совпадений, продолжить просмотр

                ; Формирование окончательного A и флагов независимо от причины завершения просмотра.
FinishCount:    LD A, B
                CP @ActionClass3CountConst.MaxCount
                RET

                endmodule
                endmodule
