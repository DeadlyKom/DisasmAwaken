"""Выделение восьми исходных байтов с явным жёстким порядком включения."""
from PublishActionRawFunction import main
import ActionClass8SpawnGateFacts as facts

if __name__=='__main__':main(facts,'ActionClass8SpawnGate',0xE863,0xE86B,16384,allow_subrange=True)
