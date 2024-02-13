import random, time, json, requests
from typing import Any, Dict

# [NOTE] Entry Point
def main(request: Any) -> Dict[str, Any]:
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_body = request.get_json()
    print(request_body)
    if request_body['run'] is True:
        time.sleep(10)
        if request_body.get('external', None) is True:
            data = json.loads(requests.get(request_body['url']).text)
            return {'code': 200, 'data': data}
        print(response := {'code': 200, 'data': list(range(int(random.random()*100)))})
        return response
    raise Exception('[RAISED] this is an exception')
