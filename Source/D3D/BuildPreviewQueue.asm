                module D3D
                module BuildPreviewQueue
                ; Документация [построение очереди объектов](../../Docs/PreviewQueueBuild.md)
                ; -----------------------------------------
                ; Подготовка коэффициентов, обход исходных записей с шагом 64, преобразование, отбор и сборка очереди перед рисованием
                ; исходная запись 6, банк 4, файловые смещения #2C28..#2DAF
                ; In:
                ;   CPU-стек действителен и не пересекается с рабочими данными, исходный SP сохраняется в операнде восстановления EEEF
                ;   банк 4 выбран и доступен для записи, маскируемые прерывания отключены, NMI и повторный вход исключены
                ;   исходный список начинается по CDC0 с шагом 64, первые десять байтов содержат три слова, смещение модели и три параметра ориентации
                ;   список имеет доступный конечный маркер 80xx с младшим байтом от 80, записи и указатели не перекрывают активные рабочие области
                ;   смещения модели выбирают допустимую пару PreviewModelPointers, младший размер заголовка байтовый, показатель старшего байта после RES 7 находится в 1..6
                ;   PreviewSceneMatrix содержит девять исходных слов, PreviewSharedSeed три сохраняемых байта с ещё не установленным общим игровым назначением
                ;   выполнены договоры TransformPreviewCoords, CheckPreviewBounds и InsertPreviewQueue, исходная FoldedSquare127 доступна
                ; Out:
                ;   Head=1 и NextFree=0 устанавливаются перед обходом, исходные невыделенные узлы не очищаются
                ;   старшие байты коэффициентов 80 заменяются на 81 в рабочих операндах, остальные копируются без изменения
                ;   первое слово 8000..807F пропускает запись, первое слово 8080..80FF прекращает обход
                ;   завершённые объекты записаны в очередь по договорам преобразования, граничных тестов и вставки, остальные пропущены по описанным условиям
                ;   при конечном маркере HL содержит сам маркер, DE и BC принадлежат последнему этапу, AF содержит A младшего байта маркера и F от AND A
                ;   HL' содержит адрес конечной записи, DE' адрес последнего продолжения умножителя либо исходный основной DE без преобразований, BC'=0040
                ;   AF', IX и IY по последним выполненным помощникам, I, IFF и IM собственным кодом не меняются
                ;   перед EEEE SP равен адресу маркера плюс 2, исполняемое там LD SP,nn восстанавливает входной CPU-стек
                ;   при заполнении очереди остановка по EEEE имеет договор полного буфера InsertPreviewQueue
                ;   успешный локальный отбор продолжается в CheckPreviewBounds без новой инструкции JP, очередь возвращает поток к NextRecord
                ;   рисующий проход после восстановления SP данным договором не объявляется разобранным
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, SP, рабочие поля, очередь, операнды коэффициентов, координат и переходов
                ; Note:
                ;   проверяется модуль старшего байта исходных координат, не модуль всего знакового слова
                ;   для первой преобразованной компоненты отрицательный старший байт инвертируется через CPL, а не NEG
                ;   выбор соседнего указателя при третьем результате меньше 1F00 не означает другой ресурс, обе исходные пары всех 11 моделей равны
                ;   три предварительных знаковых теста сходятся к DepthPlusSize, их промежуточные результаты не являются условиями пропуска объекта
                ;   полный алгоритм подготовки очереди отделён от дальнейшего чтения узлов и растеризации, игровой смысл трёх Unknown-полей не придумывается
                ; -----------------------------------------
                ; копирование первых двух исходных Unknown-параметров, их общий игровой смысл ещё не установлен
