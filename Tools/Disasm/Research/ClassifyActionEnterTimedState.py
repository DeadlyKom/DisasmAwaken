"""Публикация исходных 26 байтов отдельного рамочного входа 62B5."""
from PublishActionRawFunction import main
import ActionEnterTimedStateFacts as facts

if __name__=='__main__':main(facts,'ActionEnterTimedState',0x62B5,0x62CF,65536,allow_subrange=True)
