                module Action
                module CreateRandomClass20Record
                ; Документация [алгоритм и проверка](../../Docs/ActionClass20Spawn.md)
                ; -----------------------------------------
                ; Создание записи класса 20 из двух случайных компонент и транспонированного преобразования
                ; исходная запись 17, адреса 617D..6200
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX и IY задают сохраняемый контекст до поиска
                ;   доступен исходный список FActionRecord с завершающим маркером и условиями FindReusableRecord
                ;   подготовлены Stream8 и коэффициенты TransformVectorTransposed, выбрана страница 0, IRQ не вмешиваются
                ;   SP содержит внешний возврат, восемь дополнительных байтов стека не пересекают код, записи и таблицы
                ; Out:
                ;   при отказе поиска сохранён результат FindReusableRecord, новая запись не создаётся, поиск может очистить ReuseByte пропущенных слотов
                ;   при успехе IY указывает выбранный слот, Stream8 продвинут один раз, его слово даёт две знаковые байтовые компоненты
                ;   компонента 0 равна 4*signed8(L) плюс 1024 при L<128 либо минус 1024 иначе, компонента 1 получена так же из H
                ;   компонента 2 равна 30000 при байте 6E75=0 либо минус 30000 иначе, режим в данном входе не изменяется
                ;   TransformVectorTransposed даёт HL, DE, BC, все три результата записываются в Components даже при частичном выходе преобразования
                ;   новая запись получает ModelOffset=C0, фазы 0C, 1D, 37, StateCode=04, ClassCode=14, Unknown13=FA
                ;   ReuseByte, LinkFlags и Unknown24 сбрасываются, TargetCodeStep, Unknown10 и TargetIndex получают 02, остальные поля сохраняются
                ;   при успехе A=0 и F=44, HL, DE, BC содержат результат преобразования, HL', DE', BC' результат потока 8, AF' результат преобразования
                ;   IX, I/IM/IFF и paging сохраняются, SP после внешнего RET увеличен на два, R учитывает оба пути поиска и все дочерние процедуры
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, выбранные поля записи, Stream8, операнды и выходы преобразования, CPU-стек
                ; Note:
                ;   класс 14 указан шестнадцатерично и равен 20 десятично, назначение игрового объекта пока не доказано
                ;   внутри участка нет проверки существования записи класса 20 и нет записи обратной связи, штатный вызывающий вход не установлен
                ;   переполнение преобразования не отклоняет создание, неизменённые выходные компоненты используются согласно договору TransformVectorTransposed
                ;   модель исполняет настоящий поиск, поток и транспонированное преобразование, сверяет регистры с R, восемь банков и кратность записей
                ;   полное произведение матриц, состояний и полей, аппаратные IRQ, точные T, сборка и нативный запуск не проверялись
                ; -----------------------------------------
                ; Поиск свободного слота с исходным пропуском ReuseByte=FF на один проход.
Entry:          CALL @Action.FindReusableRecord.Entry
                RET Z                                                           ; выход, если поиск не нашёл свободного слота, сохранить его результат

                ; Создание двух знаковых байтов из отдельного случайного потока 8.
                CALL @Action.NextRandomWord8.Entry
                ; Преобразование старшего случайного байта в знаковое слово DE без изменения его значения.
                XOR A
                RLC H
                SBC A, A
                RRC H
                LD D, A
                LD E, H
                ; Преобразование младшего случайного байта в знаковое слово HL и увеличение обеих компонент в четыре раза.
                XOR A
                RLC L
                SBC A, A
                RRC L
                LD H, A
                ADD HL, HL
                ADD HL, HL
                EX DE, HL
                ADD HL, HL
                ADD HL, HL
                EX DE, HL
                ; Проверка знака первой компоненты перед отступом от нулевой области на 1024.
                BIT 7, H
                JR Z, @Action.CreateRandomClass20Record.PositiveX               ; переход, если первая компонента неотрицательна, прибавить к ней 1024

                ; Расчёт отрицательного отступа, сброс бита 2 старшего байта вычитает 1024 из этого диапазона.
                RES 2, H
                JR @Action.CreateRandomClass20Record.SelectYSign

                ; Расчёт положительного отступа, установка бита 2 старшего байта прибавляет 1024.
PositiveX:      SET 2, H
                ; Проверка знака второй компоненты перед таким же отступом.
SelectYSign:    BIT 7, D
                JR Z, @Action.CreateRandomClass20Record.PositiveY               ; переход, если вторая компонента неотрицательна, прибавить к ней 1024

                RES 2, D
                JR @Action.CreateRandomClass20Record.SelectDepth

PositiveY:      SET 2, D
                ; Выбор знака третьей компоненты по исходному байту режима, смысл всех его состояний ещё не установлен.
SelectDepth:    LD A, (@ActionClass20SpawnState.DepthSignMode)
                AND A
                LD BC, @ActionClass20SpawnConst.PositiveDepth
                JR Z, @Action.CreateRandomClass20Record.Transform               ; переход, если байт режима равен нулю, оставить третью компоненту положительной

                LD BC, @ActionClass20SpawnConst.NegativeDepth
                ; Преобразование трёх подготовленных компонент с временным транспонированием исходной матрицы.
Transform:      CALL @Action.TransformVectorTransposed.Entry
                ; Создание физических Components из всех трёх выходных слов, отдельной проверки переполнения нет.
                LD (IY + @FActionRecord.Components.Component0.Low), L
                LD (IY + @FActionRecord.Components.Component0.High), H
                LD (IY + @FActionRecord.Components.Component1.Low), E
                LD (IY + @FActionRecord.Components.Component1.High), D
                LD (IY + @FActionRecord.Components.Component2.Low), C
                LD (IY + @FActionRecord.Components.Component2.High), B
                ; Обновление фаз, модели, состояния и полного класса новой записи с исходными постоянными.
                LD (IY + @FActionRecord.OffsetPhase0), @ActionClass20SpawnConst.Phase0
                LD (IY + @FActionRecord.OffsetPhase1), @ActionClass20SpawnConst.Phase1
                LD (IY + @FActionRecord.OffsetPhase2), @ActionClass20SpawnConst.Phase2
                LD (IY + @FActionRecord.ModelOffset), @ActionClass20SpawnConst.Model
                LD (IY + @FActionRecord.ClassCode), @ActionClass20SpawnConst.Class
                LD (IY + @FActionRecord.Unknown13), @ActionClass20SpawnConst.Parameter
                LD (IY + @FActionRecord.StateCode), @ActionClass20SpawnConst.State
                ; Обновление флагов доступности, связи и неизвестного поля 24, остальные поля слота сохраняются.
                XOR A
                LD (IY + @FActionRecord.ReuseByte), A
                LD (IY + @FActionRecord.LinkFlags), A
                LD (IY + @FActionRecord.Unknown24), A
                ; Обновление числового шага и двух полей исходными значениями 02 без предположений об их общем смысле.
                LD (IY + @FActionRecord.TargetCodeStep), @ActionClass20SpawnConst.InitialStep
                LD (IY + @FActionRecord.Unknown10), @ActionClass20SpawnConst.Unknown10Value
                LD (IY + @FActionRecord.TargetIndex), @ActionClass20SpawnConst.TargetValue
                RET

                endmodule
                endmodule
