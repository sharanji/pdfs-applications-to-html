import base64
import json
import logging
import os
from google import genai
from google.genai import types


def prepare_gemini_client(base64_data):
    model = 'gemini-2.5-pro'
    client = genai.Client(
        api_key=os.environ.get('GEMINI_API_KEY'),
    )
    pdf_bytes = base64.b64decode(base64_data)

    
    contents = [
        types.Content(
            role='user',
            parts=[
                types.Part.from_bytes(
                    data=pdf_bytes, mime_type='application/pdf'
                ),
            ],
        ),
    ]

    return client, contents, model


def generate_html(base64_data, section):
    client, contents, model = prepare_gemini_client(base64_data)
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
        ),
        system_instruction=[
            types.Part.from_text(text=f"""You will receive a PDF and extract only section ${section}, converting it into a clean, editable HTML form.
              Preserve field order and labels exactly.Dont chnage the terms strictly.
              Maintain the original layout and input types (e.g., checkbox, text field).
              Use Tailwind CSS for styling. Omit headers and global CSS.
              Add a unique id for each input.
              Ignore vertically placed texts.
              Display page number and date at the top. Ignore 'Sheet No.' unless it's part of a section.
              If a section header is missing, group the content with the last valid section.
              inculde a hidden input which contains the value of total sections.
              Output only the HTML Canvas elements. No extra text."""),
        ],
    )

    content = ''
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        content += chunk.text if chunk.text else ''

    content = content.replace('```html', '')
    content = content.replace('```', '')
    return content


def get_total_sections_ai(base64_data):
    client, contents, model = prepare_gemini_client(base64_data)
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
        ),
        system_instruction=[
            types.Part.from_text(text="""You will receive a PDF and analyse total sections. 
                                 give it as json format { total_sections: <total_sections> }
                                No extra text."""),
        ],
    )

    content = ''
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        content += chunk.text if chunk.text else ''

    content = content.replace('```json', '')
    content = content.replace('```', '')
    return json.loads(content)


def warp_html_skeleton(content:str)->str:
    content = content.replace('```html', '')
    content = content.replace('```', '')
    return """
    <html>
        <head>
            <link rel="stylesheet" href="https://code.jquery.com/ui/1.13.2/themes/base/jquery-ui.css" />
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet"> 
        </head>

        <body>
        <style>
            input{
                padding : 0px 5px;
                border: 1px solid #f3f4f6 !important;
            }
        </style>
        """ \
        + content + \
        """</body>
    </html>
    """