                module Map
                module RasterizeMapLine
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [четыре ядра, фазовые маски, изменяемые команды и исключение последнего конца](../../Docs/MapLine.md)
; -----------------------------------------
; Рисование отрезка Брезенхэма в режимах Clear, Set и Xor без последнего конца
; исходная запись 7, файловые смещения #12EE..#1417
; In:
;   MapLineWork.Start и Finish содержат два байтовых X,Y, KARTA выбран
;   MapScreenTables построены, реальные экранные координаты обоих концов и всех промежуточных точек лежат в bitmap
;   Mode=ClearMode и MaskOffset=ClearMaskLow либо Mode=SetMode/XorMode и MaskOffset=SetMaskLow
;   тело рисователя и соответствующие два байта выбранного ядра доступны для самомодификации
; Out:
;   при разных концах концы упорядочиваются по возрастанию Y, при равных Y порядок не меняется
;   ровно M=max(abs(dx),dy) пикселей обработаны, начальный включён, последний после упорядочивания исключён
;   HL - адрес исключённого конца, DE - D=M, E=min(abs(dx),dy), BC - B=0, C фазовая маска исключённого конца
;   A'=floor(M/2), основные AF и альтернативный F' рабочие, выходной признак результата ими не задаётся
;   при равных концах HL=0, DE содержит Finish как Y*256+X, BC и AF' сохранены, A входной, F=42
;   HL', DE', BC', IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2
;   исходные точки и Mode не меняются, при непустом отрезке записаны только PixelOpcode и ByteCrossOpcode выбранного ядра
; Corrupt:
;   HL, DE, BC, AF, AF' только при непустом отрезке
; Note:
;   ошибка изначально floor(M/2), после каждого пикселя вычитается малый шаг, заём исправляется добавлением M
;   при abs(dx)=dy выбирается горизонтальное ядро, при M=0 ранний RET предотвращает цикл DJNZ с B=0
;   таблицы не проверяются и дополнительного отсечения нет, нарушение экранных ограничений может затронуть другие области
;   Source содержит исходные NOP и JR C, вызывающий код конфигурирует режим, Clear меняет JR C на JR NC
;   прямой вызывающий код D1AC не использует AF/AF' после рисования, внешние HL и BC снимаются со стека
; -----------------------------------------
                ; проверка совпадения двух упакованных байтовых точек до любой записи режима в код
Entry:          LD HL, (@MapLineWork.Start.X)
                LD DE, (@MapLineWork.Finish.X)
                OR A
                SBC HL, DE
                RET Z                                                           ; выход, если Start и Finish совпадают, ни одного пикселя не рисовать

                ; восстановление первой упакованной точки после проверки разности
                ADD HL, DE
                ; расчёт вертикального шага и выбор верхнего конца по беззнаковому Y
                LD A, D
                SUB H
                JR NC, @Map.RasterizeMapLine.SortedTop                          ; переход, если Y второго конца не меньше Y первого, обмен не требуется

                ; обмен концов и расчёт положительного вертикального шага
                EX DE, HL
                NEG
