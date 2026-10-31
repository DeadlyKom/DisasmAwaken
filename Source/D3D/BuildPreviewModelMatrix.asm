                module D3D
                module BuildPreviewModelMatrix
                ; Документация [матрица ориентации модели](../../Docs/PreviewModelMatrix.md)
                ; -----------------------------------------
                ; Матрица ориентации модели по трём байтовым углам либо упрощённая матрица по второму углу
                ; исходная запись 6, банк 4, файловые смещения #2F5E..#3055
                ; In:
                ;   Flags и AngleFirst..AngleThird находятся в PreviewQueueState, угловая единица равна 1/256 оборота
                ;   бит 0 Flags выбирает упрощённую ветвь, в штатной очереди он означает нулевые первый и третий углы
                ;   банк 4 доступен для записи, страницы C3 и C4 содержат исходные таблицы квадратов и синусоиды
                ;   SP указывает на обычный адрес возврата, под ним доступны два байта для вложенных CALL, повторный вход исключён
                ; Out:
                ;   девять операндов Coeff11..Coeff33 получают матрицу по формулам PreviewModelMatrix.md
                ;   HL в общей ветви содержит C3 и последний индекс табличного произведения, DE содержит sin третьего угла и последний квадрат
                ;   BC в общей ветви содержит sin первого угла и cos первого угла, AF содержит Coeff32 и флаги его коррекции
                ;   IX в общей ветви содержит P(cos второго, cos первого) и sin второго, IY содержит cos третьего и cos второго
                ;   HL в упрощённой ветви содержит C4 и второй угол, B содержит второй угол, C, DE, IX и IY сохранены
                ;   AF в упрощённой ветви равен 7F44, её девять коэффициентов записаны без вложенных вызовов
                ;   HL', DE', BC', AF', I, IFF и IM сохранены, SP после обычного RET равен входному SP+2
                ;   общая ветвь дополнительно перезаписывает два байта под входным SP адресами возврата помощников
                ; Corrupt:
                ;   HL, DE, BC, AF, IX, IY, девять операндов матрицы, два байта под входным SP в общей ветви
                ; Note:
                ;   бит 0 достаточен для выбора короткой ветви, сами первый и третий углы здесь не проверяются
                ;   P(a,b) является точной исходной табличной аппроксимацией, она не заменяется обычным произведением
                ;   при знаковом переполнении ADD или SUB выполняется NEG обёрнутого байта, при повторном переполнении NEG выполняется DEC
                ;   это отражение обёрнутого результата, не насыщение математической суммы до диапазона
                ;   при нулевых углах матрица меняет местами вторую и третью оси, именование строк и столбцов следует потребителю D54C
                ;   полный алгоритм композиции сцены, проекции и растеризации не входит в локальный договор
                ; -----------------------------------------
                ; поиск текущего признака упрощённой ориентации в распакованном узле
Entry:          LD HL, @PreviewQueueState.Flags
                ; проверка бита 0, выбирающего матрицу только по второму углу
                BIT @PreviewModelMatrixConst.OneAxisBit, (HL)
                JR Z, @D3D.BuildPreviewModelMatrix.General                      ; переход, если бит 0 сброшен, вычислить общую матрицу

                ; -----------------------------------------
                ; Упрощённая ориентация по второму углу
                ; -----------------------------------------
                ; чтение единственного используемого угла короткой ветви
                LD A, (@PreviewQueueState.AngleSecond)
                LD B, A
                ; расчёт индекса косинуса добавлением четверти оборота с байтовым оборачиванием
                ADD A, @PreviewModelMatrixConst.QuarterTurn
                ; поиск косинуса во второй четверти исходной синусоиды
                LD H, @PreviewModelMatrixConst.SinePage
                LD L, A
                LD A, (HL)
                ; обновление Coeff11 и Coeff32 одним косинусом второго угла
                LD (@PreviewModelMatrixState.Coeff11), A
                LD (@PreviewModelMatrixState.Coeff32), A
                ; поиск синуса второго угла по сохранённому исходному индексу
                LD L, B
                LD A, (HL)
                ; обновление Coeff12 синусом второго угла
                LD (@PreviewModelMatrixState.Coeff12), A
                ; расчёт отрицательного синуса для Coeff31
                NEG
                LD (@PreviewModelMatrixState.Coeff31), A
                ; обнуление четырёх отсутствующих смешанных коэффициентов
                XOR A
                LD (@PreviewModelMatrixState.Coeff13), A
                LD (@PreviewModelMatrixState.Coeff21), A
                LD (@PreviewModelMatrixState.Coeff22), A
                LD (@PreviewModelMatrixState.Coeff33), A
                ; установка единичного коэффициента Coeff23 в исходном масштабе 127
                LD A, @PreviewModelMatrixConst.Unit
                LD (@PreviewModelMatrixState.Coeff23), A
                RET

                ; -----------------------------------------
                ; Общая ориентация по трём углам
                ; -----------------------------------------
                ; поиск синуса первого угла общей матрицы
