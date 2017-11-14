from flask import Flask, render_template, request,flash
app = Flask(__name__)

import datetime
import mysql.connector

login_needed=0
try:
    conn = mysql.connector.connect(database="cricket", user="project",host="127.0.0.1",password="Cricket.1")
except:
    conn = mysql.connector.connect(database="python_mysql", user="root",host="127.0.0.1",password="vivbhav97")
cursor = conn.cursor(buffered=True)
cursor1 = conn.cursor(buffered=True)
#Even if previous user didn't logout, current_user will be cleared.
f=open("current_user.txt","w")
if login_needed:
    f.write("0")
else:
    f.write("1")
f.close()

@app.route('/')
@app.route('/login.html')
def login_page(name=None):
    return render_template('login.html', name=name)

@app.route('/statistics.html')
def stats(name=None):
    return render_template('statistics.html', name=name)

@app.route('/playervsplayer.html', methods=['POST', 'GET'])
def pvsp(name=None):
    if request.method == 'POST':
        player1 = request.form['player1']
        player2 = request.form['player2']
        cursor.execute(("select * from player where name in ('{}', '{}');".format(player1, player2)))
        rows = [i for i in cursor]
    else:
        rows = [['-'] * 17]*2           
    return render_template('playervsplayer.html', name=name, row = rows)

#just add a logout button and add link /logout.html
@app.route('/logout.html')
def logout(name=None):
    f=open("current_user.txt","w")
    f.write("0")
    f.close() #redirect to login page 
    return render_template('login.html', name=name)

@app.route('/topplayers.html')
def topplay(name=None):
    cursor.execute(("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by runs desc limit 20"))
    rows = [i for i in cursor]
    cursor1.execute(("select name, wickets, eco, fourhaul, fivehaul from player order by wickets desc limit 20"))
    rows1 = [i for i in cursor1]
    return render_template('topplayers.html', name=name, rows = rows, rows1 = rows1)

@app.route('/squadselect.html', methods=['POST', 'GET'])
def squad(name=None):
    date = "2017-05-05"#datetime.datetime.today().strftime('%Y-%m-%d')
    f=open("current_user.txt","r")
    user_id=f.read()
    f.close()
    error = ""
    cursor.execute(("select name, matches, average, strike_rate, wickets,eco,price from player where team_id in (select team1_id from matches where dates = '{}') or team_id in (select team2_id from matches where dates = '{}');".format(date,date)))
    cursor1.execute(("select budget from users where user_id = {};".format(user_id)))
    b = cursor1.fetchone()
    budget = b[0]
    if request.method == 'POST':
        try:
            name = request.form['send_button']
        except:
            try:
                name1 = request.form['send_button1']
                name = ""
            except:
                name1 = name = ""
                name2 = request.form['send_button2']
        if name:
            name = name[7:]
            cursor1.execute(("select player_id, price from player where name = '{}';".format(name)))
            a = cursor1.fetchone()
            try:
                if budget - int(a[1]) >= 0:
                    cursor1.execute(("insert into userplayer values ('{}', '{}');".format(user_id, a[0])))
                    budget -= int(a[1])
                    cursor1.execute(("update users set budget={} where user_id = {};".format(str(budget), user_id)))
                else:
                    error = "Budget is insufficient"
            except mysql.connector.Error as err:
                if err[0] == 1062:#error number
                    error = "Player already selected"
                else:#1644
                    error = "You can select at the most 10 players"
        elif name1:
            name = name1[7:]
            cursor1.execute(("select player_id, price from player where name = '{}';".format(name)))
            a = cursor1.fetchone()
            add = int(a[1])
            p_id = a[0]
            cursor1.execute(("select * from userplayer where user_id={} and player_id={};".format(user_id, p_id)))
            if cursor1.fetchone():
                cursor1.execute(("delete from userplayer where user_id={} and player_id={};".format(user_id, p_id)))
                budget += add
                cursor1.execute(("update users set budget={} where user_id = {};".format(str(budget), user_id)))
        else:
            if name2 == "Name":
                cursor.execute(("select name, matches, average, strike_rate, wickets, eco, price from player where team_id in (select team1_id from matches where dates = '{}') or team_id in (select team2_id from matches where dates = '{}') order by name ASC".format(date,date)))
            elif name2 == 'Matches':
                cursor.execute(("select name, matches, average, strike_rate, wickets, eco, price from player where team_id in (select team1_id from matches where dates = '{}') or team_id in (select team2_id from matches where dates = '{}') order by matches DESC".format(date,date)))
            elif name2 == 'Average':
                cursor.execute(("select name, matches, average, strike_rate, wickets, eco, price from player where team_id in (select team1_id from matches where dates = '{}') or team_id in (select team2_id from matches where dates = '{}') order by average DESC".format(date,date)))
            elif name2 == 'Strike Rate':
                cursor.execute(("select name, matches, average, strike_rate, wickets, eco, price from player where team_id in (select team1_id from matches where dates = '{}') or team_id in (select team2_id from matches where dates = '{}') order by strike_rate DESC".format(date,date)))
            elif name2 == 'Wickets':
                cursor.execute(("select name, matches, average, strike_rate, wickets, eco, price from player where team_id in (select team1_id from matches where dates = '{}') or team_id in (select team2_id from matches where dates = '{}') order by wickets DESC".format(date,date)))
            elif name2 == 'Economy':
                cursor.execute(("select name, matches, average, strike_rate, wickets, eco, price from player where team_id in (select team1_id from matches where dates = '{}') or team_id in (select team2_id from matches where dates = '{}') order by eco ASC".format(date,date)))
            elif name2 == 'Price':
                cursor.execute(("select name, matches, average, strike_rate, wickets, eco, price from player where team_id in (select team1_id from matches where dates = '{}') or team_id in (select team2_id from matches where dates = '{}') order by price DESC".format(date,date)))
        cursor1.execute(("commit;"))
    rows = [i for i in cursor]
    cursor1.execute(("select name, price from player where player_id in (select player_id from userplayer where user_id= '{}');".format(user_id)))
    rows1 = [j for j in cursor1]
    return render_template('squadselect.html', name=name, rows = rows, rows1 = rows1, error = error, budget = budget)

