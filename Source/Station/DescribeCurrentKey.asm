                module Station
                module DescribeCurrentKey
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [точная формула ключа и банковый договор](../../Docs/WorldSignature.md)
; -----------------------------------------
; Чтение текущего пятибайтового ключа и получение его банковой характеристики
; исходная запись 4, файловые смещения #4464..#446D
; In:
;   SignatureInput.Entry содержит физический FSignatureInput, выполняется договор DescribeKeyBanked
; Out:
;   HL - H код 0..3 внутри трёх областей либо 4 вне них, L числовой признак 1..16
;   DE - D код геометрической области 0..3, E младший двухбитовый признак 0..3, BC сохранён
;   AF - A=max((((FirstWord.high XOR FirstWord.low XOR SecondWord.high XOR SecondWord.low) AND 7)-1),0)
;   если XOR AND 7 равен 0, F=#44, если 1, F=#42, иначе F=#02, Z означает A=0
;   рабочий FSignatureKey по #631C содержит состояние после Variant+1 шагов
;   HL', DE', BC', IX, IY, I и IFF сохранены, SP восстановлен
;   AF' - страница (входная CurrentPage AND #F8) OR #10 и F от её OR, AF результата сохранён
;   порт и тень выбирают сначала (старое AND #F8) OR #11, затем (старое AND #F8) OR #10
; Corrupt:
;   HL, DE, AF, AF'
; Note:
;   входные HL, DE и A заменяются тремя физическими полями текущего ключа
;   последовательное исполнение идёт в DescribeKeyBanked.asm без дополнительного CALL
; -----------------------------------------
                ; чтение двух исходных слов текущего пятибайтового ключа
Entry:          LD HL, (@SignatureInput.Entry + FSignatureInput.FirstWord)
                LD DE, (@SignatureInput.Entry + FSignatureInput.SecondWord)
                ; чтение Variant, задающего 1..256 шагов характеристики
                LD A, (@SignatureInput.Entry + FSignatureInput.Variant)
                ; JP @Station.DescribeKeyBanked.Entry, продолжение в DescribeKeyBanked.asm

                endmodule
                endmodule
