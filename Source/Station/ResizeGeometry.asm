                module Station
                module ResizeGeometry
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [интерактивная геометрия и стековые выходы](../../Docs/TrackGeometry.md)
; -----------------------------------------
; Внутреннее продолжение изменения размера с ограничениями класса и видимого пересечения
; исходная запись 4, файловые смещения #6A1F..#6B1B
; In:
;   BC - текущая знаковая позиция, DE - текущие размеры, SP содержит FGeometryHitFrame и FPointerGuardFrame
;   Record кадра указывает запись, четыре минимума TrackState и HoldResize подготовлены TrackItemGeometry
;   выполняются геометрические и аппаратные предусловия TrackItemGeometry
; Out:
;   при запрете битом 1 FlagsCache результат соответствует CancelHitFrame
;   иначе Width,Height записи заменены результатом, PointerXY привязан к новому размеру, результат соответствует FinishGeometry
; Corrupt:
;   HL, DE, BC, AF, IX относительно входа продолжения, исходный контекст возвращается из кадра
; Note:
;   базовый кадр соответствует FPointerGuardFrame, SavedBC, SavedDE, SavedHL, SavedAF, SavedIX, ReturnAddress
;   альтернативные регистры и IY сохраняются собственными процедурами, I и IFF не меняются
;   при HALT обработчик прерывания обязан сохранить CPU-контекст, модель только задаёт входные кадры
;   отрицательный байтовый результат размера заменяется прежним размером, после этого минимум и максимум всё равно применяются
;   последующее ограничение видимого пересечения может сделать размер меньше минимума класса
;   предпросмотр удаляется теми же исходными XOR-границами перед повторением либо фиксацией размера
;   это продолжение с уже созданными кадрами, обычный CALL недопустим
; -----------------------------------------
                ; изменяемый LD A содержит FlagsCache, запрет размера находится в бите 1
Entry:          LD A, #00
                AND @PointerConst.BottomBlockMask
                JR NZ, @Station.CancelHitFrame.Entry                            ; переход, если изменение размера запрещено, снять кадр попадания без действия

                ; восстановление фона указателя перед XOR-предпросмотром размера
                CALL @Station.SuspendPointer.Entry
                ; создание Anchor в FGeometryDragFrame из абсолютного PointerXY
                LD HL, (@StationState.PointerXY)
                PUSH HL
                ; сохранение текущей геометрии и наложение её временного контура
ResizeOutline:  LD (@TrackState.RestoreOrigin), BC
                LD (@TrackState.RestoreSize), DE
                CALL @Station.XorRectOutline.Entry
                ; перенос координат в программный центр для измерения полупиксельной дельты
                LD HL, @TrackConst.CenterXY
                LD (@StationState.PointerXY), HL
                ; создание FGeometryWaitFrame для текущей геометрии и центра
                PUSH BC
                PUSH DE
                PUSH HL
                ; ожидание входного кадра изменения размера
ResizeWait:     HALT
                CALL @Station.MergeActionInputs.Entry
                ; проверка отпускания действия до проверки движения
                AND A
                JR Z, @Station.ResizeGeometry.ResizeDelta                       ; переход, если код действия нулевой, вычислить итоговую дельту

                ; проверка параметров движения при удерживаемом действии
                CALL @Station.TestMotionParameters.Entry
                JR Z, @Station.ResizeGeometry.ResizeWait                        ; переход, если движение отсутствует, снова ждать кадр

                ; расчёт дельт из разности половин текущего PointerXY и центральной точки
ResizeDelta:    POP DE
                LD HL, (@StationState.PointerXY)
                SRL H
                SRL D
                SRL L
                SRL E
                LD A, H
                SUB D
                LD H, A
                LD A, L
                SUB E
                LD L, A
                ; восстановление текущих размеров и исходной позиции из FGeometryWaitFrame
                POP DE
                POP BC
                ; расчёт новой ширины, отрицательный байтовый результат сначала заменяется прежней шириной
                LD A, E
                ADD A, L
                JP P, @Station.ResizeGeometry.LimitWidth                        ; переход, если результат ширины неотрицателен, применить экранные ограничения

                LD L, E
                LD A, L
                ; проверка ширины на превышение 32 знакомест
LimitWidth:     LD L, A
                CP @ScreenConst.ByteColumns + 1
                JP C, @Station.ResizeGeometry.MinWidth                          ; переход, если ширина не больше 32, проверить минимум класса

                SUB @ScreenConst.ByteColumns
                NEG
                ADD A, L
                LD L, A
                JP @Station.ResizeGeometry.FitWidth

                ; изменяемый CP содержит минимальную ширину класса
MinWidth:       CP @TrackConst.Class00Min
                JP NC, @Station.ResizeGeometry.FitWidth                         ; переход, если ширина не меньше минимума, сохранить её

                ; операнд LD L содержит тот же минимальный размер
                LD L, @TrackConst.Class00Min
                ; ограничение ширины для непустого пересечения с экраном при исходной колонке