SortedTop:      LD D, A
                ; расчёт фазы X первого пикселя для восьмибайтовой таблицы масок
                LD A, L
                AND #07
                ; добавление изменяемого MaskOffset, вызывающий код выбирает 20 или 28 до входа
                ADD A, #00
                LD C, A
                ; поиск маски на странице D4 с учётом переноса младшего адреса таблицы
                LD A, @MapLineConst.MaskPage
                ADC A, #00
                LD B, A
                LD A, (BC)
                EX AF, AF'
                ; поиск экранной строки первого пикселя и байтовой колонки по построенным таблицам
                LD C, L
                LD L, H
                LD H, @MapMarkerConst.RowHighPage
                LD B, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, C
                ADD A, (HL)
                LD L, A
                LD H, B
                LD A, C
                EX AF, AF'
                LD C, A
                EX AF, AF'
                ; расчёт направления горизонтального шага, исходный X первого конца минус X второго
                SUB E
                JR C, @Map.RasterizeMapLine.InitRight                           ; переход, если X первого конца меньше X второго, выбрать движение вправо

                ; сравнение абсолютного горизонтального шага с вертикальным для левого направления
                CP D
                JR C, @Map.RasterizeMapLine.InitLeftY                           ; переход, если горизонтальный шаг меньше вертикального, выбрать вертикальное ядро влево

                ; выбор M=abs(dx) и малого шага dy для горизонтального ядра влево
                LD E, D
                LD D, A
                LD B, A
                ; расчёт начальной ошибки floor(M/2) с хранением в альтернативном A
                SRL A
                EX AF, AF'
                ; обновление команды пикселя выбранного горизонтального ядра влево
                LD A, (@MapLineWork.Mode.PixelOpcode)
                LD (@MapLinePatch.LeftXPixel), A
                ; обновление условия пересечения байта, Clear использует противоположный перенос инверсной маски
                LD A, (@MapLineWork.Mode.ByteCrossOpcode)
                LD (@MapLinePatch.LeftXCross), A
                LD A, (HL)
                ; изменяемая команда одного пикселя, сюда копируется AND C, OR C или XOR C из Mode.PixelOpcode
StepLeftX:      NOP
                RLC C
                JR C, @Map.RasterizeMapLine.ByteLeftX                           ; переход, если маска пересекла левую границу байта, Clear заменяет исходный JR C на JR NC

ErrorLeftX:     EX AF, AF'
                SUB E
                JR C, @Map.RasterizeMapLine.RowLeftX                            ; переход, если ошибка после вычитания dy дала заём, добавить M и перейти к следующей строке

                EX AF, AF'
                DJNZ @Map.RasterizeMapLine.StepLeftX

                LD (HL), A
                RET

ByteLeftX:      LD (HL), A
                DEC L
                LD A, (HL)
                JP @Map.RasterizeMapLine.ErrorLeftX

RowLeftX:       ADD A, D
                EX AF, AF'
                LD (HL), A
                INC H
                LD A, H
                AND #07
                JP NZ, @Map.RasterizeMapLine.ReadLeftX                          ; переход, если новая строка остаётся внутри восьмистрочного блока, старший адрес уже готов

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Map.RasterizeMapLine.ReadLeftX                           ; переход, если прибавление 20 переполнило младший адрес, началась следующая треть экрана

                LD A, H
                SUB #08
                LD H, A
ReadLeftX:      LD A, (HL)
                DJNZ @Map.RasterizeMapLine.StepLeftX

                RET

                ; выбор M=dy и малого шага abs(dx) для вертикального ядра влево
InitLeftY:      LD E, A
                LD A, D
                LD B, D
                SRL A
                EX AF, AF'
                LD A, (@MapLineWork.Mode.PixelOpcode)
                LD (@MapLinePatch.LeftYPixel), A
                LD A, (@MapLineWork.Mode.ByteCrossOpcode)
                LD (@MapLinePatch.LeftYCross), A
StepLeftY:      LD A, (HL)
                ; изменяемая команда одного пикселя, сюда копируется AND C, OR C или XOR C из Mode.PixelOpcode
                NOP
                LD (HL), A
                INC H
                LD A, H
                AND #07
                JP NZ, @Map.RasterizeMapLine.ErrorLeftY                         ; переход, если новая строка остаётся внутри восьмистрочного блока, перейти к обновлению ошибки

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Map.RasterizeMapLine.ErrorLeftY                          ; переход, если прибавление 20 переполнило младший адрес, коррекция H на 8 не нужна

                LD A, H
                SUB #08
                LD H, A
ErrorLeftY:     EX AF, AF'
                SUB E
                JR NC, @Map.RasterizeMapLine.MoreLeftY                          ; переход, если вычитание малого шага не дало займа, сохранить текущий X

                ADD A, D
                RLC C
                JR C, @Map.RasterizeMapLine.ByteLeftY                           ; переход, если маска пересекла левую границу байта, Clear заменяет исходный JR C на JR NC

MoreLeftY:      EX AF, AF'
                DJNZ @Map.RasterizeMapLine.StepLeftY

                RET

