                module Map
                module DispatchMapClipEdge
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [обмен точек, табличный вход и два возвратных протокола](../../Docs/ClipCases.md)
; -----------------------------------------
; Обмен внутреннего первого конца и диспетчеризация отсечения на трёх подставных возвратах
; исходная запись 7, файловые смещения #148B..#14DC
; In:
;   MapClipWork.FirstPoint и SecondPoint содержат два FProjectedPoint с кодами, соответствующими их знаковым координатам
;   полные ClipCodes соответствуют девяти вариантам BuildMapPointOutcodes, разнесённая таблица DE00/DF00 содержит исходные доступные цели
;   KARTA выбран, рабочие точки, произведения, углы и выходная страница доступны для записи
;   для исполненных MultiplySigned16 и DivideSigned32To16 действуют их договоры, знаменатель ненулевой, однокомплементный модуль числителя меньше abs(знаменатель)*65536
; Out:
;   CornerBlock=1, OutputSize предварительно сброшен, запросы добавления углов подавлены
;   если первый ClipCodes=F0, полные пятибайтовые записи концов обменены, в том числе у двух внутренних точек
;   выбран индекс ((NOT первый ClipCodes)AND F0)OR(второй ClipCodes AND 0F), цель прочитана с разнесённых страниц
;   создан FClipUnwindFrame с тремя копиями UnknownD4DD.Entry и настоящим входным адресом возврата
;   обычный выход возвращает DE=UnknownD4DD.Entry, A=OutputSize, F от CP 4, размер равен 0, 2 или 4
;   у такого выхода HL, BC рабочие, Z=1 только при четырёх байтах, Carry=1 при размере 0 или 2
;   специальный выход даёт HL=D5B0, DE рабочий, BC=00D3, AF=D481, OutputSize=0
;   две внутренние точки дают размер 2 и копию исходной первой точки, этот результат не принят за отрезок
;   HL', DE', BC', IY, I и IFF сохранены, AF' и IX рабочие, SP обычного внешнего возврата равен входному SP+2
;   табличные случаи могут изменять младшие биты Corners.SeenFlags и четыре слота произведений, старшая тетрада SeenFlags сохраняется
; Corrupt:
;   HL, DE, BC, AF, AF', IX
; Note:
;   обычный RET обработчика сначала использует одну подставную копию, общий выход снимает две остальные
;   UnwindClipFrame снимает все три слова сразу, его A=D4 не является размером результата
;   проверка всех ветвей доказывает не более двух выходных точек и предварительное вычисление кэшированных числителей при CornerBlock=1
;   полный геометрический порядок действий каждого табличного случая UnknownD4DD оформляется отдельно
; -----------------------------------------
                ; установка запрета добавлять углы для этого входа отсечения
Entry:          LD A, #01
                LD (@MapClipWork.Corners.BlockCode), A
                ; проверка внутренней первой точки по полному кодовому байту F0
                LD A, (@MapClipWork.FirstPoint.ClipCodes)
                CP @MapClipConst.InsideCode
                JR NZ, @Map.DispatchMapClipEdge.PickCase                        ; переход, если первая точка не внутренняя, сохранить порядок концов

                ; обмен пятибайтовых записей, внутренняя первая точка переносится во вторую позицию
                LD B, A
                LD A, (@MapClipWork.SecondPoint.ClipCodes)
                LD (@MapClipWork.FirstPoint.ClipCodes), A
                LD A, B
                LD (@MapClipWork.SecondPoint.ClipCodes), A
                ; обмен исходных 16-битных координат X без изменения представления
                LD HL, (@MapClipWork.FirstPoint.X)
                LD DE, (@MapClipWork.SecondPoint.X)
                LD (@MapClipWork.SecondPoint.X), HL
                LD (@MapClipWork.FirstPoint.X), DE
                ; обмен исходных 16-битных координат Y с сохранением пары кодов отсечения
                LD HL, (@MapClipWork.FirstPoint.Y)
                LD DE, (@MapClipWork.SecondPoint.Y)
                LD (@MapClipWork.SecondPoint.Y), HL
                LD (@MapClipWork.FirstPoint.Y), DE
                ; сброс байтового размера перед исполнением выбранного случая
PickCase:       XOR A
                LD (@MapClipWork.OutputSize), A
                ; расчёт старшей тетрады индекса из дополнения кодов первой точки
                LD A, (@MapClipWork.FirstPoint.ClipCodes)
                CPL
                AND @MapClipConst.Complement
                LD L, A
                ; расчёт младшей тетрады индекса по кодам второй точки
                LD A, (@MapClipWork.SecondPoint.ClipCodes)
                AND @MapClipConst.SideMask
                OR L
                LD L, A
                ; поиск младшего и старшего байтов цели на разнесённых страницах DE и DF
                LD H, @MapClipConst.DispatchLowPage
                LD E, (HL)
                INC H
                LD D, (HL)
                EX DE, HL
                ; создание трёх подставных возвратов, общий и специальный выходы снимают их по-разному
                LD DE, @Map.MapClipCases.Entry
                PUSH DE
                PUSH DE
                PUSH DE
                ; передача управления обработчику без четвёртого слова возврата
                JP (HL)

                endmodule
                endmodule
