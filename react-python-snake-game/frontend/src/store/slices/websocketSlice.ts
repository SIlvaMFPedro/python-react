import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../index.ts";
import type {WebSocketMessage} from "../../utils/utils.ts";

interface WebSocketState {
    isConnected: boolean;
    connectionError: string | null;
    lastMessage: WebSocketMessage | null;
    connection: WebSocket | null;
}

const initialState: WebSocketState = {
    isConnected: false,
    connectionError: null,
    lastMessage: null,
    connection: null,
};

export const websocketSlice = createSlice({
    name: 'websocket',
    initialState,
    reducers: {
        setConnected: (state, action: PayloadAction<boolean>) => {
            state.isConnected = action.payload;
            if (action.payload) {
                state.connectionError = null;
            }
        },
        setConnectionError: (state, action: PayloadAction<string>) => {
            state.connectionError = action.payload;
            state.isConnected = false;
        },
        setLastMessage: (state, action: PayloadAction<WebSocketMessage>) => {
            state.lastMessage = action.payload;
        },
        setConnection: (state, action: PayloadAction<WebSocket | null>) => {
            state.connection = action.payload;
        },
        clearConnection: (state) => {
            state.connection = null;
            state.isConnected = false;
            state.connectionError = null;
        },
    },
});

// Actions
export const {
    setConnected,
    setConnectionError,
    setLastMessage,
    setConnection,
    clearConnection,
} = websocketSlice.actions;

// Selectors
export const selectIsConnected = (state: RootState) => state.websocket.isConnected;
export const selectConnectionError = (state: RootState) => state.websocket.connectionError;
export const selectLastMessage = (state: RootState) => state.websocket.lastMessage;
export const selectConnection = (state: RootState) => state.websocket.connection;

// Reducer
export default websocketSlice.reducer;