"""Публикация 43 исходных байтов F255 без захвата следующей таблицы."""
from PublishActionRawFunction import main
import ActionSpawnCurrentLinkFacts as facts

if __name__=='__main__':main(facts,'ActionSpawnCurrentLink',0xF255,0xF280,131072,allow_subrange=True)