@app.route('/price.html')
def plist(name=None):
    cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player")
    rows = [i for i in cursor]
    return render_template('price.html', name=name, rows=rows)

@app.route('/price.html', methods=['POST','GET'])
def batlist(name=None):
    if request.form['send_button'] == 'Name':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by name ASC")
    elif request.form['send_button'] == 'Batting Style':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by batstyle DESC")
    elif request.form['send_button'] == 'Matches':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by matches DESC")
    elif request.form['send_button'] == 'Runs':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by runs DESC")
    elif request.form['send_button'] == 'Highest Score':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by highest_score DESC")
    elif request.form['send_button'] == 'Average':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by average DESC")
    elif request.form['send_button'] == 'Strike Rate':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by strike_rate DESC")
    elif request.form['send_button'] == 'Hundreds':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by hundreds DESC")
    elif request.form['send_button'] == 'Fifties':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by fifties DESC")
    elif request.form['send_button'] == 'Fours':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by fours DESC")
    elif request.form['send_button'] == 'Sixes':
        cursor.execute("select name, batstyle, matches, runs, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player order by sixes DESC")
    else:
        cursor.execute("select name, batstyle, matches, run`s, highest_score, average, strike_rate, hundreds, fifties, fours, sixes from player")
    rows = [i for i in cursor]
    return render_template('price.html', name=name, rows=rows)

@app.route('/bowling.html', methods=['POST', 'GET'])
def bowl(name=None):
    if request.method == "POST":
        if request.form['send_button'] == 'Name':
            cursor.execute("select name, matches, wickets, eco, fourhaul,fivehaul from player order by name asc")
        elif request.form['send_button'] == 'Matches':
            cursor.execute("select name, matches, wickets, eco, fourhaul,fivehaul from player order by matches desc")
        elif request.form['send_button'] == 'Wickets':
            cursor.execute("select name, matches, wickets, eco, fourhaul,fivehaul from player order by wickets desc")
        elif request.form['send_button'] == 'Economy':
            cursor.execute("select name, matches, wickets, eco, fourhaul,fivehaul from player order by eco asc")
        elif request.form['send_button'] == '4 Wicket Hauls':
            cursor.execute("select name, matches, wickets, eco, fourhaul,fivehaul from player order by fourhaul desc")
        elif request.form['send_button'] == '5 Wicket Hauls':
            cursor.execute("select name, matches, wickets, eco, fourhaul,fivehaul from player order by fivehaul desc")
    else:
        cursor.execute("select name, matches, wickets, eco, fourhaul, fivehaul, price from player")
    rows = [i for i in cursor]
    return render_template('bowling.html', name=name, rows=rows)

@app.route('/administrator.html')
def ulist(name=None):
    cursor.execute("select * from users;")
    rows = [i for i in cursor]
    return render_template('administrator.html', name=name, rows=rows)

