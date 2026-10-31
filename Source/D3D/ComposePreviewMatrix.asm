                module D3D
                module ComposePreviewMatrix
                ; Документация [композиция матриц сцены и модели](../../Docs/PreviewMatrixCompose.md)
                ; -----------------------------------------
                ; Композиция матрицы сцены и модели с отражаемой арифметикой, одноосной ветвью и точными четвертьоборотами
                ; исходная запись 6, банк 4, файловые смещения #154C..#1818
                ; In:
                ;   девять байтовых операндов Scene11..Scene33 содержат матрицу сцены, не массив новых данных
                ;   PreviewModelMatrixState.Coeff11..Coeff33 содержат ориентацию модели, подготовленную BuildPreviewModelMatrix
                ;   Flags и AngleSecond находятся в PreviewQueueState, бит 0 выбирает одноосный путь
                ;   банк 4 доступен для записи, страница C3 содержит исходную таблицу квадратов, повторный вход исключён
                ;   SP указывает на адрес возврата, под ним доступны два байта для вложенных CALL
                ; Out:
                ;   девять операндов Coeff11..Coeff33 получают композицию, порядок вычислений приведён в PreviewMatrixCompose.md
                ;   HL в арифметической ветви содержит C3 и последний индекс произведения, DE содержит последний коэффициент модели и прочитанный квадрат
                ;   BC в арифметической ветви содержит первые два коэффициента последнего вычислявшегося столбца модели
                ;   AF полной ветви содержит Coeff33 и флаги последней коррекции, AF одноосной ветви содержит Scene32 и флаги BIT с Carry последней коррекции
                ;   IXH в арифметической ветви содержит последнюю частичную сумму, IXL сохранён, IY равен CEFA
                ;   в четвертьоборотах HL равен C300 плюс исходный L, DE, BC и IX сохранены, IY равен CEFA
                ;   AF четвертьоборота определяется последней копией и последним NEG, точные случаи перечислены в документации
                ;   HL', DE', BC', AF', I, IFF и IM сохраняются, SP после RET равен входному SP+2
                ;   арифметические ветви пишут два байта под входным SP, точные четвертьобороты вложенных CALL не выполняют
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, IY, девять выходных операндов и два байта под SP в арифметической ветви
                ; Note:
                ;   полная ветвь сначала складывает первые два табличных произведения, отражает переполнение, затем добавляет третье и снова отражает
                ;   при бите 0 средний член первых двух столбцов пропускается, третий столбец копируется из второго столбца сцены
                ;   если при бите 0 второй угол кратен 64, столбцы переставляются и меняют знак без приближённого умножения
                ;   отрицание байта 80 в точной перестановке оставляет 80, отдельной нормализации в этой ветви нет
                ;   эта процедура не выполняет преобразование вершин, проекцию, отсечение или рисование граней
                ; -----------------------------------------
                ; выбор исходной страницы квадратов для композиции коэффициентов
Entry:          LD H, @PreviewModelMatrixConst.ProductPage
                ; поиск признаков текущего распакованного объекта
                LD IY, @PreviewQueueState.Flags
                ; проверка возможности одноосной ориентации
                BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)
                JR Z, @D3D.ComposePreviewMatrix.General                         ; переход, если бит 0 сброшен, вычислить полную композицию

                ; чтение второго угла для поиска точного четвертьоборота
                LD A, (@PreviewQueueState.AngleSecond)
                ; проверка младших шести угловых разрядов, нуль означает угол 0, 64, 128 или 192
                AND @PreviewMatrixComposeConst.QuarterMask
                JP Z, @D3D.ComposePreviewMatrix.QuarterTurns                    ; переход, если угол кратен 64, переставить столбцы без табличных произведений

                ; -----------------------------------------
                ; Первый столбец композиции
                ; -----------------------------------------
                ; загрузка первого столбца матрицы модели для трёх строк композиции
