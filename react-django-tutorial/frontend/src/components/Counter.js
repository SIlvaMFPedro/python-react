import React, {useState} from "react";

// Function syntax [to create a component]

function Example(){
    // Declare a new state variable
    const [count, setCount] = useState(0);
    return (
        <div>
            <p>You clicked {count} times</p>
            <button onClick={() => setCount(count + 1)}>Click me!</button>
        </div>
    );
}

export default Example;