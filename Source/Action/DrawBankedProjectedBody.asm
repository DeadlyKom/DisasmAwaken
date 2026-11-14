                module Action
                module DrawBankedProjectedBody
                ; Документация [алгоритм и проверка](../../Docs/ProjectedBodyEntry.md)
                ; -----------------------------------------
                ; Проекция и рисование тела в банке CONTROL с шахматным рисунком
                ; исходная запись 17, банк 5, перенесённое ядро ACTION 6000..7F8E, смещения #0EBB..#0ECB
                ; In:
                ;   Component0..2 содержат исходные данные проекции, 7FFD не заблокирован
                ;   банк 1 содержит CONTROL, CPU-стек в общей RAM допускает двадцать временных байтов, IRQ не вмешиваются
                ; Out:
                ;   HL, DE, BC, F, альтернативные и индексные пары соответствуют ProjectAndDrawBody, A=10
                ;   Pattern=FFAA, CEF9=0, исходные частичные записи при отказе проекции сохраняются
                ;   7FFD получает 11 и 10, верхний банк возвращён к ACTION, SP=входной SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, R, записи проекции, Pattern, CEF9, рабочая запись круга, растр, маски, изменяемые операнды, 7FFD и до двадцати временных байтов CPU-стека
                ; Note:
                ;   4959 сценариев проверяют настоящий порт, исходные страницы, обе формы рисования и отказ проекции
                ;   внутренние значения рамки проекции и R полного прохода остаются вне проверки
                ; -----------------------------------------
                ; Выбор AA с XOR-чередованием FF, соседние строки используют AA и 55.
Entry:          LD DE, @ActionBodyPattern.Checker
                ; Подключение CONTROL для проекции и рисования.
                LD A, @ActionBankPage.Controls
                CALL @Action.SelectMemoryPage.Entry
                CALL @Controls.ProjectAndDrawBody.Entry
                ; Возврат верхнего окна ACTION с сохранением F рисователя.
                LD A, @ActionBankPage.Runtime
                CALL @Action.SelectMemoryPage.Entry
                RET

                endmodule
                endmodule
