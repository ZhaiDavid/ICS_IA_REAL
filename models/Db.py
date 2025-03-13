from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_completed = db.Table('user_completed', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
)
user_starred = db.Table('user_starred', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
)
user_scored = db.Table('user_scored', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('contest_result_id', db.Integer, db.ForeignKey('contest_result.id'))
)
user_attempted = db.Table('user_attempted', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
)
user_done_in_contest = db.Table('user_done_in_contest', 
     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('contest_question_data_id', db.Integer, db.ForeignKey('contest_question_data.id'))
)

contest_key_question = db.Table('contest_key_question', 
    db.Column('contest_key_id', db.Integer, db.ForeignKey('contest_key.id')),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
)

contest_type_contest_result = db.Table('contest_type_contest_result',
    db.Column('contest_type_id', db.Integer, db.ForeignKey('contest_type.id')),
    db.Column('contest_result_id', db.Integer, db.ForeignKey('contest_result.id'))
)
contest_type_contest_key = db.Table('contest_type_contest_key',
    db.Column('contest_type_id', db.Integer, db.ForeignKey('contest_type.id')),
    db.Column('contest_key_id', db.Integer, db.ForeignKey('contest_key.id'))
)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0) 
    contestEndTime = db.Column(db.Integer, default=0)
    doingContest = db.Column(db.Boolean, default=False)
    curContestNum = db.Column(db.Integer, default=0)
    completed = db.relationship('Question', secondary = user_completed, backref = 'completer')
    starred = db.relationship('Question', secondary = user_starred, backref = 'starrer')
    scored = db.relationship('Contest_result', secondary = user_scored, backref = 'scorer')
    attempted = db.relationship('Question', secondary = user_attempted, backref='attempter')
    done_in_contest = db.relationship('Contest_question_data', secondary = user_done_in_contest, backref='contest_doer')


    def __repr__(self):
        return f'<User {self.username}>'
    

class Question(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(50), unique = True, nullable=False)
     filename = db.Column(db.String(50), unique = True, nullable=False)
     answer = db.Column(db.String(50), unique = False, nullable=False)

     def __repr__(self):
        return f'<Question {self.filename}>'
     def setCompleted(self, userId):
         user = User.query.get(userId)
         user.completed.append(self)
     def isCompleted(self, userId):
         user = User.query.get(userId)
         return self in user.completed
     def setStarred (self, userId):
         user = User.query.get(userId)
         if not self.isStarred(userId):
            user.starred.append(self)
         else:
            user.starred.remove(self)
     def isStarred (self, userId):
         user = User.query.get(userId)
         return self in user.starred
     def setAttempted (self, userId):
         user = User.query.get(userId)
         user.attempted.append(self)
     def isAttempted (self, userId):
         user = User.query.get(userId)
         return self in user.attempted

class Contest_key(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     key = db.Column(db.String(50), unique = True, nullable=False)
     questions = db.relationship('Question', secondary = contest_key_question)

class Contest_result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique = False, nullable=False)
    result = db.Column(db.Integer, default=0)
    time = db.Column(db.Integer, default=0)
    def addTo (self, userId):
        user = User.query.get(userId)
        user.scored.append(self)
        
class Contest_question_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, unique =False, nullable=False)
    contestNumber = db.Column(db.Integer, unique = False, nullable=False)
    user_answer = db.Column(db.String(255), nullable=True)


class Contest_type(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(50), unique = True, nullable=False)
     results = db.relationship('Contest_result', secondary = contest_type_contest_result, backref = 'type')
     contests = db.relationship('Contest_key', secondary = contest_type_contest_key, backref='type')
   











   
    