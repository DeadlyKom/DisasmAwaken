                module PreviewSharedSeed
                ; Документация [подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)
                assert $ == #C200
                ; -----------------------------------------
                ; исходная физическая запись Value
Value:          FPreviewSharedSeed {
                    #00,                                                        ; InitialAngle0, начальный первый угол Eye_a, копируется в AngleFirst до обхода записей
                    #00,                                                        ; PlanarAngleBase, вычитаемый угловой отсчёт плоской модели, единица 1/256 оборота
                    #00                                                         ; InitialAngle2, начальный третий угол Eye_g, копируется в AngleThird до обхода записей
                }
                assert $ == #C203
                endmodule
