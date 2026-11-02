                module Controls
                module InitializeBufferPoints
                ; Документация [алгоритм и проверка](../../Docs/ControlsBufferPoints.md)
                ; -----------------------------------------
                ; Подготовка 35 координат Y,X с исходным ограничением диапазонов
                ; исходная запись 22, банк 1, смещения #0AB3..#0AE2
                ; In:
                ;   HL, DE, BC, AF входных аргументов не задают, начальное состояние берётся из Seed
                ;   банк 1 выбран, Seed и все 70 байтов ControlsBufferPoints доступны для записи
                ;   на CPU-стеке внешний возврат, ещё два байта используются настоящими CALL генератора
                ; Out:
                ;   HL=адрес после Point22, DE и BC сохранены, A=46, F=42
                ;   подготовлены 35 записей Y,X, Y=1..94, X=1..253, распределение неравномерное
                ;   Seed обновлён 70 раз, перед каждой парой сначала генерируется X, затем Y, физически сохраняются Y, затем X
                ;   HL', DE', BC' содержат последний результат генератора, A' содержит Y последней точки, F' только Carry последнего ограничения Y
                ;   IX и IY, I, IM и IFF сохраняются, SP=входной SP+2
                ; Corrupt:
                ;   HL, AF, HL', DE', BC', AF', 70 байтов точек, Seed, два байта CPU-стека, R
                ; Note:
                ;   X=0 заменяется на 2, X>=254 уменьшается на 2
                ;   Y сначала ограничивается AND 7F, нуль заменяется на 2, значения >=95 уменьшаются на 64
                ;   изменённые границы или равномерный генератор исправили бы оригинальный алгоритм, здесь они не вводятся
                ; -----------------------------------------
                ; выбор первой физической записи Y,X в таблице из 35 точек
Entry:          LD HL, @ControlsBufferPoints.Point00
                ; создание горизонтальной координаты настоящим вызовом генератора
NextPoint:      CALL @Controls.NextBufferRandom.Entry
                ; проверка нулевой горизонтальной координаты перед заменой на 2
                CP @BufferPointConst.MinCoordinate
                JR NC, @Controls.InitializeBufferPoints.LimitX                  ; переход, если X не равен нулю, пропустить замену нулевой координаты

                ADD A, @BufferPointConst.EdgeStep
                ; проверка верхней границы горизонтальной координаты
LimitX:         CP @BufferPointConst.XUpperLimit
                JR C, @Controls.InitializeBufferPoints.GenerateY                ; переход, если X меньше 254, оставить полученное значение

                SUB @BufferPointConst.EdgeStep
                ; сохранение X в альтернативном A на время второго вызова генератора
GenerateY:      EX AF, AF'
                CALL @Controls.NextBufferRandom.Entry
                ; ограничение вертикальной координаты семью битами
                AND @BufferPointConst.YIndexMask
                ; проверка нулевой вертикальной координаты перед заменой на 2
                CP @BufferPointConst.MinCoordinate
                JR NC, @Controls.InitializeBufferPoints.LimitY                  ; переход, если Y не равен нулю, пропустить замену нулевой координаты

                ADD A, @BufferPointConst.EdgeStep
                ; проверка верхней границы вертикальной координаты
LimitY:         CP @BufferPointConst.YUpperLimit
                JR C, @Controls.InitializeBufferPoints.StorePoint               ; переход, если Y меньше 95, оставить полученное значение

                SUB @BufferPointConst.YFold
                ; сохранение Y первым физическим байтом записи, затем восстановление и сохранение X
StorePoint:     LD (HL), A
                INC L
                EX AF, AF'
                LD (HL), A
                INC L
                LD A, L
                ; проверка заполнения всех 70 байтов таблицы
                CP @BufferPointConst.ByteCount
                JP C, @Controls.InitializeBufferPoints.NextPoint                ; переход, если младший байт указателя меньше 46, подготовить следующую точку

                RET

                endmodule
                endmodule
