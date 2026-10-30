                module MapArcWork
; Документация [поля и исходные значения состояния дуги](../../../Docs/ArcWorkspace.md)
                assert $ == #DFAB
                ; AbsY=0, AbsX=0, QuadrantCode=0F с неизвестными старшими битами, Radius=28
                ; OffsetY, OffsetX, RowY, CenterX, StartY исходно нулевые
                ; RasterStack=0, SqrtTarget=0, LeftMask=0, RasterDown=0
                ; UpperRow=4000, LowerRow=5800, это исходные адреса до настройки окна
                ; MaxY, ReferenceX, HalfY и обе копии HalfX исходно нулевые
State:          FMapArcWorkspace { #00, #00, #0F, #28, #00, #00, #00, #00, #00, #0000, #0000, #00, #00, #4000, #5800, #00, #00, #00, #00, #00 }
                assert $ == #DFC3
                endmodule
