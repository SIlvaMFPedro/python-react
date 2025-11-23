import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../index.ts";

interface WebSocketState {
    isConnected: boolean;
    connectionError: string | null;
    connection: WebSocket | null;
}

const initialState: WebSocketState = {
    isConnected: false,
    connectionError: null,
    connection: null,
};

export const webSocketSlice = createSlice({
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
    setConnection,
    clearConnection
} = webSocketSlice.actions;

// Selectors
export const selectIsConnected = (state: RootState) => state.websocket.isConnected;
export const selectConnectionError = (state: RootState) => state.websocket.connectionError;
export const selectConnection = (state: RootState) => state.websocket.connection;

// Reducer
export default webSocketSlice.reducer;