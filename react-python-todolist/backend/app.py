from crypt import methods

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# In memory "database"
# to_do_list = [{"id": 1, "task": "Learn React + Flask"}]

# Define a Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task
        }

# Create the database tables
with app.app_context():
    db.create_all()

@app.route("/api/todos", methods=["GET"])
def get_todo_list():
    todos_list = Todo.query.all()
    return jsonify([t.to_dict() for t in todos_list])

@app.route("/api/todos", methods=["POST"])
def add_todo():
    data = request.get_json()
    new_todo = Todo(task=data["task"])
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201

@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Todo item not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)

