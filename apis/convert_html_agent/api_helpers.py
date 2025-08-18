from sqlalchemy.orm import Session
from convert_html_agent.models import ConvertedTemplates


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
