                module StationBoot
                module InitializeStation
                ; Документация [перенос станционного ядра](../../Docs/StationBootstrap.md)
; Документация [StationBoot](../../Docs/FunctionDetails/StationBoot.md)
; -----------------------------------------
; Перенос ядра из #65CE в #6322 и очистка экрана банка 7
; исходная запись 4, файловые смещения #0319..#0342
                ; In:
                ;   загрузчик перенесён в #4000, исходное ядро доступно по #65CE, 7FFD разблокирован
                ;   стек в общей RAM, прерывания не вмешиваются в начальный перенос
                ; Out:
                ;   #1C6A байтов перенесены в #6322, #1B00 байтов экрана банка 7 обнулены
                ;   HL=#DAFF, DE=#DB00, BC=0, A=#18, выбран банк 0, IFF=0
                ;   альтернативные и индексные регистры, I, IM и SP сохранены, переход на StartStation
                ; Corrupt:
                ;   HL, DE, BC, AF, IFF, R, бордюр, #9E78, общая RAM, экран банка 7, тень и порт 7FFD, временный стек
                ; Note:
                ;   12 сценариев сверили размещение, два банковых перехода, регистры и экран
; -----------------------------------------
Entry:          LD HL, #65CE
                LD DE, #6322
                LD BC, #1C6A
                LDIR
                DI
                XOR A
                OUT (#FE), A
                LD (#9E78), A
                LD A, #17
                CALL @Station.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #C001
                LD BC, #1AFF
                LD (HL), L
                LDIR
                LD A, #18
                CALL @Station.SelectMemoryPage.Entry
                JR @StationBoot.StartStation.Entry


                endmodule
                endmodule
