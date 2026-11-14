"""Имя уже доказанного входа перенесённой копии LoadStation, не новая память."""


def name_operands(region,address,operation):
    if (region,address)==('Intro',0x6500):
        return operation.replace('#5D3B','@IntroStationRuntime.Entry')
    if (region,address)==('Intro',0x65B7):
        return operation.replace('LD DE, #5CDD','LD DE, @TrDosState.Descriptor').replace('LD BC, #0009','LD BC, @FTrDosFileKey')
    return operation
