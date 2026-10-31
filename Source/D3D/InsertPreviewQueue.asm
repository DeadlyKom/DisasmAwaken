                module D3D
                module InsertPreviewQueue
                ; Документация [двухключевая очередь объектов](../../Docs/PreviewQueue.md)
                ; -----------------------------------------
                ; Вставка четырнадцатибайтового узла по двум ключам с выбором по биту 7 и прекращением обхода при заполнении
                ; исходная запись 6, банк 4, файловые смещения #2E24..#2EED
                ; In:
                ;   Head содержит 1 либо индекс первого существующего узла в странице C7, цепочка бесцикловая и заканчивается индексом 1
                ;   NextFree равен 14*n при n=0..18, выделенные узлы имеют индексы 0, 14 и далее, все ссылки принадлежат им
                ;   PreviewTransformState.ResultThird и InputSecond содержат первый и второй ключи нового узла
                ;   ResultFirst, ResultSecond, Flags, ModelOffset и три Angle подготовлены для сохраняемой записи
                ;   банк 4 выбран и доступен для записи, маскируемые прерывания отключены, NMI и повторный вход исключены
                ;   продолжение ECAE принимает успешную вставку, EEEE принимает прекращение обхода при заполнении, CPU-возврат не используется
                ; Out:
                ;   при наличии места цепочка получает новый узел, Head либо Next предыдущего узла меняется, NextFree увеличивается на 14
                ;   HL после упаковки равен ModelOffset*256+Flags, DE второй ключ, BC первый ключ, AF содержит A=AngleThird и F от ADD старый NextFree, 14
                ;   SP после упаковки равен C700+старый NextFree+1, переход к ECAE без чтения CPU-стека
                ;   при NextFree=FC память не записывается, SP исходный, A=FC, F=6A от CP FC, FC, переход к EEEE завершает обход
                ;   при полном буфере BC и DE уже прочитаны, HL, IX и IY принадлежат фактически выполненному поиску позиции
                ;   IX при непустой цепочке указывает на прежнюю голову либо предшественника, IY меняется только при поиске после головы
                ;   HL', DE', BC', AF', I, IFF и IM сохраняются, на пустой цепочке IX и IY также сохраняются
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, IY, SP, ссылки очереди и новый физический узел
                ; Note:
                ;   если бит 7 хотя бы одного сравниваемого Flags установлен, берётся SecondInput, иначе ThirdResult
                ;   позиция выбирается только по S после SBC старыйКлюч,новыйКлюч, переполнение P/V не учитывается
                ;   равный ключ пропускает старый узел, новая запись идёт после уже встретившихся равных сравнений
                ;   проверка FC выполняется после поиска позиции, это точное равенство, не общая защита произвольного NextFree
                ;   PUSH AF временно пишет F в байт AngleSecond, следующий PUSH HL заменяет его настоящим параметром
                ;   полная очередь прекращает обход объектов через EEEE, а не только пропускает текущую запись
                ;   последующая растеризация и восстановление настоящего SP принадлежат другим участкам ядра
                ; -----------------------------------------
                ; чтение первого ключа нового узла из третьего результата преобразования
