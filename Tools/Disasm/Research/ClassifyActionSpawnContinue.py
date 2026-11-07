"""Публикация шести исходных байтов F24F, доказанных полной композицией State02."""
from PublishActionRawFunction import main
import ActionSpawnContinueFacts as facts

if __name__=='__main__':main(facts,'ActionSpawnContinue',0xF24F,0xF255,44656,allow_subrange=True,proof_tag='ActionLinkedTargetState')
