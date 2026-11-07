"""Публикация исходных 74 байтов общего фазового помощника 6201."""
from PublishActionRawFunction import main
import ActionRandomPhaseStepFacts as facts

if __name__=='__main__':main(facts,'ActionRandomPhaseStep',0x6201,0x624B,131072,allow_subrange=True)
