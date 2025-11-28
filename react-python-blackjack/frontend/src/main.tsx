import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import App from "./App";
import { store } from "./store";
import "./styles/global.scss";

const darkTheme = createTheme({
    palette: {
        mode: "dark",
        primary: {
            main: "#4ecdc4",
        },
        secondary: {
            main: "#9b59b6",
        },
        background: {
            default: "#0f0f1e",
            paper: "#16213e",
        },
    },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
        <Provider store={store}>
            <ThemeProvider theme={darkTheme}>
                <CssBaseline />
                <App/>
            </ThemeProvider>
        </Provider>
    </React.StrictMode>
);