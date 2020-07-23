import os
import json
import time
import random
from flask import Flask, url_for, jsonify, request, make_response
from celery import Celery, states
from flask_cors import CORS, cross_origin

import numpy as np
import pandas as pd


app = Flask(__name__)
CORS(app)

# Additional Celery configurations to flask's config

#app.config['CELERY_RESULT_BACKEND'] = 'amqp://[USERNAME]:[PASSWORD]@localhost/[VHOST_NAME]'
app.config['CELERY_BROKER_URL'] = 'amqp://admin:password@localhost/test'
app.config['CELERY_RESULT_BACKEND'] = 'amqp://admin:password@localhost/test'

# Instantiate Celery object, provided with broker url
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

# Add additional configurations from flask’s config.
celery.conf.update(app.config)


@app.route('/upload', methods=['POST'])
def upload():
    '''
    Here, the server receives the csv file with the POST request, 
    then saves it to a folder, /uploads. 
    Then we apply a Celery task asynchronously with .apply_async(), 
    with read_csv_task as the Celery task. Once that’s sent off, 
    we send the id of the task back to the client.
    '''
    file_obj = request.files.get('file')
    file_name = file_obj.filename

    path = os.path.join('./uploads', file_name)

    file_obj.read(0)

    try:
        file_obj.save(path)
    except IOError:
        print('I/O Error')

    file_obj.close()

    task_list = []

    for i in range(0, 2):
        file_task = read_csv_task.apply_async(args=[path])
        task_list.append(str(file_task.task_id))

    return make_response(jsonify({'task_list': task_list}))


@app.route('/task/<task_id>', methods=['GET'])
def check_task_status(task_id):
    '''
    .AsyncResult() gives you access to the task state (pending, success, or failure), 
    using the task id. Our response object includes the state, 
    and the result if the task is complete.
    '''
    task = read_csv_task.AsyncResult(task_id)
    state = task.state
    response = {}
    response['state'] = state

    if state == states.SUCCESS:
        response['result'] = task.get()
    elif state == states.FAILURE:
        try:
            response['error'] = task.info.get('error')
        except Exception as e:
            response['error'] = 'Unknown error occurred'

    return make_response(jsonify(response))


@celery.task(bind=True)
def read_csv_task(self, path):
    '''
    Each task needs to have a decorator, @celery.task. 
    By setting bind=True, the task function can access self as an argument, 
    where we can update the task status with useful information.
    '''
    self.update_state(state=states.PENDING)
    time.sleep(random.randint(30, 50))
    df = pd.read_csv(path)
    result = compute_properties(df)

    return result


def compute_properties(df):
    '''
    Give summary stats about each column with pandas and numpy.
    '''
    properties = {}

    properties['num_rows'] = len(df)
    properties['num_columns'] = len(df.columns)

    properties['column_data'] = get_column_data(df)

    return properties


def get_column_data(df):
    result = []

    for c in df:
        info = {}
        col = df[c]

        info['name'] = c
        info['num_null'] = str(col.isnull().sum())

        if col.dtypes == 'int64':
            info['mean'] = str(np.mean(col))
            info['median'] = str(np.median(col))
            info['stddev'] = str(np.std(col))
            info['min'] = str(col.min())
            info['max'] = str(col.max())
        else:
            unique_values = col.unique().tolist()
            print(len(unique_values), len(df))
            if len(unique_values) < len(df):
                info['unique_values'] = unique_values
            else:
                info['unique_values'] = True

        result.append(info)

    return result


if __name__ == '__main__':
    app.run(port=8982, debug=True)
