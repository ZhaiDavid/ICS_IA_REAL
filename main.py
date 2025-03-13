from flask import Flask, render_template, request, redirect,  session, jsonify, Response
import os
from pathlib import Path
from models.Db import Contest_question_data, db, User, Question, Contest_result, Contest_key, Contest_type
import time

app = Flask(__name__)


app.secret_key = "secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
with app.app_context():
    db.drop_all()
    db.create_all() 
    for folder in Path("static").iterdir():
        if folder.is_dir():
            existing = Contest_type.query.filter_by(name = folder.name).first()
            type = Contest_type(name=folder.name)
            if not existing:
                db.session.add(type)
                db.session.commit()
            for sub_folder in Path("static/"+folder.name).iterdir():
                prefix = "static/"+folder.name+"/"+sub_folder.name+"/"
                names = []
                fileNames = []
                answers = []

                cKey = sub_folder.name
                existing = Contest_key.query.filter_by(key = cKey).first()
                contest_key = Contest_key(key = cKey)
                if not existing:
                    type.contests.append(contest_key)
                    db.session.add(contest_key)
                    db.session.commit()

                totalNum = 0 
                for image in Path(prefix+"Problems/").iterdir():
                    totalNum+=1

                for i in range (totalNum):
                    fileNames.append(prefix+"Problems/P"+str(1+i)+".png")
                    names.append(sub_folder.name+" P" +str(1+i))

                f = open(prefix+"Answers.txt")
                for x in f:
                    answers.append(x.strip())
                for i in range(len(names)):
                    existing = Question.query.filter_by(filename=fileNames[i]).first()
                    if not existing:
                        question = Question(name = names[i], filename = fileNames[i], answer = answers[i])
                        contest_key.questions.append(question)
                        db.session.add(question)
                        db.session.commit()
             


#ok
@app.route('/', methods=['GET', 'POST'])
def register():
    session['user_id'] = None
    warning = False
    warning2 = False
    warning3 = False
    submitted = False
    success = False
    if request.method == 'POST':
          submitted = True
          username = request.form.get('username')
          password = request.form.get('password')
          confirm = request.form.get('confirm')
          try:
            if (confirm == password and password != '' and username != ''):
                user = User(username = username, password=password) 
                db.session.add(user)
                db.session.commit()
                success=True
          except:
              warning = True
          if username == '' or password == '' or confirm == '':
              warning2 = True
          if confirm != password:
              warning3= True
         
    return render_template('register.html', warn = warning, warn2 = warning2, warn3 = warning3, submitted = submitted, success = success)

#ok
@app.route('/login', methods=['GET', 'POST'])
def login():
    warning = False
    if request.method == 'POST':
          name = request.form.get('username')
          password = request.form.get('password')
          user = User.query.filter_by(username = name).first()
          try:
            if user.password == password:
                session['userId']=user.id 
                return redirect('/practice')
            else:
                warning=True
          except:
              warning = True

    return render_template('login.html', warn = warning)

@app.route('/practice')
def practice():
    user = User.query.get(session['userId'])
    return render_template('practice.html', userId = session['userId'], 
           questions = Question.query.all(), user=user)

@app.route('/attempted')
def attempted():
    user = User.query.get(session['userId'])
    return render_template('attempted.html', user=user, user_id = session['userId'])

@app.route('/starred')
def starred():
    user = User.query.get(session['userId'])
    return render_template('starred.html', user=user, user_id = session['userId'])

@app.route('/search')
def search():
    value = request.args.get("searchbar")
    if value:
        q = Question.query.filter(Question.name.ilike(f"%{value}%")).all()
    else:
        q=Question.query.all()


    return render_template('searchResults.html', user_id = session['userId'], 
           questions = q)

@app.route('/handle_question', methods =['POST'])
def handle_question():
    question_id = request.form.get('question_id')
    q = Question.query.filter_by(filename = question_id).first()
    q.setStarred(session['userId'])
    db.session.commit()
    return Response(status=204)  


@app.route('/handle_choice', methods = ['POST'])
def handle_choice():
    contest = request.form.get('contest')
    year = request.form.get('year')
    session['contest_key']=year+" " + contest
    return redirect('/contest')
    

