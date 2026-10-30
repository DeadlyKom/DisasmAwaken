                module Intro
                module DrawScrolledTexture
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Обновление двух смещений modulo 64, выбор строки текстуры и вывод двух половин кадра
; исходная запись 3, файловые смещения #03A3..#03E1
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   D и E задают приращения двух младших смещений, значения ограничиваются маской #3F
;   две шестибайтовые записи выбирают младший и старший байты начального адреса текстуры
;   HL второго набора регистров проходит две группы по 16 страниц, затем общий вывод PresentInterlacedFrame
; -----------------------------------------
Entry:          CALL @Intro.WaitInterrupt.Entry
                PUSH BC
                CALL @Intro.SelectMemoryPage.Entry
                ; расчёт горизонтального смещения по модулю 64, исходный байт меняется в операнде
                LD A, (#66EC)
                ADD A, D
                AND #3F
                LD (#66EC), A
                ; расчёт второго смещения по модулю 64 с сохранением старшего бита страницы #80
                LD A, (#66ED)
                ADD A, E
                AND #3F
                OR #80
                LD (#66ED), A
                ; обновление первого состояния, старший байт задаёт младшую часть адреса выборок
                CALL @Intro.AdvanceParameters.Entry
                SUB #60
                ADD A, A
                LD (#66D4), A
                ; получение второго указателя состояния из сохранённого BC
                POP HL
                CALL @Intro.AdvanceParameters.Entry
                ADD A, #50
                LD (#66D5), A
                LD D, #80
                EXX
                LD HL, #CD40
                CALL @Intro.SampleTextureRows.Entry
                CALL @Intro.WaitInterrupt.Entry
                CALL @Intro.SampleTextureRows.Entry
                JP @Intro.PresentInterlacedFrame.Entry


                endmodule
                endmodule
