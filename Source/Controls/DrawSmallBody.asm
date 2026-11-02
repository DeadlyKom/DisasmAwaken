                module Controls
                module DrawSmallBody
                ; Документация [алгоритм и проверка](../../Docs/ControlsSmallBodies.md)
                ; -----------------------------------------
                ; Рисование малой симметричной фигуры радиуса 2..8 строковыми масками в линейном растре
                ; исходная запись 22, банк 1, смещения #19DE..#1AB8
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают, исходный F сохраняется в AF' при ранних выходах до подготовителя
                ;   банк 1 выбран, физический FBodyProjection.Value задаёт OffsetY, OffsetX, Flags и Radius
                ;   Mode=CEF9 ограничивает режимы значениями 0..3, Pattern=D240 задаёт два байта рисунка и XOR-чередования
                ;   исходная команда LD A, #AF по D9DE и затравки масок сохранены, Row00..Row0B, LeftMask и растр доступны для записи
                ;   код, растр и CPU-стек не перекрываются, на стеке внешний возврат, ещё шесть байтов нужны для локальной рамки, IRQ не вмешиваются
                ; Out:
                ;   при Mode>=4 либо Radius вне 2..8 HL, DE и BC сохраняются, A=Radius, F соответствует последнему CP, точные случаи описаны в документации
                ;   после подготовки OffsetX>127 либо OffsetY>72 возвращают A=0, F=44, подготовленные маски сохраняются, точные HL, DE и BC зависят от места отказа
                ;   при проходе рисования A=0, F=42, DE содержит D=флаги отсечения OR 80 и E=Radius
                ;   при рисовании HL указывает байт последней строки, C содержит фазу X, B равен повёрнутым флагам последней видимой строки либо нулю без видимых строк
                ;   HL', DE', BC' сохраняются, AF' до подготовки содержит A'=#AF и исходный F, после подготовки A'=Radius и F от CP Radius, 2
                ;   IX сохраняется, IY сохраняется до прохода рисования, после него IYH=HIGH Pattern и IYL=LOW Pattern XOR HIGH Pattern
                ;   I, IM и IFF сохраняются, SP=входной SP+2, R соответствует всем M1 выбранного пути, модель сверяет его буквально
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IY, строки масок, LeftMask, пиксели растра, шесть байтов CPU-стека, R
                ; Note:
                ;   каждая фигура содержит 2*Radius-1 строк, строки вне 0..95 не рисуются, но переключают рисунок и продвигают профиль
                ;   профиль является исходной симметричной маской, а не заменённой геометрически идеальной окружностью
                ;   промежуточный X равен 127 плюс или минус OffsetX, фактический центр симметричного пиксельного профиля на один пиксель левее
                ;   флаги в D имеют бит 7 верхней половины, биты 1 и 0 правого и левого отсечения, биты 6..2 остаются нулевыми
                ;   входные Flags используют здесь только биты 0 и 1, назначение остальных разрядов других путей не объявляется доказанным
                ;   CP 60 пропускает страницы ниже 60 в пиксельный путь, при исходных аргументах этот путь отдельно не достигается, команда сохранена
                ;   подготовитель вызывается настоящим CALL, все повторные записи и EX (SP),HL проверены, модель не является нативной игрой
                ; -----------------------------------------
                ; подготовка ненулевого селектора Alternate для BuildSmallBodyMasks через альтернативный AF
