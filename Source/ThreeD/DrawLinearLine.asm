                module ThreeD
                module DrawLinearLine
                ; Документация [алгоритм и проверка](../../Docs/ThreeDOverlayMirror.md)
                ; -----------------------------------------
                ; Растеризация отрезка в линейный буфер страницы 80 с режимами AND, OR и XOR без конечной точки
                ; исходная запись 19, банк 0, смещения #1DF0..#1EEF
                ; In:
                ;   FirstPoint и SecondPoint задают Second от 0 до 255 и First от 0 до 95 в пикселях, младший байт соответствует Second
                ;   PixelOpcode, BranchOpcode и MaskOffset согласованы как A1/30/18 для очистки, B1/38/10 для OR либо A9/38/10 для XOR
                ;   исходные восемь масок E010 и восемь инверсных E018 сохранены, буфер 8000..8BFF доступен на запись
                ;   HL, DE и BC входных аргументов не задают, входные AF и альтернативный AF существенны только для случая равных концов
                ;   3DPART находится в банке 0 и доступен на запись, на CPU-стеке внешний возврат, прерывания не вмешиваются во временный SP=0020
                ; Out:
                ;   HL при равных концах равен нулю, иначе содержит линейный адрес байта нормализованной конечной точки
                ;   DE при равных концах содержит исходную упакованную SecondPoint, иначе D содержит большую длину и E меньшую
                ;   BC при равных концах сохраняется, иначе B=0 и C содержит конечную фазовую маску
                ;   AF при равных концах сохраняет A и возвращает F=42, иначе соответствует последнему пиксельному байту, вращению маски и изменению адреса
                ;   HL', DE', BC' сохраняются
                ;   AF' при равных концах сохраняется, иначе A' равен половине большей длины с округлением вниз, F' определяется последней коррекцией ошибки или маски
                ;   IX и IY сохраняются, I, IM, IFF и paging сохраняются, SP восстановлен и после RET равен входному SP+2
                ;   R добавляет 7 M1 при равных концах, иначе стоимость префикса, пикселей и коррекций по формулам Note, бит 7 R сохраняется
                ;   при разных концах First упорядочивается по возрастанию, при равной First исходный порядок сохраняется, выданы max(abs(deltaSecond),abs(deltaFirst)) пикселей
                ;   первый нормализованный конец включён, последний исключён, при равных концах основной вход ничего не записывает
                ;   переписаны SavedSP и два opcode выбранного из четырёх ядер, остальные ядра сохраняются, порты не используются
                ;   для пологого пути A может содержать загруженный неизменённый соседний байт, точные AF и AF' задаются числовой моделью raster
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', R, пиксельные байты с точными дополнительными сохранениями, SavedSP и два opcode выбранного ядра
                ; Note:
                ;   дисковая копия слота 19 побайтово совпадает с ACTION по исходным смещениям 6000..801F
                ;   перенос доказательств требует тех же внешней RAM, банка 0, состояния входа и договоров общих процедур вне файла
                ;   нативная загрузка отдельного 3DPART не выполнялась, CF08 сохраняет отдельную неоднозначность исполнения
                ;   код не проверяет First<=95, расширенная серия First 0..255 подтверждает записи до 9FFF, их игровая допустимость отдельно не доказана
                ;   буфер линейный, адрес равен 8000 плюс First*32 плюс Second DIV 8, это не адресная раскладка экрана ULA
                ;   ошибка начинается с половины большой длины, меньшая координата продвигается только при строго отрицательной ошибке
                ;   пологие ядра накапливают байт и сохраняют его при смене байта, строки либо завершении, возможны записи неизменённого соседнего байта
                ;   крутые ядра сохраняют байт для каждого пикселя, конечная точка всё равно исключена
                ;   AND использует инверсную маску и JR NC, OR/XOR прямую маску и JR C, сохраняются фактические изменяемые байты инструкций
                ;   SP=0020 является шагом строки, DI/EI здесь нет, ISR не должен использовать этот временный стек, новые области памяти не выделяются
                ;   P=53+3*Swap+2*Right-Steep для основного непустого входа, для DrawPacked P меньше на 8 M1
                ;   Swap означает обмен концов по First, Right направление вправо, Steep крутое ядро, N число пикселей, Krow число коррекций отрицательной ошибки, Kbyte число переходов между байтами
                ;   пологий путь имеет P+9*N+4*Krow+4*Kbyte+4-LastRow M1, LastRow=1 только при коррекции строки на последнем пикселе
                ;   крутой путь имеет P+9*N+4*Krow+Kbyte+3-LastRightByte M1, LastRightByte=1 только при правом байтовом переходе на последнем пикселе
                ;   для равных концов DrawPacked N=256, хотя большая длина равна нулю, этот путь не заменяется пустым основным входом
                ;   56064 сценария основного входа сверили все регистры с R, полное число M1, всю физическую RAM и кратность записей, все 256 исходных R охвачены
                ;   77824 сценария вызывающего сверили R обоих прямых рисователей, включая 512 равных концов, точные T, все совместные входы, IRQ, сборка и нативный запуск не доказаны
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
                LD (@ActionLineRasterState.SavedSP), SP
                LD SP, @ActionLineRasterConst.RowBytes
                ; Расчёт разности First, при отрицательном результате концы меняются местами.
                LD A, D
                SUB H
                JR NC, @ThreeD.DrawLinearLine.OrderedY                          ; переход, если First второго конца не меньше First первого, обмен концов не нужен

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
                JR C, @ThreeD.DrawLinearLine.Rightward                          ; переход, если Second первого конца меньше Second второго, рисовать вправо

                ; Проверка большой длины для левого направления, равенство выбирает пологое ядро.
                CP D
                JR C, @ThreeD.DrawLinearLine.SteepLeft                          ; переход, если модуль deltaSecond меньше deltaFirst, выбрать крутое левое ядро

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
                LD (@ThreeD.DrawLinearLine.ApplyLeft), A
                LD A, (@ActionLineRasterState.BranchOpcode)
                LD (@ThreeD.DrawLinearLine.LeftBoundary), A
                LD A, (HL)
                ; Исходный NOP заменяется AND C, OR C либо XOR C, значения исходного образа не исправляются.
