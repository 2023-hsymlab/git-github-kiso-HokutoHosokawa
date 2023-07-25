#!/usr/bin/env python
# coding: utf-8

# In[2]:


from tkinter import *
from tkinter import ttk
import smtplib
import random
import math
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import sqlite3
import hashlib
import datetime
import sys
import socket


# In[3]:


dbname = ('userinfo.db')
conn = sqlite3.connect(dbname, isolation_level=None)


# In[4]:


cursor = conn.cursor()
sql = """CREATE TABLE IF NOT EXISTS userinfo(email, id, password, latest_ip_address, web_login)"""

cursor.execute(sql)
conn.commit()


# In[8]:


def limit_char6(str):
    return len(str) <= 6

def limit_char16(str):
    return len(str) <= 16

def login_home():
    #ログインのホーム画面の作成
    global frame
    global label3

    frame = ttk.Frame(root)
    frame.pack(fill = BOTH, pady=20)

    label = ttk.Label(frame, text='ユーザー名またはメールアドレス')
    label.grid(row=0, column=0)

    entry = ttk.Entry(frame) #ユーザー名やメールアドレスの入力ボックス
    entry.grid(row=0, column=1, sticky=EW, padx=20)

    label2 = ttk.Label(frame, text='パスワード')
    label2.grid(row=1, column=0)

    entry2 = ttk.Entry(frame, show='*') #パスワードの入力ボックス
    entry2.grid(row=1, column=1, sticky=EW, padx=20)
    ###パスワードは半角英数、記号だけで構成されているかどうかを確認する必要あり。

    button = ttk.Button(frame, text='ログイン', command=lambda:login_panel(entry.get(), entry2.get()))
    button.grid(row=2, column=0, columnspan=2)

    label3 = ttk.Label(frame, text="", foreground='red')
    label3.grid(row=3, column=0, columnspan=2)
    ###上のラベルはログインに失敗した場合に「ユーザー名またはパスワードが違います」を表示するよう

    link = ttk.Label(frame, text='パスワードを忘れた場合はこちら',foreground='blue',cursor='hand1',font=('MSゴシック', 12, 'underline'))
    link.grid(row=5, column=0, columnspan=2)
    link.bind("<Button-1>",lambda e:forget_pass())

    link2 = ttk.Label(frame, text='新規登録はこちら',foreground='blue',cursor='hand1',font=('MSゴシック',12,'underline'))
    link2.grid(row=6, column=0, columnspan=2)
    link2.bind("<Button-1>",lambda e:make_account())

    frame.grid_columnconfigure(1, weight=1)

def frame_destroy(frame_name):
    #受け取ったフレームを削除し、ログインホーム画面に戻る
    frame_name.destroy()
    login_home()

def forget_pass():
    """
    ここはパスワードを忘れた場合である。

    ユーザー名に対応したメールアドレス（または入力してもらったシステムに使用しているメールアドレス)に仮パスワード（認証コード)を送る
    仮パスワードをシステムに入力してもらい、本人確認が取れたらパスワード変更画面に遷移
    パスワード変更完了
    """
    global frame_forget
    global label_forget2

    frame.destroy()

    frame_forget = ttk.Frame(root)
    frame_forget.pack(fill = BOTH, pady = 20)

    label_forget1 = ttk.Label(frame_forget, text='ユーザー名またはメールアドレス')
    label_forget1.pack()

    entry_forget1 = ttk.Entry(frame_forget, width=65) #ユーザー名やメールアドレスの入力ボックス
    entry_forget1.pack()

    button_forget1 = ttk.Button(frame_forget, text='パスワードを変更する', command=lambda:mail_check(entry_forget1.get()))
    button_forget1.pack()

    label_forget2 = ttk.Label(frame_forget, text="", foreground="red")
    label_forget2.pack()

    ttk.Button(frame_forget, text="ログイン画面に戻る", command=lambda:frame_destroy(frame_forget)).pack(side=BOTTOM)
    ###登録されているユーザー名またはメールアドレスと一致するかどうかを確認する
    ###メールで確認コードを送信して、メールの確認を行う。コードはランダムな6桁の数字とかがいい？

