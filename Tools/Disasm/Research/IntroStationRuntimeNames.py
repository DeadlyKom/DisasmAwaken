"""Имя уже доказанного входа перенесённой копии LoadStation, не новая память."""


def name_operands(region,address,operation):
    if (region,address)==('Intro',0x6500):
        return operation.replace('#5D3B','@IntroStationRuntime.Entry')
    return operation