General:        LD B, #00
                LD C, #00
                LD D, #00
                ; расчёт 1-го табличного произведения для выходного Coeff11, Scene11 на коэффициент модели 11
                LD A, #00
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; проверка, нужно ли учитывать средний член для Coeff11
                BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)
                JR NZ, @D3D.ComposePreviewMatrix.Last11                         ; переход, если бит 0 установлен, пропустить средний член Coeff11

                ; расчёт 2-го табличного произведения для выходного Coeff11, Scene12 на коэффициент модели 21
                LD A, #00
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff11
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair11                         ; переход, если знакового переполнения нет, принять результат Coeff11

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair11                         ; переход, если NEG не переполнился, принять отражённый Coeff11

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair11:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff11, Scene13 на коэффициент модели 31
Last11:         LD A, #00
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff11
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store11                        ; переход, если знакового переполнения нет, принять результат Coeff11

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store11                        ; переход, если NEG не переполнился, принять отражённый Coeff11

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store11:        LD (@PreviewMatrixComposeState.Coeff11), A
                ; расчёт 1-го табличного произведения для выходного Coeff21, Scene21 на коэффициент модели 11
                LD A, #00
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; проверка, нужно ли учитывать средний член для Coeff21
                BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)
                JR NZ, @D3D.ComposePreviewMatrix.Last21                         ; переход, если бит 0 установлен, пропустить средний член Coeff21

                ; расчёт 2-го табличного произведения для выходного Coeff21, Scene22 на коэффициент модели 21
                LD A, #00
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff21
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair21                         ; переход, если знакового переполнения нет, принять результат Coeff21

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair21                         ; переход, если NEG не переполнился, принять отражённый Coeff21

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair21:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff21, Scene23 на коэффициент модели 31
Last21:         LD A, #00
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff21
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store21                        ; переход, если знакового переполнения нет, принять результат Coeff21

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store21                        ; переход, если NEG не переполнился, принять отражённый Coeff21

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store21:        LD (@PreviewMatrixComposeState.Coeff21), A
                ; расчёт 1-го табличного произведения для выходного Coeff31, Scene31 на коэффициент модели 11
                LD A, #00
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; проверка, нужно ли учитывать средний член для Coeff31
                BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)
                JR NZ, @D3D.ComposePreviewMatrix.Last31                         ; переход, если бит 0 установлен, пропустить средний член Coeff31

                ; расчёт 2-го табличного произведения для выходного Coeff31, Scene32 на коэффициент модели 21
                LD A, #00
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff31
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair31                         ; переход, если знакового переполнения нет, принять результат Coeff31

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair31                         ; переход, если NEG не переполнился, принять отражённый Coeff31

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair31:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff31, Scene33 на коэффициент модели 31
Last31:         LD A, #00
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff31
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store31                        ; переход, если знакового переполнения нет, принять результат Coeff31

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store31                        ; переход, если NEG не переполнился, принять отражённый Coeff31

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store31:        LD (@PreviewMatrixComposeState.Coeff31), A
                ; -----------------------------------------
                ; Второй столбец композиции
                ; -----------------------------------------
                ; загрузка второго столбца матрицы модели для следующих трёх строк
                LD B, #00
                LD C, #00
                LD D, #00
                ; расчёт 1-го табличного произведения для выходного Coeff12, Scene11 на коэффициент модели 12
                LD A, (@PreviewMatrixComposeState.Scene11)
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; проверка, нужно ли учитывать средний член для Coeff12
                BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)
                JR NZ, @D3D.ComposePreviewMatrix.Last12                         ; переход, если бит 0 установлен, пропустить средний член Coeff12

                ; расчёт 2-го табличного произведения для выходного Coeff12, Scene12 на коэффициент модели 22
                LD A, (@PreviewMatrixComposeState.Scene12)
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff12
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair12                         ; переход, если знакового переполнения нет, принять результат Coeff12

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair12                         ; переход, если NEG не переполнился, принять отражённый Coeff12

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair12:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff12, Scene13 на коэффициент модели 32
Last12:         LD A, (@PreviewMatrixComposeState.Scene13)
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff12
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store12                        ; переход, если знакового переполнения нет, принять результат Coeff12

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store12                        ; переход, если NEG не переполнился, принять отражённый Coeff12

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store12:        LD (@PreviewMatrixComposeState.Coeff12), A
                ; расчёт 1-го табличного произведения для выходного Coeff22, Scene21 на коэффициент модели 12
                LD A, (@PreviewMatrixComposeState.Scene21)
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; проверка, нужно ли учитывать средний член для Coeff22
                BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)
                JR NZ, @D3D.ComposePreviewMatrix.Last22                         ; переход, если бит 0 установлен, пропустить средний член Coeff22

                ; расчёт 2-го табличного произведения для выходного Coeff22, Scene22 на коэффициент модели 22
                LD A, (@PreviewMatrixComposeState.Scene22)
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff22
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair22                         ; переход, если знакового переполнения нет, принять результат Coeff22

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair22                         ; переход, если NEG не переполнился, принять отражённый Coeff22

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair22:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff22, Scene23 на коэффициент модели 32
Last22:         LD A, (@PreviewMatrixComposeState.Scene23)
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff22
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store22                        ; переход, если знакового переполнения нет, принять результат Coeff22

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store22                        ; переход, если NEG не переполнился, принять отражённый Coeff22

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store22:        LD (@PreviewMatrixComposeState.Coeff22), A
                ; расчёт 1-го табличного произведения для выходного Coeff32, Scene31 на коэффициент модели 12
                LD A, (@PreviewMatrixComposeState.Scene31)
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; проверка, нужно ли учитывать средний член для Coeff32
                BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)
                JR NZ, @D3D.ComposePreviewMatrix.Last32                         ; переход, если бит 0 установлен, пропустить средний член Coeff32

                ; расчёт 2-го табличного произведения для выходного Coeff32, Scene32 на коэффициент модели 22
                LD A, (@PreviewMatrixComposeState.Scene32)
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff32
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair32                         ; переход, если знакового переполнения нет, принять результат Coeff32

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair32                         ; переход, если NEG не переполнился, принять отражённый Coeff32

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair32:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff32, Scene33 на коэффициент модели 32
Last32:         LD A, (@PreviewMatrixComposeState.Scene33)
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff32
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store32                        ; переход, если знакового переполнения нет, принять результат Coeff32

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store32                        ; переход, если NEG не переполнился, принять отражённый Coeff32

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store32:        LD (@PreviewMatrixComposeState.Coeff32), A
                ; -----------------------------------------
                ; Третий столбец или точная копия
                ; -----------------------------------------
                ; проверка, можно ли заменить третий столбец точной копией второго столбца сцены
                BIT @PreviewModelMatrixConst.OneAxisBit, (IY+@FPreviewDrawState.Flags)
                JP NZ, @D3D.ComposePreviewMatrix.CopySecond                     ; переход, если бит 0 установлен, скопировать второй столбец сцены

                ; загрузка третьего столбца матрицы модели для полной композиции
                LD B, #00
                LD C, #00
                LD D, #00
                ; расчёт 1-го табличного произведения для выходного Coeff13, Scene11 на коэффициент модели 13
                LD A, (@PreviewMatrixComposeState.Scene11)
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; расчёт 2-го табличного произведения для выходного Coeff13, Scene12 на коэффициент модели 23
                LD A, (@PreviewMatrixComposeState.Scene12)
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff13
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair13                         ; переход, если знакового переполнения нет, принять результат Coeff13

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair13                         ; переход, если NEG не переполнился, принять отражённый Coeff13

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair13:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff13, Scene13 на коэффициент модели 33
                LD A, (@PreviewMatrixComposeState.Scene13)
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff13
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store13                        ; переход, если знакового переполнения нет, принять результат Coeff13

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store13                        ; переход, если NEG не переполнился, принять отражённый Coeff13

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store13:        LD (@PreviewMatrixComposeState.Coeff13), A
                ; расчёт 1-го табличного произведения для выходного Coeff23, Scene21 на коэффициент модели 13
                LD A, (@PreviewMatrixComposeState.Scene21)
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; расчёт 2-го табличного произведения для выходного Coeff23, Scene22 на коэффициент модели 23
                LD A, (@PreviewMatrixComposeState.Scene22)
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff23
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair23                         ; переход, если знакового переполнения нет, принять результат Coeff23

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair23                         ; переход, если NEG не переполнился, принять отражённый Coeff23

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair23:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff23, Scene23 на коэффициент модели 33
                LD A, (@PreviewMatrixComposeState.Scene23)
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff23
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store23                        ; переход, если знакового переполнения нет, принять результат Coeff23

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store23                        ; переход, если NEG не переполнился, принять отражённый Coeff23

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store23:        LD (@PreviewMatrixComposeState.Coeff23), A
                ; расчёт 1-го табличного произведения для выходного Coeff33, Scene31 на коэффициент модели 13
                LD A, (@PreviewMatrixComposeState.Scene31)
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; расчёт 2-го табличного произведения для выходного Coeff33, Scene32 на коэффициент модели 23
                LD A, (@PreviewMatrixComposeState.Scene32)
                CALL @D3D.LookupPreviewProductC.Entry
                ; расчёт обёрнутой суммы первых двух произведений для Coeff33
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Pair33                         ; переход, если знакового переполнения нет, принять результат Coeff33

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Pair33                         ; переход, если NEG не переполнился, принять отражённый Coeff33

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Pair33:         LD IXH, A
                ; расчёт 3-го табличного произведения для выходного Coeff33, Scene33 на коэффициент модели 33
                LD A, (@PreviewMatrixComposeState.Scene33)
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой полной суммы с третьим произведением для Coeff33
                ADD A, IXH
                JP PO, @D3D.ComposePreviewMatrix.Store33                        ; переход, если знакового переполнения нет, принять результат Coeff33

                ; отражение обёрнутого результата сменой знака при переполнении
                NEG
                JP PO, @D3D.ComposePreviewMatrix.Store33                        ; переход, если NEG не переполнился, принять отражённый Coeff33

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
Store33:        LD (@PreviewMatrixComposeState.Coeff33), A
                RET

                ; -----------------------------------------
                ; Копирование второго столбца сцены
                ; -----------------------------------------
                ; копирование второго столбца сцены в третий выходной столбец без приближения P(a,127)