def mail_check(txt):
    """
    入力されたメールアドレスにメールを送信するプログラムを作成する。
    """
    #@が含まれているかどうかで、メールアドレスかユーザー名かを判別する
    if '@' in txt:
        sql = """SELECT * FROM userinfo WHERE email = ?"""
    else:
        sql = """SELECT * FROM userinfo WHERE id = ?"""

    cursor.execute(sql,[txt])
    fit = cursor.fetchall()
    if len(fit) == 0:
        label_forget2["text"]="そのユーザー名またはメールアドレスは登録されていません。"
    else:
        txt, *_ = fit[0]

        smtp_server = "smtp.gmail.com"
        port = 587

        server = smtplib.SMTP(smtp_server, port)
        server.starttls()

        #login_address = "p.seminar.vts@gmail.com"
        #login_password = "aoxorgtkblyaptjc"

        #確認メールの送信

        server.login(login_address, login_password)

        message = MIMEMultipart()

        message["Subject"] = "【Virtual Trading System】パスワード変更のお知らせ"
        message["From"] = login_address
        message["To"] = txt

        rand = math.floor(1 + (random.random() * 9)) * 100000 + math.floor(random.random() * 10) * 10000 + math.floor(random.random() * 10) * 1000 + math.floor(random.random() * 10) * 100 + math.floor(random.random() * 10) * 10 + math.floor(random.random() * 10)
        text = MIMEText("パスワードの再設定をご希望の場合は次の認証コードをアプリケーションに入力し、パスワードの変更を行ってください。\n\n認証コード:"+str(rand) + "\n\n本メールにお心当たりのない場合は、お手数ですが本メールの破棄をお願いいたします。")
        message.attach(text)

        server.send_message(message)

        server.quit()


        frame_forget.destroy()
        ###確認コード入力画面を作成
        global CheckCodeFrame_forget

        CheckCodeFrame_forget = ttk.Frame(root)
        CheckCodeFrame_forget.pack(fill = BOTH, pady = 20)

        CheckCodeLabel_forget = ttk.Label(CheckCodeFrame_forget, text='入力したメールアドレスに届いた確認コードを入力してください')
        CheckCodeLabel_forget.pack()

        vc = root.register(limit_char6)
        CheckCodeEntry_forget = ttk.Entry(CheckCodeFrame_forget, validate='key',validatecommand=(vc, "%P"), width=7) #確認コードの入力ボックス
        CheckCodeEntry_forget.pack()

        CheckCodeButton_forget = ttk.Button(CheckCodeFrame_forget, text="確認する", command=lambda:checkCode_forget(str(rand), CheckCodeEntry_forget.get(), txt))
        CheckCodeButton_forget.pack()

def checkCode_forget(rand, received, address):
    global remake_pass_frame
    global remake_pass_label4
    if rand == received:
        ###ここにコードが正しい場合の処理(パスワード変更画面に遷移)を書く
        CheckCodeFrame_forget.destroy()

        remake_pass_frame = ttk.Frame(root)
        remake_pass_frame.pack()

        remake_pass_label1 = ttk.Label(remake_pass_frame, text="パスワード")
        remake_pass_label1.grid(row=0, column=0)
        
        remake_pass_entry1 = ttk.Entry(remake_pass_frame, show="*") #パスワードの入力ボックス
        remake_pass_entry1.grid(row=0, column=1, sticky=EW, padx=20)

        remake_pass_label2 = ttk.Label(remake_pass_frame, text="パスワード(確認)")
        remake_pass_label2.grid(row=1, column=0)

        remake_pass_entry2 = ttk.Entry(remake_pass_frame, show="*") #パスワード（2回目）の入力ボックス
        remake_pass_entry2.grid(row=1, column=1, sticky=EW, padx=20)

        remake_pass_label3 = ttk.Label(remake_pass_frame, text="パスワードは8~32文字の半角アルファベットと数字、記号で構成してください。")
        remake_pass_label3.grid(row=2, column=0, columnspan=2)

        remake_pass_button = ttk.Button(remake_pass_frame, text="再設定する", command=lambda:remake_pass_check(address, remake_pass_entry1.get(), remake_pass_entry2.get()))
        remake_pass_button.grid(row=3, column=0, columnspan=2)

        remake_pass_label4 = ttk.Label(remake_pass_frame, text="", foreground="red")
        remake_pass_label4.grid(row=4, column=0, columnspan=2)

        remake_pass_frame.grid_columnconfigure(1, weight=1)
    else:
        ###ここにコードが間違っていた場合の処理を書く(確認コードが間違っています、程度を出力すれば問題ないと思われる。)
        ###入力ミスが一定回数を超えた場合にやり直させる。
        print("missed")


