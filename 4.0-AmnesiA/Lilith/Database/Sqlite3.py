import sqlite3
import hashlib


class MailDB():
    def __init__(self):
        self.connection = sqlite3.connect("./Files/Mail/mail.db")
        self.cursor = self.connection.cursor()
        self.User = None
        self.Password = None
        self.UserId = None
        self.is_Authed = False
        self.MailList = []
        self.was_starttls = False
        self.was_hello = False
        self.AckMail = False
        self.RcptTo = []
        self.MailFrom = None

    def Auth(self):
        self.cursor.execute("select id from accounts where user=? and pass=?",
                            (self.User, self.Password))
        r = self.cursor.fetchone()
        if(r is not None):
            self.UserId = r[0]
            self.is_Authed = True
        else:
            self.is_Authed = False
        return(self.is_Authed)

    def GetStat(self):
        self.cursor.execute(
            "select count(id), total(octet) from mail_box where user_id=?", (self.UserId,))
        r = self.cursor.fetchone()
        mail_vol = r[0]
        mail_octets = int(r[1])
        return(mail_vol, mail_octets)

    def GetList(self):
        mail_vol, mail_octets = self.GetStat()
        self.MailList = []
        R = b""
        if(0 < mail_vol):
            self.cursor.execute(
                "select octet from mail_box where user_id=?", (self.UserId,))
            r = self.cursor.fetchall()
            for a in r:
                self.MailList.append(a[1])
                R += (b"%d %d\r\n" % (i, a[0]))
                i += 1
        return(R)

    def GetUidl(self):
        mail_vol, mail_octets = self.GetStat()
        self.MailList = []
        R = b""
        if(0 < mail_vol):
            self.cursor.execute(
                "select uidl from mail_box where user_id=?", (self.UserId,))
            r = self.cursor.fetchall()
            i = 1
            for a in r:
                self.MailList.append(a[0])
                R += (b"%d %b\r\n" % (i, a[0].encode("utf-8")))
                i += 1
        return(R)

    def Delete(self, p):
        self.cursor.execute(
            "delete from mail_box where uidl=? and user_id=?", (self.MailList[p], self.UserId))

    def Retr(self, p):
        self.cursor.execute("select octet, message, mail_from from mail_box where uidl=? and user_id=?", (
            self.MailList[int(p)-1], self.UserId))
        r = c.fetchone()
        return(r)

    def RecvMail(self, to, mail_data):
        self.cursor.execute("select id from accounts where user=?",
                            (to.decode("utf-8"),))
        r = self.cursor.fetchone()
        self.cursor.execute("insert into mail_box(user_id, message, octet, uidl, mail_from) values(?, ?, ?, ?, ?)",
                            (r[0], mail_data.decode("utf-8"), len(mail_data), hashlib.md5(mail_data).hexdigest(), self.MailFrom.decode("utf-8")))

    def Commit(self):
        self.connection.commit()

    def Close(self):
        self.connection.close()
