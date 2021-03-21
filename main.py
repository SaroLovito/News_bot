from bs4 import BeautifulSoup
import redis
from password import bot_email_pw
import requests



# source
class Scraper:
    def __init__(self, keywords):
        self.markup = requests.get('https://news.ycombinator.com/').text
        self.keywords = keywords

    # parser
    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup.findAll("a", {'class': 'storylink'})
        self.saved_links = []
        for link in links:
            for keyword in self.keywords:
                if keyword in link.text:
                    self.saved_links.append(link)
        print(self.saved_links)

    # storage
    def store(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        for link in self.saved_links:
            r.set(link.text, str(link))

    def email(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        links = [str(r.get(k)) for k in r.keys()]
        print(links)

        # email
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        fromEmail = "enter_bot_email"
        toEmail = "enter_your_email"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg['From'] = fromEmail
        msg['To'] = toEmail

        html = """
            <h4> %s links you might find interesting today: </h4>
            %s

        """ % (len(links), '<br/><br/>'.join(links))

        mime = MIMEText(html, 'html')

        msg.attach(mime)

        try:
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login(fromEmail, bot_email_pw)
            mail.sendmail(fromEmail, toEmail, msg.as_string())
            mail.quit()
            print(('Email sent!'))
        except Exception as exc:
            print('something might went wrong...%s' % exc)

        # flush redis
        r.flushdb()


s = Scraper(['Game'])
s.parse()
s.store()
s.email()
