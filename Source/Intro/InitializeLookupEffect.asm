                module Intro
                module InitializeLookupEffect
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Создание трёх развёрнутых обработчиков, фазовых таблиц и таблицы указателей эффекта
; исходная запись 3, файловые смещения #099C..#0A69
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   восстанавливается текстура #1300 байт из банка 4 и создаются цепочки #9100, #9900 и #A800
;   таблицы фаз #9400..#97FF строятся с шагами 9, 6, 8 и 5
;   в #9800..#98FF хранится старший полубайт индекса, таблица #F000 содержит 256 строк по 16 байт
;   значение таблицы указателей равно #89 + floor((clamp(E,#70,#7F)-#70)/2)
;   старт E задаётся D, D уменьшается через итерацию благодаря изменяемому операнду LD A,n
;   40 обновлений фаз выполняются до показа первого кадра
; -----------------------------------------
Entry:          LD A, #14
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #AD00
                LD BC, #1300
                LDIR
                CALL @Intro.SelectIntroPage.Entry
                LD DE, #9100
                LD HL, #6D78
                LD BC, #4006
                CALL @Intro.RepeatPattern.Entry
                DEC HL
                LD DE, #6BED
                CALL @Intro.WriteJump.Entry
                LD DE, #9900
                LD HL, #6D7E
                LD BC, #000F
                CALL @Intro.RepeatPattern.Entry
                DEC HL
                DEC HL
                LD (HL), #C9
                LD HL, #A800
                LD DE, #C000
                LD C, #26
Point6CDA:      LD B, #08
Point6CDC:      LD (HL), #E1
                INC HL
                LD (HL), #22
                INC HL
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                INC E
                INC E
                DJNZ @Intro.InitializeLookupEffect.Point6CDC

                LD E, #00
                INC D
                DEC C
                JR NZ, @Intro.InitializeLookupEffect.Point6CDA                  ; переход, если ещё не созданы писатели всех 38 строк


                LD DE, #6BBC
                CALL @Intro.WriteJump.Entry
                LD HL, #9800
                ; создание таблицы старших полубайтов для индексов от 0 до 255
Point6CF9:      LD A, L
                RRCA
                RRCA
                RRCA
                RRCA
                AND #0F
                LD (HL), A
                INC L
                JR NZ, @Intro.InitializeLookupEffect.Point6CF9                  ; переход, если таблица ещё не содержит все 256 старших полубайтов


                LD H, #64
                LD DE, #9400
                LD C, #09
                CALL @Intro.BuildPhaseTable.Entry
                LD C, #06
                CALL @Intro.BuildPhaseTable.Entry
                LD C, #08
                CALL @Intro.BuildPhaseTable.Entry
                LD C, #05
                CALL @Intro.BuildPhaseTable.Entry
                LD HL, #F000
                LD D, #B0
                LD C, #00
                ; создание очередных 16 указателей на страницы результата, начало диапазона задаёт D
Point6D24:      LD E, D
                LD B, #10
Point6D27:      LD A, E
                CP #80
                JR C, @Intro.InitializeLookupEffect.Point6D2E                   ; переход, если значение меньше верхнего ограничения #80


                LD A, #7F
Point6D2E:      CP #70
                JR NC, @Intro.InitializeLookupEffect.Point6D34                  ; переход, если значение не меньше нижнего ограничения #70


                LD A, #70
                ; расчёт страницы результата после ограничения значения диапазоном #70..#7F
Point6D34:      SUB #70
                SRL A
                ADD A, #89
                LD (HL), A
                DEC E
                INC HL
                DJNZ @Intro.InitializeLookupEffect.Point6D27

                ; изменение операнда LD A,n на #00 либо #80 для уменьшения D через итерацию
                LD A, #80
                ADD A, #80
                LD (#6D40), A
                JR NZ, @Intro.InitializeLookupEffect.Point6D49                  ; переход, если новая фаза равна #80 и D уменьшать не нужно


                DEC D
Point6D49:      DEC C
                JR NZ, @Intro.InitializeLookupEffect.Point6D24                  ; переход, если ещё не созданы все 256 строк указателей


                LD IXL, #28
Point6D4F:      CALL @Intro.AdvanceTexturePhases.Entry
                DEC IXL
                JR NZ, @Intro.InitializeLookupEffect.Point6D4F                  ; переход, если ещё не выполнены 40 начальных обновлений фаз


                LD A, #88
                LD (#6993), A
                LD IXL, #89
                LD DE, #8000
                LD BC, #0040
                CALL @Intro.BuildAttributeWriter.Entry
                JP @Intro.PresentAttributes.Entry


                endmodule
                endmodule
