"""Защищённая публикация исходных 58 байтов State01 без изменения размещения."""
from PublishActionRawFunction import main
import ActionWideVectorStateFacts as facts

if __name__=='__main__':main(facts,'ActionWideVectorState',0xF0BE,0xF0F8,69632,allow_subrange=True)
