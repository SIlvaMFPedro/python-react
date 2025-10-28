import { useState, useEffect } from "react";

function App() {
  const [todos, setTodos] = useState([]);
  const [newTask, setNewTask] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/todos")
        .then((res) => res.json())
        .then(setTodos);
  }, []);

  const addTodo = () => {
    fetch("http://127.0.0.1:5000/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task: newTask }),
    })
        .then((res) => res.json())
        .then((todo) => setTodos([...todos, todo]));

    setNewTask("");
  };

  const deleteTodo = (id) => {
    fetch(`http://127.0.0.1:5000/api/todos/${id}`, { method: "DELETE" })
        .then(() => setTodos(todos.filter((t) => t.id !== id)));
  };

  return (
      <div style={{ margin: "2rem" }}>
        <h1>📝 To-Do List</h1>

        <input
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="New task"
        />
        <button onClick={addTodo}>Add</button>

        <ul>
          {todos.map((t) => (
              <li key={t.id}>
                {t.task}
                <button onClick={() => deleteTodo(t.id)}>❌</button>
              </li>
          ))}
        </ul>
      </div>
  );
}

export default App;
