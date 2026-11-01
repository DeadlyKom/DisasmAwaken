                module Station
                module PrintEquipmentRows
                ; Документация [параллельные таблицы, счётчик маркера 80, физические кадры и особый EXX-выход](../../Docs/EquipmentListPanels.md)
                ; -----------------------------------------
                ; Имена оснащения и четыре параллельные колонки количества, цены, веса и проверки типа корабля
                ; исходная запись 4, файловые смещения #14F8..#15EA
                ; In:
                ;   HL полный индекс TopRow, имена выбираются младшим байтом, таблицы используют полное слово с оборачиванием 16 бит
                ;   EquipmentListData содержит читаемые количества, цены, пары порог-вес и наборы четырёх типов, достигается маркер 80 либо допустимый выход окна
                ;   CurrentModels.ShipIndex и EquipmentListState.KeySize подготовлены, выбран банк станции 0, код по ShipOperand доступен для записи
                ;   TextWindow и колонки подготовлены, Style=0 и штатный LineEndCode, действуют договоры PrintAfterCR, DrawGlyph и числовых печатателей
                ;   стек вмещает FEquipmentRowsFrame и FEquipmentMarkFrame, исходные шрифт и таблицы доступны, параллельные писатели исключены
                ; Out:
                ;   обычно HL содержит следующий байт количества, DE следующий адрес цены, BC результат последнего числа, после хвоста C=Height
                ;   на обычном пути HL' содержит следующий порог-вес, DE' следующий набор кораблей, BC'=4 после хвоста либо 4×TopRow до него
                ;   при маркере 80 AF=8042, при отказе глифа A=1 либо 2 возвращается AF=0042, при границе следующей строки AF содержит новый Y и флаги CP Height
                ;   A' содержит число попыток modulo 256, включая попытку чтения маркера 80, F' от INC с Carry=0
                ;   при раннем отказе маркера FB обратный EXX не исполнен, HL адрес текущего набора кораблей, DE следующий порог-вес, BC прежний альтернативный контекст
                ;   на этом особом выходе HL', DE', BC' содержат соответственно следующий байт количества, следующую цену и результат числового печатателя
                ;   IX, IY, I, IFF и IM сохранены, SP обычного возврата входному+2, порты и банк не меняются
                ;   CursorY сначала 24, после каждой полной строки увеличивается на 8 только если новый Y меньше Height, CursorX и bitmap содержат фактический вывод
                ;   EquipmentListState.ShipOperand содержит исходный CurrentModels.ShipIndex, остальные таблицы не меняются
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', ShipOperand, курсор, bitmap и изменяемые операнды глифа
                ; Note:
                ;   80 является отдельным ограничителем количества, остальные байты с bit7=1 инвертируются через CPL, ноль и FF печатаются дефисом
                ;   вес печатается только при KeySize не меньше первого байта пары, иначе дефис, цена является полным беззнаковым словом
                ;   маркер FB печатается только для неотрицательного ShipIndex, отсутствующего во всех четырёх байтах набора
                ;   код отказа ширины 3 не завершает таблицу, коды 1 и 2 дают ранний RET, уже выведенное не отменяется
                ;   входной высокий байт TopRow не отбрасывается при адресации таблиц, ограничение индекса является обязанностью вызывающей стороны
                ; -----------------------------------------
                ; сохранение полного TopRow для параллельной адресации таблиц
