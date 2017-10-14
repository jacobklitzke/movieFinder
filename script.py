import requests
import sys
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL=''
EMAIL_USERNAME = ''
EMAIL_PASSWORD = ''

me = EMAIL
you = EMAIL

msg = MIMEMultipart('alternative')
msg['Subject'] = "Script Results"
msg['From'] = me
msg['To'] = you

res = requests.get('http://localhost:5000/findItems')
if res.content == "NoResults":
    sys.exit()
else:
    results = res.json()
    html = ("<html><head><style>table,th,td {border: 1px solid black;}</style></head><body><table>" +
            "<tr><th>Title</th><th>Price</th><th>Listing Type</th><th>Time Left</th><th>Link</th></tr>")
    for result in results:
        html = (html + "<tr><th>" + result["title"] + "</th>" +
                "<th>" + str(result["price"]) + "</th>" +
                "<th>" + result["listingType"] + "</th>" +
                "<th>" + result["timeLeft"] + "</th>" +
                "<th><a href=\"" + result["link"] + "\">Link</a></th></tr>")
    html = html + "</table></body></html>"
    part = MIMEText(html, 'html', 'utf-8')
    msg.attach(part)
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    mail.sendmail(me, you, msg.as_string())
    mail.quit()
