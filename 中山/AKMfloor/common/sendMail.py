from email.mime.text import MIMEText
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.header import Header
import os,sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

mail_mul = MIMEMultipart()
mail_text = MIMEText("Hello, i am fastprint!", "plain", "utf-8")
mail_mul.attach(mail_text)

from_addr = "combafastprintsend@163.com"
from_pwd = "combafastprint20"
to_addr = "combafastprintrcvd@163.com"
smtp_srv = "smtp.163.com"

mail_mul['Subject']=Header('fastprint log', 'utf8')
mail_mul['From']=from_addr
mail_mul['To']=to_addr

def attach(cur,fileList):
    for filename in fileList:
        with open(cur+'/'+filename, "rb") as f:
            s = f.read()
            m = MIMEText(s, 'base64', "utf-8")
            m["Content-Type"] = "application/octet-stream"
            m["Content-Disposition"] = "attachment; filename={}".format(filename)
            mail_mul.attach(m)
    return mail_mul

def main():
    fileList = []
    cur = os.path.abspath(os.path.dirname(__file__))

    print(cur+'\log')
    for file in os.listdir(cur+'\log'):
    	if file.split('.')[-1] == 'log':
            fileList.append(file)
    print(fileList)
    mail_mul = attach(cur+'\log',fileList)

    try:
        import smtplib
        srv = smtplib.SMTP_SSL(smtp_srv.encode(), 465)
        # smtpObj = smtplib.SMTP()
        # smtpObj.connect(smtp_srv, 25)    # 25 为 SMTP 端口号

        srv.login(from_addr, from_pwd)
        srv.sendmail(from_addr, [from_addr,to_addr], mail_mul.as_string())
        srv.quit()
        print('send email done')
    except Exception as e:
        print(e)



if __name__ == "__main__":
    main()
