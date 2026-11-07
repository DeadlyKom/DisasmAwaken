                module Action
                module AllocateLargeEffect
                ; Документация [алгоритм и проверка](../../Docs/ActionLargeEffectContinuation.md)
                ; -----------------------------------------
                ; Выделение большого эффекта и создание дочерних записей перед освобождением объекта
                ; исходная запись 17, адреса EA3D..EAE8
                ; In:
                ;   HL содержит заголовок модели, DE и BC числовых аргументов не задают, альтернативный AF учитывается при отказе выделения эффекта
                ;   IX указывает исходную FActionRecord, ChildMask уже задан, H заголовка определяет Mode эффекта
                ;   страницы ACTION и VOXAL доступны, игровые и эффектные списки имеют конечные маркеры, ROM по фактическому paging доступна для двух соседних чтений
                ;   SP в общей RAM, IRQ не вмешиваются во временные рамки, смену страниц и чтения R
                ; Out:
                ;   при наличии слота создан большой эффект с ресурсом C400, State=8 и параметрами 14/14/0280, обход включён и Frames не меньше 16 даже при отказе
                ;   для полного класса ниже 16 запрашиваются от двух до пяти игровых детей по R, фактически создаётся столько, сколько найдено слотов до маркера
                ;   игровой поиск проверяет High=80 и Low=80 напрямую, ReuseByte не проверяется и не очищается
                ;   дети получают Components источника, ModelOffset=B8, StateCode=4, LinkFlags=0, ClassCode=10, Unknown13=10, Unknown14=FF, Unknown15=FF, SavedStateCode=0
                ;   Unknown0D/0E получают соседние байты ROM по R и R+1, Unknown10 равен ChildMask OR (отдельный R AND 1F), прочие поля сохраняются
                ;   HL=EE4D, курсор AY-канала B обновлён, исходная запись получает Component0=8000 и ReuseByte=FF после создания детей
                ;   при классе не меньше 16 DE=0280, BC=0012, A=класс, F от CP класса с 10
                ;   при полном выполнении запроса детей DE=IX+6, BC=FFEB, A=0/F=42, при достижении маркера DE=0040, BC=0012 до первого ребёнка либо FFEB после него, A=80/F=42
                ;   HL', DE', BC' содержат исходные Components, AF' определяется выделением эффекта либо счётчиком и указателем последнего игрового ребёнка, точный результат задан числовой моделью
                ;   IY указывает выбранную запись эффекта либо его маркер, IX, I/IM/IFF сохраняются, SP после внешнего RET равен входному SP+2
                ;   собственные OUT выбирают 13 и 10, дополнительный вход PrepareLargeEffect перед этим выбирает 14 и 10 для OBJECT3D
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY, R, регистр страницы, записи эффектов и объектов, временная рамка стека
                ; Note:
                ;   режим эффекта берётся из старшего байта заголовка, IX восстанавливается перед дочерними записями
                ;   полная цепь EA29 проверена в 51840 сценариях классов 16..255 и 16384 сценариях классов 0..15, включая все R и разные свободные списки
                ;   сверены точные регистры, флаги, R, восемь банков, кратность записей и четыре OUT полного входа, State08 проверен дополнительно до внешнего RET
                ;   ROM синтетическая, значения 0000 и 0100 различаются, соседний адрес после образца FF равен 0100, а не 0000
                ;   полное произведение входов, аппаратные IRQ, точные T, сборка и нативная игра не доказаны
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
