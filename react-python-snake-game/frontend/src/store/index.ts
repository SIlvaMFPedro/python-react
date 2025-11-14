import { configureStore } from '@reduxjs/toolkit';
import gameReducer from './slices/gameSlice';
import websocketReducer from './slices/websocketSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
    reducer: {
        game: gameReducer,
        websocket: websocketReducer,
        ui: uiReducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                // Ignore these action types for WebSocket instances
                ignoredActions: ['websocket/setConnection'],
                // Ignore these paths in the state
                ignoredPaths: ['websocket.connection'],
            },
        }),
    // devTools: process.env.NODE_ENV !== 'production',
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;