Entry:          LD A, #AF
                EX AF, AF'
                ; проверка допустимого режима перед чтением Radius без изменения результатов CP
                LD A, (@ControlsSmallBodiesState.Mode)
                CP @SmallBodyConst.ModeLimit
                LD A, (@ControlsBodyProjection.Value.Radius)
                RET NC                                                          ; выход, если Mode не меньше ModeLimit, вернуть Radius и F от сравнения режима

                ; проверка верхнего исключённого радиуса малого профиля
                CP @SmallBodyConst.RadiusLimit
                RET NC                                                          ; выход, если Radius не меньше RadiusLimit, большая фигура этим входом не рисуется

                ; проверка минимального радиуса с ненулевым количеством сдвигов затравки
                CP @SmallBodyConst.RadiusMin
                RET C                                                           ; выход, если Radius меньше RadiusMin, подготовитель не вызывается

                ; создание строковых масок настоящим вызовом BuildSmallBodyMasks
                CALL @Controls.BuildSmallBodyMasks.Entry
                ; чтение пары физических полей OffsetY и OffsetX, Y попадает в L, X в H
                LD HL, (@ControlsBodyProjection.Value.OffsetY)
                LD A, (@ControlsBodyProjection.Value.Flags)
                LD B, A
                ; проверка верхней границы горизонтального смещения
                LD A, @SmallBodyConst.XBias
                CP H
                JR C, @Controls.DrawSmallBody.RejectPosition                    ; переход, если OffsetX больше XBias, завершить без пикселей через RejectPosition

                ; вычисление промежуточного X как XBias+OffsetX до выбора направления
                ADD A, H
                ; проверка разряда 0 входных Flags, установленный разряд выбирает положительное смещение X
                RRC B
                JR C, @Controls.DrawSmallBody.StoreXCenter                      ; переход, если разряд 0 Flags установлен, сохранить положительное смещение в StoreXCenter

                ; вычисление XBias-OffsetX двумя вычитаниями из предварительной суммы
                SUB H
                SUB H
                ; сохранение промежуточного X и проверка пересечения левого соседнего байта
StoreXCenter:   LD C, A
                CP @SmallBodyConst.BytePixels
                JR NC, @Controls.DrawSmallBody.CheckRightClip                   ; переход, если X не меньше BytePixels, не устанавливать левое отсечение

                ; установка разряда 0 флагов D для отсутствующего левого соседнего байта
                INC D
                ; проверка пересечения правого соседнего байта растра
CheckRightClip: CP @SmallBodyConst.RightClipFrom
                JR C, @Controls.DrawSmallBody.CheckYRange                       ; переход, если X меньше RightClipFrom, не устанавливать правое отсечение

                ; установка разряда 1 флагов D двумя INC из исходного нулевого значения
                INC D
                INC D
                ; проверка максимального вертикального смещения
CheckYRange:    LD A, @SmallBodyConst.YMaxOffset
                CP L
                JR NC, @Controls.DrawSmallBody.BuildPosition                    ; переход, если OffsetY не больше YMaxOffset, вычислить положение в BuildPosition

                ; формирование отказа A=0, F=44 после уже выполненной подготовки масок
RejectPosition: XOR A
                RET

                ; вычисление предварительного Y как YBias+OffsetY
BuildPosition:  LD A, @SmallBodyConst.YBias
                ADD A, L
                ; проверка разряда 1 входных Flags, установленный разряд меняет знак вертикального смещения
                RRC B
                JR NC, @Controls.DrawSmallBody.AddRadius                        ; переход, если разряд 1 Flags сброшен, использовать положительное смещение Y в AddRadius

                ; вычисление YBias-OffsetY перед выбором нижней строки фигуры
                SUB L
                SUB L
                ; вычисление адреса строки после нижнего края, 8000+32*((Y+Radius) AND FF)+floor(X/8)
AddRadius:      ADD A, E
                LD L, A
                LD A, C
                LD H, @SmallBodyConst.RasterFactor
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                SRL C
                SRL C
                SRL C
                LD B, #00
                ADD HL, BC
                ; вычисление пиксельной фазы X внутри байта из младших трёх разрядов
                AND @SmallBodyConst.PhaseMask
                LD C, A
                ; сохранение входного IX и выбор таблицы строковых масок и слова Pattern
                PUSH IX
                LD IX, @ControlsSmallMaskRows.Row00
                LD IY, (@ControlsSmallBodiesState.Pattern)
                XOR A
                ; -----------------------------------------
                ; Обход профиля снизу вверх, включая невидимые строки
                ; -----------------------------------------
                ; сохранение номера строки профиля и его F на CPU-стеке
DrawRow:        PUSH AF
                ; вычисление рисунка строки как IYL XOR IYH до проверки видимости
                LD A, IYL
                XOR IYH
                LD IYL, A
                ; вычисление адреса предыдущей строки растра вычитанием RowBytes
                LD A, L
                SUB @SmallBodyConst.RowBytes
                LD L, A
                JR NC, @Controls.DrawSmallBody.ClipRow                          ; переход, если вычитание RowBytes не потребовало заёма из H, продолжить с ClipRow

                ; коррекция старшей страницы адреса после заёма младшего байта
                DEC H
                ; проверка исходного пропуска нижних страниц и границ линейного буфера
