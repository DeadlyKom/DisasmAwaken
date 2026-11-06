"""Публикация тринадцати исходных байтов IY-варианта, соседние байты остаются явно неизвестными."""
from PublishActionRawFunction import main
import ActionIYRecordReuseFacts as facts

if __name__=='__main__':main(facts,'ActionIYRecordReuse',0xF03D,0xF04A,7450,allow_subrange=True)
