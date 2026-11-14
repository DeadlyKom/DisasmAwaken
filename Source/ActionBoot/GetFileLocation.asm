                module ActionBoot
                module GetFileLocation
                ; Проверка [координаты с настоящим TR-DOS](../../Docs/ActionBootFileKeys.md#координаты-каталога-и-физический-номер-сектора)
                ; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
                ; -----------------------------------------
                ; Поиск девятибайтового имени, чтение заголовка каталога и возврат числа секторов и начального положения
                ; исходная запись 17, файловые смещения #00EE..#0108
                ; In:
                ;   HL - адрес девятибайтового имени TR-DOS, файл присутствует на диске, каталожный номер сектора лежит в 0..15, системное состояние TR-DOS подготовлено, TrDosState.SearchKeyLength=FTrDosFileKey
                ; Out:
                ;   HL - H логическая дорожка из #5CEC, L физический номер сектора 1..16 из #5CEB+1, AF - A число секторов из #5CEA
                ; Corrupt:
                ;   HL, DE, BC, AF, R, буферы каталога и остальные побочные эффекты определяются TR-DOS
                ; Note:
                ;   имя копируется в #5CDD, вызываются поиск #0A и чтение записи #08
                ;   INC L переводит каталожный номер 0..15 в физический 1..16, сектор 16 остаётся на прежней логической дорожке
                ;   после вызовов нет ветвления по ошибке TR-DOS
                ; -----------------------------------------
Entry:          LD DE, @TrDosState.Descriptor
                LD BC, @FTrDosFileKey
                LDIR
                LD C, #0A
                CALL @TrDos.Dispatch
                LD A, C
                LD C, #08
                CALL @TrDos.Dispatch
                LD HL, (#5CEB)
                INC L
                LD A, (#5CEA)
                RET


                endmodule
                endmodule
