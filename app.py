from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

class ToDoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200))
    day = db.Column(db.String(100))

# db.create_all() #create the database when server is run

todos = {
    1: {'task': 'build an API', 'day': 'Monday'},
}

task_post_args = reqparse.RequestParser()
task_post_args.add_argument('task', type=str, required=True, help='No task provided', location='json')
task_post_args.add_argument('day', type=str, required=True, help='No day provided', location='json')

task_put_args = reqparse.RequestParser()
task_put_args.add_argument('task', type=str, location='json')
task_put_args.add_argument('day', type=str, location='json')

resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'day': fields.String,
}

class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message='Todo {} not found'.format(todo_id))
        return task
        

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        task = ToDoModel.query.filter_by(task=args['task']).first()
        if task:
            abort(409, message='Todo {} already exists'.format(todo_id))
        
        todo = ToDoModel(id=todo_id, task=args['task'], day=args['day'])
        db.session.add(todo)
        db.session.commit()
        return todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message='Todo {} not found'.format(todo_id))
        if args['task']:
            task.task = args['task']
        if args['day']:
            task.day = args['day']
        db.session.commit()
        return task, 200

    #delete a todo item
    def delete(self, todo_id):
        task = ToDoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404, message='Todo {} not found'.format(todo_id))
        db.session.delete(task)
        db.session.commit()
        return '', 204


class ToDoList(Resource):
    def get(self):
        tasks = ToDoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {'task': task.task, 'day': task.day}
        return todos

api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(ToDoList, '/todos')

if __name__ == '__main__':
    app.run(debug=True)
