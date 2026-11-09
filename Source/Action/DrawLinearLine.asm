                module Action
                module DrawLinearLine
                ; Физическое состояние [упакованные точки и полные коды режима](../../Docs/ActionRasterWorkData.md)
                ; Документация [алгоритм и проверка](../../Docs/ActionLineRaster.md)
                ; -----------------------------------------
                ; Растеризация отрезка в линейный буфер страницы 80 с режимами AND, OR и XOR без конечной точки
                ; исходная запись 17, адреса DDF0..DEEF
                ; In:
                ;   FirstPoint и SecondPoint задают Second от 0 до 255 и First от 0 до 95 в пикселях, младший байт соответствует Second
                ;   PixelOpcode, BranchOpcode и MaskOffset согласованы как A1/30/18 для очистки, B1/38/10 для OR либо A9/38/10 для XOR
                ;   исходные восемь масок E010 и восемь инверсных E018 сохранены, буфер 8000..8BFF доступен на запись
                ;   HL, DE и BC входных аргументов не задают, входные AF и альтернативный AF существенны только для случая равных концов
                ;   ACTION находится в банке 0 и доступен на запись, на CPU-стеке внешний возврат, прерывания не вмешиваются во временный SP=0020
                ; Out:
                ;   при равных концах HL=0, DE содержит исходную упакованную SecondPoint, BC и A сохраняются, F=42, альтернативный набор сохранён, RAM не записывается
                ;   при разных концах при необходимости выполняется обмен по First, рисование идёт от меньшей First к большей, при равной First порядок концов сохраняется
                ;   выданы max(abs(deltaSecond),abs(deltaFirst)) пикселей, первый включён, нормализованный конечный исключён
                ;   HL содержит линейный адрес байта конечной точки, B=0, C содержит маску её фазы, D большую длину, E меньшую
                ;   A' равен половине большей длины с округлением вниз, точные основной AF и F' зависят от последнего вращения маски, изменения адреса и шага ошибки
                ;   все AF и AF' задаются числовой моделью raster в CheckActionLineRaster.py, для пологого пути A может содержать загруженный неизменённый следующий байт
                ;   HL', DE', BC', IX и IY сохраняются, I, IM, IFF и paging сохраняются, SP восстановлен и после RET равен входному SP+2, R меняется
                ;   переписаны SavedSP и два opcode выбранного из четырёх ядер, остальные ядра сохраняются, порты не используются
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', R, пиксельные байты с точными дополнительными сохранениями, SavedSP и два opcode выбранного ядра
                ; Note:
                ;   код не проверяет First<=95, расширенная серия First 0..255 подтверждает записи до 9FFF, их игровая допустимость отдельно не доказана
                ;   буфер линейный, адрес равен 8000 плюс First*32 плюс Second DIV 8, это не адресная раскладка экрана ULA
                ;   ошибка начинается с половины большой длины, меньшая координата продвигается только при строго отрицательной ошибке
                ;   пологие ядра накапливают байт и сохраняют его при смене байта, строки либо завершении, возможны записи неизменённого соседнего байта
                ;   крутые ядра сохраняют байт для каждого пикселя, конечная точка всё равно исключена
                ;   AND использует инверсную маску и JR NC, OR/XOR прямую маску и JR C, сохраняются фактические изменяемые байты инструкций
                ;   SP=0020 является шагом строки, DI/EI здесь нет, ISR не должен использовать этот временный стек, новые области памяти не выделяются
                ;   49920 сценариев проверяют все регистры кроме R, всю физическую RAM и кратность записей, точное R/T, все совместные входы, IRQ, сборка и нативный запуск не доказаны
                ; -----------------------------------------
                ; -----------------------------------------
                ; Проверка совпадающих концов
                ; Чтение двух упакованных точек, сравнение полного слова с очищенным Carry.
Entry:          LD HL, (@ActionLineRasterState.FirstPoint)
                LD DE, (@ActionLineRasterState.SecondPoint)
                OR A
                SBC HL, DE
                RET Z                                                           ; выход, если оба упакованных конца совпадают, пиксели и изменяемые opcode не записывать

                ADD HL, DE
                ; -----------------------------------------
                ; Рабочий SP как шаг строки
                ; Сохранение CPU-стека в операнде и установка SP=32 для ADD HL,SP между линейными строками.
                ; -----------------------------------------
                ; Дополнительный вход DrawPacked
                ; In, HL и DE содержат упакованные концы, Second в младшем байте, First в старшем, BC и AF числовых аргументов не задают.
                ; In, режим и маски согласованы как у основного входа, весь путь пиксельных записей доступен и не пересекается с исполняемым кодом или внешним CPU-стеком.
                ; Out, для разных концов действует основной договор, исходные FirstPoint и SecondPoint не читаются.
                ; Out, при равных концах проверка равенства пропущена, нулевой B даёт 256 итераций по убыванию Second вместо пустого вывода.
                ; Corrupt, регистры, пиксели, временный SP и операнды из основного договора, R растеризатора независимо не доказан.
                ; Note, 77824 сценария прямого вызывающего включили 512 реальных равных отрезков с First=95, общий профиль равных точек у верхней границы буфера не доказан.
                ; -----------------------------------------
                ; Сохранение CPU-стека и установка исходного SP=32 для шага линейной строки.
