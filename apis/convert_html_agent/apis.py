import json
from sqlalchemy import JSON
from convert_html_agent.models import TemplateSections, ConvertedTemplates
from common.reponse_utils import event_stream_wrapper
from common.utils import generate_request_id
from db import session_wrap
from convert_html_agent.utils import generate_html, warp_html_skeleton, get_total_sections_ai
from app_redis.client import RedisClient
from app_redis.redis_commands.hash_commands import RedisHash
from flask import Flask, request
from convert_html_agent.api_helpers import create_template_with_sections
import time
import logging
from cachetools import TTLCache
import requests

cache = TTLCache(maxsize=100, ttl=60)

def upload_template_api() -> dict:
    uploaded_file_bytes = request.get_json()['file']
    request_id = generate_request_id()
    cache[request_id] = uploaded_file_bytes

    return {'message': 'uploaded successfully', 'request_id': request_id}


@event_stream_wrapper
def upload_template_sections_api(id):
    """returns total sections"""

    # base_64_file = cache.get(id)
    # total_sections = get_total_sections_ai(base_64_file)
    logging.info('start')
    for i in range(2):
        yield {'name' : 'sharanji'}
        # time.sleep(5)

    # yield total_sections
    # yield upload_and_get_sections(base_64_file, id, total_sections['total_sections'])
    # yield {'close': 'end of response'}


@session_wrap
def upload_and_get_sections(uploaded_file, request_id, total_section, session=None) -> dict:
    sections = []
    model_sections = []
    for section in range(1, total_section+1):
        current_section = generate_html(
            base64_data=uploaded_file, section=section
        )

        sections.append(warp_html_skeleton(current_section))
        model_sections.append(
            TemplateSections(
                section_name='POC',
                section_content=current_section,
                order=section,
            )
        )

    create_template_with_sections(request_id, model_sections, '1', session)

    return {'sections': sections}


def template_save_api(id):
    pass


def template_delete_api(id):
    pass


def template_listing_api():
    return template_listing_helper()


@session_wrap
def template_listing_helper(session=None, batch_size: int = 100):
    batch = session.query(ConvertedTemplates).offset(0).limit(batch_size).all()
    return [record.to_dict(include_relationships=False) for record in batch]


def template_view_api(id):
    return template_view_helper(id)


@session_wrap
def template_view_helper(request_id, session):
    template = (
        session.query(ConvertedTemplates)
        .filter(ConvertedTemplates.request_id == request_id)
        .first()
    )

    template_dict = template.to_dict(include_relationships=True)
    for section in template_dict['sections']:
        section['section_content'] = warp_html_skeleton(section['section_content'])
    return template_dict



def test_listing():
    url = "http://s4hana2021.estservers.com:8701/zsupplier/supplier_detail?sap-client=500"
    headers = {
        'Authorization': 'Basic VlM0U01VU0VSMTI6V2VsY29tZUAxMjM=',
        'Cookie': 'SAP_SESSIONID_MAH_500=BrDAxhB7y0tDhj3Dt9itou5_rlF9tBHwovwAFV0AFAM%3d; sap-usercontext=sap-client=500'
    }
    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)


def test_save():
    return {
        'message' : 'ok'
    }