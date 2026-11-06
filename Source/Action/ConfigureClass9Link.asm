                module Action
                module ConfigureClass9Link
                ; Документация [алгоритм и проверка](../../Docs/ActionClass9Link.md)
                ; -----------------------------------------
                ; Запись кода 0D с сохранением LinkedIndex либо кода 01 со сбросом LinkedIndex в FF
                ; исходная запись 17, адреса 65C6..65DD
                ; In:
                ;   HL, DE, BC, AF аргументов не задают, IX указывает доступную FActionRecord
                ;   Unknown16 читается, Unknown0A и LinkedIndex доступны для записи, CPU-стек содержит внешний возврат
                ;   R является входным состоянием аппаратного счётчика M1, прерывания не вмешиваются
                ; Out:
                ;   при Unknown16=0D Unknown0A=0D, LinkedIndex сохранён, A=0D, F=4A
                ;   иначе Unknown0A=01, LinkedIndex=FF, A=R после шести M1, F соответствует сравнению A с 70
                ;   HL, DE, BC, HL', DE', BC', AF', IX, IY сохраняются
                ;   R получает 7 M1 для кода 0D либо 12 для остальных, его бит 7 сохраняется
                ;   SP=входной SP+2, I, IM, IFF и страница сохраняются, CPU-стек не записывается
                ; Corrupt:
                ;   AF, R, Unknown0A, при Unknown16 не равном 0D также LinkedIndex
                ; Note:
                ;   цель Class09 исходной таблицы, полный игровой смысл Unknown16 и Unknown0A пока не доказан
                ;   CP 70 после LD A,R не управляет ветвью, он меняет только выходные флаги, обе записи выполняются при любом R
                ;   72192 сценария покрыли все пары Unknown16 и R и все 26 исследовательских позиций существующих записей
                ;   проверены регистры включая R, восемь банков RAM и точный порядок байтовых записей
                ;   IRQ, точные T, сборка и нативное исполнение не доказаны
                ; -----------------------------------------
                ; Чтение управляющего байта, специальным является только полное значение 0D.
Entry:          LD A, (IX + @FActionRecord.Unknown16)
                ; Проверка ветви, сохраняющей LinkedIndex без чтения R.
                CP @ActionClass9Const.SpecialCode
                JR NZ, @Action.ConfigureClass9Link.ResetLink                    ; переход, если Unknown16 отличается от 0D, записать код 01 и LinkedIndex=FF

                ; Обновление Unknown0A специальным исходным кодом, LinkedIndex остаётся неизменным.
                LD (IX + @FActionRecord.Unknown0A), A
                RET

                ; Чтение R после шести M1 от входа, его старший бит сохраняет входное значение.
ResetLink:      LD A, R
                ; Формирование выходных флагов, проверка порога не управляет дальнейшими записями.
                CP @ActionClass9Const.FlagThreshold
                ; Обновление Unknown0A и LinkedIndex для всех неспециальных значений Unknown16.
                LD (IX + @FActionRecord.Unknown0A), @ActionClass9Const.DefaultCode
                LD (IX + @FActionRecord.LinkedIndex), @ActionClass9Const.DefaultIndex
                RET

                endmodule
                endmodule
