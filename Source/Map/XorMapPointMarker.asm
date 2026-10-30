                module Map
                module XorMapPointMarker
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [упаковка точки, строгие границы и семь двухбайтовых строк](../../Docs/MapPointMarker.md)
; -----------------------------------------
; Отсечение и XOR семистрочного фазового маркера точки карты
; исходная запись 7, файловые смещения #0231..#0324
; In:
;   HL - начало ресурса с восемью фазами по 16 байтов, первые 14 байтов каждой фазы доступны для чтения
;   DE - первое слово точки, BC - второе, координаты X=256*E+C и Y=256*D+B до перестановки
;   MapViewState содержит согласованные начала и размеры, для обычной области Width>=8, Height>=7 без оборачивания вычитаний
;   MapScreenTables.RowHigh, RowLow и ColumnByte построены для этой области, KARTA выбран
;   допущенный прямоугольник семи строк и двух байтов полностью лежит в доступном bitmap, стек и ресурс вне него
; Out:
;   вычисляет DX=(X-OriginX-3) modulo 65536 и DY=(Y-OriginY-3) modulo 65536
;   при ненулевом старшем байте DX или DY, DXlow>=(Width-8) modulo 256 либо DYlow>=(Height-7) modulo 256 возвращает без записи
;   на отказе HL=DY, DE=DX, BC исходный адрес ресурса, AF от проверки старших байтов либо последнего CP границы
;   при допуске выбирает фазу DX AND 7 со смещением 16*(DX AND 7) от ресурса
;   семь строк по два байта объединяются с bitmap операцией XOR, атрибуты не меняются
;   при допуске HL=ресурс+смещение фазы+13, DE адрес второго байта седьмой строки, BC исходный ресурс
;   AF при допуске содержит итоговый второй байт седьмой строки и логические флаги этого XOR
;   все альтернативные и индексные регистры, I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   равенство каждой границе отсекается отдельным RET Z, нельзя заменить сравнения нестрогими
;   вычитания Width-8 и Height-7 байтовые, для нештатных малых размеров сохраняется их оборачивание
;   адрес первой строки складывается из RowHigh[DY], RowLow[DY] и ColumnByte[DX], перенос младшего сложения в D не добавляется
;   семь строк развёрнуты без счётчика, между ними применяется исходная схема экранного адреса Spectrum
;   два последних байта каждой 16-байтовой фазы этим входом не читаются, их общее назначение не объявляется отсутствующим
;   FMapPointMarkerFrame описывает максимальную глубину трёх сохранённых слов до отсечения, все они сняты перед любым RET
; -----------------------------------------
                ; перестановка старших координатных байтов для получения полной координаты X в BC и Y в DE
Entry:          LD A, B
                LD B, E
                LD E, A
                ; сохранение адреса фазового ресурса и полной координаты Y до расчёта относительного положения
                PUSH HL
                PUSH DE
                ; чтение разнесённых байтов начала области и их перепаковка в OriginX и OriginY
                LD HL, (@MapViewState.OriginHigh)
                LD DE, (@MapViewState.OriginLow)
                LD A, D
                LD D, L
                LD L, A
                ; сохранение OriginY и расчёт DX=X-OriginX-3 с полным 16-битным оборачиванием
                PUSH HL
                LD H, B
                LD L, C
                OR A
                SBC HL, DE
                DEC HL
                DEC HL
                DEC HL
                EX DE, HL
                ; расчёт DY=Y-OriginY-3 и возврат адреса ресурса в BC до первых выходов
                POP BC
                POP HL
                OR A
                SBC HL, BC
                DEC HL
                DEC HL
                DEC HL
                POP BC
                ; проверка нулевых старших байтов обеих относительных координат
                LD A, H
                OR D
                RET NZ                                                          ; выход, если старший байт DX или DY ненулевой, маркер находится вне байтовой области

                ; расчёт исключённой правой границы Width-8 и сравнение с DX
                LD A, (@MapViewState.Width)
                SUB @MapMarkerConst.RightInset
                CP E
                RET C                                                           ; выход, если DX больше правой границы Width-8, маркер не помещается

                RET Z                                                           ; выход, если DX равен исключённой правой границе Width-8

                ; расчёт исключённой нижней границы Height-7 и сравнение с DY
                LD A, (@MapViewState.Height)
                SUB @MapMarkerConst.BottomInset
                CP L
                RET C                                                           ; выход, если DY больше нижней границы Height-7, маркер не помещается

                RET Z                                                           ; выход, если DY равен исключённой нижней границе Height-7

                ; поиск первой экранной строки через RowHigh[DY] и RowLow[DY]
                LD H, @MapMarkerConst.RowHighPage
                LD D, (HL)
                INC H
                LD A, (HL)
                ; расчёт горизонтального байтового адреса через ColumnByte[DX] без переноса в старший байт
                INC H
                LD L, E
                ADD A, (HL)
                LD E, A
                ; расчёт смещения восьми фаз, младшие три разряда DX умножаются на 16
                LD A, L
                AND #07
                RLCA
                RLCA
                RLCA
                RLCA
                LD L, A
                ; прибавление смещения фазы к сохранённому адресу ресурса
                LD H, #00
                ADD HL, BC
                ; объединение двух байтов строки 1 маркера с экраном через XOR
