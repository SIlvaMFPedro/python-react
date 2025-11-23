import { configureStore } from "@reduxjs/toolkit";
import blackjackReducer from './slices/gameSlice';
import blackjackUIReducer from './slices/uiSlice';
import websocketReducer from './slices/webSocketSlice';

export const store = configureStore({
    reducer: {
        blackjack: blackjackReducer,
        blackjackUI: blackjackUIReducer,
        websocket: websocketReducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                // Ignore these actions for WebSocket instances
                ignoredActions: ['websocket/setConnection'],
                // Ignore these paths in the state
                ignoredPaths: ['websocket.connection'],
            },
        }),
    // devTools: process.env.NODE_ENV !== 'production'
});

// Infer the 'RootState' and 'AppDispatch' types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;

