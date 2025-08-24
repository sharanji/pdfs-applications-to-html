from convert_html_agent.apis import (
    upload_template_sections_api,
    upload_template_api,
    template_listing_api,
    template_delete_api,
    template_save_api,
    template_view_api,
    supplier_listing,
    template_form_save,
    get_saved_templates,
    get_saved_template,
)

api_routes = [
    ('/api/v1/convert/upload', upload_template_api, ['POST']),
    ('/api/v1/templates/list', template_listing_api, ['GET']),
    ('/api/v1/templates/view/<id>', template_view_api, ['GET']),
    ('/api/v1/convert/extract/<id>', upload_template_sections_api, ['GET']),
    ('/api/v1/convert/save/<id>', template_save_api, ['GET']),
    ('/api/v1/convert/delete/<id>', template_delete_api, ['GET']),
    ('/api/testing/supplier_listing', supplier_listing, ['GET']),
    ('/api/template/save', template_form_save, ['POST']),
    ('/api/get/saved/templates', get_saved_templates, ['GET']),
    ('/api/get/saved/template/<saved_form_id>', get_saved_template, ['GET']),
]
