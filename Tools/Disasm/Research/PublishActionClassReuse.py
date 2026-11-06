"""Выделение исходного хвоста E65F..E684 из бинарного ресурса с сохранением его соседей."""
from PublishActionRawFunction import main
import ActionClassReuseFacts as facts

if __name__=='__main__':main(facts,'ActionClassReuse',0xE65F,0xE685,2129,allow_subrange=True)
