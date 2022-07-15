from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import json
import requests

app = Flask(__name__)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2d46b6b4-cbf6-40eb-bbce-6251e6ba0300.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32328;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=vgx48679;PWD=5jcEETKHLJMDxCgR",'','')

@app.route('/registration')
def home():
    return render_template('register.html')

@app.route('/register',methods=['POST'])
def register():
    x = [x for x in request.form.values()]
    print(x)
    name=x[0]
    email=x[1]
    phone=x[2]
    city=x[3]
    infect=x[4]
    blood=x[5]
    password=x[6]
    sql = "SELECT * FROM user WHERE email =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    if account:
        return render_template('register.html', pred="You are already a member, please login using your details")
    else:
        insert_sql = "INSERT INTO  user VALUES (?, ?, ?, ?, ?, ?, ?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, name)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, phone)
        ibm_db.bind_param(prep_stmt, 4, city)
        ibm_db.bind_param(prep_stmt, 5, infect)
        ibm_db.bind_param(prep_stmt, 6, blood)
        ibm_db.bind_param(prep_stmt, 7, password)
        ibm_db.execute(prep_stmt)
        return render_template('register.html', pred="Registration Successful, please login using your details")
       
           
        

@app.route('/')    
@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/loginpage',methods=['POST'])
def loginpage():
    user = request.form['user']
    passw = request.form['passw']
    sql = "SELECT * FROM user WHERE email =? AND password=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user)
    ibm_db.bind_param(stmt,2,passw)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print (account)
    print(user,passw)
    if account:
            return redirect(url_for('stats'))
    else:
        return render_template('login.html', pred="Login unsuccessful. Incorrect username / password !") 
    
        
@app.route('/stats')
def stats():
    sql = "SELECT count(*) FROM user"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    count = ibm_db.fetch_assoc(stmt)
    print(count)
    no_of_donors=count['1']
    sql1 = "SELECT blood,count(blood) FROM user group by blood"
    stmt1 = ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    count1 = ibm_db.fetch_assoc(stmt1)
    Opositive_count=0
    Apositive_count=0
    Bpositive_count=0
    ABpositive_count=0
    Onegative_count=0
    Anegative_count=0
    Bnegative_count=0
    ABnegative_count=0
    while count1 != False:
         print(count1)
         if count1["BLOOD"] == 'O Positive':
            Opositive_count=count1['2']
         elif count1["BLOOD"] == "A Positive":
            Apositive_count=count1['2']
         elif count1["BLOOD"] == "B Positive":
            Bpositive_count=count1['2']  
         elif count1["BLOOD"] == "AB Positive":
            ABpositive_count=count1['2']
         elif count1["BLOOD"] == "O Negative":
            Onegative_count=count1['2']
         elif count1["BLOOD"] == "A Negative":
            Anegative_count=count1['2']
         elif count1["BLOOD"'blood'] == "B Negative":
            Bnegative_count=count1['2'] 
         elif count1["BLOOD"] == "AB Negative":
            ABnegative_count=count1['2']                 
         count1 = ibm_db.fetch_assoc(stmt1)
    
    return render_template('stats.html',b=no_of_donors,b1=Opositive_count,b2=Apositive_count,b3=Bpositive_count,b4=ABpositive_count,b5=Onegative_count,b6=Anegative_count,b7=Bnegative_count,b8=ABnegative_count)
@app.route('/requester')
def requester():
    return render_template('request.html')


@app.route('/requested',methods=['POST'])
def requested():
    bloodgrp = request.form['bloodgrp']
    address = request.form['address']
    print(address)
    sql = "SELECT * FROM user WHERE blood=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,bloodgrp)
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt)
   # msg = "Need Plasma of your blood group for: "+address
    msg="Greetings from Inft Tech :" + address
    while data != False:
        print ("The Phone is : ", data["PHONE"])
       # url="https://www.fast2sms.com/dev/bulkV2?authorization=sGp1w1DgUKm6dXy4VzpA5ubMEwip9fu9nDoDw3CoTIvARaqL4DWmS0jlpHBo&sender_id=FASTSM &message="+msg+"&language=english&route=p&numbers="+str(data["PHONE"])
        url = "https://www.fast2sms.com/dev/bulkV2"
        my_data = {
            'sender_id': 'FTWSMS', 
            'message': msg, 
            'language': 'english',
            'route': 'p',
            'numbers':str(data["PHONE"])
        }
        headers = {
            'authorization': 'sGp1w1DgUKm6dXy4VzpA5ubMEwip9fu9nDoDw3CoTIvARaqL4DWmS0jlpHBo',
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache"
        }
        result=requests.request("POST",url,data=my_data,headers=headers)
        #load json data from source
        returned_msg = json.loads(result.text)
        print(returned_msg['message'])
          #print(result) 
        data = ibm_db.fetch_assoc(stmt)
    return render_template('request.html', pred="Your request is sent to the concerned people.")
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