FitWidth:       LD A, C
                DEC A
                ADD A, L
                JP P, @Station.ResizeGeometry.RightWidth                        ; переход, если правая грань неотрицательна, проверить правый предел

                NEG
                ADD A, L
                LD L, A
                JP @Station.ResizeGeometry.HeightDelta

                ; проверка правой крайней колонки после изменения ширины
RightWidth:     CP @ScreenConst.ByteColumns
                JP C, @Station.ResizeGeometry.HeightDelta                       ; переход, если правая грань меньше 32, сохранить ширину

                SUB @ScreenConst.LastColumn
                NEG
                ADD A, L
                LD L, A
                ; расчёт новой высоты, отрицательный байтовый результат сначала заменяется прежней высотой
HeightDelta:    LD A, D
                ADD A, H
                JP P, @Station.ResizeGeometry.LimitHeight                       ; переход, если результат высоты неотрицателен, применить экранные ограничения

                LD H, D
                LD A, H
                ; проверка высоты на превышение 24 знакомест
LimitHeight:    LD H, A
                CP @ScreenConst.CharRows + 1
                JP C, @Station.ResizeGeometry.MinHeight                         ; переход, если высота не больше 24, проверить минимум класса

                SUB @ScreenConst.CharRows
                NEG
                ADD A, H
                LD H, A
                JP @Station.ResizeGeometry.FitHeight

                ; изменяемый CP содержит минимальную высоту класса
MinHeight:      CP @TrackConst.Class00Min
                JP NC, @Station.ResizeGeometry.FitHeight                        ; переход, если высота не меньше минимума, сохранить её

                ; операнд LD H содержит тот же минимальный размер
                LD H, @TrackConst.Class00Min
                ; ограничение высоты для видимости хотя бы части элемента при исходной строке
FitHeight:      LD A, B
                DEC A
                ADD A, H
                JP P, @Station.ResizeGeometry.BottomHeight                      ; переход, если нижняя грань неотрицательна, проверить нижний предел

                NEG
                ADD A, H
                LD H, A
                JP @Station.ResizeGeometry.PreviewSize

                ; проверка нижней крайней строки после изменения высоты
BottomHeight:   CP @ScreenConst.CharRows
                JP C, @Station.ResizeGeometry.PreviewSize                       ; переход, если нижняя грань меньше 24, сохранить высоту

                SUB @ScreenConst.CharRows - 1
                NEG
                ADD A, H
                LD H, A
                ; сохранение новой геометрии в FGeometryPreview перед чтением прежних Origin и Size
PreviewSize:    EX DE, HL
                PUSH BC
                PUSH DE
                LD BC, (@TrackState.RestoreOrigin)
                LD DE, (@TrackState.RestoreSize)
                ; ожидание кадра перед удалением прежнего XOR-контура
WaitSizeErase:  HALT
                CALL @Station.XorRectOutline.Entry
                ; восстановление новых размеров и проверка продолжения ввода
                POP DE
                POP BC
                CALL @Station.MergeActionInputs.Entry
                ; изменяемый CP HoldResize, исходный операнд один
                CP #01
                JP Z, @Station.ResizeGeometry.ResizeOutline                     ; переход, если код действия равен HoldResize, повторить предпросмотр с новым размером

                ; перестановка Anchor, ClickCell и Record для записи новых физических размеров
CommitSize:     POP HL
                EX (SP), HL
                POP HL
                EX (SP), HL
                ; переход к FInterfaceItem.Width и сохранение прежней ширины перед заменой
                INC HL
                INC HL
                LD A, (HL)
                ; запись новых Width и Height, остальные поля записи сохраняются
                LD (HL), E
                INC HL
                LD (HL), D
                ; чтение исходного абсолютного указателя и расчёт изменения ширины в E
                POP HL
                SUB E
                NEG
                LD E, A
                ; расчёт новой колонки указателя из исходной колонки и изменения ширины
                LD A, L
                SRL A
                SRL A
                SRL A
                ADD A, E
                JP P, @Station.ResizeGeometry.ScalePointerX                     ; переход, если новая колонка указателя неотрицательна, сохранить её

                XOR A
                ; преобразование колонки в пиксели без отдельного верхнего ограничения, младшие биты захвата сохраняются
ScalePointerX:  SLA A
                SLA A
                SLA A
                LD E, A
                LD A, L
                AND @PointerConst.Low3Mask
                OR E
                LD L, A
                ; расчёт последней строки нового прямоугольника для привязки Y указателя
                LD A, B
                ADD A, D
                DEC A
                RLCA
                RLCA
                RLCA
                LD B, A
                LD A, H
                AND @PointerConst.Low3Mask
                OR B
                LD H, A
                ; фиксация пиксельного указателя и переход к общему выполненному выходу
                LD (@StationState.PointerXY), HL
                JP @Station.FinishGeometry.Entry

                endmodule
                endmodule
