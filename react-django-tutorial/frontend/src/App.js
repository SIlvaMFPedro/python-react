// import logo from './logo.svg';
// import './App.css';
//
// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }
//
// export default App;

import axios from "axios";
import React from "react";
import Hello from "./components/Hello";
import Example from "./components/Counter";

// class App extends React.Component {
//   render() {
//     return(
//         <div>
//           <Hello name="Pedro"/>
//           <Example/>
//         </div>
//     );
//   }
// }

class App extends React.Component {
    state = {details: [], }

    componentDidMount() {
        let data;
        axios.get('http://localhost:8000').then(res => {data = res.data; this.setState({details: data});})
            .catch(err => {})
    }

    render(){
        return (
            <div>
                <header>Data Generated from Django</header>
                <hr></hr>
                {this.state.details.map((output, id) => (
                    <div key={id}>
                        <div>
                            <h2>{output.employee}</h2>
                            <h3>{output.department}</h3>
                        </div>
                    </div>
                ))}
            </div>
        )
    }
}

export default App;