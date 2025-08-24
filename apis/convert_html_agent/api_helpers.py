from sqlalchemy.orm import Session
from .models import ConvertedTemplates, TemplateFormData


def create_template_with_sections(
    request_id, sections, user_id, session: Session
):
    template = ConvertedTemplates(
        request_id=request_id,
        created_by=user_id,
        status='pending',
        sections=sections,
    )

    session.add(template)
    session.commit()
    session.refresh(template)

    return template

def template_saver_helper(formData, section_id, session: Session=None):

    form_name = formData.get('auto_form_name', '').split(':')[-1]
    template_form_data = TemplateFormData(
        template_id=formData.get('template_id'),
        form_data=formData,
        name=form_name,
        section_id=section_id,
    )

    session.add(template_form_data)
    session.commit()
    
    return template_form_data.to_dict()