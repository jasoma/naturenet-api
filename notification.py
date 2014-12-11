
from db_def import Note
from db_def import Account
import smtplib

gmail_user = "naturenet.aces@gmail.com"
gmail_pwd = "nature-net"
FROM = 'naturenet.aces@gmail.com'
TO = ['mj_mahzoon@yahoo.com', 'k.grace@uncc.edu']

def send_new_note_notification_email(activity_name, username, useremail, comment, timestamp):
    if activity_name.lower() != "stump the community":
        return
    subject = "New NatureNet Question"
    message_text = "Dear ACES,\r\n\r\nNatureNet user " + username +\
                   " posted this" + ":\r\n\r\n\"" + comment + "\"\r\n\r\n" +\
                   "Reply to "+ useremail + " to continue the conversation.\r\n\r\nRegards,\r\nThe NatureNet Team.\r\n"
    to_list = populate_notification_list_aces()
    print "sending notification to: "
    print to_list
    send_email(subject, message_text, to_list)

def populate_notification_list_aces():
    to_list = []
    to_list.append(TO[0])
    to_list.append(TO[1])
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
        print "failed to send mail"
