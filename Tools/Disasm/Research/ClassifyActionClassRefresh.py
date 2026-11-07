"""Публикация шести исходных байтов общего хвоста, 52 байта State0E сохраняются отдельно."""
from PublishActionRawFunction import main
import ActionClassRefreshFacts as facts

if __name__=='__main__':main(facts,'ActionClassRefresh',0xF003,0xF009,39936,allow_subrange=True)