CopySecond:     LD A, (@PreviewMatrixComposeState.Scene12)
                LD (@PreviewMatrixComposeState.Coeff13), A
                LD A, (@PreviewMatrixComposeState.Scene22)
                LD (@PreviewMatrixComposeState.Coeff23), A
                LD A, (@PreviewMatrixComposeState.Scene32)
                LD (@PreviewMatrixComposeState.Coeff33), A
                RET

                ; -----------------------------------------
                ; Четыре точных четвертьоборота
                ; -----------------------------------------
                ; копирование неизменного для всех четвертьоборотов третьего столбца результата
QuarterTurns:   LD A, (@PreviewMatrixComposeState.Scene12)
                LD (@PreviewMatrixComposeState.Coeff13), A
                LD A, (@PreviewMatrixComposeState.Scene22)
                LD (@PreviewMatrixComposeState.Coeff23), A
                LD A, (@PreviewMatrixComposeState.Scene32)
                LD (@PreviewMatrixComposeState.Coeff33), A
                ; чтение полного угла, младшие шесть битов уже проверены на нуль
                LD A, (@PreviewQueueState.AngleSecond)
                ; проверка нулевого угла, одновременно подготовка знака и чётности для остальных трёх случаев
                AND A
                JR Z, @D3D.ComposePreviewMatrix.Quarter0                        ; переход, если угол равен 0, скопировать первый и третий столбцы сцены

                JP P, @D3D.ComposePreviewMatrix.Quarter1                        ; переход, если угол равен 64, взять отрицательный третий и первый столбцы

                JP PO, @D3D.ComposePreviewMatrix.Quarter2                       ; переход, если угол равен 128, изменить знак первого и третьего столбцов

                ; угол 192, первый выходной столбец получает третий столбец сцены, второй получает отрицательный первый
                LD A, (@PreviewMatrixComposeState.Scene13)
                LD (@PreviewMatrixComposeState.Coeff11), A
                LD A, (@PreviewMatrixComposeState.Scene23)
                LD (@PreviewMatrixComposeState.Coeff21), A
                LD A, (@PreviewMatrixComposeState.Scene33)
                LD (@PreviewMatrixComposeState.Coeff31), A
                LD A, (@PreviewMatrixComposeState.Scene11)
                NEG
                LD (@PreviewMatrixComposeState.Coeff12), A
                LD A, (@PreviewMatrixComposeState.Scene21)
                NEG
                LD (@PreviewMatrixComposeState.Coeff22), A
                LD A, (@PreviewMatrixComposeState.Scene31)
                NEG
                LD (@PreviewMatrixComposeState.Coeff32), A
                RET

                ; угол 0, первый выходной столбец получает первый столбец сцены, второй получает третий