ApplyLeft:      NOP
                RLC C
LeftBoundary:   JR C, @ThreeD.DrawLinearLine.LeftByte                           ; переход, если вращение маски требует предыдущего байта, режим AND меняет opcode проверки Carry на NC

                ; Расчёт следующей ошибки, пиксельный аккумулятор временно сохраняется в альтернативном AF.
LeftError:      EX AF, AF'
                SUB E
                JR C, @ThreeD.DrawLinearLine.LeftRow                            ; переход, если ошибка после вычитания меньшей длины отрицательна, перейти к следующей строке

                EX AF, AF'
                DJNZ @ThreeD.DrawLinearLine.ApplyLeft

                LD (HL), A
                JP @ThreeD.DrawLinearLine.RestoreStack

                ; Сохранение накопленного байта перед переходом в предыдущий байт линейной строки.
LeftByte:       LD (HL), A
                DEC L
                LD A, (HL)
                JP @ThreeD.DrawLinearLine.LeftError

                ; Коррекция отрицательной ошибки и сохранение байта перед прибавлением шага строки.
LeftRow:        ADD A, D
                EX AF, AF'
                LD (HL), A
                ADD HL, SP
                LD A, (HL)
                DJNZ @ThreeD.DrawLinearLine.ApplyLeft

                JP @ThreeD.DrawLinearLine.RestoreStack

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
                LD (@ThreeD.DrawLinearLine.ApplyDownLeft), A
                LD A, (@ActionLineRasterState.BranchOpcode)
                LD (@ThreeD.DrawLinearLine.LeftDownBound), A
                ; Чтение текущего пиксельного байта, маска применяется подготовленной командой.
LeftDownPixel:  LD A, (HL)
ApplyDownLeft:  NOP
                LD (HL), A
                ADD HL, SP
                ; Расчёт ошибки после обязательного продвижения на строку.
                EX AF, AF'
                SUB E
                JR NC, @ThreeD.DrawLinearLine.LeftDownNext                      ; переход, если ошибка неотрицательна, горизонтальную фазу не менять

                ADD A, D
                RLC C
