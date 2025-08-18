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


def upload_template_api() -> dict:
    uploaded_file_bytes = request.get_json()['file']

    redis_client: RedisClient = RedisClient()
    redis_hash: RedisHash = redis_client('hash')
    request_id = generate_request_id()
    redis_hash.set(request_id, {'encrypted_file': uploaded_file_bytes}, secs=20)

    return {'message': 'uploaded successfully', 'request_id': request_id}


@event_stream_wrapper
def upload_template_sections_api(id):
    """returns total sections"""

    redis_hash: RedisHash = RedisClient()('hash')
    base_64_file = redis_hash.get_field(id, 'encrypted_file')
    total_sections = get_total_sections_ai(base_64_file)

    yield total_sections
    yield upload_and_get_sections(base_64_file, id, total_sections['total_sections'])
    yield {'close': 'end of response'}


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
    return [
        {'LIFNR': '0000003003', 'NAME1': 'SV Vendor new'},
        {'LIFNR': '0000200000', 'NAME1': 'Vendor 1 bp1'},
        {'LIFNR': '1000000002', 'NAME1': 'SVR ime Vendor'},
        {'LIFNR': '0000003005', 'NAME1': 'Sanofi Ridgefield'},
        {'LIFNR': '0000100000', 'NAME1': 'Bio Chemicals'},
        {'LIFNR': '0000003004', 'NAME1': 'Sanofi Bio chemicals'},
        {'LIFNR': '0000003002', 'NAME1': 'Sanofi Bio chemicals'},
        {'LIFNR': '0000100001', 'NAME1': 'bio'},
        {'LIFNR': '0000100002', 'NAME1': 'San Northborough'},
        {'LIFNR': '0000003006', 'NAME1': 'Sanofi Ridgefield'},
        {'LIFNR': '0000003007', 'NAME1': 'SV New Vendor'},
        {'LIFNR': '0000050000', 'NAME1': 'Vendor Abhi'},
        {'LIFNR': '0000002001', 'NAME1': 'IBM'},
        {'LIFNR': '0000007502', 'NAME1': 'horizon gen1'},
        {'LIFNR': '0000007503', 'NAME1': 'horizon vendor pur'},
        {'LIFNR': '0000007002', 'NAME1': 'Pepsi Vendor Acc'},
        {'LIFNR': 'MAY_2025', 'NAME1': 'May_2025'},
        {'LIFNR': '1000000005', 'NAME1': 'TEST3'},
        {'LIFNR': '0000007506', 'NAME1': 'horizon customer bp1'},
        {'LIFNR': '0000002401', 'NAME1': 'Ashok Ltd.'},
        {'LIFNR': '0000002402', 'NAME1': 'Ceat'},
        {'LIFNR': '0000007000', 'NAME1': 'Pepsi'},
        {'LIFNR': '0000007005', 'NAME1': 'Pepsi BP 4'},
        {'LIFNR': '0000007006', 'NAME1': 'Pepsi Cola BP 1'},
        {'LIFNR': '0000007507', 'NAME1': 'test 1'},
        {'LIFNR': '0000007007', 'NAME1': 'Pepsi Cola BP 2'},
        {'LIFNR': '0000010003', 'NAME1': 'lavender bp ven1'},
        {'LIFNR': '0000010004', 'NAME1': 'lavender bp ven2'},
        {'LIFNR': '0000010005', 'NAME1': 'lavender bp ven3'},
        {'LIFNR': '0000010006', 'NAME1': 'lavender bp ven4'},
        {'LIFNR': '0000010007', 'NAME1': 'lavender bp vc1'},
        {'LIFNR': '0000010008', 'NAME1': 'lavender bp vc2'},
        {'LIFNR': '0000010009', 'NAME1': 'lavender bp vp1'},
        {'LIFNR': '0000010010', 'NAME1': 'lavender bp vp2'},
        {'LIFNR': '0000002201', 'NAME1': 'Anchor'},
        {'LIFNR': '0000002700', 'NAME1': 'test'},
        {'LIFNR': '0000007009', 'NAME1': 'Pepsi Cola BP 3'},
        {'LIFNR': '0000003014', 'NAME1': "DECCAN COOPER'S"},
        {'LIFNR': '0000003008', 'NAME1': 'SV Food Supplies'},
        {'LIFNR': '0000003009', 'NAME1': 'SS Supplier'},
        {'LIFNR': '0100700001', 'NAME1': 'MR.Vendor'},
        {'LIFNR': '0000002214', 'NAME1': 'sprite'},
        {'LIFNR': '0000003010', 'NAME1': 'RFQ Ven 1'},
        {'LIFNR': '0000003011', 'NAME1': 'RFQ Ven 2'},
        {'LIFNR': '0000007001', 'NAME1': 'HP'},
        {'LIFNR': '0100700000', 'NAME1': 'SB Vendor'},
    ]


def test_save():
    return {
        'message' : 'ok'
    }