DrawPacked:     LD (@ActionLineRasterState.SavedSP), SP
                LD SP, @ActionLineRasterConst.RowBytes
                ; Расчёт разности First, при отрицательном результате концы меняются местами.
                LD A, D
                SUB H
                JR NC, @Action.DrawLinearLine.OrderedY                          ; переход, если First второго конца не меньше First первого, обмен концов не нужен

                EX DE, HL
                NEG
                ; -----------------------------------------
                ; Адрес и маска первого пикселя
                ; Чтение фазы Second AND 7 и выбор прямой либо инверсной таблицы по изменяемому MaskOffset.
OrderedY:       LD D, A
                LD A, L
                AND @ActionLineRasterConst.PhaseMask
                ADD A, #00
                LD C, A
                LD A, @ActionLineRasterConst.MaskPage
                ADC A, #00
                LD B, A
                LD A, (BC)
                LD C, A
                ; Расчёт линейного адреса 8000+First*32+Second DIV 8, SCF вводит старший бит страницы 80.
                LD A, L
                SRL H
                RR L
                SRL H
                RR L
                SCF
                RR H
                RR L
                ; Расчёт разности Second и выбор горизонтального направления.
                SUB E
                JR C, @Action.DrawLinearLine.Rightward                          ; переход, если Second первого конца меньше Second второго, рисовать вправо

                ; Проверка большой длины для левого направления, равенство выбирает пологое ядро.
                CP D
                JR C, @Action.DrawLinearLine.SteepLeft                          ; переход, если модуль deltaSecond меньше deltaFirst, выбрать крутое левое ядро

                ; -----------------------------------------
                ; Пологое левое ядро
                ; Подготовка D как большой длины, E как меньшей и альтернативного A как половины большой длины.
                LD E, D
                LD D, A
                LD B, A
                SRL A
                EX AF, AF'
                ; Обновление opcode пикселя и условия переноса между байтами для текущего режима.
                LD A, (@ActionLineRasterState.PixelOpcode)
                LD (@Action.DrawLinearLine.ApplyLeft), A
                LD A, (@ActionLineRasterState.BranchOpcode)
                LD (@Action.DrawLinearLine.LeftBoundary), A
                LD A, (HL)
                ; Исходный NOP заменяется AND C, OR C либо XOR C, значения исходного образа не исправляются.
ApplyLeft:      NOP
                RLC C
LeftBoundary:   JR C, @Action.DrawLinearLine.LeftByte                           ; переход, если вращение маски требует предыдущего байта, режим AND меняет opcode проверки Carry на NC

                ; Расчёт следующей ошибки, пиксельный аккумулятор временно сохраняется в альтернативном AF.
LeftError:      EX AF, AF'
                SUB E
                JR C, @Action.DrawLinearLine.LeftRow                            ; переход, если ошибка после вычитания меньшей длины отрицательна, перейти к следующей строке

                EX AF, AF'
                DJNZ @Action.DrawLinearLine.ApplyLeft

                LD (HL), A
                JP @Action.DrawLinearLine.RestoreStack

                ; Сохранение накопленного байта перед переходом в предыдущий байт линейной строки.
LeftByte:       LD (HL), A
                DEC L
                LD A, (HL)
                JP @Action.DrawLinearLine.LeftError

                ; Коррекция отрицательной ошибки и сохранение байта перед прибавлением шага строки.
LeftRow:        ADD A, D
                EX AF, AF'
                LD (HL), A
                ADD HL, SP
                LD A, (HL)
                DJNZ @Action.DrawLinearLine.ApplyLeft

                JP @Action.DrawLinearLine.RestoreStack

                ; -----------------------------------------
                ; Крутое левое ядро
                ; Подготовка количества строк и ошибки, каждое прохождение записывает один пиксельный байт.
SteepLeft:      LD E, A
                LD A, D
                LD B, D
                SRL A
                EX AF, AF'
                ; Обновление opcode выбранного крутого ядра.
                LD A, (@ActionLineRasterState.PixelOpcode)
                LD (@Action.DrawLinearLine.ApplyDownLeft), A
                LD A, (@ActionLineRasterState.BranchOpcode)
                LD (@Action.DrawLinearLine.LeftDownBound), A
                ; Чтение текущего пиксельного байта, маска применяется подготовленной командой.
