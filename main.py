from flask import Flask, jsonify, render_template, request
from elasticsearch import Elasticsearch, helpers
import getpass, warnings
from configparser import ConfigParser

file = 'config.ini'
config = ConfigParser()
config.read(file)

url = config['ELASTIC URL']['ELASTIC_URL']
username = config['ELASTIC URL']['userid']
password = config['ELASTIC URL']['password']

es = Elasticsearch(url,
                   http_auth=(username, password),
                   scheme="HTTP",
                   port=9200,
                   use_ssl=False, verify_certs=False, ssl_show_warn=False)

app = Flask(__name__)


@app.route('/home')
def hello_world():
    return render_template("index.html")


@app.route('/greeting/<name>', endpoint='say_hello')
def give_greeting(name):
    return 'Hello, {0}!'.format(name)


@app.route('/api/v1/data', methods=['GET'])
def get_data():
    return render_template("indices.html")
    # data = request.args.get("data")
    # es2 = es.search(index='neteng-flowdata-lstash-', body={'query': {'match': {'source.address': '160.238.74.167'}}})

    # return jsonify(es2)
    #


@app.route('/api/v1/data/index', methods=['GET'])
def get_all_indices_data():
    """ Based on user input fetching data """
    id = request.args.get('index_name')
    es2 = es.search(index=id, body={"query": {"match_all": {}}})
    try:
        id = request.args.get('index_name')
        es2 = es.search(index=id, body={"query": {"match_all": {}}})
    # print("value", es2)
        return jsonify(es2)
    except Exception as e:
        return "Error Occurred due to --> {}".format(e)


@app.route('/api/v1/data/index/ephemeral_id', methods=['GET'])
def get_all_id_data():
    """ Based on user input fetching data """
    try:
        id = request.args.get('index_name')
        es2 = es.search(index=id, body={'query': {'match': {'fileset.name': 'syslog'}}})
        es_d = es.search(index=id, body={"query": {"match": {"agent.hostname": "masteres.laas.neustar.biz"}},
                                         "fields": ["@timestamp"], "_source": 'false'})
        es_t = es.search(index=id, body={"query": {"match": {"fileset.name": "syslog"}},
                                         "fields": ["event.ingested", "@timestamp"], "_source": 'false'})
        return jsonify(es_t)
    except Exception as e:
        return "Error Occurred due to --> {}".format(e)


@app.route('/api/v1/fetch_index_data', methods=['GET'])
def index():
    # es2 = es.search(index='neteng-flowdata-lstash-', body={'query': {'match': {'source.address': '160.238.74.167'}}})
    # ind1 = es.search(index='filebeat-*,metricbeat-*', body={"query": {"match_all": {}}})
    ind = es.search(index='filebeat-*,metricbeat-*', body={"query": {"match_all": {}}, "aggs": {
        "dt": {"date_histogram": {"field": "@timestamp", "fixed_interval": "30m"},
               "aggs": {"id": {"terms": {"field": "process.name"}}}}}})
    #  helpers.bulk(es, actions=[ind])
    return jsonify(ind)


if __name__ == ('__main__'):
    app.run(debug=True, port=5001)