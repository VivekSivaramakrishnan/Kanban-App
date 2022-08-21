from flask_login import *
from flask import jsonify, request, send_file
from password import hasher
from flask_restful import Api, Resource, abort
from datetime import datetime
import pandas as pd
from io import BytesIO
from app import app, db
from models import *
import jwt
from api_token_auth import token_required

api = Api(app)

class LoginAPI(Resource):

    def post(self):

        username = request.json['username']
        password = request.json['password']

        if username is None:
            return abort(400, message='Username not provided.')

        if password is None:
            return abort(400, message='Password not provided.')

        user = db.session.query(User).get(username)

        if not user:
            return abort(401, message='Username does not exist.')

        if user.password != hasher(username, password):
            return abort(401, message='Wrong password')

        # Login credentials verified. Return log in token now
        token = jwt.encode({'user':username}, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'message':f'Welcome to the kanban app, {username}.', 'api_key':token})


class ListAPI(Resource):

    @token_required
    def get(self, current_user=''):

        user = db.session.query(User).get(current_user.username)
        result = {'message':f'Lists for {current_user.username}', 'lists':[]}

        for list in user.lists:
            list_result = {'id':list.id, 'name':list.name, 'description':list.description, 'tasks':[]}
            for task in list.tasks:
                list_result['tasks'].append({'title':task.title, 'content':task.content, 'deadline':task.deadline, 'status':task.status, 'created':task.created, 'updated':task.updated})
            result['lists'].append(list_result)

        return jsonify(result)

    @token_required
    def post(self, current_user=''):

        if len(current_user.lists) == 5:
            return abort(400, message='Cannot add: 5 is the maximum number of lists for a user')

        data = request.json
        list = List(name=data['name'],
                    description=data['description'],
                    username=current_user.username)
        db.session.add(list)
        db.session.commit()

        return jsonify({'message':f'successfully created list! List id: {list.id}'})

    @token_required
    def put(self, current_user=''):

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

    @token_required
    def delete(self, current_user=''):
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

    @token_required
    def get(self, list_id, current_user=''):

        list = db.session.query(List).get(list_id)

        if not list:
            return abort(400, message="List ID does not exist")

        if list.username != current_user.username:
            return abort(400, message='Specified list id does not come under login scope')

        result = {'id':list.id, 'name':list.name, 'description':list.description, 'tasks':[]}
        for task in list.tasks:
            result['tasks'].append({'title':task.title, 'content':task.content, 'deadline':task.deadline, 'status':task.status, 'created':task.created, 'updated':task.updated})

        return jsonify(result)

    @token_required
    def post(self, list_id, current_user=''):

        list = db.session.query(List).get(list_id)

        if not list:
            return abort(400, message="List ID does not exist")

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

    @token_required
    def put(self, list_id, current_user=''):

        data = request.json

        try:
            deadline = datetime.date(datetime.strptime(data['deadline'], '%d/%m/%Y'))
        except:
            return abort(400, message='Deadline format incorrect. Try DD/MM/YYYY')

        if deadline < datetime.date(datetime.now()) and not data['status']:
            return abort(400, message='Deadline cannot be earlier than today if incomplete!')

        task = db.session.query(Task).get((data['title'], list_id))
        list = db.session.query(List).get(list_id)

        if not list:
            return abort(400, message="List ID does not exist")

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

    def delete(self, list_id):

        data = request.json

        task = db.session.query(Task).get((data['title'], list_id))
        list = db.session.query(List).get(list_id)

        if not list:
            return abort(400, message="List ID does not exist")

        if list.username != current_user.username:
            return abort(400, message='Specified task does not come under login scope')

        if not task:
            return abort(400, message="Task not found")

        db.session.delete(task)
        db.session.commit()

        return jsonify({'message':'Successfully deleted task!'})

class StatsAPI(Resource):

    @token_required
    def get(self, current_user=''):

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        table = []

        for list in current_user.lists:
            c_task, ic_task, p_task = 0, 0, 0
            for task in list.tasks:
                if task.status:
                    c_task += 1
                elif task.deadline <= datetime.date(datetime.now()):
                    ic_task += 1
                else:
                    p_task += 1

            table.append([list.id, list.name, c_task, ic_task, p_task])

        df = pd.DataFrame(table, columns=['List ID', 'Name', 'Completed Tasks', 'Incomplete Tasks', 'Pending tasks'])
        df.to_excel(writer, startrow = 0, merge_cells = False, sheet_name = f"{current_user.username}")
        writer.close()

        output.seek(0)

        return send_file(output, mimetype="application/msexcel", attachment_filename=f"{current_user.username}_list_stats.xlsx", as_attachment=True)


api.add_resource(LoginAPI, '/api/login')
api.add_resource(ListAPI, '/api/list')
api.add_resource(TaskAPI, '/api/task/<int:list_id>')
api.add_resource(StatsAPI, '/api/stats')