Quarter0:       LD A, (@PreviewMatrixComposeState.Scene11)
                LD (@PreviewMatrixComposeState.Coeff11), A
                LD A, (@PreviewMatrixComposeState.Scene21)
                LD (@PreviewMatrixComposeState.Coeff21), A
                LD A, (@PreviewMatrixComposeState.Scene31)
                LD (@PreviewMatrixComposeState.Coeff31), A
                LD A, (@PreviewMatrixComposeState.Scene13)
                LD (@PreviewMatrixComposeState.Coeff12), A
                LD A, (@PreviewMatrixComposeState.Scene23)
                LD (@PreviewMatrixComposeState.Coeff22), A
                LD A, (@PreviewMatrixComposeState.Scene33)
                LD (@PreviewMatrixComposeState.Coeff32), A
                RET

                ; угол 64, первый выходной столбец получает отрицательный третий столбец сцены, второй получает первый
Quarter1:       LD A, (@PreviewMatrixComposeState.Scene13)
                NEG
                LD (@PreviewMatrixComposeState.Coeff11), A
                LD A, (@PreviewMatrixComposeState.Scene23)
                NEG
                LD (@PreviewMatrixComposeState.Coeff21), A
                LD A, (@PreviewMatrixComposeState.Scene33)
                NEG
                LD (@PreviewMatrixComposeState.Coeff31), A
                LD A, (@PreviewMatrixComposeState.Scene11)
                LD (@PreviewMatrixComposeState.Coeff12), A
                LD A, (@PreviewMatrixComposeState.Scene21)
                LD (@PreviewMatrixComposeState.Coeff22), A
                LD A, (@PreviewMatrixComposeState.Scene31)
                LD (@PreviewMatrixComposeState.Coeff32), A
                RET

                ; угол 128, оба используемых столбца сцены копируются с отрицанием
Quarter2:       LD A, (@PreviewMatrixComposeState.Scene11)
                NEG
                LD (@PreviewMatrixComposeState.Coeff11), A
                LD A, (@PreviewMatrixComposeState.Scene21)
                NEG
                LD (@PreviewMatrixComposeState.Coeff21), A
                LD A, (@PreviewMatrixComposeState.Scene31)
                NEG
                LD (@PreviewMatrixComposeState.Coeff31), A
                LD A, (@PreviewMatrixComposeState.Scene13)
                NEG
                LD (@PreviewMatrixComposeState.Coeff12), A
                LD A, (@PreviewMatrixComposeState.Scene23)
                NEG
                LD (@PreviewMatrixComposeState.Coeff22), A
                LD A, (@PreviewMatrixComposeState.Scene33)
                NEG
                LD (@PreviewMatrixComposeState.Coeff32), A
                RET

                ; -----------------------------------------
                endmodule
                endmodule
