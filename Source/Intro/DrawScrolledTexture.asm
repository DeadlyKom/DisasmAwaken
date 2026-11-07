                module Intro
                module DrawScrolledTexture
                ; Документация [прокручиваемая текстура](../../Docs/IntroScrolledFrame.md)
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Обновление двух смещений modulo 64, выбор строки текстуры и вывод двух половин кадра
; исходная запись 3, файловые смещения #03A3..#03E1
                ; In:
                ;   HL, BC указывают две записи FTexturePhase, DE задаёт два байтовых приращения смещения
                ;   AF задаёт полную конфигурацию 7FFD в A, порт разблокирован
                ;   подготовлены цепочки выборок и писатель, указатели и назначения доступны
                ;   IM 1, ПЗУ, клавиатура и рабочий стек удовлетворяют договорам WaitInterrupt и PresentInterlacedFrame
                ; Out:
                ;   обновлены обе записи фаз, два байта смещения и указатель строки выборок
                ;   32 строки выборок переданы PresentInterlacedFrame, экран обновлён по текущей фазе
                ;   итоговые регистры определяются договором PresentInterlacedFrame, SP после RET равен входному SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', R, IFF, фазовые записи, операнды, буфер, экран, стек, 7FFD
                ; Note:
                ;   72 прохода сверили выборки и конечный вывод с настоящим ROM, оба знака фаз и обе раскладки
                ;   произвольные указатели, времена IRQ и нативный запуск не входят в проверенный профиль
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
