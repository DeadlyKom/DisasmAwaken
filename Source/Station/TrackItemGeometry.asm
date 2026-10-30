                module Station
                module TrackItemGeometry
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [интерактивная геометрия и стековые выходы](../../Docs/TrackGeometry.md)
; -----------------------------------------
; Выбор и полный цикл изменения позиции либо размера элемента с XOR-предпросмотром
; исходная запись 4, файловые смещения #687C..#6A03
; In:
;   HL, DE, BC, IX - сохраняемый контекст, AF - исходный A возвращается, входной Z выбирает удерживаемый код 1 при Z=1 либо 2 при Z=0
;   StationState.PointerXY - видимые пиксельные координаты, карта владельцев и её пары индексов доступны
;   для допустимого владельца FInterfaceItem имеет Width=1..32,Height=1..24 и непустое пересечение с экраном
;   TrackState.FlagsCache задаёт запреты, вызывающий код подготавливает его отдельно от текущего Flags записи
;   таблицы адресов готовы, выполняются предусловия SuspendPointer и XorRectOutline, HALT получает корректное пробуждение
; Out:
;   HL, DE и BC сохранены, A исходный, IX сохранён
;   без выбранного действия F=AND(A), Carry=0, геометрия и PointerXY сохранены
;   при выполненном действии F=(AND_flags(A) AND #C4) OR (A AND #28) OR 1
;   после действия изменены X,Y либо Width,Height, указатель привязан к результату, EventEnabled=0,UpdateBlocked=1
;   фон XOR-предпросмотра восстановлен, ResumePointer не вызывается
; Corrupt:
;   AF
; Note:
;   базовый кадр соответствует FPointerGuardFrame, SavedBC, SavedDE, SavedHL, SavedAF, SavedIX, ReturnAddress
;   альтернативные регистры и IY сохраняются собственными процедурами, I и IFF не меняются
;   при HALT обработчик прерывания обязан сохранить CPU-контекст, модель только задаёт входные кадры
;   HoldMove и HoldResize записываются даже без владельца, четыре минимума обновляются при допустимом индексе
;   минимум равен 3 для Flags AND #C0=0, 2 для #40, иначе 1, бит 5 в этом выборе не участвует
;   перемещение запрещается битом 2 FlagsCache, размер битом 1, это тот же набор разрядов, который меняет краевые формы указателя
;   при отсутствии владельца и старшем байте индексной пары #FF происходит симметричный возврат без действия
;   дельта каждого кадра равна floor(новый пиксель/2)-floor(центральный пиксель/2), центр X=128,Y=96
;   повторное изменение может завершиться с прежними значениями геометрии, Carry всё равно установлен
;   кадры FGeometryHitFrame, FGeometryDragFrame, FGeometryWaitFrame и FGeometryPreview описывают вложенные PUSH и EX (SP),HL
;   полное продолжение размера находится в ResizeGeometry.asm, правила выбора и границы подробно описаны в TrackGeometry.md
;   SP восстанавливается на штатных путях, аппаратный ввод и ISR моделью не проверены
; -----------------------------------------
                ; сохранение исходного контекста в существующей раскладке FPointerGuardFrame
Entry:          PUSH IX
                PUSH AF
                PUSH HL
                PUSH DE
                PUSH BC
                ; выбор кода удержания по входному Z, LD A не меняет проверяемый флаг
                LD A, #01
                JR Z, @Station.TrackItemGeometry.SetHoldCodes                   ; переход, если входной Z установлен, удерживаемый код равен 1

                INC A
                ; сохранение кода удержания в обоих изменяемых CP циклов
SetHoldCodes:   LD (@TrackState.HoldMove), A
                LD (@TrackState.HoldResize), A
                ; поиск владельца и символьных координат под пиксельным указателем
                CALL @Station.GetPointerOwner.Entry
                ; проверка отсутствующего владельца перед обращением к индексной паре
                AND A
                JP Z, @Station.ReturnGeometry.Entry                             ; переход, если владельца нет, вернуть исходный A без Carry

                ; расчёт адреса двухбайтового индекса по ненулевому коду владельца
                DEC A
                RLCA
                LD L, A
                LD H, #85
                LD A, (HL)
                INC L
                LD H, (HL)
                LD L, A
                ; проверка старшего байта индексной пары на #FF
                INC H
                JP Z, @Station.ReturnGeometry.Entry                             ; переход, если пара недействительна, вернуть исходный контекст без вложенных слов

                DEC H
                ; получение начала FInterfaceItem по нулевому смещению
                XOR A
                CALL @Station.GetItemField.Entry
                ; создание FGeometryHitFrame из адреса записи и символьных координат попадания
                PUSH HL
                PUSH BC
                ; чтение X,Y,Width,Height из физических полей записи в C,B,E,D
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                ; проверка старших двух разрядов Flags для минимального размера
                LD A, (HL)
                AND @PointerConst.PlainShapeMask
                JR NZ, @Station.TrackItemGeometry.CheckClass40                  ; переход, если старшие два бита ненулевые, проверить класс #40

                LD A, @TrackConst.Class00Min
                JR @Station.TrackItemGeometry.StoreMinimum

                ; проверка класса с минимумом два знакоместа
CheckClass40:   CP @InterfaceFlags.FrontGroup
                JR NZ, @Station.TrackItemGeometry.OtherMinimum                  ; переход, если класс не равен #40, выбрать минимум один

                LD A, @TrackConst.Class40Min
                JR @Station.TrackItemGeometry.StoreMinimum

OtherMinimum:   LD A, #01
                ; самоподмена четырёх операндов сравнения и присваивания минимального размера
StoreMinimum:   LD (@TrackState.MinHeightTest), A
                LD (@TrackState.MinHeightValue), A
                LD (@TrackState.MinWidthTest), A
                LD (@TrackState.MinWidthValue), A
                ; расчёт правой и нижней границ в знакоместах, пока без экранного отсечения
                LD A, E
                ADD A, C
                LD L, A
                LD A, B
                ; проверка отрицательного Y, у такого элемента выбирается перемещение
                AND A
                JP M, @Station.TrackItemGeometry.MoveCheck                      ; переход, если Y отрицателен, проверить разрешение перемещения

                ADD A, D
                LD H, A
                LD A, L
                ; проверка правой границы перед исключением двух крайних исходных колонок
                CP @ScreenConst.ByteColumns
                JR C, @Station.TrackItemGeometry.HitBorder                      ; переход, если правая граница меньше 32, продолжить проверку попадания

                ; проверка исходной колонки на значения больше 29 при правой границе не меньше 32
                LD A, @ScreenConst.LastColumn - 2
                SUB C
                JR C, @Station.TrackItemGeometry.MoveCheck                      ; переход, если исходная колонка больше 29, выбрать перемещение

                ; проверка класса #40, у него требуется совпадение правого нижнего угла
HitBorder:      LD A, (@TrackState.MinHeightTest)
                CP #02
                LD A, D
                JR NZ, @Station.TrackItemGeometry.ClickPlusOne                  ; переход, если класс другой, использовать высоту для выбора типа проверки

                LD A, #01
                ; получение CellX+1 и CellY+1 из Workspace на стеке без потери правой и нижней границ
ClickPlusOne:   EX DE, HL
                EX (SP), HL
                INC L
                INC H
                PUSH HL
                ; проверка однострочного режима, у него сравниваются обе координаты угла
                DEC A
                JR NZ, @Station.TrackItemGeometry.CheckBottom                   ; переход, если режим многострочный, сравнить только нижнюю строку

                ; сравнение упакованной точки Cell+1 с правой нижней границей
                OR A
                SBC HL, DE
                JR @Station.TrackItemGeometry.RestoreClick

                ; сравнение только строки CellY+1 с нижней границей
CheckBottom:    LD A, H
                SUB D
                ; возврат исходного кадра попадания после временного EX (SP),HL
RestoreClick:   POP HL
                EX (SP), HL
                EX DE, HL
                JP Z, @Station.TrackItemGeometry.PixelCorner                    ; переход, если нижняя грань либо угол совпали, уточнить действие по пиксельной позиции

                ; проверка верхней строки по CellY-Y после снятия смещения на единицу
CheckTop:       EX (SP), HL
                LD A, H
                SUB B
                DEC A
                EX (SP), HL
                JR Z, @Station.TrackItemGeometry.MoveCheck                      ; переход, если попадание на верхней строке, выбрать перемещение

                ; снятие кадра попадания при отсутствии действия на границе
                POP BC
                POP HL
                JP @Station.ReturnGeometry.Entry

                ; проверка особого случая обеих пиксельных координат меньше восьми
PixelCorner:    LD HL, (@StationState.PointerXY)
                LD A, L
                OR H
                AND @TrackConst.CellBitsMask
                JP NZ, @Station.ResizeGeometry.Entry                            ; переход, если указатель вне первого знакоместа экрана, выбрать изменение размера

                ; чтение отдельного кэша FlagsCache и проверка запрета перемещения битом 2
MoveCheck:      LD A, (@TrackState.FlagsCache)
                AND @PointerConst.TopBlockMask
                JP NZ, @Station.CancelHitFrame.Entry                            ; переход, если перемещение запрещено, снять кадр попадания и вернуть отсутствие действия

                ; восстановление фона указателя и запрет его периодического обновления
                CALL @Station.SuspendPointer.Entry
                ; расчёт относительного пиксельного захвата PointerXY-8*Origin по модулю 256
                LD HL, (@StationState.PointerXY)
                LD A, B
                SLA A
                SLA A
                SLA A
                SUB H
                NEG
                LD H, A
                LD A, C
                SLA A
                SLA A
                SLA A
                SUB L
                NEG
                LD L, A
                ; создание Anchor в FGeometryDragFrame из относительной точки захвата
                PUSH HL
                ; сохранение текущих Origin и Size в операндах, которыми позже удаляется XOR-предпросмотр
MoveOutline:    LD (@TrackState.RestoreOrigin), BC
                LD (@TrackState.RestoreSize), DE
                ; наложение временного XOR-контура исходной геометрии кадра
                CALL @Station.XorRectOutline.Entry
                ; перенос программных координат указателя в центр X=128,Y=96 для измерения дельты
                LD HL, @TrackConst.CenterXY
                LD (@StationState.PointerXY), HL
                ; создание FGeometryWaitFrame, Origin, Size и центральная точка
                PUSH BC
                PUSH DE
                PUSH HL
                ; ожидание входного кадра без самостоятельного включения прерываний
MoveWait:       HALT
                CALL @Station.MergeActionInputs.Entry
                ; проверка объединённого кода действий, ноль завершает ожидание даже без движения
                AND A
                JR Z, @Station.TrackItemGeometry.MoveDelta                      ; переход, если код действий нулевой, рассчитать итоговую дельту

                ; проверка восьми байтов параметров движения при ненулевом коде действия
                CALL @Station.TestMotionParameters.Entry
                JR Z, @Station.TrackItemGeometry.MoveWait                       ; переход, если движения нет, снова ждать кадр

                ; снятие центральной точки и расчёт дельт как разности половин текущих и центральных координат
MoveDelta:      POP DE
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
                ; восстановление текущих размеров и позиции из FGeometryWaitFrame
                POP DE
                POP BC
                ; расчёт новой колонки с ограничением непустого пересечения, диапазон 1-Width..31
                LD A, C
                ADD A, L
                LD L, A
                JP M, @Station.TrackItemGeometry.ClampLeft                      ; переход, если новая колонка отрицательна, проверить левую границу пересечения

                CP @ScreenConst.ByteColumns
                JP C, @Station.TrackItemGeometry.ClampY                         ; переход, если новая колонка меньше 32, сохранить её

                SUB @ScreenConst.LastColumn
                NEG
                ADD A, L
                LD L, A
                JP @Station.TrackItemGeometry.ClampY

                ; проверка непустого пересечения справа от отрицательного начала
ClampLeft:      DEC A
                ADD A, E
                JP P, @Station.TrackItemGeometry.ClampY                         ; переход, если правая грань остаётся видимой, сохранить отрицательную колонку

                NEG
                ADD A, L
                LD L, A
                ; расчёт новой строки с ограничением непустого пересечения, диапазон 1-Height..23
ClampY:         LD A, B
                ADD A, H
                LD H, A
                JP M, @Station.TrackItemGeometry.ClampTop                       ; переход, если новая строка отрицательна, проверить верхнюю границу пересечения

                CP @ScreenConst.CharRows
                JP C, @Station.TrackItemGeometry.SaveMove                       ; переход, если новая строка меньше 24, сохранить её

                SUB @ScreenConst.CharRows - 1
                NEG
                ADD A, H
                LD H, A
                JP @Station.TrackItemGeometry.SaveMove

                ; проверка видимости нижней грани при отрицательном начале
ClampTop:       DEC A
                ADD A, D
                JP P, @Station.TrackItemGeometry.SaveMove                       ; переход, если нижняя грань остаётся видимой, сохранить отрицательную строку

                NEG
                ADD A, H
                LD H, A
                ; перенос рассчитанной позиции в BC перед удалением старого контура
SaveMove:       LD B, H
                LD C, L
                ; ожидание следующего кадра перед обратным XOR старой геометрии
WaitMoveErase:  HALT
                ; создание FGeometryPreview с новой позицией, чтение прежних Origin и Size из операндов
                PUSH BC
                PUSH DE
                LD BC, #0000
                LD DE, #0000
                ; обратное наложение прежнего контура, восстановление исходных пикселей
                CALL @Station.XorRectOutline.Entry
                ; снятие предпросмотра и проверка продолжения по коду действия
                POP DE
                POP BC
                CALL @Station.MergeActionInputs.Entry
                ; изменяемый CP HoldMove, исходный операнд один
                CP #01
                JP Z, @Station.TrackItemGeometry.MoveOutline                    ; переход, если код действия совпадает с HoldMove, повторить кадр с новой позицией

                ; перестановка Anchor, ClickCell и Record через POP и EX (SP),HL без потери сохранённого контекста
CommitMove:     POP HL
                EX (SP), HL
                POP HL
                EX (SP), HL
                ; запись только X и Y выбранной FInterfaceItem, Saved-поля не меняются
                LD (HL), C
                INC HL
                LD (HL), B
                ; чтение относительной точки захвата для привязки указателя к новой позиции
                POP DE
                ; расчёт итоговой колонки указателя по относительному знакоместу и новой позиции
                LD A, E
                SRL A
                SRL A
                SRL A
                ADD A, C
                JP P, @Station.TrackItemGeometry.ClampPointerX                  ; переход, если колонка указателя неотрицательна, проверить правый предел

                XOR A
                ; проверка правого предела указателя по 32 знакоместам
ClampPointerX:  CP @ScreenConst.ByteColumns
                JR C, @Station.TrackItemGeometry.ScalePointerX                  ; переход, если колонка указателя меньше 32, сохранить её

                LD A, @ScreenConst.LastColumn
                ; восстановление пиксельного X из колонки и исходных младших трёх битов захвата
ScalePointerX:  RLCA
                RLCA
                RLCA
                LD L, A
                LD A, E
                AND @PointerConst.Low3Mask
                OR L
                LD L, A
                ; расчёт итоговой строки указателя по относительному знакоместу и новой позиции
                LD A, D
                SRL A
                SRL A
                SRL A
                ADD A, B
                JP P, @Station.TrackItemGeometry.ClampPointerY                  ; переход, если строка указателя неотрицательна, проверить нижний предел

                XOR A
                ; проверка нижнего предела указателя по 24 знакоместам
ClampPointerY:  CP @ScreenConst.CharRows
                JR C, @Station.TrackItemGeometry.ScalePointerY                  ; переход, если строка указателя меньше 24, сохранить её

                LD A, @ScreenConst.CharRows - 1
                ; восстановление пиксельного Y из строки и исходных младших трёх битов захвата
ScalePointerY:  RLCA
                RLCA
                RLCA
                LD H, A
                LD A, D
                AND @PointerConst.Low3Mask
                OR H
                LD H, A
                ; фиксация новой пиксельной позиции указателя перед общим завершением
                LD (@StationState.PointerXY), HL
                ; JP @Station.FinishGeometry.Entry, продолжение в FinishGeometry.asm

                endmodule
                endmodule
