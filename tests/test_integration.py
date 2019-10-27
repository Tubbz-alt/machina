import requests

def test_multiple_session_contexts(threaded_server):
    s1 = requests.Session()
    s2 = requests.Session()
    s3 = requests.Session()

    s1.get('http://localhost:5000/set?key=name&value=jonny')
    s1.get('http://localhost:5000/set?key=pet&value=dog')
    s1.get('http://localhost:5000/get')

    s2.get('http://localhost:5000/set?key=name&value=biscuit')
    s2.get('http://localhost:5000/set?key=color&value=blue')
    s2.get('http://localhost:5000/get')

    assert False

    s3.get('http://localhost:5000/set?key=name&value=susie')
    s3.get('http://localhost:5000/set?key=food&value=corn')
    s3.get('http://localhost:5000/get')

    s1.close()
    s2.close()
    s3.close()

def test_trial_save():
    pass

def test_trial_autosave():
    pass