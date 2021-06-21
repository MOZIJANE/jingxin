#coding=utf-8 
# ycat			2017-04-11      create
import sys,os
if "common" not in sys.path:
    sys.path.append("common")
if ".." not in sys.path:
    sys.path.append("..")
     
import datetime 
import elasticsearch 
from elasticsearch import helpers
es = None

def batch_op(table,actions):
	global es
	now = datetime.datetime.utcnow()
	index = table + "-" + now.strftime("%Y.%m.%d")
	return batch_op2(index,table,actions)

def batch_op2(table,type,actions):
	global es
	aa = []
	for a in actions:
		action = {
			"_index": table,
			"_type": type,
			"_source": {
			}
        } 
		action["_source"].update(a)
		if "@timestamp" not in action["_source"]:
			action["_source"]["@timestamp"] = datetime.datetime.utcnow()

		aa.append(action)
	try:
		#print(aa)
		helpers.bulk(es, aa)
	except elasticsearch.exceptions.ConnectionTimeout as e:
		print("\n\n*"*10+" ERROR " + "*"*10)
		print(str(e))		
		
		
#使用过滤的方法 
#GET virtual_machine-2017.05.11/_search?filter_path=hits.hits._source.project_name
def search(**param):
	rrr = es.search(**param)
	rr = rrr["hits"]["hits"]
	return rr

def scan(**param):
	#print(help(helpers.scan))
	rrr = helpers.scan(es,**param)
	rr = []
	for r in rrr:
		rr.append(r)
	return rr	
	
def delete(**param):
	es.delete_by_query(**param)	

def open():
	import config
	global es
	es = elasticsearch.Elasticsearch(config.get("elk","host"))
	return es
	
#['bulk', 'cat', 'clear_scroll', 'cluster', 'count', 'count_percolate', 'create', 'delete', 'delete_by_query', 'delete_script', 'delete_template', 'exists', 'exists_source', 'explain', 'field_stats', 'get', 'get_script', 'get_source', 'get_template', 'index', 'indices', 'info', 'ingest', 'mget', 'mpercolate', 'msearch', 'msearch_template', 'mtermvectors', 'nodes', 'percolate', 'ping', 'put_script', 'put_template', 'reindex', 'reindex_rethrottle', 'render_search_template', 'scroll', 'search', 'search_shards', 'search_template', 'snapshot', 'suggest', 'tasks', 'termvectors', 'transport', 'update', 'update_by_query']
	
if __name__ == '__main__':
	batch_op([])

	