LeftDownPixel:  LD A, (HL)
ApplyDownLeft:  NOP
                LD (HL), A
                ADD HL, SP
                ; Расчёт ошибки после обязательного продвижения на строку.
                EX AF, AF'
                SUB E
                JR NC, @Action.DrawLinearLine.LeftDownNext                      ; переход, если ошибка неотрицательна, горизонтальную фазу не менять

                ADD A, D
                RLC C
LeftDownBound:  JR C, @Action.DrawLinearLine.LeftDownByte                       ; переход, если горизонтальный шаг пересёк байт, режим AND меняет opcode проверки Carry на NC

LeftDownNext:   EX AF, AF'
                DJNZ @Action.DrawLinearLine.LeftDownPixel

                JP @Action.DrawLinearLine.RestoreStack

LeftDownByte:   DEC L
                EX AF, AF'
                DJNZ @Action.DrawLinearLine.LeftDownPixel

                JP @Action.DrawLinearLine.RestoreStack

                ; -----------------------------------------
                ; Правое направление
                ; Расчёт модуля deltaSecond, затем выбор крутой либо пологой ветви.
Rightward:      NEG
                CP D
                JR C, @Action.DrawLinearLine.SteepRight                         ; переход, если модуль deltaSecond меньше deltaFirst, выбрать крутое правое ядро

                ; Подготовка большой и меньшей длин пологого правого ядра.
                LD E, D
                LD D, A
                LD B, A
                SRL A
                EX AF, AF'
                ; Обновление opcode пикселя и перехода между байтами правого ядра.
                LD A, (@ActionLineRasterState.PixelOpcode)
                LD (@Action.DrawLinearLine.ApplyRight), A
                LD A, (@ActionLineRasterState.BranchOpcode)
                LD (@Action.DrawLinearLine.RightBoundary), A
                LD A, (HL)
ApplyRight:     NOP
                RRC C
RightBoundary:  JR C, @Action.DrawLinearLine.RightByte                          ; переход, если вращение маски требует следующего байта, режим AND меняет opcode проверки Carry на NC

                ; Расчёт следующей ошибки пологого правого ядра.
RightError:     EX AF, AF'
                SUB E
                JR C, @Action.DrawLinearLine.RightRow                           ; переход, если ошибка отрицательна, скорректировать её и перейти к следующей строке

                EX AF, AF'
                DJNZ @Action.DrawLinearLine.ApplyRight

                LD (HL), A
                JP @Action.DrawLinearLine.RestoreStack

                ; Сохранение накопленного байта перед переходом в следующий байт строки.
RightByte:      LD (HL), A
                INC L
                LD A, (HL)
                JP @Action.DrawLinearLine.RightError

                ; Коррекция ошибки и переход на следующую линейную строку.
RightRow:       ADD A, D
                EX AF, AF'
                LD (HL), A
                ADD HL, SP
                LD A, (HL)
                DJNZ @Action.DrawLinearLine.ApplyRight

                JP @Action.DrawLinearLine.RestoreStack

                ; -----------------------------------------
                ; Крутое правое ядро
                ; Подготовка длины по строкам и половинной ошибки.
SteepRight:     LD E, A
                LD A, D
                LD B, D
                SRL A
                EX AF, AF'
                ; Обновление opcode выбранного правого крутого ядра.
                LD A, (@ActionLineRasterState.PixelOpcode)
                LD (@Action.DrawLinearLine.ApplyDownRight), A
                LD A, (@ActionLineRasterState.BranchOpcode)
                LD (@Action.DrawLinearLine.RightDownBound), A
                ; Чтение и запись текущего пиксельного байта до продвижения на следующую строку.
RightDownPixel: LD A, (HL)
ApplyDownRight: NOP
                LD (HL), A
                ADD HL, SP
                ; Расчёт ошибки и необходимости продвижения горизонтальной фазы.
                EX AF, AF'
                SUB E
                JR NC, @Action.DrawLinearLine.RightDownNext                     ; переход, если ошибка неотрицательна, горизонтальную фазу не менять

                ADD A, D
                RRC C
RightDownBound: JR C, @Action.DrawLinearLine.RightDownByte                      ; переход, если горизонтальный шаг требует следующего байта, режим AND меняет opcode проверки Carry на NC

RightDownNext:  EX AF, AF'
                DJNZ @Action.DrawLinearLine.RightDownPixel

                JP @Action.DrawLinearLine.RestoreStack

RightDownByte:  INC L
                EX AF, AF'
                DJNZ @Action.DrawLinearLine.RightDownPixel

                ; -----------------------------------------
                ; Возврат к CPU-стеку
                ; Восстановление исходного SP перед настоящим RET, временный шаг строки больше не используется.
RestoreStack:   LD SP, #0000
                RET

                ; -----------------------------------------
                endmodule
                endmodule
