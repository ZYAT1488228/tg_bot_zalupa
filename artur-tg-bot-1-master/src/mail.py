import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
from io import BytesIO

def send_email_with_attachment(sender_email, sender_password, receiver_email, subject, message, attachments,chat_id):
    # Создание объекта сообщения
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Добавление текстового сообщения
    msg.attach(MIMEText(message, 'plain'))

    # Добавление вложения
    for attach in attachments[chat_id]:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attach['file'].getvalue())
        encoders.encode_base64(part)

        # encoded_filename = Header(name, "utf-8").encode()
        part.add_header('Content-Disposition', "attachment", filename=attach['name'])
        msg.attach(part)


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

if __name__ == "__main__":
    file = BytesIO()

    with open(r'C:\Users\nikhi\Documents\work\artur\artur-tg-bot-1\templates\template.docx', 'rb') as f:
        file.write(f.read())

    

    send_email_with_attachment(
        sender_email='viktoriya2008propuska@gmail.com',
        sender_password= "mimxzfykczjmequf",
        receiver_email='nikhin24@outlook.com',
        subject='Начальнику',
        message='',
        attachment=file,
        name = 'Начальнику.docx'
    )