Entry:          LD BC, (@PreviewTransformState.ResultThird)
                ; чтение второго ключа из второй исходной координаты
                LD DE, (@PreviewTransformState.InputSecond)
                ; чтение младшего индекса головы очереди
                LD A, (@PreviewQueueState.Head)
                ; проверка маркера пустой активной цепочки
                CP @PreviewQueueConst.EndMarker
                JR Z, @D3D.InsertPreviewQueue.InsertHead                        ; переход, если Head равен 1, новая запись станет головой

                ; выбор страницы узлов и прежней головы для первого сравнения
                LD IXH, @PreviewQueueConst.Page
                LD IXL, A
                ; проверка общего бита 7 нового и существующего узла для выбора ключа
                LD A, (@PreviewQueueState.Flags)
                OR (IX+@FPreviewQueueNode.Flags)
                JP M, @D3D.InsertPreviewQueue.HeadSecond                        ; переход, если бит 7 установлен хотя бы у одного узла, сравнить второй ключ

                ; чтение первого ключа существующей головы
                LD L, (IX+@FPreviewQueueNode.ThirdResult)
                LD H, (IX+@FPreviewQueueNode.ThirdResult+#01)
                ; расчёт обёрнутой разности первого ключа головы и нового узла
                SBC HL, BC
                JP M, @D3D.InsertPreviewQueue.InsertHead                        ; переход, если разность первого ключа имеет знак минус, вставить перед головой

                JP @D3D.InsertPreviewQueue.FindNext

                ; чтение второго ключа существующей головы
HeadSecond:     LD L, (IX+@FPreviewQueueNode.SecondInput)
                LD H, (IX+@FPreviewQueueNode.SecondInput+#01)
                ; расчёт обёрнутой разности второго ключа головы и нового узла
                SBC HL, DE
                JP M, @D3D.InsertPreviewQueue.InsertHead                        ; переход, если разность второго ключа имеет знак минус, вставить перед головой

                ; выбор страницы следующего узла без изменения младшего IYL
FindNext:       LD IYH, @PreviewQueueConst.Page
                ; поиск следующей записи после текущего предшественника IX
ReadNext:       LD A, (IX+@FPreviewQueueNode.Next)
                ; проверка конца цепочки перед чтением следующего узла
                CP @PreviewQueueConst.EndMarker
                JR Z, @D3D.InsertPreviewQueue.AppendTail                        ; переход, если Next равен 1, добавить новый узел в хвост

                ; выбор следующего существующего узла в IY
                LD IYL, A
                ; проверка общего бита 7 для сравнения с последующим узлом
                LD A, (@PreviewQueueState.Flags)
                OR (IY+@FPreviewQueueNode.Flags)
                JP M, @D3D.InsertPreviewQueue.NextSecond                        ; переход, если бит 7 установлен хотя бы у одного узла, сравнить второй ключ

                ; чтение первого ключа следующего существующего узла
                LD L, (IY+@FPreviewQueueNode.ThirdResult)
                LD H, (IY+@FPreviewQueueNode.ThirdResult+#01)
                ; расчёт обёрнутой разности первого ключа следующего и нового узлов
                SBC HL, BC
                JP M, @D3D.InsertPreviewQueue.InsertMiddle                      ; переход, если разность первого ключа имеет знак минус, вставить после IX перед IY

                ; обновление предшественника до уже просмотренного узла
                LD A, IYL
                LD IXL, A
                JP @D3D.InsertPreviewQueue.ReadNext

                ; чтение второго ключа следующего существующего узла
NextSecond:     LD L, (IY+@FPreviewQueueNode.SecondInput)
                LD H, (IY+@FPreviewQueueNode.SecondInput+#01)
                ; расчёт обёрнутой разности второго ключа следующего и нового узлов
                SBC HL, DE
                JP M, @D3D.InsertPreviewQueue.InsertMiddle                      ; переход, если разность второго ключа имеет знак минус, вставить после IX перед IY

                ; обновление предшественника после сравнения второго ключа
                LD A, IYL
                LD IXL, A
                JP @D3D.InsertPreviewQueue.ReadNext

                ; чтение свободного индекса перед вставкой новой головы
InsertHead:     LD A, (@PreviewQueueState.NextFree)
                ; проверка полного буфера из 18 узлов
                CP @PreviewQueueConst.FullIndex
                JP Z, #EEEE                                                     ; переход, если NextFree равен FC, прекратить обход объектов без записи

                LD L, A
                LD H, @PreviewQueueConst.Page
                ; сохранение прежней головы как Next нового узла
                LD A, (@PreviewQueueState.Head)
                LD (HL), A
                ; обновление Head индексом нового узла
                LD A, L
                LD (@PreviewQueueState.Head), A
                JP @D3D.InsertPreviewQueue.PackNode

                ; чтение свободного индекса перед добавлением в хвост
AppendTail:     LD A, (@PreviewQueueState.NextFree)
                ; проверка полного буфера перед изменением ссылки хвоста
                CP @PreviewQueueConst.FullIndex
                JR Z, #EEEE                                                     ; переход, если NextFree равен FC, прекратить обход объектов без записи

                ; обновление Next прежнего хвоста новым индексом
                LD (IX+@FPreviewQueueNode.Next), A
                LD L, A
                LD H, @PreviewQueueConst.Page
                ; запись маркера конца в Next нового хвоста
                LD (HL), @PreviewQueueConst.EndMarker
                JP @D3D.InsertPreviewQueue.PackNode

                ; чтение свободного индекса перед вставкой между существующими узлами
InsertMiddle:   LD A, (@PreviewQueueState.NextFree)
                ; проверка полного буфера перед разрывом прежней ссылки
                CP @PreviewQueueConst.FullIndex
                JR Z, #EEEE                                                     ; переход, если NextFree равен FC, прекратить обход объектов без записи

                LD L, A
                LD H, @PreviewQueueConst.Page
                ; сохранение прежнего Next предшественника для нового узла
                LD A, (IX+@FPreviewQueueNode.Next)
                ; обновление Next предшественника индексом новой записи
                LD (IX+@FPreviewQueueNode.Next), L
                ; запись прежней ссылки в Next нового узла
                LD (HL), A
                LD A, L
                ; расчёт следующего свободного индекса с шагом физической структуры
PackNode:       ADD A, @FPreviewQueueNode
                ; обновление NextFree до упаковки оставшихся полей
                LD (@PreviewQueueState.NextFree), A
                ; выбор конца нового узла для обратной записи через PUSH
                LD L, A
                ; перевод SP в рабочий узел, настоящий CPU-стек не используется
                LD SP, HL
                ; сохранение второго ключа в SecondInput
                PUSH DE
                ; сохранение первого ключа в ThirdResult
                PUSH BC
                ; чтение второго результата преобразования для сохранения в узле
                LD HL, (@PreviewTransformState.ResultSecond)
                PUSH HL
                ; чтение первого результата преобразования
                LD HL, (@PreviewTransformState.ResultFirst)
                PUSH HL
                ; чтение третьего параметра ориентации для старшего байта PUSH AF
                LD A, (@PreviewQueueState.AngleThird)
                ; запись третьего параметра и временного байта F
                PUSH AF
                ; пропуск временного F перед записью первых двух параметров
                INC SP
                ; чтение первых двух параметров ориентации
                LD HL, (@PreviewQueueState.AngleFirst)
                PUSH HL
                ; чтение Flags и ModelOffset для двух первых байтов после Next
                LD HL, (@PreviewQueueState.Flags)
                ; сохранение Flags и ModelOffset, итоговый SP равен адресу поля Flags
                PUSH HL
                ; продолжение исходного обхода по ECAE после успешной вставки
                JP @D3D.BuildPreviewQueue.NextRecord

                endmodule
                endmodule
