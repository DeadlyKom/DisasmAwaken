                module D3D
                module PreparePreviewVertexProducts
                ; Документация [девять физических операндов, порядок столбцов, точные регистры и переход в генератор](../../Docs/PreviewVertexProducts.md)
                ; -----------------------------------------
                ; Девять табличных произведений общей матрицы с последовательным продолжением в генератор группы
                ; исходная запись 6, банк 4, файловые смещения #18BE..#1907
                ; In:
                ;   DE - D третий байтовый параметр группы, входной E не используется
                ;   BC - B первый и C второй байтовые параметры группы, таблица работает с их знаковыми байтовыми значениями
                ;   IX - IXL маска комбинаций, бит i выбирает комбинацию i
                ;   девять Coeff11..Coeff33 в PreviewMatrixComposeState содержат исходную композицию сцены и модели
                ;   параметры перспективы, NextOffset и выходной буфер подготовлены по договору ProjectPreviewVertexGroup
                ;   SP указывает на CPU-возврат, под ним доступны два байта для CALL табличных помощников
                ;   банк 4 доступен для записи, прерывания отключены, NMI и повторный вход исключены
                ; Out:
                ;   в девять байтов PackedFirst..PackedThird и DepthFirst..DepthThird записаны произведения по таблице PreviewVertexProducts.md
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX и IY после общего возврата принадлежат точному договору ProjectPreviewVertexGroup
                ;   CPU-SP после возврата через генератор равен входному SP+2, исходные два байта адреса возврата сохранены
                ;   два байта под входным CPU-SP содержат последний адрес возврата табличного помощника
                ;   I, IFF и IM сохраняются, исходные параметры B/C/D и коэффициенты повторно не сохраняются
                ;   рабочий буфер и операнды комбинаций обновлены генератором и настоящей перспективой
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, два байта под CPU-SP, девять произведений и рабочие записи генератора
                ; Note:
                ;   столбцы общей матрицы читаются в физическом порядке 1,3,2, первые две строки упаковываются в слова
                ;   каждое P является исходной разностью свёрнутых квадратов, не заменяется математическим умножением
                ;   последний LD переходит в ProjectPreviewVertexGroup без настоящего JP, порядок include 0,1 обязателен
                ;   собственного RET здесь нет, обычный CPU-стек восстанавливает и читает генератор группы
                ;   физический обход групп D896 исследуется отдельно от этой композиции
                ; -----------------------------------------
                ; выбор исходной таблицы квадратов для общей матрицы
Entry:          LD H, @PreviewModelMatrixConst.ProductPage
                ; -----------------------------------------
                ; Произведения строки 1
                ; -----------------------------------------
                ; расчёт P(Coeff11,B), первый параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductB.Entry
                ; обновление произведения PackedFirst старший байт в операнде генератора
                LD (@PreviewVertexGroupState.PackedFirst+#01), A
                ; расчёт P(Coeff13,C), второй параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductC.Entry
                ; обновление произведения PackedSecond старший байт в операнде генератора
                LD (@PreviewVertexGroupState.PackedSecond+#01), A
                ; расчёт P(Coeff12,D), третий параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductD.Entry
                ; обновление произведения PackedThird старший байт в операнде генератора
                LD (@PreviewVertexGroupState.PackedThird+#01), A
                ; -----------------------------------------
                ; Произведения строки 2
                ; -----------------------------------------
                ; расчёт P(Coeff21,B), первый параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductB.Entry
                ; обновление произведения PackedFirst младший байт в операнде генератора
                LD (@PreviewVertexGroupState.PackedFirst), A
                ; расчёт P(Coeff23,C), второй параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductC.Entry
                ; обновление произведения PackedSecond младший байт в операнде генератора
                LD (@PreviewVertexGroupState.PackedSecond), A
                ; расчёт P(Coeff22,D), третий параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductD.Entry
                ; обновление произведения PackedThird младший байт в операнде генератора
                LD (@PreviewVertexGroupState.PackedThird), A
                ; -----------------------------------------
                ; Произведения строки 3
                ; -----------------------------------------
                ; расчёт P(Coeff31,B), первый параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductB.Entry
                ; обновление произведения DepthFirst в операнде генератора
                LD (@PreviewVertexGroupState.DepthFirst), A
                ; расчёт P(Coeff33,C), второй параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductC.Entry
                ; обновление произведения DepthSecond в операнде генератора
                LD (@PreviewVertexGroupState.DepthSecond), A
                ; расчёт P(Coeff32,D), третий параметр группы
                LD A, #00
                CALL @D3D.LookupPreviewProductD.Entry
                ; обновление произведения DepthThird в операнде генератора
                LD (@PreviewVertexGroupState.DepthThird), A
                ; JP @D3D.ProjectPreviewVertexGroup.Entry, продолжение в ProjectPreviewVertexGroup.asm

                ; -----------------------------------------
                endmodule
                endmodule
