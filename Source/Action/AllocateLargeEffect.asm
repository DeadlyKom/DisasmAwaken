                module Action
                module AllocateLargeEffect
                ; Документация [алгоритм и проверка](../../Docs/ActionLargeEffectContinuation.md)
                ; -----------------------------------------
                ; Выделение большого эффекта и создание дочерних записей перед освобождением объекта
                ; исходная запись 17, адреса EA3D..EAE8
                ; In:
                ;   HL содержит заголовок модели, IX указывает исходную запись, ChildMask уже задан
                ;   страницы ACTION и VOXAL доступны, списки объектов и эффектов имеют конечные маркеры
                ;   SP в общей RAM, IRQ не вмешиваются в выполнение и чтения R
                ; Out:
                ;   создан большой эффект при наличии места, общий счётчик кадров не меньше 16
                ;   для класса ниже 16 создаются до пяти дочерних записей, при заполненном списке раньше срабатывает маркер
                ;   канал B получает курсор #EE4D, исходная запись помечается для отложенного повторного использования
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, регистр страницы, записи эффектов и объектов, временная рамка стека
                ; Note:
                ;   режим эффекта берётся из старшего байта заголовка, IX восстанавливается перед дочерними записями
                ;   два байта каждой дочерней записи зависят от ROM и R, проверка использует синтетическую таблицу ROM
                ; -----------------------------------------
                ; Передача режима из заголовка и трёх слов исходной записи в VOXAL.
Entry:          LD A, H
                EX AF, AF'
                LD L, (IX + @FActionRecord.Components.Component0.Low)
                LD H, (IX + @FActionRecord.Components.Component0.High)
                LD E, (IX + @FActionRecord.Components.Component1.Low)
                LD D, (IX + @FActionRecord.Components.Component1.High)
                LD C, (IX + @FActionRecord.Components.Component2.Low)
                LD B, (IX + @FActionRecord.Components.Component2.High)
                LD A, #08
                EXX
                LD HL, @Voxel.CreateLargeEffect.Entry
                PUSH IX
                CALL @Action.DispatchBank3Callback.Entry
                POP IX
                ; Включение кадрового обхода эффектов независимо от результата выделения.
                LD A, #01
                LD (#6D39), A
                ; Проверка оставшейся длительности обхода.
                LD A, (#6D3D)
                CP #10
                JR NC, @Action.AllocateLargeEffect.CheckClass                   ; переход, если общий счётчик уже не меньше #10

                LD A, #10
                LD (#6D3D), A
                ; Проверка класса перед созданием дочерних записей.
CheckClass:     LD A, (IX + @FActionRecord.ClassCode)
                CP #10
                JP NC, @Action.AllocateLargeEffect.ReleaseObject                ; переход, если класс не меньше #10, дочерние записи не создаются

                ; Подготовка сканирования списка и счётчика от двух до пяти по R.
                LD HL, #A0C1
                LD A, R
                AND #03
                ADD A, #02
SaveCount:      EX AF, AF'
                LD DE, #0040
                ; Поиск записи со старшим байтом первой компоненты #80.
FindSlot:       ADD HL, DE
                LD A, (HL)
                CP #80
                JP NZ, @Action.AllocateLargeEffect.FindSlot                     ; переход, если проверенная запись занята

                ; Проверка младшего байта найденного маркера.
                DEC HL
                LD A, (HL)
                CP #80
                JP Z, @Action.AllocateLargeEffect.ReleaseObject                 ; переход, если достигнут конечный маркер #8080

                ; Копирование трёх слов исходного объекта в найденную запись.
                LD D, IXH
                LD E, IXL
                EX DE, HL
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                ; Инициализация постоянных полей дочерней записи.
                LD A, #B8
                LD (DE), A
                INC E
                INC E
                INC E
                INC E
                LD A, #04
                LD (DE), A
                INC E
                INC E
                XOR A
                LD (DE), A
                INC E
                ; Выбор двух соседних байтов ROM по текущему R.
                LD A, R
                LD C, A
                LD B, #00
                LD A, (BC)
                LD (DE), A
                INC E
                INC BC
                LD A, (BC)
                LD (DE), A
                INC E
                INC E
                ; Формирование кода из пяти младших битов R и ChildMask.
                LD A, R
                AND #1F
                OR #A0
                LD (DE), A
                INC E
                INC E
                LD A, #10
                LD (DE), A
                INC E
                LD (DE), A
                INC E
                LD A, #FF
                LD (DE), A
                INC E
                LD (DE), A
                XOR A
                INC E
                LD (DE), A
                ; Возврат указателя к старшему байту первой компоненты созданной записи.
                LD BC, #FFEB
                EX DE, HL
                ADD HL, BC
                EX AF, AF'
                DEC A
                JP NZ, @Action.AllocateLargeEffect.SaveCount                    ; переход, если запрошены ещё дочерние записи

                ; Выбор звукового потока канала B и передача в освобождение объекта.
ReleaseObject:  LD HL, #EE4D
                LD (#ECF6), HL
                JP @Action.MarkRecordForReuse.Entry

                endmodule
                endmodule
