                module AssignmentScratch
; Документация [присваивание](../../../Docs/AssignmentPipeline.md)
                assert $ == #CA7B
Entry:          FAssignmentExpression { #0000, #0000, #0000 }                   ; Writer, Operator, Right, исходные рабочие слова
                assert $ == #CA81
                ; При RHS в скобках временный левый операнд занимает Entry.Right.
NestedTail:     FAssignmentNestedTail { #0000, #0000 }                          ; Operator, Right вложенного выражения, исходные рабочие слова
                assert $ == #CA85
                endmodule
