                module Station
                module RegisterAndFillItem
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [Interface.md](../../Docs/Interface.md)
; -----------------------------------------
; Регистрация видимых знакомест элемента и заливка его bitmap с возвратом указателя Flags
; исходная запись 4, файловые смещения #5FAD..#5FF4
; In:
;   HL - индекс существующей записи FInterfaceItem с шириной 1..32 и высотой 1..24
;   исходная геометрия записи имеет непустое пересечение с экраном, после снятия прежней регистрации имеется свободная индексная пара
;   таблицы #82..#84 подготовлены, в окне #C000 выбрана страница станционного кода, FillMode задаёт бит заполнения
; Out:
;   HL - адрес поля Flags исходной записи, StationState.Items + 16*исходный индекс + FInterfaceItem.Flags
;   DE - D равен нулю, E видимая ширина, BC - видимые Y и X, AF соответствует FillRectangle для отсечённого прямоугольника
;   AF' - рабочее состояние RegisterItemCells, A'=2*(32-видимая ширина), F' от INC (32-видимая ширина), Carry'=0
;   видимые знакоместа зарегистрированы кодом владельца, bitmap залит по FillMode, текстовое окно настроено по исходной геометрии
; Corrupt:
;   HL, DE, BC, AF, AF'
; Note:
;   первые четыре поля X, Y, Width, Height читаются без изменения исходной записи
;   EX (SP),HL обменивает сохранённый индекс с указателем Flags перед RegisterItemCells, последующий POP HL возвращает именно указатель Flags
;   FillRectangle вызывается хвостовым JP и возвращается исходному вызывающему коду
;   альтернативные HL', DE', BC', индексные регистры, I и IFF сохраняются, SP восстанавливается
;   атрибуты не меняются, проверки пустого пересечения и отсутствия свободной пары здесь нет
; -----------------------------------------
                ; сохранение исходного индекса до чтения геометрии записи
Entry:          PUSH HL
                ; выбор начала FInterfaceItem по нулевому смещению поля
                XOR A
                CALL @Station.GetItemField.Entry
                ; чтение X, Y, Width и Height в C, B, E и D
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                ; настройка текстового окна по исходной геометрии до экранного отсечения
                CALL @Station.SetupTextWindow.Entry
                ; проверка знака левой байтовой колонки элемента
                LD A, C
                AND A
                JP P, @Station.RegisterAndFillItem.ClipRight                    ; переход, если левая колонка неотрицательна, проверяется правый край

                ; расчёт ширины после пропуска отрицательных колонок
                ADD A, E
                LD E, A
                LD C, #00
                JP @Station.RegisterAndFillItem.ClipY

                ; расчёт исключённой правой колонки исходного прямоугольника
ClipRight:      ADD A, E
                ; проверка, что правая граница не превышает 32 колонки
                CP @ScreenConst.ColumnEndLimit
                JP C, @Station.RegisterAndFillItem.ClipY                        ; переход, если правая граница не превышает 32, ширина сохраняется

                ; расчёт ширины до правого края экрана
                SUB @ScreenConst.ByteColumns
                NEG
                ADD A, E
                LD E, A
                ; проверка знака верхней строки знакомест элемента
ClipY:          LD A, B
                AND A
                JP P, @Station.RegisterAndFillItem.ClipBottom                   ; переход, если верхняя строка неотрицательна, проверяется нижний край

                ; расчёт высоты после пропуска отрицательных строк знакомест
                ADD A, D
                LD D, A
                LD B, #00
                JP @Station.RegisterAndFillItem.KeepFlags

                ; расчёт исключённой нижней строки исходного прямоугольника
ClipBottom:     ADD A, D
                ; проверка, что нижняя граница не превышает 24 строки знакомест
                CP @ScreenConst.RowEndLimit
                JP C, @Station.RegisterAndFillItem.KeepFlags                    ; переход, если нижняя граница не превышает 24, высота сохраняется

                ; расчёт высоты до нижнего края экрана
                SUB @ScreenConst.CharRows
                NEG
                ADD A, D
                LD D, A
                ; замена сохранённого индекса указателем Flags, индекс передаётся регистрации через HL
KeepFlags:      EX (SP), HL
                ; регистрация видимых знакомест до фактической заливки bitmap
                CALL @Station.RegisterItemCells.Entry
                ; возврат указателя Flags для дальнейшего обработчика рисования элемента
                POP HL
                JP @Station.FillRectangle.Entry

                endmodule
                endmodule