LeftDownBound:  JR C, @ThreeD.DrawLinearLine.LeftDownByte                       ; переход, если горизонтальный шаг пересёк байт, режим AND меняет opcode проверки Carry на NC

LeftDownNext:   EX AF, AF'
                DJNZ @ThreeD.DrawLinearLine.LeftDownPixel

                JP @ThreeD.DrawLinearLine.RestoreStack

LeftDownByte:   DEC L
                EX AF, AF'
                DJNZ @ThreeD.DrawLinearLine.LeftDownPixel

                JP @ThreeD.DrawLinearLine.RestoreStack

                ; -----------------------------------------
                ; Правое направление
                ; Расчёт модуля deltaSecond, затем выбор крутой либо пологой ветви.
Rightward:      NEG
                CP D
                JR C, @ThreeD.DrawLinearLine.SteepRight                         ; переход, если модуль deltaSecond меньше deltaFirst, выбрать крутое правое ядро

                ; Подготовка большой и меньшей длин пологого правого ядра.
                LD E, D
                LD D, A
                LD B, A
                SRL A
                EX AF, AF'
                ; Обновление opcode пикселя и перехода между байтами правого ядра.
                LD A, (@ActionLineRasterState.PixelOpcode)
                LD (@ThreeD.DrawLinearLine.ApplyRight), A
                LD A, (@ActionLineRasterState.BranchOpcode)
                LD (@ThreeD.DrawLinearLine.RightBoundary), A
                LD A, (HL)
ApplyRight:     NOP
                RRC C
RightBoundary:  JR C, @ThreeD.DrawLinearLine.RightByte                          ; переход, если вращение маски требует следующего байта, режим AND меняет opcode проверки Carry на NC

                ; Расчёт следующей ошибки пологого правого ядра.
RightError:     EX AF, AF'
                SUB E
                JR C, @ThreeD.DrawLinearLine.RightRow                           ; переход, если ошибка отрицательна, скорректировать её и перейти к следующей строке

                EX AF, AF'
                DJNZ @ThreeD.DrawLinearLine.ApplyRight

                LD (HL), A
                JP @ThreeD.DrawLinearLine.RestoreStack

                ; Сохранение накопленного байта перед переходом в следующий байт строки.
RightByte:      LD (HL), A
                INC L
                LD A, (HL)
                JP @ThreeD.DrawLinearLine.RightError

                ; Коррекция ошибки и переход на следующую линейную строку.
RightRow:       ADD A, D
                EX AF, AF'
                LD (HL), A
                ADD HL, SP
                LD A, (HL)
                DJNZ @ThreeD.DrawLinearLine.ApplyRight

                JP @ThreeD.DrawLinearLine.RestoreStack

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
                LD (@ThreeD.DrawLinearLine.ApplyDownRight), A
                LD A, (@ActionLineRasterState.BranchOpcode)
                LD (@ThreeD.DrawLinearLine.RightDownBound), A
                ; Чтение и запись текущего пиксельного байта до продвижения на следующую строку.
RightDownPixel: LD A, (HL)
ApplyDownRight: NOP
                LD (HL), A
                ADD HL, SP
                ; Расчёт ошибки и необходимости продвижения горизонтальной фазы.
                EX AF, AF'
                SUB E
                JR NC, @ThreeD.DrawLinearLine.RightDownNext                     ; переход, если ошибка неотрицательна, горизонтальную фазу не менять

                ADD A, D
                RRC C
RightDownBound: JR C, @ThreeD.DrawLinearLine.RightDownByte                      ; переход, если горизонтальный шаг требует следующего байта, режим AND меняет opcode проверки Carry на NC

RightDownNext:  EX AF, AF'
                DJNZ @ThreeD.DrawLinearLine.RightDownPixel

                JP @ThreeD.DrawLinearLine.RestoreStack

RightDownByte:  INC L
                EX AF, AF'
                DJNZ @ThreeD.DrawLinearLine.RightDownPixel

                ; -----------------------------------------
                ; Возврат к CPU-стеку
                ; Восстановление исходного SP перед настоящим RET, временный шаг строки больше не используется.
RestoreStack:   LD SP, #0000
                RET

                ; -----------------------------------------
                endmodule
                endmodule
