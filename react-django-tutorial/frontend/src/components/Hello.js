import React, {Component} from "react";

// Function syntax [to create a component]

// function Hello(props){
//     return (
//         <div>
//             <h1>Hello from {props.name} Component!</h1>
//             <button>Click to enter</button>
//         </div>
//     )
// }

// Class syntax : ES6 class based [to create a component]
class Hello extends React.Component {
    render(){
        return (
            <h1>Hello {this.props.name}</h1>
        )
    }
}
export default Hello;