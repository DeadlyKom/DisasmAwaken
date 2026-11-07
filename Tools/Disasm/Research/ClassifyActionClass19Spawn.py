"""Публикация исходных 200 байтов перенесённого ядра, две части старого бинарного диапазона сохраняются."""
from PublishActionRawFunction import main
import ActionClass19SpawnFacts as facts

if __name__=='__main__':main(facts,'ActionClass19Spawn',0x6417,0x64DF,92160,allow_subrange=True)