@app.route('/schedule.html')
def sched(name=None):    
    date = datetime.datetime.today().strftime('%Y-%m-%d')

    cursor1.execute("""select team1_id, team2_id, dates, ground_id from matches where dates > '%s';""" % (date))
    ans = []
    new = cursor1.fetchone()
    while new:
        a = []
        team1 = new[0]
        team2 = new[1]
        ground = new[3]
        cursor.execute("""select name from team where team_id = '%d';""" %(team1))
        t = cursor.fetchone()
        a.append(t[0])

        cursor.execute("""select name from team where team_id = '%d';""" %(team2))
        t = cursor.fetchone()
        a.append(t[0])

        a.append(new[2])

        cursor.execute("""select name from ground where ground_id = '%d';""" %(ground))
        t = cursor.fetchone()
        a.append(t[0])
        ans.append(a)
        new = cursor1.fetchone()

    return render_template('schedule.html', name=name, ans=ans)


@app.route('/home.html')
def matchinfo(name=None):
    return render_template('home.html', name=name)

@app.route('/', methods=['POST','GET'])
@app.route('/login.html', methods=['POST','GET'])
def login_page_post(name=None):
    username, password = request.form['username'],request.form['password']
    cursor.execute(("select password, user_id from users where username ='{}';".format(username)))
    a = cursor.fetchone()
    if not a:
        return render_template('login.html', name=name,error1="Incorrect username",error2="")
    if a[0] == password:
        f=open("current_user.txt","w")
        f.write(str(a[1]))
        f.close()
        return render_template('home.html', name=name)
    else:
        return  render_template('login.html', name=name,error2="Incorrect Password",error1="")

@app.route('/registration.html')
def registration_page(name=None):
    return render_template('registration.html', name=name)


@app.route('/registration.html', methods=['POST','GET'])
def registration_page_post(name=None):
    firstname = request.form['firstname']
    if not firstname:
        return  render_template('registration.html', name=name,error="Enter firstname")
    lastname = request.form['lastname']
    if not lastname:
        return  render_template('registration.html', name=name,error="Enter lastname")
    username = request.form['username']
    if not username:
        return  render_template('registration.html', name=name,error="Enter username")
    email = request.form['emailid']
    if not email:
        return  render_template('registration.html', name=name,error="Enter email-id")
    favteam = request.form['favouriteteam']
    if not favteam:
        return  render_template('registration.html', name=name,error="Enter name of your favourite team")
    password = request.form['password']
    if not password:
        return  render_template('registration.html', name=name,error="Password not entered")
    cpassword = request.form['cpassword']
    if password != cpassword:
        return  render_template('registration.html', name=name,error="Passwords do not match")
    cursor.execute(("select password from users where username ='{}';".format(username)))
    a = cursor.fetchone()
    if not a:
        cursor.execute(("insert into users(username, password,firstname,lastname, email, favteam, budget) values('{}', '{}', '{}', '{}', '{}', '{}', 1300000);".format(username, password,firstname,lastname, email, favteam)))
        cursor.execute(("select user_id from users where username ='{}';".format(username)))
        a = cursor.fetchone()
        f=open("current_user.txt","w")
        f.write(str(a[0]))
        f.close()
        cursor.execute(("delimiter //"))
        cursor.execute(("""create trigger t{} before insert on userplayer for each row begin if (select count(player_id) from userplayer where user_id = {} group by user_id) > 9 then signal sqlstate "10000" set message_text = 'no';end if; end//""".format(str(a[0]),str(a[0]))))
        cursor.execute(("delimiter ;"))
        cursor.execute(("commit;"))
        return render_template('home.html', name=name)
    else:
        return  render_template('registration.html', name=name,error="Username is already taken!")

@app.route('/creategroup.html')
def create_group_page(name=None):
    f=open("current_user.txt","r")
    user_id=f.read()
    f.close()
    if not user_id:
        return render_template('login.html', name=name)
    return render_template('creategroup.html', name=name)

@app.route('/creategroup.html', methods=['POST','GET'])
def create_group(name=None):
    grpname = request.form['grpname']
    cursor.execute(("select group_id from groups where groupname='{}';".format(grpname)))
    a = cursor.fetchone()
    if a:
        return render_template('creategroup.html', name=name,error="Group name is already taken!")
    cursor.execute(("insert into groups(groupname) values('{}');".format(grpname)))
    cursor.execute(("commit;"))
    cursor.execute(("select group_id from groups where groupname='{}';".format(grpname)))
    a = cursor.fetchone()
    group_id = a[0]
    f=open("current_user.txt","r")
    user_id=f.read()
    f.close()
    cursor.execute(("insert into user_group(user_id, group_id) values('{}','{}');".format(user_id, group_id)))
    cursor.execute(("commit;"))
    return render_template('addtogroup.html', name=name)

