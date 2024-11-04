from docx import Document
from datetime import date
from docx.shared import Pt

from io import BytesIO
import os

def make_pass(
    names: list[str],
    start_date: date,
    end_date: date,
    created_at: date,
    auto_model:str,
    auto_plates:str,
    num: str
):
    doc = Document('./templates/template.docx')
    
    start_date = start_date.strftime("%d.%m.%Y")
    end_date = end_date.strftime("%d.%m.%Y")
    created_at = created_at.strftime("%d.%m.%Y")

    names_replaced = 0

    for paragraph in doc.paragraphs:

        if '<date_start>' in paragraph.text:
            paragraph.text = paragraph.text.replace('<date_start>', start_date)
            
        if '<date_end>' in paragraph.text:
            paragraph.text = paragraph.text.replace('<date_end>', end_date)
            
        # if '<fullname>' in paragraph.text:
        #     if names_replaced < len(names):
        #         paragraph.text = paragraph.text.replace('<fullname>', names[names_replaced])
        #     else:
        #         paragraph.text = paragraph.text.replace('<fullname>', '')
        #     names_replaced += 1

        if '<todaysdate>' in paragraph.text:
            paragraph.text = paragraph.text.replace('<todaysdate>', created_at)
        if '<automodel>' in paragraph.text:
            if auto_model:
                paragraph.text = paragraph.text.replace('<automodel>',f'Авто: {auto_model}')
            else:
                paragraph.text = paragraph.text.replace('<automodel>','')
        if '<autoplates>' in paragraph.text:
                if auto_plates:
                    paragraph.text = paragraph.text.replace('<autoplates>',f'Гос.Номер: {auto_plates}')
                else:
                    paragraph.text = paragraph.text.replace('<autoplates>','')
        if '<number>' in paragraph.text:
            paragraph.text = paragraph.text.replace('<number>', num)
        for run in paragraph.runs:
            run.font.size = Pt(16)
            run.font.name = 'Times New Roman'

        if '<fullname>' in paragraph.text:
            if names_replaced < len(names):
 
                paragraph.text = paragraph.text.replace('<fullname>', names[names_replaced])

            else:
                paragraph.text = paragraph.text.replace('<fullname>', '')
            names_replaced += 1

            for run in paragraph.runs:
                run.font.size = Pt(17)
                run.font.name = 'Times New Roman'

    
    new_word_file = fr'{num}_{names[0]}_{start_date}_{end_date}.docx'
    
    file_stream = BytesIO()
    
    doc.save(file_stream)

    return file_stream, new_word_file