Entry:          EX DE, HL
                ; создание FEquipmentRowsFrame.PricesBase
                LD HL, @EquipmentListData.Prices
                PUSH HL
                ; чтение типа текущего корабля для SavedShipAF и последующего операнда
                LD A, (@CurrentModels.ShipIndex)
                PUSH AF
                ; сохранение ShipSetsBase для четырёх типов на строку
                LD HL, @EquipmentListData.ShipSets
                PUSH HL
                ; сохранение ThresholdBase для пар минимальная модель и вес
                LD HL, @EquipmentListData.Weights
                PUSH HL
                ; сохранение QuantityBase для одного байта количества на строку
                LD HL, @EquipmentListData.Quantities
                PUSH HL
                ; поиск CR-имён только по младшему байту TopRow, начало текста X=0 и Y=24
                LD HL, @EquipmentListText.Names
                LD BC, @EquipmentListConst.FirstCursor
                LD (@TextWindow.CursorX), BC
                ; создание FEquipmentRowsFrame.TopRow поверх пяти сохранённых слов
                PUSH DE
                LD A, E
                CALL @Station.PrintAfterCR.Entry
                ; возврат Y к первой числовой строке независимо от статуса вывода имён
                LD A, @EquipmentListConst.FirstRowY
                LD (@TextWindow.CursorY), A
                ; расчёт адреса количества по полному слову TopRow
                POP BC
                POP HL
                ADD HL, BC
                EX DE, HL
                ; расчёт удвоенного индекса для двухбайтовых цен и порогов
                SLA C
                RL B
                ; передача удвоенного индекса в альтернативный набор через CPU-стек
                PUSH BC
                EXX
                POP BC
                ; расчёт адресов порога-веса и четырёх типов корабля в альтернативном наборе
                POP HL
                ADD HL, BC
                EX DE, HL
                ; расчёт четырёхкратного индекса набора типов
                SLA C
                RL B
                POP HL
                ADD HL, BC
                EX DE, HL
                EXX
                ; восстановление CurrentModels.ShipIndex и обновление существующего ShipOperand
                POP AF
                LD (@EquipmentListState.ShipOperand), A
                ; расчёт адреса первого слова цены
                POP HL
                ADD HL, BC
                EX DE, HL
                ; создание нулевого альтернативного счётчика попыток с Carry=0
                XOR A
                EX AF, AF'
                ; выбор X количества перед чтением следующего байта
NextRow:        LD A, (@TextStreamState.Column2X)
                LD (@TextWindow.CursorX), A
                ; расчёт счётчика до проверки ограничителя, попытка чтения 80 также учитывается
                EX AF, AF'
                INC A
                EX AF, AF'
                LD A, (HL)
                INC HL
                ; проверка отдельного маркера конца количеств 80
                CP @EquipmentListConst.EndQuantity
                RET Z                                                           ; выход, если прочитан маркер конца количеств 80, попытка уже посчитана

                ; проверка инверсного кодирования количества по bit7
                AND A
                JP P, @Station.PrintEquipmentRows.TestQuantity                  ; переход, если количество неотрицательно, инверсия не требуется

                CPL
                ; проверка нулевого количества после возможного CPL
TestQuantity:   AND A
                JR NZ, @Station.PrintEquipmentRows.PrintQuantity                ; переход, если количество ненулевое, печатать число вместо дефиса

                ; печать дефиса для нуля, в том числе исходного FF
                LD A, @SystemNameConst.Dash
                CALL @Station.DrawGlyph.Entry
                JR @Station.PrintEquipmentRows.AfterQuantity

PrintQuantity:  LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
AfterQuantity:  JR C, @Station.PrintEquipmentRows.PrintPrice                    ; переход, если количество выведено успешно, продолжить ценой

                DEC A
                RET Z                                                           ; выход, если глиф количества вернул код физической границы 1

                DEC A
                RET Z                                                           ; выход, если глиф количества вернул код высоты 2

                ; чтение полного слова цены и продвижение его указателя на два байта
PrintPrice:     LD A, (@TextStreamState.Column3X)
                LD (@TextWindow.CursorX), A
                LD A, (DE)
                LD C, A
                INC DE
                LD A, (DE)
                LD B, A
                INC DE
                ; выбор нулевого бюджета ведущих нулей цены
                XOR A
                CALL @Station.PrintWord.Entry
                JR C, @Station.PrintEquipmentRows.PrintWeight                   ; переход, если цена выведена успешно, продолжить весом

                DEC A
                RET Z                                                           ; выход, если глиф цены вернул код физической границы 1

                DEC A
                RET Z                                                           ; выход, если глиф цены вернул код высоты 2

                ; расчёт X веса с исходным четырёхпиксельным отступом