def remake_pass_check(address, pass1, pass2):
    #変更されたパスワードの確認を行う
    global repass_registar_frame
    if pass1 != pass2:
        remake_pass_label4["text"] = "確認用パスワードがパスワードと異なります。"
    elif len(pass1) < 8 or len(pass1) > 64:
        remake_pass_label4["text"] = "パスワードの文字数は8~32文字です。"
    else:
        re_alnumsym = re.compile(r'^[!-\[\]-\}]+$')
        if re.match(re_alnumsym, pass1) == None:
            remake_pass_label4["text"]="パスワードに使用できない文字が含まれています。"
        else:
            sql = """SELECT * FROM userinfo WHERE email = ?"""

            cursor.execute(sql,[address])
            fit = cursor.fetchall()
            address, user_name, _, g1, g2 = fit[0]

            sql = """DELETE FROM userinfo WHERE id = ?"""
            cursor.execute(sql,[user_name])
            conn.commit()

            sql = """INSERT INTO userinfo VALUES(?, ?, ?, ?, ?)"""
            data = ((address, user_name, hashlib.sha256(pass1.encode()).hexdigest(), socket.gethostbyname(host), True))
            cursor.execute(sql, data)
            conn.commit()
            
            ###メールの送信

            remake_pass_frame.destroy()

            repass_registar_frame = ttk.Frame(root)
            repass_registar_frame.pack()

            repass_registar_label = ttk.Label(repass_registar_frame, text="パスワードの再設定が完了しました。")
            repass_registar_label.pack()
            ttk.Button(repass_registar_frame, text="ログイン画面に戻る", command=lambda:frame_destroy(repass_registar_frame)).pack(side=BOTTOM)

def make_account():
    """
    ここは、新規アカウントの作成を行う場合である。

    メールアドレスの入力（すでに使われているメールアドレスでないかどうかの確認)
    入力してもらったメールアドレスに仮パスワードを送信
    仮パスワードを入力してもらい、本人確認が取れたら本パスワードを作ってもらう。（半角英数字、記号、文字数制限)（2回同じパスワードを入力してもらう)
    登録完了
    """
    global frame_make_account
    global label_make_account1

    frame.destroy()

    frame_make_account = ttk.Frame(root)
    frame_make_account.pack(fill = BOTH, pady = 20)

    label_make_account = ttk.Label(frame_make_account, text="メールアドレスを入力してください。")
    label_make_account.pack()

    entry_make_account = ttk.Entry(frame_make_account, width=65) #メールアドレスの入力ボックス
    entry_make_account.pack()

    button_make_account = ttk.Button(frame_make_account, text="メールを送信する",command=lambda:makeAccountCheckCode(entry_make_account.get()))
    button_make_account.pack()

    label_make_account1 = ttk.Label(frame_make_account, text="", foreground='red')
    label_make_account1.pack()

    ttk.Button(frame_make_account, text="ログイン画面に戻る", command=lambda:frame_destroy(frame_make_account)).pack(side=BOTTOM)

