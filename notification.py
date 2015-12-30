
from db_def import Note
from db_def import Account
import smtplib
import traceback
import urllib2
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

gmail_user = "naturenet.aces@gmail.com"
gmail_pwd = "nature-net"
FROM = 'naturenet.aces@gmail.com'
TO = ['mj_mahzoon@yahoo.com', 'k.grace@uncc.edu', 'naturenet@aspennature.org', 'kazjon@me.com', 'tchris26@uncc.edu']

def send_new_note_notification_email(note, media, include_img):
    try:
        if note.context.title.lower() != "ask a naturalist":
            return
        subject = "New NatureNet Question"
        date = note.created_at.strftime("%I:%M%p on %A, %d %B %Y UTC")
        
        message_text1 = "Dear ACES Staff,\r\n\r\nNatureNet user " + note.account.username +\
                        " posted the following:\r\n\r\n\"" + note.content + "\"\r\n"
        message_text2 = "\r\nAdded at " + date + ". (Full sized image available at " +\
                        "http://www.nature-net.org/#/observation/" + str(note.id) + ")\r\n\r\n" +\
                        "Reply to "+ note.account.email + " to continue the conversation." +\
                        "\r\n\r\nRegards,\r\nThe NatureNet Team.\r\n"
        
        html_text1 = "Dear ACES Staff,<br /><br />NatureNet user " + note.account.username +\
                     " posted the follwing:<br /><br /><i>\"" + note.content + "\"</i><br />"
        html_text2 = "<br />Added at " + date + ". (Full sized image available at " +\
                     "http://www.nature-net.org/#/observation/" + str(note.id) + ")<br /><br />" +\
                     "Reply to "+ note.account.email + " to continue the conversation." +\
                     "<br /><br />Regards,<br />The NatureNet Team.<br />"
        
        to_list = populate_notification_list_aces()
        print "sending notification to: "
        print to_list
        if include_img:
            send_multipart_email(subject, html_text1, html_text2, media.get_url_smallsized(), note.account.email, to_list)
        else:
            send_email(subject, message_text1 + message_text2, to_list)
    except:
        print traceback.format_exc()

def populate_notification_list_aces():
    to_list = []
    to_list.append(TO[0])
    to_list.append(TO[1])
    to_list.append(TO[2])
    to_list.append(TO[3])
    #accounts = Account.query.filter(Account.affiliation.ilike('aces')).all()
    #for a in accounts:
    #    if a.email:
    #        to_list.append(a.email)
    return to_list

def send_email(subject, message_text, to_list):
    message = """\From: %s\r\nTo: %s\nSubject: %s\r\n\r\n%s""" % (FROM, ", ".join(to_list), subject, message_text)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, to_list, message)
        #server.quit()
        server.close()
        print 'successfully sent the mail'
    except:
        print traceback.format_exc()

def send_multipart_email(subject, text_part1, text_part2, img_url, replyto, to_list):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = FROM
    msgRoot['To'] = ", ".join(to_list)
    msgRoot.add_header('reply-to', replyto)
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    msgText = MIMEText(text_part1 + text_part2);
    msgAlternative.attach(msgText)
    msgText = MIMEText(text_part1.replace("\r\n", "<br />") +\
                       '<img src="cid:image1">' +\
                       text_part2.replace("\r\n", "<br />"), 'html')
    msgAlternative.attach(msgText)
    content=urllib2.urlopen(img_url).read()
    msgImage = MIMEImage(content)
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)
    smtp = smtplib.SMTP()
    smtp.connect('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(gmail_user, gmail_pwd)
    smtp.sendmail(FROM, to_list, msgRoot.as_string())
    smtp.quit()
