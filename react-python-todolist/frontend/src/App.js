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

    const toggleComplete = (id, completed) => {
        fetch(`http://127.0.0.1:5000/api/todos/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ completed: !completed }),
        })
            .then((res) => res.json())
            .then((updated) =>
                setTodos(todos.map((t) => (t.id === id ? updated : t)))
            );
    };

    return (
        <div style={{ margin: "2rem" }}>
            <h1>✅ To-Do List</h1>

            <input
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="New task"
            />
            <button onClick={addTodo}>Add</button>

            <ul>
                {todos.map((t) => (
                    <li key={t.id} style={{ margin: "0.5rem 0" }}>
                        <input
                            type="checkbox"
                            checked={t.completed}
                            onChange={() => toggleComplete(t.id, t.completed)}
                        />
                        <span
                            style={{
                                textDecoration: t.completed ? "line-through" : "none",
                                marginLeft: "0.5rem",
                            }}
                        >
              {t.task}
            </span>
                        <button
                            onClick={() => deleteTodo(t.id)}
                            style={{ marginLeft: "1rem" }}
                        >
                            ❌
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default App;