DrawRow0:       LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                DEC E
                ; расчёт следующего пиксельного адреса внутри восьмистрочного блока Spectrum
                INC D
                LD A, D
                AND #07
                JP NZ, @Map.XorMapPointMarker.DrawRow1                          ; переход, если младшие три разряда D не обнулились, рисовать следующую строку внутри блока

                ; расчёт следующей символьной строки после перехода границы восьми пикселей
                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Map.XorMapPointMarker.DrawRow1                           ; переход, если прибавление 20 переполнило E, адрес уже перешёл в следующую треть экрана

                LD A, D
                SUB @MapMarkerConst.RightInset
                LD D, A
                ; объединение двух байтов строки 2 маркера с экраном через XOR
DrawRow1:       LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                DEC E
                ; расчёт следующего пиксельного адреса внутри восьмистрочного блока Spectrum
                INC D
                LD A, D
                AND #07
                JP NZ, @Map.XorMapPointMarker.DrawRow2                          ; переход, если младшие три разряда D не обнулились, рисовать следующую строку внутри блока

                ; расчёт следующей символьной строки после перехода границы восьми пикселей
                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Map.XorMapPointMarker.DrawRow2                           ; переход, если прибавление 20 переполнило E, адрес уже перешёл в следующую треть экрана

                LD A, D
                SUB @MapMarkerConst.RightInset
                LD D, A
                ; объединение двух байтов строки 3 маркера с экраном через XOR
DrawRow2:       LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                DEC E
                ; расчёт следующего пиксельного адреса внутри восьмистрочного блока Spectrum
                INC D
                LD A, D
                AND #07
                JP NZ, @Map.XorMapPointMarker.DrawRow3                          ; переход, если младшие три разряда D не обнулились, рисовать следующую строку внутри блока

                ; расчёт следующей символьной строки после перехода границы восьми пикселей
                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Map.XorMapPointMarker.DrawRow3                           ; переход, если прибавление 20 переполнило E, адрес уже перешёл в следующую треть экрана

                LD A, D
                SUB @MapMarkerConst.RightInset
                LD D, A
                ; объединение двух байтов строки 4 маркера с экраном через XOR
DrawRow3:       LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                DEC E
                ; расчёт следующего пиксельного адреса внутри восьмистрочного блока Spectrum
                INC D
                LD A, D
                AND #07
                JP NZ, @Map.XorMapPointMarker.DrawRow4                          ; переход, если младшие три разряда D не обнулились, рисовать следующую строку внутри блока

                ; расчёт следующей символьной строки после перехода границы восьми пикселей
                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Map.XorMapPointMarker.DrawRow4                           ; переход, если прибавление 20 переполнило E, адрес уже перешёл в следующую треть экрана

                LD A, D
                SUB @MapMarkerConst.RightInset
                LD D, A
                ; объединение двух байтов строки 5 маркера с экраном через XOR
DrawRow4:       LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                DEC E
                ; расчёт следующего пиксельного адреса внутри восьмистрочного блока Spectrum
                INC D
                LD A, D
                AND #07
                JP NZ, @Map.XorMapPointMarker.DrawRow5                          ; переход, если младшие три разряда D не обнулились, рисовать следующую строку внутри блока

                ; расчёт следующей символьной строки после перехода границы восьми пикселей
                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Map.XorMapPointMarker.DrawRow5                           ; переход, если прибавление 20 переполнило E, адрес уже перешёл в следующую треть экрана

                LD A, D
                SUB @MapMarkerConst.RightInset
                LD D, A
                ; объединение двух байтов строки 6 маркера с экраном через XOR
DrawRow5:       LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                DEC E
                ; расчёт следующего пиксельного адреса внутри восьмистрочного блока Spectrum
                INC D
                LD A, D
                AND #07
                JP NZ, @Map.XorMapPointMarker.DrawRow6                          ; переход, если младшие три разряда D не обнулились, рисовать следующую строку внутри блока

                ; расчёт следующей символьной строки после перехода границы восьми пикселей
                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Map.XorMapPointMarker.DrawRow6                           ; переход, если прибавление 20 переполнило E, адрес уже перешёл в следующую треть экрана

                LD A, D
                SUB @MapMarkerConst.RightInset
                LD D, A
                ; объединение двух байтов строки 7 маркера с экраном через XOR
DrawRow6:       LD A, (DE)
                XOR (HL)
                LD (DE), A
                INC HL
                INC E
                LD A, (DE)
                XOR (HL)
                LD (DE), A
                RET

                endmodule
                endmodule