Entry:          LD HL, (@PreviewSharedSeed.Value.Unknown00)
                LD (@PreviewQueueState.AngleFirst), HL
                ; копирование третьего исходного Unknown-параметра в начальное рабочее состояние
                LD A, (@PreviewSharedSeed.Value.Unknown02)
                LD (@PreviewQueueState.AngleThird), A
                ; чтение старшего байта исходного коэффициента 11
                LD A, (@PreviewSceneMatrix.Value.Coeff11+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff11Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 11
Coeff11Ready:   LD (@PreviewTransformState.Coeff11), A
                ; чтение старшего байта исходного коэффициента 21
                LD A, (@PreviewSceneMatrix.Value.Coeff21+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff21Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 21
Coeff21Ready:   LD (@PreviewTransformState.Coeff21), A
                ; чтение старшего байта исходного коэффициента 31
                LD A, (@PreviewSceneMatrix.Value.Coeff31+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff31Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 31
Coeff31Ready:   LD (@PreviewTransformState.Coeff31), A
                ; чтение старшего байта исходного коэффициента 12
                LD A, (@PreviewSceneMatrix.Value.Coeff12+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff12Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 12
Coeff12Ready:   LD (@PreviewTransformState.Coeff12), A
                ; чтение старшего байта исходного коэффициента 22
                LD A, (@PreviewSceneMatrix.Value.Coeff22+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff22Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 22
Coeff22Ready:   LD (@PreviewTransformState.Coeff22), A
                ; чтение старшего байта исходного коэффициента 32
                LD A, (@PreviewSceneMatrix.Value.Coeff32+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff32Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 32
Coeff32Ready:   LD (@PreviewTransformState.Coeff32), A
                ; чтение старшего байта исходного коэффициента 13
                LD A, (@PreviewSceneMatrix.Value.Coeff13+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff13Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 13
Coeff13Ready:   LD (@PreviewTransformState.Coeff13), A
                ; чтение старшего байта исходного коэффициента 23
                LD A, (@PreviewSceneMatrix.Value.Coeff23+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff23Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 23
Coeff23Ready:   LD (@PreviewTransformState.Coeff23), A
                ; чтение старшего байта исходного коэффициента 33
                LD A, (@PreviewSceneMatrix.Value.Coeff33+#01)
                ; проверка запрещённого для семибитного умножителя значения 80
                CP @PreviewQueueBuildConst.CoeffMinBad
                JR NZ, @D3D.BuildPreviewQueue.Coeff33Ready                      ; переход, если коэффициент не равен 80, сохранить исходное значение

                ; замена 80 на 81, минимальный штатный коэффициент минус 127
                INC A
                ; обновление рабочего операнда коэффициента 33
Coeff33Ready:   LD (@PreviewTransformState.Coeff33), A
                ; создание пустого активного списка, младший байт Head=1, старший NextFree=0
                LD HL, @PreviewQueueConst.EndMarker
                LD (@PreviewQueueState.Head), HL
                ; выбор исходного шага физических записей объектов
                LD BC, @PreviewQueueBuildConst.RecordStep
                ; выбор исходного начала списка объектов
                LD HL, @PreviewQueueBuildConst.Objects
                ; сохранение настоящего CPU-стека в существующем операнде будущего LD SP
                LD (@PreviewQueueBuildState.SavedSP), SP
                JR @D3D.BuildPreviewQueue.ReadRecord

                ; проверка знака младшего байта специальной записи с высоким байтом 80
CheckMarker:    LD A, L
                AND A
                JP M, #EEEE                                                     ; переход, если младший байт маркера имеет бит 7, прекратить обход и восстановить SP

                ; возврат указателя записи и шага из альтернативного набора
NextRecord:     EXX
                ; расчёт адреса следующей записи с исходным шагом 64
                ADD HL, BC
                ; перевод SP на запись для последовательного чтения её слов
ReadRecord:     LD SP, HL
                ; выбор старшего байта специального маркера
                LD A, @PreviewQueueBuildConst.MarkerHigh
                ; сохранение адреса записи и шага в альтернативном наборе на время её обработки
                EXX
                ; чтение первой исходной координаты либо специального маркера
                POP HL
                ; проверка старшего байта 80 до обычного отбора координаты
                CP H
                JR Z, @D3D.BuildPreviewQueue.CheckMarker                        ; переход, если старший байт первого слова равен 80, проверить отключение либо конец списка

                ; сохранение прочитанной первой координаты в рабочем слове
                LD (@PreviewQueueBuildState.RawFirst), HL
                ; чтение старшего байта первой координаты для проверки его модуля
                LD A, H
                AND A
                JP P, @D3D.BuildPreviewQueue.FirstHigh                          ; переход, если старший байт первой координаты неотрицателен, отрицание не требуется

                ; расчёт байтового модуля старшего байта без изменения исходного слова
                NEG
                ; проверка исключённого предела 112 для модуля старшего байта
FirstHigh:      CP @PreviewQueueBuildConst.RawHighLimit
                JR NC, @D3D.BuildPreviewQueue.NextRecord                        ; переход, если модуль старшего байта первой координаты не меньше 112, пропустить запись

                ; обновление операнда первой координаты переходного преобразования
                LD (@PreviewTransformState.InputFirst), HL
                ; чтение второй исходной координаты из той же записи
                POP HL
                ; сохранение второй координаты в рабочем слове
                LD (@PreviewQueueBuildState.RawSecond), HL
                ; чтение старшего байта второй координаты для проверки его модуля
                LD A, H
                AND A
                JP P, @D3D.BuildPreviewQueue.SecondHigh                         ; переход, если старший байт второй координаты неотрицателен, отрицание не требуется

                ; расчёт модуля старшего байта второй координаты
                NEG
                ; проверка того же исключённого предела 112 для второй координаты
SecondHigh:     CP @PreviewQueueBuildConst.RawHighLimit
                JR NC, @D3D.BuildPreviewQueue.NextRecord                        ; переход, если модуль старшего байта второй координаты не меньше 112, пропустить запись

                ; обновление операнда второй координаты преобразования
                LD (@PreviewTransformState.InputSecond), HL
                ; чтение третьей исходной координаты
                POP HL
                ; сохранение третьей координаты в рабочем слове
                LD (@PreviewQueueBuildState.RawThird), HL
                ; чтение старшего байта третьей координаты для проверки его модуля
                LD A, H
                AND A
                JP P, @D3D.BuildPreviewQueue.ThirdHigh                          ; переход, если старший байт третьей координаты неотрицателен, отрицание не требуется

                ; расчёт модуля старшего байта третьей координаты
                NEG
                ; проверка исключённого предела 112 для третьей координаты
ThirdHigh:      CP @PreviewQueueBuildConst.RawHighLimit
                JR NC, @D3D.BuildPreviewQueue.NextRecord                        ; переход, если модуль старшего байта третьей координаты не меньше 112, пропустить запись

                ; обновление операнда третьей координаты преобразования
                LD (@PreviewTransformState.InputThird), HL
                ; чтение смещения модели и первого параметра ориентации одной парой
                POP HL
                ; сохранение байтового смещения модели
                LD A, L
                LD (@PreviewQueueState.ModelOffset), A
                ; сохранение первого параметра ориентации из старшего байта пары
                LD A, H
                LD (@PreviewQueueState.AngleFirst), A
                ; чтение второго и третьего параметров ориентации
                POP HL
                LD (@PreviewQueueState.AngleSecond), HL
                ; проверка совместного нуля первого и третьего параметров ориентации
                LD A, (@PreviewQueueState.AngleThird)
                LD B, A
                LD A, (@PreviewQueueState.AngleFirst)
                OR B
                LD A, @PreviewQueueBuildConst.ZeroPairFlag
                JR Z, @D3D.BuildPreviewQueue.StoreKind                          ; переход, если первый и третий параметры равны нулю, сохранить признак 1

                ; обнуление признака для общего случая ориентации
                XOR A
                ; сохранение бита 0 подготовленного узла до чтения заголовка модели
StoreKind:      LD (@PreviewQueueState.Flags), A
                ; выбор продолжения трёх строк преобразования без CPU-возврата
                LD IY, @D3D.BuildPreviewQueue.AfterTransform
                JP @D3D.TransformPreviewCoords.Entry

AfterTransform: JP PE, @D3D.BuildPreviewQueue.NextRecord                        ; переход, если преобразование вернуло знаковое переполнение, пропустить запись

                ; чтение третьего и первого преобразованных слов для следующего отбора
                LD DE, (@PreviewTransformState.ResultThird)
                LD HL, (@PreviewTransformState.ResultFirst)
                ; проверка знака старшего байта первой преобразованной компоненты
                LD A, H
                AND A
                JP P, @D3D.BuildPreviewQueue.CheckFirst                         ; переход, если старший байт неотрицателен, использовать его без инверсии

                ; инверсия отрицательного старшего байта через CPL, это не полный модуль слова
                CPL
                ; проверка исключённого предела 96 свёрнутого старшего байта
CheckFirst:     CP @PreviewQueueBuildConst.FirstHighEnd
                JP NC, @D3D.BuildPreviewQueue.NextRecord                        ; переход, если свёрнутый старший байт не меньше 96, пропустить запись

                ; проверка отрицательного третьего результата преобразования
                LD A, D
                AND A
                JP M, @D3D.BuildPreviewQueue.NextRecord                         ; переход, если третий результат отрицателен, пропустить запись

                ; проверка старшего байта третьего результата перед выбором пары указателей
                CP @PreviewQueueBuildConst.BaseIndexHigh
                LD A, (@PreviewQueueState.ModelOffset)
                JP P, @D3D.BuildPreviewQueue.ModelPointer                       ; переход, если старший байт не меньше 31, выбрать основной указатель

                ; расчёт смещения соседнего двухбайтового указателя модели
                ADD A, @FPreviewModelPointers.AlternatePtr
                ; сохранение рабочего смещения с добавкой 2
                LD (@PreviewQueueState.ModelOffset), A
                ; выбор исходной страницы пар указателей моделей
ModelPointer:   LD H, @PreviewQueueBuildConst.ModelPage
                LD A, (@PreviewQueueState.ModelOffset)
                LD L, A
                ; чтение выбранного указателя через рабочий SP
                LD SP, HL
                POP HL
                ; перевод SP на исходный заголовок модели
                LD SP, HL
                ; чтение байтового размера и показателя масштаба заголовка
                POP BC
                ; выделение бита 7 заголовка для выбора ключа очереди
                LD A, B
                AND @PreviewQueueConst.SecondKeyMask
                LD HL, #CEFA
                OR (HL)
                ; обновление Flags объединением заголовочного бита и признака ориентации
                LD (HL), A
                ; исключение флагового бита из числового показателя масштаба
                RES @PreviewQueueConst.SecondKeyBit, B
                ; расчёт пропуска части пяти удвоений, смещение равно 6-b
                LD A, @PreviewQueueBuildConst.ScaleStart
                SUB B
                ; обновление трёх исходных JR, масштаб основного размера и обоих граничных размеров одинаков
                LD (@PreviewQueueBuildState.SizeSkip), A
                LD (@PreviewBoundsState.FirstSkip), A
                LD (@PreviewBoundsState.SecondSkip), A
                ; создание беззнакового слова исходного размера
                LD L, C
                LD H, #00
                ; масштабирование радиуса подготовленным JR, исходное FE не является рабочим смещением
ScaleSize:      JR @D3D.BuildPreviewQueue.ScaleSize

                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ; восстановление настоящего SP для двух временных PUSH
                LD SP, (@PreviewQueueBuildState.SavedSP)
                ; сохранение исходных показателя масштаба и размера во временном CPU-кадре
                PUSH BC
                ; сохранение масштабированного слова размера для общих выходов
                PUSH HL
                ; расчёт половины масштабированного размера перед первым предварительным тестом
                SRL H
                RR L
                ; чтение первой исходной координаты для предварительной суммы
                LD DE, (@PreviewTransformState.InputFirst)
                ; проверка знака первой координаты без сброса предыдущего Carry
                BIT 7, D
                JR Z, @D3D.BuildPreviewQueue.FirstSubtract                      ; переход, если первая координата неотрицательна, выполнить вычитание

                ; расчёт предварительной суммы с отрицательной первой координатой и текущим Carry
                ADC HL, DE
                JP @D3D.BuildPreviewQueue.FirstSign

                ; расчёт предварительной разности с неотрицательной первой координатой и текущим Carry
FirstSubtract:  SBC HL, DE
FirstSign:      JP M, @D3D.BuildPreviewQueue.DepthPlusSize                      ; переход, если первый предварительный результат отрицателен, перейти к общей проверке размера

                ; возврат полного размера перед вторым предварительным тестом
                POP HL
                PUSH HL
                ; чтение третьей исходной координаты для второго предварительного теста
                LD DE, (@PreviewTransformState.InputThird)
                ; проверка её знака с сохранением переноса предыдущего расчёта
                BIT 7, D
                JR Z, @D3D.BuildPreviewQueue.ThirdSubtract                      ; переход, если третья координата неотрицательна, выполнить вычитание

                ; расчёт суммы с отрицательной третьей координатой
                ADC HL, DE
                JP @D3D.BuildPreviewQueue.ThirdSign

                ; расчёт разности с неотрицательной третьей координатой
ThirdSubtract:  SBC HL, DE
ThirdSign:      JP M, @D3D.BuildPreviewQueue.DepthPlusSize                      ; переход, если второй предварительный результат отрицателен, перейти к общей проверке размера

                ; повторное восстановление полного размера перед третьим предварительным тестом
                POP HL
                PUSH HL
                ; чтение второй исходной координаты
                LD DE, (@PreviewTransformState.InputSecond)
                ; проверка её знака с текущим Carry
                BIT 7, D
                JR Z, @D3D.BuildPreviewQueue.SecondSubtract                     ; переход, если вторая координата неотрицательна, выполнить вычитание

                ; расчёт третьей предварительной суммы, её результат заменяется в общем хвосте
                ADC HL, DE
                JP @D3D.BuildPreviewQueue.DepthPlusSize

                ; расчёт третьей предварительной разности, её флаги также заменяются
SecondSubtract: SBC HL, DE
                ; восстановление размера и исходной пары показателя и размера независимо от предварительных тестов
DepthPlusSize:  POP DE
                POP BC
                ; чтение третьего результата для фактического общего знакового теста
                LD HL, (@PreviewTransformState.ResultThird)
                ; очистка Carry, результаты предыдущих трёх знаковых тестов больше не участвуют
                AND A
                ; расчёт обёрнутой суммы третьего результата и полного размера
                ADC HL, DE
                JP M, @D3D.BuildPreviewQueue.NextRecord                         ; переход, если сумма третьего результата и размера отрицательна, пропустить объект

                ; сохранение исходного байтового размера для второй пары граничных вычислений
                LD IXL, C
                ; JP @D3D.CheckPreviewBounds.Entry, продолжение в CheckPreviewBounds.asm

                endmodule
                endmodule