General:        LD A, (@PreviewQueueState.AngleFirst)
                LD H, @PreviewModelMatrixConst.SinePage
                LD L, A
                LD B, (HL)
                ; расчёт индекса косинуса первого угла по модулю 256
                ADD A, @PreviewModelMatrixConst.QuarterTurn
                LD L, A
                LD C, (HL)
                ; поиск синуса второго угла, сохраняемого в IXL
                LD A, (@PreviewQueueState.AngleSecond)
                LD L, A
                LD A, (HL)
                LD IXL, A
                LD A, L
                ; расчёт индекса косинуса второго угла, сохраняемого в IYL
                ADD A, @PreviewModelMatrixConst.QuarterTurn
                LD L, A
                LD A, (HL)
                LD IYL, A
                ; поиск синуса третьего угла, сохраняемого в D
                LD A, (@PreviewQueueState.AngleThird)
                LD L, A
                LD A, (HL)
                LD D, A
                ; расчёт Coeff13 как отрицательного синуса третьего угла
                NEG
                LD (@PreviewModelMatrixState.Coeff13), A
                LD A, L
                ; расчёт индекса косинуса третьего угла, сохраняемого в IYH
                ADD A, @PreviewModelMatrixConst.QuarterTurn
                LD L, A
                LD A, (HL)
                LD IYH, A
                ; выбор исходной страницы квадратов для всех последующих табличных произведений
                LD H, @PreviewModelMatrixConst.ProductPage
                ; расчёт Coeff11=P(c3,c2), P обозначает точную табличную аппроксимацию
                LD E, IYL
                CALL @D3D.LookupPreviewProductE.Entry
                LD (@PreviewModelMatrixState.Coeff11), A
                ; расчёт Coeff12=P(s2,c3)
                LD A, IXL
                LD E, IYH
                CALL @D3D.LookupPreviewProductE.Entry
                LD (@PreviewModelMatrixState.Coeff12), A
                ; расчёт добавочного члена P(s2,s1) для Coeff21
                LD A, IXL
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; расчёт основного члена P(P(c2,c1),s3) для Coeff21
                LD A, IYL
                CALL @D3D.LookupPreviewProductC.Entry
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой суммы членов Coeff21 и признака знакового переполнения
                ADD A, IXH
                JP PO, @D3D.BuildPreviewModelMatrix.Store21                     ; переход, если знакового переполнения нет, сохранить Coeff21

                ; отражение обёрнутого результата сменой знака, исходная коррекция не является насыщением
                NEG
                JP PO, @D3D.BuildPreviewModelMatrix.Store21                     ; переход, если NEG не переполнился, сохранить отражённый Coeff21

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
                ; обновление окончательного операнда Coeff21
Store21:        LD (@PreviewModelMatrixState.Coeff21), A
                ; расчёт Coeff23=P(c3,c1)
                LD A, IYH
                CALL @D3D.LookupPreviewProductC.Entry
                LD (@PreviewModelMatrixState.Coeff23), A
                ; расчёт вычитаемого P(c2,s1) для Coeff22
                LD A, IYL
                CALL @D3D.LookupPreviewProductB.Entry
                LD IXH, A
                ; расчёт основного члена P(P(s2,c1),s3) для Coeff22
                LD A, IXL
                CALL @D3D.LookupPreviewProductC.Entry
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой разности членов Coeff22 и признака знакового переполнения
                SUB IXH
                JP PO, @D3D.BuildPreviewModelMatrix.Store22                     ; переход, если знакового переполнения нет, сохранить Coeff22

                ; отражение обёрнутого результата сменой знака, исходная коррекция не является насыщением
                NEG
                JP PO, @D3D.BuildPreviewModelMatrix.Store22                     ; переход, если NEG не переполнился, сохранить отражённый Coeff22

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
                ; обновление окончательного операнда Coeff22
Store22:        LD (@PreviewModelMatrixState.Coeff22), A
                ; расчёт вычитаемого P(s2,c1) для Coeff31
                LD A, IXL
                CALL @D3D.LookupPreviewProductC.Entry
                LD IXH, A
                ; расчёт основного члена P(P(c2,s1),s3) для Coeff31
                LD A, IYL
                CALL @D3D.LookupPreviewProductB.Entry
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой разности членов Coeff31 и признака знакового переполнения
                SUB IXH
                JP PO, @D3D.BuildPreviewModelMatrix.Store31                     ; переход, если знакового переполнения нет, сохранить Coeff31

                ; отражение обёрнутого результата сменой знака, исходная коррекция не является насыщением
                NEG
                JP PO, @D3D.BuildPreviewModelMatrix.Store31                     ; переход, если NEG не переполнился, сохранить отражённый Coeff31

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
                ; обновление окончательного операнда Coeff31
Store31:        LD (@PreviewModelMatrixState.Coeff31), A
                ; расчёт Coeff33=P(c3,s1)
                LD A, IYH
                CALL @D3D.LookupPreviewProductB.Entry
                LD (@PreviewModelMatrixState.Coeff33), A
                ; расчёт добавочного члена P(c2,c1) для Coeff32
                LD A, IYL
                CALL @D3D.LookupPreviewProductC.Entry
                LD IXH, A
                ; расчёт основного члена P(P(s2,s1),s3) для Coeff32
                LD A, IXL
                CALL @D3D.LookupPreviewProductB.Entry
                CALL @D3D.LookupPreviewProductD.Entry
                ; расчёт обёрнутой суммы членов Coeff32 и признака знакового переполнения
                ADD A, IXH
                JP PO, @D3D.BuildPreviewModelMatrix.Store32                     ; переход, если знакового переполнения нет, сохранить Coeff32

                ; отражение обёрнутого результата сменой знака, исходная коррекция не является насыщением
                NEG
                JP PO, @D3D.BuildPreviewModelMatrix.Store32                     ; переход, если NEG не переполнился, сохранить отражённый Coeff32

                ; замена особого результата 80 после переполнившегося NEG на 7F
                DEC A
                ; обновление окончательного операнда Coeff32
Store32:        LD (@PreviewModelMatrixState.Coeff32), A
                RET

                ; -----------------------------------------
                endmodule
                endmodule
