from settings import app, db
from models import *
from flask_login import *
from flask import jsonify, request, send_from_directory
from password import hasher
from flask_restful import Resource, Api, abort
from datetime import datetime

api = Api(app)

class LoginAPI(Resource):

    def post(self):

        username = request.json['username']
        password = request.json['password']

        if username is None:
            return abort(400, message='Username not provided.', sample='/api/login?username=test&password=qq')

        if password is None:
            return abort(400, message='Password not provided.', sample='/api/login?username=test&password=qq')

        user = db.session.query(User).get(username)

        if not user:
            return abort(401, message='Username does not exist.')

        if user.password != hasher(username, password):
            return abort(401, message='Wrong password')

        # Login credentials verified. Log in user now.
        login_user(user)

        return jsonify({'message':f'Welcome to the kanban app, {username}. You have been logged in successfully!'})

class LogoutAPI(Resource):

    @login_required
    def get(self):
        logout_user()
        return jsonify({'message':'Logged out successfully'})

class ListAPI(Resource):

    @login_required
    def get(self):

        user = db.session.query(User).get(current_user.username)
        result = {'message':f'Lists for {current_user.username}', 'lists':[]}

        for list in user.lists:
            list_result = {'id':list.id, 'name':list.name, 'description':list.description, 'tasks':[]}
            for task in list.tasks:
                list_result['tasks'].append({'title':task.title, 'content':task.content, 'deadline':task.deadline, 'status':task.status, 'created':task.created, 'updated':task.updated})
            result['lists'].append(list_result)

        return jsonify(result)

    @login_required
    def post(self):

        if len(current_user.lists) == 5:
            return abort(400, 'Cannot add: 5 is the maximum number of lists for a user')

        data = request.json
        list = List(name=data['name'],
                    description=data['description'],
                    username=current_user.username)
        db.session.add(list)
        db.session.commit()

        return jsonify({'message':f'successfully created list! List id: {list.id}'})

    @login_required
    def put(self):

        data = request.json

        list = db.session.query(List).get(data['id'])

        if not list:
            return abort(400, message="List ID does not exist")

        if list.username != current_user.username:
            return abort(400, message='Specified list does not come under login scope')

        list.name = data['name']
        list.description = data['description']

        db.session.add(list)
        db.session.commit()

        return jsonify({'message':f'successfully updated {list.name}.'})

    @login_required
    def delete(self):
        data = request.json

        list = db.session.query(List).get(data['id'])

        if not list:
            return abort(400, message="List ID does not exist")

        if list.username != current_user.username:
            return abort(400, message='Specified list does not come under login scope')

        db.session.delete(list)
        db.session.commit()

        return jsonify({'message':f'successfully deleted {list.name}.'})

class TaskAPI(Resource):

    @login_required
    def get(self, list_id):

        list = db.session.query(List).get(list_id)

        if list.username != current_user.username:
            return abort(400, message='Specified task does not come under login scope')

        result = {'id':list.id, 'name':list.name, 'description':list.description, 'tasks':[]}
        for task in list.tasks:
            result['tasks'].append({'title':task.title, 'content':task.content, 'deadline':task.deadline, 'status':task.status, 'created':task.created, 'updated':task.updated})

        return jsonify(result)

    @login_required
    def post(self, list_id):

        list = db.session.query(List).get(list_id)

        if list.username != current_user.username:
            return abort(400, message='Specified task does not come under login scope')

        data = request.json

        try:
            deadline = datetime.date(datetime.strptime(data['deadline'], '%d/%m/%Y'))
        except:
            return abort(400, message='Deadline format incorrect. Try DD/MM/YYYY')

        if deadline < datetime.date(datetime.now()) and not data['status']:
            return abort(400, message='Deadline cannot be earlier than today if incomplete!')

        task = db.session.query(Task).get((data['title'], list_id))
        if task:
            return abort(400, message='Task name already taken')

        task = Task(title = data['title'],
                    content = data['content'],
                    deadline = deadline,
                    status = data['status'],
                    created = datetime.now(),
                    updated = datetime.now(),
                    list_id = list_id)
        db.session.add(task)
        db.session.commit()

        return jsonify({'message':'Successfully added task!'})

    @login_required
    def put(self, list_id):

        data = request.json

        try:
            deadline = datetime.date(datetime.strptime(data['deadline'], '%d/%m/%Y'))
        except:
            return abort(400, message='Deadline format incorrect. Try DD/MM/YYYY')

        if deadline < datetime.date(datetime.now()) and not data['status']:
            return abort(400, message='Deadline cannot be earlier than today if incomplete!')

        task = db.session.query(Task).get((data['title'], list_id))
        list = db.session.query(List).get(list_id)

        if list.username != current_user.username:
            return abort(400, message='Specified task does not come under login scope')

        if not task:
            return abort(400, message="Task not found")

        task.title = data['title']
        task.content = data['content']
        task.deadline = deadline
        task.status = data['status']
        task.updated = datetime.now()
        task.list_id = list_id

        db.session.commit()

        return jsonify({'message':'Successfully updated task!'})

class StatsAPI(Resource):

    @login_required
    def get(self):

        with open(f'generated_reports/{current_user.username}_list_stats.csv', 'w', encoding="utf-8") as f:
            f.write('List ID, Name, Completed Tasks, Incomplete Tasks, Pending tasks\n')

            for list in current_user.lists:
                c_task, ic_task, p_task = 0, 0, 0
                for task in list.tasks:
                    if task.status:
                        c_task += 1
                    elif task.deadline <= datetime.date(datetime.now()):
                        ic_task += 1
                    else:
                        p_task += 1

                f.write(', '.join([str(i) for i in [list.id, list.name, c_task, ic_task, p_task]]))
                f.write('\n')

        return send_from_directory('generated_reports', f'{current_user.username}_list_stats.csv', as_attachment=True)


api.add_resource(LoginAPI, '/api/login')
api.add_resource(LogoutAPI, '/api/logout')
api.add_resource(ListAPI, '/api/list')
api.add_resource(TaskAPI, '/api/task/<int:list_id>')
api.add_resource(StatsAPI, '/api/stats')