def makeAccountCheckCode(address):
    """
    ここで、メールアドレスが正しいかどうかを最初に確認し、正しくない場合は（@が含まれていないなど)不正であることを伝える。
    そして、正しい場合は確認コードを載せたメールをそのメールアドレスに送信し、確認コードが正しいことを確認する。
    確認コードが正しいことが確認できたら、次のパネルに行く。
    """
    check = True
    re_isTrue = re.compile(r'^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$')
    if re.match(re_isTrue, address) == None:
        label_make_account1["text"]="不正なメールアドレスです。"
        check = False
    

    ###使用されているメールアドレスかどうかを確認する。(label_make_account1["text"] = "そのメールアドレスはすでに使用されています。")
    sql = """SELECT * FROM userinfo WHERE email = ?"""

    cursor.execute(sql,[address])
    fit = cursor.fetchall()

    if len(fit) != 0:
        label_make_account1["text"] = "そのメールアドレスはすでに使用されています。"
        check = False

    if check:
        frame_make_account.destroy()
        ###メールの送信、確認コードの確認など
        smtp_server = "smtp.gmail.com"
        port = 587

        server = smtplib.SMTP(smtp_server, port)
        server.starttls()

        #login_address = "p.seminar.vts@gmail.com"
        #login_password = "aoxorgtkblyaptjc"

        server.login(login_address, login_password)

        message = MIMEMultipart()

        message["Subject"] = "【Virtual Trading System】新規登録のお知らせ"
        message["From"] = login_address
        message["To"] = address

        rand = math.floor(1 + (random.random() * 9)) * 100000 + math.floor(random.random() * 10) * 10000 + math.floor(random.random() * 10) * 1000 + math.floor(random.random() * 10) * 100 + math.floor(random.random() * 10) * 10 + math.floor(random.random() * 10)
        text = MIMEText("会員登録のお手続きありがとうございます。\nこの度はVirtual Trading Systemに仮登録していただき、ありがとうございます。\n\n現在の段階では会員登録手続きは完了しておりません。会員登録を完了するには次の認証コードをアプリケーションに入力し、ユーザー名とパスワードを設定してください。\n\n認証コード:"+str(rand) + "\n\n本メールにお心当たりのない場合は、お手数ですが本メールの破棄をお願いいたします。")
        message.attach(text)

        server.send_message(message)

        server.quit()

        global CheckCodeFrame_make

        CheckCodeFrame_make = ttk.Frame(root)
        CheckCodeFrame_make.pack(fill = BOTH, pady = 20)

        CheckCodeLabel_make = ttk.Label(CheckCodeFrame_make, text='入力したメールアドレスに届いた確認コードを入力してください')
        CheckCodeLabel_make.pack()

        vc = root.register(limit_char6)
        CheckCodeEntry_make = ttk.Entry(CheckCodeFrame_make, validate='key',validatecommand=(vc, "%P"), width=7) #確認コードの入力ボックス
        CheckCodeEntry_make.pack()

        CheckCodeButton_make = ttk.Button(CheckCodeFrame_make, text="確認する", command=lambda:checkCode_make(str(rand), CheckCodeEntry_make.get(), address))
        CheckCodeButton_make.pack()

def checkCode_make(rand, text, address):
    global setting_label4
    global setting_frame
    if rand==text:
        ###確認コードが正しい場合の処理
        ###ユーザー名とパスワードの設定をする。パスワードは2回記述させる。
        CheckCodeFrame_make.destroy()

        setting_frame = ttk.Frame(root)
        setting_frame.pack(fill = BOTH, pady = 20)

        setting_label1 = ttk.Label(setting_frame, text="ユーザー名")
        setting_label1.grid(row=0, column=0)

        vc = root.register(limit_char16)
        setting_entry1 = ttk.Entry(setting_frame, validate='key',validatecommand=(vc, "%P")) #ユーザー名の入力ボックス
        setting_entry1.grid(row=0, column=1, sticky=EW, padx=20)

        setting_label2 = ttk.Label(setting_frame, text="パスワード")
        setting_label2.grid(row=1, column=0)

        setting_entry2 = ttk.Entry(setting_frame, show="*") #パスワードの入力ボックス
        setting_entry2.grid(row=1, column=1, sticky=EW, padx=20)

        setting_label3 = ttk.Label(setting_frame, text="パスワード(確認用)")
        setting_label3.grid(row=2, column=0)

        setting_entry3 = ttk.Entry(setting_frame, show="*") #パスワード（2回目）の入力ボックス
        setting_entry3.grid(row=2, column=1, sticky=EW, padx=20)

        setting_label5 = ttk.Label(setting_frame, text="ユーザー名は16文字以内の半角アルファベットと数字で構成してください。")
        setting_label5.grid(row=3, column=0, columnspan=2)

        setting_label6 = ttk.Label(setting_frame, text="パスワードは8~32文字の半角アルファベットと数字、記号で構成してください。")
        setting_label6.grid(row=4, column=0, columnspan=2)

        setting_button = ttk.Button(setting_frame, text="登録する", command=lambda:registar_check(address, setting_entry1.get(), setting_entry2.get(), setting_entry3.get()))
        setting_button.grid(row=5, column=0, columnspan=2)

        setting_label4 = ttk.Label(setting_frame, text="",foreground="red")
        setting_label4.grid(row=6, column=0, columnspan=2)

        setting_frame.grid_columnconfigure(1, weight=1)

    else:
        ###確認コードが間違っている場合の処理
        print("Missed")

