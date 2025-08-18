from convert_html_agent.apis import (
    upload_template_sections_api,
    upload_template_api,
    template_listing_api,
    template_delete_api,
    template_save_api,
    template_view_api,
    test_listing,
)

api_routes = [
    ('/api/v1/convert/upload', upload_template_api, ['POST']),
    ('/api/v1/templates/list', template_listing_api, ['GET']),
    ('/api/v1/templates/view/<id>', template_view_api, ['GET']),
    ('/api/v1/convert/extract/<id>', upload_template_sections_api, ['GET']),
    ('/api/v1/convert/save/<id>', template_save_api, ['GET']),
    ('/api/v1/convert/delete/<id>', template_delete_api, ['GET']),
    ('/api/testing/listing', test_listing, ['GET'])
]
