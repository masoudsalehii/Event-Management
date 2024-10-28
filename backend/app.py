from flask import Flask, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_socketio import SocketIO
import datetime
from flask_cors import CORS
import secrets


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)  

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", allow_credentials=True)
socketio.init_app(app, cors_allowed_origins="http://localhost:3000", allow_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/event_backend'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  


socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  



event_joiners = db.Table('event_joiners',
    db.Column('event_id', db.Integer, db.ForeignKey('event.event_id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'
    
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False)  
    password_hash = db.Column(db.String(128), nullable=False)
    created_events_by = db.relationship('Event', backref='organizer', lazy=True)

    def __init__(self, name, role, password):
        if role not in ['Organizer', 'Joiner']:
            raise ValueError("Role must be 'Organizer' or 'Joiner'")
        self.name = name
        self.role = role
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.user_id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True




class Event(db.Model):
    __tablename__ = 'event'

    event_id = db.Column(db.Integer, primary_key=True)
    event_title = db.Column(db.String(100))
    event_location = db.Column(db.String(100))
    event_date = db.Column(db.DateTime, default = datetime.datetime.now )
    event_duration = db.Column(db.Time, nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    joiners = db.relationship('User', secondary=event_joiners, lazy='subquery',
                              backref=db.backref('joined_events', lazy=True))

    
    def __init__(self, event_title, event_location, event_date, event_duration, organizer_id):
        self.event_title = event_title
        self.event_location = event_location
        self.event_date = event_date
        self.event_duration = event_duration
        self.organizer_id = organizer_id



class UserSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'name', 'role')
        

class EventSchema(ma.Schema):
    class Meta:
        fields = ('event_id', 'event_title', 'event_location', 'event_date', 'event_duration','organizer_id','joiners')


user_schema = UserSchema()
users_schema = UserSchema(many=True)  
event_schema = EventSchema()
events_schema = EventSchema(many=True)  


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('name')
    password = request.json.get('password')
    user = User.query.filter_by(name=username).first()

    if user and user.check_password(password):
        login_user(user)  
        user_data = user_schema.dump(user)  
        return jsonify({
            "message": f"User {username} logged in successfully.",
            "user": user_data,  
            "role": user.role   
        })
    else:
        return jsonify({"error": "Invalid credentials"}), 401




@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()  
    events_data = events_schema.dump(events)  

    for event in events_data:
        event['joiners'] = users_schema.dump(event['joiners'])

    return jsonify(events_data)



@app.route('/register', methods=['POST'])
def register():
    name = request.json.get('name')
    role = request.json.get('role')
    password = request.json.get('password')

    if not name or not role or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if role not in ['Organizer', 'Joiner']:
        return jsonify({"error": "Role must be either 'Organizer' or 'Joiner'"}), 400

    existing_user = User.query.filter_by(name=name).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409


    new_user = User(name=name, role=role, password=password)
    print(f"Creating user {name} with role {role} and password {password}")
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"user_id": new_user.user_id}), 201



@app.route('/add_event', methods = ['POST'])
@login_required
def add_events():
    user = current_user

    event_title = request.json['event_title']
    event_location = request.json['event_location']
    event_date = request.json['event_date']
    event_duration = request.json['event_duration']
    organizer_id = request.json['organizer_id']

    event = Event(event_title, event_location, event_date, event_duration, organizer_id)
    if user.role == 'Organizer':
        db.session.add(event)
        db.session.commit()
        socketio.emit('event_added', {
            'event': event_schema.dump(event),
            'message': f"Event {event.event_id} has been successfully added."
            })
        return event_schema.jsonify(event)
    else: 
        return jsonify({"error": "User must be an Organizer"}), 404




@app.route('/join_event/<int:event_id>', methods=['POST'])
def join_event(event_id):
    user = current_user  

    if not user.is_authenticated:
        return jsonify({"error": "User must be logged in to join an event."}), 401

    event = db.session.get(Event, event_id)

    if event and user.role == 'Joiner':
        event.joiners.append(user)
        db.session.commit()
        socketio.emit('joiner_joined', {
            'event_id': event_id,
            'user_id': user.user_id,
            'name': user.name,
            'message': f"User {user.name} joined event {event_id}."
        })
        return jsonify({"message": f"User {user.name} joined event {event_id}."})
    else:
        return jsonify({"error": "Event not found or user is not a Joiner."}), 404




@app.route('/cancel_event/<int:event_id>', methods=['DELETE'])
@login_required
def cancel_event(event_id):
    event = Event.query.get(event_id)
    user = current_user
    if event and user:
        if event.organizer_id == user.user_id:
            db.session.delete(event)
            db.session.commit()
            socketio.emit('event_canceled', {
                'event_id': event_id,
                'message': f"Event {event_id} has been canceled."
            })
            return jsonify({"message": f"Event {event_id} canceled."})
        else:
            return jsonify({"error": "Only the organizer can cancel this event."}), 403
    else:
        return jsonify({"error": "User or event not found"}), 404



@app.route('/leave_event/<int:event_id>', methods=['POST'])
@login_required
def leave_event(event_id):
    event = Event.query.get(event_id)
    user = current_user

    if event and user in event.joiners:
        event.joiners.remove(user)
        db.session.commit()
        socketio.emit('joiner_left', {
            'event_id': event_id,
            'user_id': user.user_id,
            'message': f"User {user.name} left event {event_id}."
        })
        return jsonify({"message": f"User {user.name} left event {event_id}."})
    else:
        return jsonify({"error": "User or event not found"}), 404
    

@app.route('/check_join_status/<int:event_id>', methods=['GET'])
@login_required
def check_join_status(event_id):
    user = current_user
    event = Event.query.get(event_id)

    if event and user in event.joiners:
        return jsonify({"joined": True})
    elif event:
        return jsonify({"joined": False})
    else:
        return jsonify({"error": "Event not found"}), 404



@app.route('/events/<int:event_id>/joiners', methods=['GET'])
@login_required
def get_event_joiners(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    
    joiners = users_schema.dump(event.joiners)  
    return jsonify(joiners)


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "User logged out successfully."})


if __name__ == '__main__':
    socketio.run(app, debug=True)