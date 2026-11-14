                module Action
                module PrepareObjectOffsetTransform
                ; Документация [алгоритм и проверка](../../Docs/ActionObjectOffsetTransfer.md)
                ; -----------------------------------------
                ; Проверка маркера записи и подготовка смещений для вычислителя 6D06
                ; исходная запись 17, адреса F0F8..F137
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, IX указывает доступную FActionRecord
                ;   читается Component0.High, для активной записи доступны остальные фазовые поля, класс, состояние и порог
                ;   OffsetScaleLow и OffsetScaleHigh активной записи доступны для записи, ACTION банка 0 и общая RAM доступны
                ;   действует договор ApplyObjectOffsetVector, шесть байтов под SP и внешний возврат не перекрывают его код, таблицы, операнды и результаты
                ;   IRQ и повторный вход исключены
                ; Out:
                ;   при Component0.High=80 внешний RET даёт AF=8042, SP=входной SP+2, R учитывает четыре M1, остальные регистры и RAM сохранены
                ;   на активной ветви нижеследующие результаты вычислителя относятся к V из прежнего OffsetScaleLow и выбранного старшего байта
                ;   HL=(-Q) AND FFFF при бите 7 S=1, иначе HL=Q, DE=Q при бите 7 S=1, иначе DE=abs(V)
                ;   BC - B=W[Offset0], C=0
                ;   AF - A=S, F от 16-разрядного 0-Q при бите 7 S=1, иначе флаги логического XOR с результатом S
                ;   HL', DE', BC' сохраняются
                ;   AF' - A'=U, F'=(U AND 28) OR (40 при U=0) OR (10 при 2*((P SHR 16) AND 0F)+(U AND 1)>0F), остальные биты F' нулевые
                ;   IX восстановлен, IYH сохраняется, IYL=W[(Offset1+64) AND FF]
                ;   Coefficient0..2 содержат результат построителя, Base0..2 содержат три произведения с одним входным V
                ;   SP=входной SP+2, I, IM, IFF и paging сохраняются, порты не используются
                ;   Offset0..2 получают OffsetPhase0, wrap8(OffsetPhase1+80) и OffsetPhase2
                ;   OffsetScaleLow получает wrap8(старое+1), если этот кандидат ниже Phase2OrTarget, иначе сохраняется прежний байт
                ;   OffsetScaleHigh обнулён при ClassCode<10 и StateCode не равном 13, иначе сохранён
                ;   на активной ветви R учитывает 30+Hold+4*Small+2*Small*Different M1 подготовки плюс полный вычислитель, старший бит R сохраняется
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IYL, R, Coefficient0..2, Base0..2 и шесть временных байтов CPU-стека, три фазовых операнда и условно OffsetScaleLow/OffsetScaleHigh
                ;   на ветви маркера из этого списка изменяются только AF и R, обычный RET снимает внешний возврат
                ; Note:
                ;   эффективное слово V перед 6D06 содержит прежний OffsetScaleLow в E и итоговый OffsetScaleHigh в D, это не входное DE всей процедуры
                ;   Hold=1 при сохранении прежнего младшего масштаба, иначе 0, Small=1 при ClassCode<10, Different=1 при StateCode не равном 13, иначе соответствующий признак нулевой
                ;   10, 13 и 80 в условиях полей обозначают шестнадцатеричные коды, числа M1 десятичные
                ;   c2 обозначает третий байтовый коэффициент, m=abs(s8(c2)) AND 7F, P=m*abs(V), Q=floor(P/128), U=P SHR 15, S=c2 XOR HIGH слова V
                ;   нулевой фактор для коэффициента 80 сохранён, знак определяется исходным байтом коэффициента и старшим байтом V
                ;   каждое Base равно -floor((abs(s8(c_i)) AND 7F)*abs(V)/128) при бите 7 c_i XOR HIGH V, иначе положительному частному, всё по модулю 65536
                ;   шесть временных байтов после возврата содержат исходный IX по SP-2, слово V по SP-4 и внутренний возврат 6D0C по SP-6, POP не очищает RAM
                ;   для фактора m>0 умножение даёт 35+floor(log2(m))+2*popcount(m) M1, при m=0 даёт 32 M1
                ;   к каждому умножению добавляются семь M1 при V<0, две при бите 7 коэффициента и четыре при бите 7 его XOR HIGH V
                ;   ранний маркер возвращается до фазовых записей и не вызывает вычислитель, на активном пути внешний RET выполняет его хвост
                ;   196608 прежних сценариев останавливаются перед 6D06 либо на раннем RET, новая композиция проверяет 15616 случаев до полного внешнего возврата
                ;   полное произведение всех аргументов, точные T, IRQ и нативная игра не доказаны
                ; -----------------------------------------
                ; Проверка маркера отсутствующей записи перед обновлением операндов.
Entry:          LD A, (IX + @FActionRecord.Components.Component0.High)
                CP #80
                RET Z                                                           ; выход, если старший байт первой компоненты равен 80

                ; Подготовка трёх байтов смещений вычислителя, второй сдвинут на 128 по модулю байта.
                LD A, (IX + @FActionRecord.OffsetPhase0)
                LD (@ActionObjectOffsetTransferState.Offset0), A
                LD A, (IX + @FActionRecord.OffsetPhase1)
                ADD A, #80
                LD (@ActionObjectOffsetTransferState.Offset1), A
                LD A, (IX + @FActionRecord.OffsetPhase2)
                LD (@ActionObjectOffsetTransferState.Offset2), A
                ; Расчёт кандидата следующего счётчика с сохранением старого значения в E.
                LD A, (IX + @FActionRecord.OffsetScaleLow)
                LD E, A
                INC A
                CP (IX + @FActionRecord.Phase2OrTarget)
                JR C, @Action.PrepareObjectOffsetTransform.StoreCounter         ; переход, если байтовый кандидат меньше Phase2OrTarget, записать его

                DEC A
StoreCounter:   LD (IX + @FActionRecord.OffsetScaleLow), A
                ; Проверка класса и состояния перед сбросом фазового счётчика.
                LD A, (IX + @FActionRecord.ClassCode)
                CP #10
                JR NC, @Action.PrepareObjectOffsetTransform.LoadPhase           ; переход, если класс не меньше 16, сохранить фазовый счётчик

                LD A, (IX + @FActionRecord.StateCode)
                CP #13
                JR Z, @Action.PrepareObjectOffsetTransform.LoadPhase            ; переход, если состояние равно 13, сохранить фазовый счётчик

                LD (IX + @FActionRecord.OffsetScaleHigh), #00
                ; Подготовка D для вычислителя и хвостовая передача с прежним CPU-стеком.
LoadPhase:      LD D, (IX + @FActionRecord.OffsetScaleHigh)
                JP @Action.ApplyObjectOffsetVector.Entry

                endmodule
                endmodule
