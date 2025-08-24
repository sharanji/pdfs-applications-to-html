import json
from flask import request
import requests

def submit_forms_to_sap(formData):

    url = "https://s4hana2021.estservers.com:8006/zmaterial/material_create?sap-client=500"
    headers = {
        'Authorization': 'Basic VlM0U01VU0VSMTI6V2VsY29tZUAxMjM0',
        'x-csrf-token': 'fetch',
    }
    session = requests.Session()
    response = session.get(url, headers=headers, verify=False)

    csrf_token = response.headers.get('x-csrf-token')
    cookies = response.cookies
 
    payload = json.dumps(formData)

    post_headers = {
        'Authorization': 'Basic VlM0U01VU0VSMTI6V2VsY29tZUAxMjM0',
        'Content-Type': 'application/json',
        'x-csrf-token': csrf_token,
    }

    post_response = session.post(url, headers=post_headers, cookies=cookies, data=payload, verify=False)

    return {
        'message': 'ok',
        'status': post_response.status_code,
        'data': json.loads(post_response.text),
    }