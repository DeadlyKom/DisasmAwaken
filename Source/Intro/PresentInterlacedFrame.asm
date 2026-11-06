                module Intro
                module PresentInterlacedFrame
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
                ; Документация [алгоритм и проверка](../../Docs/IntroInterlacedFrame.md)
                ; Документация [экранный перенос](../../Docs/IntroScatter.md)
; -----------------------------------------
; Чередование двух раскладок, синхронизация с кадром и перенос данных текстуры в экран
; исходная запись 3, файловые смещения #04F1..#0526
                ; In:
                ;   FramePhase - исходный байт фазы 0 либо 80, FirstRecords и SecondRecords содержат по 38 записей указателей и назначений
                ;   FirstMatrix и SecondMatrix содержат по 32 слова, писатель 68A9..6928 подготовлен с исходным IXL=80 либо C0
                ;   IM=1, IY=5C3A, проверенный 48K ROM, клавиши не нажаты, KSTATE по 5C00 и 5C04 равны FF
                ;   входной IFF может быть нулём либо единицей, фаза прихода IRQ влияет на число прерываний до вывода
                ;   SP указывает внешний возврат, 16 байтов ниже него доступны, назначения не повреждают код, записи указателей и CPU-стек
                ;   источники могут перекрываться с назначениями писателя, порядок чтения и записи должен сохраняться
                ; Out:
                ;   HL - последний адрес источника второй половины плюс один, DE - конец последней строки второй половины после коррекции назначения
                ;   BC - входное BC минус 2432 modulo 65536, A=0, F=42 при исходной FramePhase=0 либо 43 при исходной FramePhase=80
                ;   HL', DE', BC', AF', IX и IY сохраняются, I и IM сохраняются, IFF=0, SP после RET равен входному SP+2
                ;   FramePhase переключён между 0 и 80, AddressPatch равен 00 14 для новой нулевой фазы либо 00 00 для новой 80
                ;   выведены две половины по 1216 байтов и 64 байта матрицы между ними, источники читаются из актуальной RAM
                ;   для новой фазы 0 порядок SecondRecords, FirstMatrix, FirstRecords, назначения сдвинуты увеличением D на один
                ;   для новой фазы 80 порядок FirstRecords, SecondMatrix, SecondRecords без коррекции назначения
                ;   RecordCursor указывает за последней записью второй половины, CpuSavedSP содержит входной SP, IntroAttrState.SavedSP содержит входной SP минус два
                ;   FRAMES увеличен каждым принятым IRQ, в проверенных начальных состояниях принято одно либо два прерывания
                ; Corrupt:
                ;   HL, DE, BC, AF, R, IFF, FramePhase, общие операнды переноса и писателя, FRAMES, 2496 байтов назначений и 16 временных байтов ниже SP
                ; Note:
                ;   после CALL WaitInterrupt DI запрещает IRQ на время обеих половин и писателя, исходный Carry сложения фазы определяет конечный Carry
                ;   при разрешённом входном IFF возможен ранний IRQ до WaitInterrupt, последующий HALT принимает ещё один, число FRAMES нельзя считать всегда равным единице
                ;   вторая половина выполняется хвостовым переходом, её RET снимает внешний адрес возврата всего обработчика
                ;   1536 комбинаций данных на каждую исходную фазу исполнили настоящий ROM и все дочерние процедуры, всего 3072 сценария
                ;   в том числе проверены чтения источников, уже изменённых писателем с адресами 8080..8787
                ;   регистры кроме R, все физические банки и кратность записей совпали с числовой композицией
                ;   доказаны начальные моменты 0, 100 и 69880 периода 69888, произвольные фазовые байты, времена, ROM, клавиши, NMI и нативный показ не доказаны
                ; -----------------------------------------
                ; расчёт фазы чередования, операнд #67F2 переключается между нулём и #80
                ; -----------------------------------------
                ; Две фазы вывода
                ; Чтение собственного операнда FramePhase, штатные значения 0 и 80 чередуются добавлением 80.
Entry:          LD A, #00
                ; Расчёт новой фазы, Carry равен единице только при исходной фазе 80 и сохраняется дочерними переносами.
                ADD A, #80
                ; Обновление исходного операнда фазы для следующего вызова.
                LD (@IntroAttrState.FramePhase), A
                LD HL, #0000
                JR NZ, @Intro.PresentInterlacedFrame.StorePatch                 ; переход, если новая FramePhase равна 80 и коррекция страницы назначения не нужна


                ; Создание слова 1400, little-endian запись даст вставку NOP и INC D.
                LD H, @IntroFrameConst.IncrementD
                ; обновление двух байтов кода коррекции адреса, NOP NOP либо NOP INC D
                ; Обновление двух исходных байтов AddressPatch до ожидания кадрового IRQ.
StorePatch:     LD (@IntroScatterState.AddressPatch), HL
                ; Ожидание следующего IRQ и запрет дальнейших IRQ перед временными стеками, ROM сохраняет AF проверки фазы.
                CALL @Intro.WaitInterrupt.Entry
                JR NZ, @Intro.PresentInterlacedFrame.FirstThenSecond            ; переход, если новая FramePhase равна 80 и первой выводится FirstRecords


                ; -----------------------------------------
                ; Нулевая фаза
                ; Вывод SecondRecords, затем FirstMatrix и хвостовой FirstRecords с коррекцией страницы назначения.
                LD HL, @IntroFrameConst.SecondRecords
                CALL @Intro.ScatterTextureToScreen.Entry
                LD HL, @IntroAttrConst.FirstMatrix
                CALL @Intro.RunAttributeWriter.Entry
                LD HL, @IntroFrameConst.FirstRecords
                JR @Intro.ScatterTextureToScreen.Entry


                ; -----------------------------------------
                ; Фаза 80
                ; Вывод FirstRecords, затем SecondMatrix и хвостовой SecondRecords без коррекции назначения.
FirstThenSecond:LD HL, @IntroFrameConst.FirstRecords
                CALL @Intro.ScatterTextureToScreen.Entry
                LD HL, @IntroAttrConst.SecondMatrix
                CALL @Intro.RunAttributeWriter.Entry
                LD HL, @IntroFrameConst.SecondRecords
                ; JP @Intro.ScatterTextureToScreen.Entry, продолжение в ScatterTextureToScreen.asm

                endmodule
                endmodule