@app.route('/solve/<string:id>', methods=['GET', 'POST'])
def question(id):
    previous_url = request.referrer
    print (previous_url)
    q = Question.query.get(id)
    if not previous_url or not previous_url.startswith('/solve/<string:id>'):
        right = False
        wrong = False

    if request.method=='POST':
        ans = request.form.get('answer')
        if not q.isAttempted(session['userId']):
            q.setAttempted(session['userId'])
            db.session.commit()
        if not q.isCompleted(session['userId']) and ans == q.answer:
            q.setCompleted(session['userId'])
            db.session.commit()
        if (ans == q.answer):
            right = True
        else:
            wrong = True
       

    return render_template('problem.html', q=q, right = right, wrong = wrong, userId = session['userId'])


@app.route('/contest', methods=['GET', 'POST'])
def contest():
    empty = 0
    correct = 0
   
    contest_key = Contest_key.query.filter_by(key = session['contest_key']).first()
    contestQuestions = contest_key.questions
    user = User.query.get(session['userId'])
    user.curContestNum+=1

    values=[]
    type = contest_key.type[0].name
    f=open('static/' + type +"/" + session['contest_key']+ '/ScoreScheme.txt')
    for x in f:
        values.append(float(x.strip()))

    correctPoints = values[0]
    emptyPoints = values[1]
    totalPoints = values[2]
    contestDuration = values[3]*60

    if not user.doingContest:
        user.doingContest=True
        user.contestEndTime=contestDuration +time.time()
        db.session.commit()
    
    if request.method == 'POST' or (time.time() >= user.contestEndTime and user.doingContest):
         user.doingContest=False
         user.contestEndTime = 0
         for q in contestQuestions:
            ans = request.form.get(q.filename)
            if ans != '' and not q.isAttempted(session['userId']):
                q.setAttempted(session['userId'])

            if ans == q.answer:
                q.setCompleted(session['userId'])
                correct+=1
            elif ans == '':
                empty+=1
   
            
    
            data = Contest_question_data(question_id=q.id, contestNumber = user.curContestNum, user_answer = ans)
            user.done_in_contest.append(data)
            db.session.commit()

         score = correct*correctPoints+empty*emptyPoints
         
         f=open('static/' + type + '/'+  session['contest_key']+ '/Percentile.txt')
         scores=[]
         people=[]
         totalPeople=0
         worse=0

         for x in f:
             a = x.split(' ')
             scores.append(float(a[0]))
             people.append(int(a[1]))
             totalPeople+=int(a[1])

         for i in range (len(scores)):
             s =scores[i]
             if s <= score:
                 worse+=people[i]
        
                 
         res = Contest_result(result = round(100*(worse/totalPeople),2), key = session['contest_key'], time = time.time())
         session['max']=totalPoints
         session['score']=score
         res.addTo(session['userId'])
         contest_key.type[0].results.append(res)
         db.session.commit()
         return redirect('/contestResult')

    return render_template('contest.html', contestQuestions = contestQuestions)

@app.route('/contestResult')
def contestResult():
    user = User.query.get(session['userId'])
    data = []
    for d in user.done_in_contest:
        if d.contestNumber == user.curContestNum:
            data.append(d)
    return render_template('contestResult.html', data = data, Question = Question, score = session['score'], max = session['max'])

@app.route('/contestChoice', methods=['GET', 'POST'])
def contestChoice():
    return render_template('contestChoice.html')




@app.route('/remaining_time')
def remaining_time():
    user = User.query.get(session['userId'])
    seconds_left = int(user.contestEndTime-time.time())
     
        

    return jsonify({'seconds_left': seconds_left})

@app.route('/reload')
def reload():
    user = User.query.get(session['userId'])
    
    if time.time() >= user.contestEndTime and user.doingContest:
        return jsonify({'reload': 'Y'})
    

    return jsonify({'reload': None})





@app.route('/profile')
def profile ():
    user = User.query.get(session['userId'])
    scores = []
    times = []
    keys = []
    if not session.get('graph_contest'):
        session['graph_contest']='--'
    for s in user.scored: 
        type = s.type[0].name
        if type == session['graph_contest']:
            scores.append(s.result)
            times.append(s.time)
            keys.append(s.key)

    return render_template('profile.html', scores = scores, keys = keys, times = times, selected = session['graph_contest'], types = Contest_type.query.all())

@app.route('/handle_graph', methods=['POST'])
def handle_graph():
    contest = request.form.get('contest')
    session['graph_contest']=contest
    return redirect('/profile')


if __name__ == '__main__':
    app.run(debug=True)