PrintWeight:    LD A, (@TextStreamState.Column4X)
                ADD A, @EquipmentListConst.ColumnInset
                LD (@TextWindow.CursorX), A
                EXX
                ; проверка текущей модели станции относительно первого байта пары
                LD A, #00
                CP (HL)
                INC HL
                JR NC, @Station.PrintEquipmentRows.WeightValue                  ; переход, если KeySize не меньше порога, прочитать байт веса

                ; пропуск недоступного веса и возврат основного набора для дефиса
                INC HL
                EXX
                LD A, @SystemNameConst.Dash
                CALL @Station.DrawGlyph.Entry
                JR @Station.PrintEquipmentRows.AfterWeight

                ; чтение доступного байта веса и возврат основного набора для числа
WeightValue:    LD A, (HL)
                INC HL
                EXX
                LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
AfterWeight:    JR C, @Station.PrintEquipmentRows.CheckShip                     ; переход, если вес или дефис выведен успешно, продолжить проверкой корабля

                DEC A
                RET Z                                                           ; выход, если глиф веса вернул код физической границы 1

                DEC A
                RET Z                                                           ; выход, если глиф веса вернул код высоты 2

                ; расчёт X колонки Уст с четырёхпиксельным отступом
CheckShip:      LD A, (@TextStreamState.Column5X)
                ADD A, @EquipmentListConst.ColumnInset
                LD (@TextWindow.CursorX), A
                ; переход к набору четырёх типов и создание FEquipmentMarkFrame.TablePointer
                EXX
                EX DE, HL
                PUSH HL
                LD A, #00
                ; проверка отрицательного типа корабля, тогда маркер пропускается
                OR A
                JP M, @Station.PrintEquipmentRows.MaybeMark                     ; переход, если ShipOperand имеет bit7=1, пропустить маркер с Carry=0

                ; поиск типа корабля в четырёх исходных байтах набора
                CP (HL)
                INC HL
                JR Z, @Station.PrintEquipmentRows.MaybeMark                     ; переход, если тип совпал с первым байтом, пропустить маркер

                CP (HL)
                INC HL
                JR Z, @Station.PrintEquipmentRows.MaybeMark                     ; переход, если тип совпал со вторым байтом, пропустить маркер

                CP (HL)
                INC HL
                JR Z, @Station.PrintEquipmentRows.MaybeMark                     ; переход, если тип совпал с третьим байтом, пропустить маркер

                CP (HL)
                INC HL
                JR Z, @Station.PrintEquipmentRows.MaybeMark                     ; переход, если тип совпал с четвёртым байтом, пропустить маркер

                ; установка Carry только при отсутствии типа во всём наборе
                SCF
MaybeMark:      LD A, @EquipmentListConst.ShipMismatch
                CALL C, @Station.DrawGlyph.Entry                                ; вызов, если неотрицательный тип отсутствует в наборе, вывести маркер FB
                ; восстановление начала набора, основной и альтернативный наборы пока обменены
                POP HL
                JR C, @Station.PrintEquipmentRows.NextTables                    ; переход, если маркер выведен успешно, завершить строку с обратным EXX

                DEC A
                RET Z                                                           ; выход, если маркер вернул код границы 1, обратный EXX ещё не исполнен

                DEC A
                RET Z                                                           ; выход, если маркер вернул код высоты 2, обратный EXX ещё не исполнен

                ; расчёт адреса следующего четырёхбайтового набора и восстановление обычного порядка EXX
NextTables:     LD BC, @EquipmentListConst.ShipSetSize
                ADD HL, BC
                EX DE, HL
                EXX
                ; расчёт следующего Y по модулю 256 и проверка границы Height
                LD A, (@TextWindow.Height)
                LD C, A
                LD A, (@TextWindow.CursorY)
                ADD A, @ScreenConst.PixelsPerChar
                CP C
                RET NC                                                          ; выход, если следующий Y не меньше Height, текущий CursorY не менять

                ; обновление CursorY только после успешной проверки следующей строки
                LD (@TextWindow.CursorY), A
                JP @Station.PrintEquipmentRows.NextRow

                endmodule
                endmodule