@app.route('/addtogroup.html')
def addto_group_page(name=None):
    f=open("current_user.txt","r")
    user_id=f.read()
    f.close()
    if not user_id:
        return render_template('login.html', name=name)
    return render_template('addtogroup.html', name=name)

@app.route('/addtogroup.html', methods=['POST','GET'])
def addto_group(name=None):
    username = request.form['username']
    grpname="sdf"#get it from html page
    cursor.execute(("select user_id from users where username ='{}';".format(username)))
    a = cursor.fetchone()
    if not a:
        return render_template('addtogroup.html', name=name,error="Invalid username")
    else:
        uid = a[0]
    cursor.execute(("select group_id from group where groupname='{}';".format(grpname)))
    a = cursor.fetchone()
    gid = a[0]
    cursor.execute(("select * from user_group where (user_id='{}' and group_id='{}');".format(uid,gid)))
    a = cursor.fetchone()
    if not a:
        return render_template('addtogroup.html', name=name,error="User is already part of group!")
    cursor.execute(("insert into user_group values('{}','{}');".format(uid,gid)))
    cursor.execute(("commit;"))
    return render_template('addtogroup.html', name=name)

@app.route('/teamvsteam.html', methods=['POST','GET'])
def tvst(name=None):
    c = 0
    rows = []
    t1 = t2 = ""
    if request.method == 'POST':
        t1 = request.form['t1']
        t2 = request.form['t2']
        cursor.execute(("select team_id from team where name='{}'".format(t1)))
        a = cursor.fetchone()
        t1i = a[0]
        cursor.execute(("select team_id from team where name='{}'".format(t2)))
        a = cursor.fetchone()
        t2i = a[0]
        cursor.execute(("select match_id from matches where ((team1_id={} and team2_id={}) or (team1_id={} and team2_id={}))".format(t1i, t2i, t2i, t1i)))
        cur = cursor.fetchall()
        print(cur)
        for i in cur:
            cursor.execute(("select * from match_team_performance where match_id = {}".format(int(i[0]))))
            row = [j for j in cursor]
            rows.append(row)
            c += 1
    return render_template('teamvsteam.html', name=name, rows = rows, count = c, name1 = t1, name2 = t2)

@app.route('/playerground.html', methods=['POST','GET'])
def playerground(name=None):
    name = p1= c1 =""
    bat = bowl = []
    if request.method == 'POST':
        p1 = request.form['p1']
        c1 = request.form['c1']
        cursor.execute(("select ground_id from ground where city='{}'".format(c1)))
        a = cursor.fetchone()
        gid = a[0]
        cursor.execute(("select player_id from player where name='{}'".format(p1)))
        a = cursor.fetchone()
        pid = a[0]
        cursor.execute(("select * from match_player_bat where player_id={} and match_id in (select match_id from matches where ground_id = {})".format(pid, gid)))
        bat = [i for i in cursor]
        cursor.execute(("select * from match_player_bowl where player_id={} and match_id in (select match_id from matches where ground_id = {})".format(pid, gid)))
        bowl = [i for i in cursor]
    return render_template('playerground.html', name=name, bat = bat, bowl = bowl, nam = p1)

@app.route('/playerteam.html', methods=['POST','GET'])
def playerteam(name=None):
    name = p1= t1 =""
    bat = bowl = []
    if request.method == 'POST':
        p1 = request.form['p1']
        t1 = request.form['t1']
        cursor.execute(("select team_id from team where name='{}'".format(t1)))
        a = cursor.fetchone()
        tid = a[0]
        cursor.execute(("select player_id from player where name='{}'".format(p1)))
        a = cursor.fetchone()
        pid = a[0]
        cursor.execute(("select * from match_player_bat where player_id={} and match_id in (select match_id from matches where team1_id = {} or team2_id = {})".format(pid, tid, tid)))
        bat = [i for i in cursor]
        cursor.execute(("select * from match_player_bowl where player_id={} and match_id in (select match_id from matches where team1_id = {} or team2_id = {})".format(pid, tid, tid)))
        bowl = [i for i in cursor]
    return render_template('playerteam.html', name=name, bat = bat, bowl = bowl, pname = p1)
