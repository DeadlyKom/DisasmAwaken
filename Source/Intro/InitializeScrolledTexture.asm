                module Intro
                module InitializeScrolledTexture
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Создание 64 развёрнутых выборок по шаблону #6722, подготовка текстуры и экранной раскладки
; исходная запись 3, файловые смещения #03FB..#0421
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   образец #6722 имеет вид POP HL, ADD HL,BC, RES 6,H, LD A,(HL), LD (DE),A, INC E
;   после 64 копий дописывается JP NextSampledRow, бит 6 H ограничивает обращение областью текстуры
;   это инициализация, выход ведёт через PresentAttributes к писателю атрибутов
; -----------------------------------------
Entry:          LD DE, #7E00
                LD HL, #6722
                LD BC, #4007
                CALL @Intro.RepeatPattern.Entry
                LD DE, #66F3
                CALL @Intro.WriteJump.Entry
                LD IXL, #80
                CALL @Intro.ExpandTextureRows.Entry
                LD IXL, #80
                LD DE, #80C0
                LD BC, #0100
                CALL @Intro.BuildAttributeWriter.Entry
                JP @Intro.PresentAttributes.Entry


                endmodule
                endmodule