ClipRow:        LD A, H
                CP @SmallBodyConst.LowPagePass
                JR C, @Controls.DrawSmallBody.ExpandMask                        ; переход, если H меньше LowPagePass, выполнить исходный пиксельный путь ExpandMask

                CP @SmallBodyConst.BufferEndPage
                JR NC, @Controls.DrawSmallBody.RestoreRow                       ; переход, если H не меньше BufferEndPage, пропустить строку через RestoreRow

                CP @SmallBodyConst.BufferFirstPage
                JR C, @Controls.DrawSmallBody.RestoreRow                        ; переход, если H меньше BufferFirstPage, пропустить строку через RestoreRow

                ; сохранение адреса назначения перед разворачиванием симметричной маски
ExpandMask:     PUSH HL
                LD A, (IX+#00)
                LD B, @SmallBodyConst.BytePixels
                ; вычисление зеркального порядка восьми битов маски в H
ReverseBits:    RLCA
                RR H
                DJNZ @Controls.DrawSmallBody.ReverseBits

                ; вычисление 15-битового симметричного профиля, reverse8(mask)*256+((mask*2) AND FF)
                ADD A, A
                LD L, A
                LD A, @SmallBodyConst.BytePixels
                SUB C
                LD B, A
                XOR A
                ; выравнивание профиля в трёх байтах по фазе X, старший байт накапливается в A
AlignMask:      ADD HL, HL
                RLA
                DJNZ @Controls.DrawSmallBody.AlignMask

                ; сохранение флагов D и радиуса E через EX (SP),HL и восстановление адреса назначения
                LD B, D
                EX DE, HL
                EX (SP), HL
                ; проверка разряда левого отсечения в копии флагов B
                RRC B
                JR C, @Controls.DrawSmallBody.DrawCenter                        ; переход, если левый соседний байт выходит за растр, начать с DrawCenter

                ; обновление левого соседнего байта двумя исходными записями, сначала очистка маски, затем рисунок
                DEC HL
                ; сохранение старшего байта маски в существующем операнде LeftMask
                LD (@ControlsSmallBodiesState.LeftMask), A
                CPL
                AND (HL)
                LD (HL), A
                LD A, #00
                AND IYL
                OR (HL)
                LD (HL), A
                INC HL
                ; обновление центрального байта теми же двумя записями независимо от нулевых разрядов маски
DrawCenter:     LD A, D
                CPL
                AND (HL)
                LD (HL), A
                LD A, D
                AND IYL
                OR (HL)
                LD (HL), A
                ; проверка разряда правого отсечения следующим поворотом B
                RRC B
                JR C, @Controls.DrawSmallBody.RestorePair                       ; переход, если правый соседний байт выходит за растр, восстановить радиус и флаги в RestorePair

                ; обновление правого соседнего байта и возврат HL к центральному
                INC HL
                LD A, E
                CPL
                AND (HL)
                LD (HL), A
                LD A, E
                AND IYL
                OR (HL)
                LD (HL), A
                DEC HL
                ; восстановление радиуса E и флагов D из подменённого слова CPU-стека
RestorePair:    POP DE
                ; восстановление счётчика профиля и проверка перехода в верхнюю половину
RestoreRow:     POP AF
                BIT @SmallBodyConst.UpperHalfBit, D
                JR NZ, @Controls.DrawSmallBody.UpperHalf                        ; переход, если разряд UpperHalfBit установлен, уменьшить индекс через UpperHalf

                ; вычисление следующего индекса расширяющейся нижней половины профиля
                INC A
                INC IX
                ; проверка достижения центральной строки по Radius в E
                CP E
                JR NZ, @Controls.DrawSmallBody.DrawRow                          ; переход, если индекс ещё не достиг Radius, продолжить с DrawRow

                ; установка разряда верхней половины и исключение повторной центральной строки
                SET @SmallBodyConst.UpperHalfBit, D
                DEC IX
                ; вычисление предыдущего индекса зеркальной верхней половины
UpperHalf:      DEC IX
                DEC A
                JR NZ, @Controls.DrawSmallBody.DrawRow                          ; переход, если верхняя половина ещё не завершена, продолжить с DrawRow

                ; восстановление входного IX, итоговые A=0 и F=42 сохраняются после последнего DEC A
                POP IX
                ; -----------------------------------------
                RET

                ; -----------------------------------------
                endmodule
                endmodule
