                module Action
                module ApplyObjectOffsetVector
                ; Документация [алгоритм и проверка](../../Docs/ActionObjectOffsetVector.md)
                ; -----------------------------------------
                ; Расчёт трёх базовых слов записи по коэффициентам смещения
                ; исходная запись 17, адреса 6D06..6D37
                ; In:
                ;   HL числового аргумента не задаёт, DE содержит знаковое слово масштаба V=s16(DE), BC и AF числовых аргументов не задают
                ;   действует договор BuildObjectOffsetCoefficients с тремя байтовыми индексами Offset0..2 и исходными таблицами
                ;   три байта Coefficient0..2 и слова Base0..2 доступны для записи, ACTION банка 0 выбран
                ;   внешний возврат и шесть доступных байтов под SP не перекрывают код, таблицы, операнды и выходные слова, IRQ и повторный вход исключены
                ; Out:
                ;   HL=(-Q) AND FFFF при бите 7 S=1, иначе HL=Q, DE=Q при бите 7 S=1, иначе DE=abs(V)
                ;   BC - B=W[Offset0], C=0
                ;   AF - A=S, F от 16-разрядного 0-Q при бите 7 S=1, иначе флаги логического XOR с результатом S
                ;   HL', DE', BC' сохраняются
                ;   AF' - A'=U, F'=(U AND 28) OR (40 при U=0) OR (10 при 2*((P SHR 16) AND 0F)+(U AND 1)>0F), остальные биты F' нулевые
                ;   IX восстановлен, IYH сохраняется, IYL=W[(Offset1+64) AND FF]
                ;   Coefficient0..2 содержат результат построителя, Base0..2 содержат три произведения с одним входным V
                ;   SP=входной SP+2, I, IM, IFF и paging сохраняются, порты не используются
                ;   R учитывает 27 M1 обёртки, все M1 построителя и трёх умножений, старший бит R сохраняется
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IYL, R, Coefficient0..2, Base0..2 и шесть временных байтов CPU-стека
                ; Note:
                ;   c2 обозначает третий байтовый коэффициент, m=abs(s8(c2)) AND 7F, P=m*abs(V), Q=floor(P/128), U=P SHR 15, S=c2 XOR HIGH входного DE
                ;   нулевой фактор для коэффициента 80 сохранён, знак определяется исходным байтом коэффициента и старшим байтом V
                ;   каждое Base равно -floor((abs(s8(c_i)) AND 7F)*abs(V)/128) при бите 7 c_i XOR HIGH V, иначе положительному частному, всё по модулю 65536
                ;   шесть временных байтов после возврата содержат исходный IX по SP-2, входное DE по SP-4 и внутренний возврат 6D0C по SP-6, POP не очищает RAM
                ;   для фактора m>0 умножение даёт 35+floor(log2(m))+2*popcount(m) M1, при m=0 даёт 32 M1
                ;   к каждому умножению добавляются семь M1 при V<0, две при бите 7 коэффициента и четыре при бите 7 его XOR HIGH V
                ;   73728 сценариев обёртки, включая все входные DE и дополнительные фазовые профили, сверяют регистры, R и записи, реальные дети исполняются
                ;   полное произведение таблиц и аргументов, IRQ, точные T и нативный запуск не доказаны
                ; -----------------------------------------
                ; Сохранение IX записи и слова масштаба перед расчётом трёх коэффициентов.
Entry:          PUSH IX
                PUSH DE
                CALL @Action.BuildObjectOffsetCoefficients.Entry
                POP DE
                ; Расчёт первого базового слова настоящим MultiplySignedScaled с продолжением через IX.
                LD A, #00
                PUSH DE
                LD IX, @Action.ApplyObjectOffsetVector.Store0
                JP @Action.MultiplySignedScaled.Entry

                ; Запись первого базового слова и повторное использование исходного масштаба.
Store0:         POP DE
                LD (@ActionRecordUpdateState.Base0), HL
                LD A, #00
                PUSH DE
                LD IX, @Action.ApplyObjectOffsetVector.Store1
                JP @Action.MultiplySignedScaled.Entry

                ; Запись второго базового слова и расчёт третьего без дополнительного сохранения DE.
Store1:         POP DE
                LD (@ActionRecordUpdateState.Base1), HL
                LD A, #00
                LD IX, @Action.ApplyObjectOffsetVector.Store2
                JP @Action.MultiplySignedScaled.Entry

                ; Запись третьего базового слова и восстановление указателя записи.
Store2:         LD (@ActionRecordUpdateState.Base2), HL
                POP IX
                RET

                endmodule
                endmodule