def registar_check(address, user_name, user_pass1, user_pass2):
    ###ここでは登録情報のチェックを行い、正しく登録できる場合は登録完了のむねをメールと画面で伝えるようにする。
    ###登録情報のチェックとしては(1)ユーザー名が使用されていないか、(2)パスワードの文字数や使用文字が適切か(3)パスワードの入力欄とパスワード(確認)の入力欄の文字列が一致するか、がある。
    global registar_frame

    sql = """SELECT * FROM userinfo WHERE id = ?"""

    cursor.execute(sql,[user_name])
    fit = cursor.fetchall()

    if len(fit) != 0:
        setting_label4['text'] = "そのユーザー名はすでに使用されています。"
    else:
        re_alnum = re.compile(r'^[a-zA-z0-9]+$')
        if re.match(re_alnum, user_name) == None:
            setting_label4["text"]="ユーザー名に使用できない文字が含まれています。"
        elif len(user_name) == 0:
            setting_label4["text"]="ユーザー名を入力してください。"
        else:
            if user_pass1 != user_pass2:
                setting_label4["text"] = "確認用パスワードがパスワードと異なります。"
            elif len(user_pass1) < 8 or len(user_pass1) > 64:
                setting_label4["text"] = "パスワードの文字数は8~32文字です。"
            else:
                re_alnumsym = re.compile(r'^[!-\[\]-\}]+$')
                if re.match(re_alnumsym, user_pass1) == None:
                    setting_label4["text"]="パスワードに使用できない文字が含まれています。"
                else:
                    sql = """INSERT INTO userinfo VALUES(?, ?, ?, ?, ?)"""
                    data = ((address, user_name, hashlib.sha256(user_pass1.encode()).hexdigest(), socket.gethostbyname(host), True))
                    cursor.execute(sql, data)
                    conn.commit()
                    
                    ###メールの送信

                    setting_frame.destroy()
                    registar_frame = ttk.Frame(root)
                    registar_frame.pack()

                    registar_label = ttk.Label(registar_frame, text="登録が完了しました。")
                    registar_label.pack()

                    ttk.Button(registar_frame, text="ログイン画面に戻る", command=lambda:frame_destroy(registar_frame)).pack(side=BOTTOM)




def login_panel(user_name, user_pass):
    """
    ここではログインボタンを押された時に行う処理をかく。

    ユーザー名とパスワードの組のタプルが存在するかどうかをSQliteで確認して、もし正しい組が存在するのであればログインする。
    存在しないのであれば、間違っていることをlabel3["text"]="ユーザー名またはパスワードが違います"で知らせる。
    """

    if '@' in user_name:
        sql = """SELECT * FROM userinfo WHERE email = ?"""
    else:
        sql = """SELECT * FROM userinfo WHERE id = ?"""

    cursor.execute(sql,[user_name])
    fit = cursor.fetchall()
    if len(fit) == 0:
        label3["text"]="ユーザー名(メールアドレス)またはパスワードが違います"
    else:
        a, b, c, g1, g2 = fit[0]
        if '@' in user_name:
            tuple1 = (a,c)
        else:
            tuple1 = (b,c)
        user_tuple = (user_name, hashlib.sha256(user_pass.encode()).hexdigest())
        if tuple1 != user_tuple:
            label3["text"]="ユーザー名(メールアドレス)またはパスワードが違います"
        else:
            home(user_name)
            ###ここにログイン後の処理を書く

def home(user_name):
    print("Hello"+ user_name+".")

root = Tk()
root.geometry('450x200')
root.title('Virtual Trading System')
global login_address
global login_password
login_address = "p.seminar.vts@gmail.com"
login_password = "aoxorgtkblyaptjc"
host = socket.gethostname()

print(len(sys.argv))
for i in range(len(sys.argv)):
    print(sys.argv[i])

if not len(sys.argv) <= 1:
    login_name = sys.argv[1]
    login_IP = sys.argv[2]
    sql = """SELECT * FROM userinfo WHERE id = ?"""
    cursor.execute(sql,[login_name])
    fit = cursor.fetchall()
    g1, loginId, g2, loginIP, webLogin = fit[0]
    if loginIP == login_IP and webLogin == 1:
        home(login_name)
    else:
        login_home()
else:
    login_home()

root.mainloop()


# In[53]:


#sql = """DELETE FROM userinfo WHERE id = ?"""
#cursor.execute(sql,["test"])
#conn.commit()

