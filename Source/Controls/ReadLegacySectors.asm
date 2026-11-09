                module Controls
                module ReadLegacySectors
                ; Документация [старое чтение секторов, распаковка и восстановление полётного контекста](../../Docs/ControlsLegacyLoadChain.md)
                ; -----------------------------------------
                ; Чтение последовательных секторов через внутренние входы ROM с повтором при ошибке
                ; исходная запись 23, согласованные адреса старой копии, фактический перенос игрой неизвестен, адреса 5E4D..5ED1
                ; In:
                ;   HL, начало доступного назначения, DE, D логический трек, E сектор 1..16, BC, B ненулевое число секторов
                ;   дисковые сигналы и внутренние ROM-входы доступны, 5CC2 содержит системный RET, конфигурация 5D16 подготовлена
                ;   CPU-стек допускает рамки внутренних ROM, области чтения не задевают выполняемые команды и живой стек
                ; Out:
                ;   записаны B входных секторов по 256 байтов, после ошибки по 5CCD AND 7F повторяется тот же сектор и тот же адрес
                ;   на проверенном возврате DE указывает логический трек и сектор следующего блока, B=0, HL' равен концу назначения
                ;   SP увеличен на два после обычного RET, R и регистры зависят от достигнутых ROM
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, CPU-стек, дисковое состояние ROM, назначение, порты и R
                ; Note:
                ;   после 16 сектора увеличивается D, при новом чётном D выполняется команда 58
                ;   при успехе увеличивается H, младший L сохраняется, при повторе не продвигаются ни адрес, ни сектор
                ;   нулевой B в исходном коде не проверяется, такой вход не входит в доказанный рабочий договор
                ;   16 сценариев сверены на четырёх ROM с моделью портов и выборки ROM, в том числе повтор и переход трека
                ; -----------------------------------------
                ; Расчёт физического трека как D SHR 1 и начальная команда позиционирования.
Entry:          LD A, D
                SRL A
                LD C, @TrDosLegacy.DataPort
                CALL @Controls.WriteLegacyDiskPort.Entry
                LD IX, @TrDosLegacy.SeekInitial
                CALL @Controls.CallLegacyDosRom.Entry
                ; Перенос координат и счётчика в другой набор регистров перед последовательным чтением.
                PUSH DE
                PUSH BC
                EXX
                POP BC
                POP DE
                ; Обновление управляющего порта с выбором стороны по чётности логического трека.
NextSector:     LD A, (@TrDosLegacy.DriveConfig)
                AND #2F
                LD C, A
                XOR A
                ; Проверка бита стороны, чётный логический трек устанавливает бит 4 порта.
                BIT 0, D
                JR NZ, @Controls.ReadLegacySectors.SelectSide                   ; переход, если логический трек нечётный, оставить бит стороны сброшенным

                LD A, #10
SelectSide:     OR C
                LD C, @TrDosLegacy.DrivePort
                CALL @Controls.WriteLegacyDiskPort.Entry
                ; Запись физического трека и текущего номера сектора.
                LD A, D
                SRL A
                LD C, @TrDosLegacy.TrackPort
                CALL @Controls.WriteLegacyDiskPort.Entry
                LD A, E
                LD C, @TrDosLegacy.SectorPort
                CALL @Controls.WriteLegacyDiskPort.Entry
                EXX
                ; Чтение одной попытки, адрес HL сохраняется для повтора.
ReadAttempt:    PUSH HL
                LD A, #80
                LD C, @TrDosLegacy.CommandPort
                CALL @Controls.WriteLegacyDiskPort.Entry
                LD C, @TrDosLegacy.DataPort
                LD IX, @TrDosLegacy.ReceiveSector
                CALL @Controls.CallLegacyDosRom.Entry
                EXX
                ; Передача текущего физического трека ROM и получение статуса по 5CCD.
                LD A, D
                EXX
                SRL A
                LD D, A
                LD A, #01
                LD (@TrDosLegacy.ReadContext), A
                LD IX, @TrDosLegacy.ReadStatus
                CALL @Controls.CallLegacyDosRom.Entry
                ; Проверка всех младших семи битов статуса перед продвижением.
                LD A, (@TrDosLegacy.SavedStatus)
                AND #7F
                POP HL
                JR NZ, @Controls.ReadLegacySectors.ReadAttempt                  ; переход, если статус после маски ненулевой, повторить чтение в прежний адрес

                ; Продвижение адреса на 256 и номера сектора на один после успеха.
                INC H
                EXX
                INC E
                LD A, E
                ; Проверка границы логического трека после увеличения сектора.
                CP #11
                JR C, @Controls.ReadLegacySectors.CountDown                     ; переход, если следующий сектор меньше 17, продолжить отсчёт

                ; Переход к следующему логическому треку и сектору 1.
                INC D
                LD E, #01
                ; Проверка чётности следующего трека для команды шага головки.
                BIT 0, D
                JR NZ, @Controls.ReadLegacySectors.CountDown                    ; переход, если следующий логический трек нечётный, не двигать головку

                ; Выдача команды 58 и ожидание завершения перед новым треком.
                EXX
                LD A, #58
                LD C, @TrDosLegacy.CommandPort
                CALL @Controls.WriteLegacyDiskPort.Entry
                LD IX, @TrDosLegacy.WaitReady
                CALL @Controls.CallLegacyDosRom.Entry
                EXX
                ; Проверка числа оставшихся секторов после обновления адреса и координат.
CountDown:      DEC B
                JP NZ, @Controls.ReadLegacySectors.NextSector                   ; переход, если осталось прочитать хотя бы один сектор

                RET

                endmodule
                endmodule
