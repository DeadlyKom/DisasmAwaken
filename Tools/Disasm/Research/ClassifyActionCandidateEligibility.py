"""Публикация двух отдельных договоров и сохранение соседних неизвестных байтов."""
from PublishActionRawFunction import main
import ActionCandidateClassFacts as classes
import ActionCandidateGateFacts as gate

if __name__=='__main__':
    main(classes,'ActionCandidateClass',0xEA00,0xEA15,69632,allow_subrange=True,proof_tag='ActionCandidateEligibility')
    main(gate,'ActionCandidateGate',0xEA15,0xEA29,69632,allow_subrange=True,proof_tag='ActionCandidateEligibility')
