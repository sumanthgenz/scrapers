from urllib.request import urlopen
import smtplib, ssl
import time

url = "https://deepmind.com/careers/internships"
page = urlopen(url)
html_bytes = page.read()
html = html_bytes.decode("utf-8")

check1 = "Our internship applications are currently closed but applications for 2022 will open later this year."
check2 = "Thank you for your interest in an internship at DeepMind. Unfortunately, we do not currently have any open roles. Please check back again later."

def f(send=True):
    intern_app_open = send
    if check1 in html or check2 in html:
        intern_app_open = not send
    print(intern_app_open)

    username = ""
    password = ""
    to = ""
    msg = f"""\
    Subject: DeepMind Internships

    2022 internships open: {intern_app_open}
    """

    if intern_app_open:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as server:
            server.login(username, password)
            server.sendmail(username, to, msg)

while True:
    f()
    time.sleep(43200)