ByteLeftY:      DEC L
                EX AF, AF'
                DJNZ @Map.RasterizeMapLine.StepLeftY

                RET

                ; расчёт положительного горизонтального шага для движения вправо
InitRight:      NEG
                CP D
                JR C, @Map.RasterizeMapLine.InitRightY                          ; переход, если горизонтальный шаг меньше вертикального, выбрать вертикальное ядро вправо

                LD E, D
                LD D, A
                LD B, A
                SRL A
                EX AF, AF'
                LD A, (@MapLineWork.Mode.PixelOpcode)
                LD (@MapLinePatch.RightXPixel), A
                LD A, (@MapLineWork.Mode.ByteCrossOpcode)
                LD (@MapLinePatch.RightXCross), A
                LD A, (HL)
                ; изменяемая команда одного пикселя, сюда копируется AND C, OR C или XOR C из Mode.PixelOpcode
StepRightX:     NOP
                RRC C
                JR C, @Map.RasterizeMapLine.ByteRightX                          ; переход, если маска пересекла правую границу байта, Clear заменяет исходный JR C на JR NC

ErrorRightX:    EX AF, AF'
                SUB E
                JR C, @Map.RasterizeMapLine.RowRightX                           ; переход, если ошибка после вычитания dy дала заём, добавить M и перейти к следующей строке

                EX AF, AF'
                DJNZ @Map.RasterizeMapLine.StepRightX

                LD (HL), A
                RET

ByteRightX:     LD (HL), A
                INC L
                LD A, (HL)
                JP @Map.RasterizeMapLine.ErrorRightX

RowRightX:      ADD A, D
                EX AF, AF'
                LD (HL), A
                INC H
                LD A, H
                AND #07
                JP NZ, @Map.RasterizeMapLine.ReadRightX                         ; переход, если новая строка остаётся внутри восьмистрочного блока, старший адрес уже готов

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Map.RasterizeMapLine.ReadRightX                          ; переход, если прибавление 20 переполнило младший адрес, началась следующая треть экрана

                LD A, H
                SUB #08
                LD H, A
ReadRightX:     LD A, (HL)
                DJNZ @Map.RasterizeMapLine.StepRightX

                RET

                ; выбор M=dy и малого шага abs(dx) для вертикального ядра вправо
InitRightY:     LD E, A
                LD A, D
                LD B, D
                SRL A
                EX AF, AF'
                LD A, (@MapLineWork.Mode.PixelOpcode)
                LD (@MapLinePatch.RightYPixel), A
                LD A, (@MapLineWork.Mode.ByteCrossOpcode)
                LD (@MapLinePatch.RightYCross), A
StepRightY:     LD A, (HL)
                ; изменяемая команда одного пикселя, сюда копируется AND C, OR C или XOR C из Mode.PixelOpcode
                NOP
                LD (HL), A
                INC H
                LD A, H
                AND #07
                JP NZ, @Map.RasterizeMapLine.ErrorRightY                        ; переход, если новая строка остаётся внутри восьмистрочного блока, перейти к обновлению ошибки

                LD A, L
                ADD A, #20
                LD L, A
                JR C, @Map.RasterizeMapLine.ErrorRightY                         ; переход, если прибавление 20 переполнило младший адрес, коррекция H на 8 не нужна

                LD A, H
                SUB #08
                LD H, A
ErrorRightY:    EX AF, AF'
                SUB E
                JR NC, @Map.RasterizeMapLine.MoreRightY                         ; переход, если вычитание малого шага не дало займа, сохранить текущий X

                ADD A, D
                RRC C
                JR C, @Map.RasterizeMapLine.ByteRightY                          ; переход, если маска пересекла правую границу байта, Clear заменяет исходный JR C на JR NC

MoreRightY:     EX AF, AF'
                DJNZ @Map.RasterizeMapLine.StepRightY

                RET

ByteRightY:     INC L
                EX AF, AF'
                DJNZ @Map.RasterizeMapLine.StepRightY

                RET

                endmodule
                endmodule
