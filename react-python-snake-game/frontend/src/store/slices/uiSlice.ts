import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../index';
import type { AIStrategy } from '../../utils/utils';


interface UIState {
    isPlaying: boolean;
    isPaused: boolean;
    aiMode: boolean;
    aiStrategy: AIStrategy;
    showSettings: boolean;
    showLeaderboard: boolean;
    debugMode: boolean;
}

const initialState: UIState = {
    isPlaying: false,
    isPaused: false,
    aiMode: false,
    aiStrategy: 'astar',
    showSettings: false,
    showLeaderboard: false,
    debugMode: false,
};

export const uiSlice = createSlice({
    name: 'ui',
    initialState,
    reducers: {
        setPlaying: (state, action: PayloadAction<boolean>) => {
            state.isPlaying = action.payload;
            if (action.payload) {
                state.isPaused = false;
            }
        },
        setPaused: (state, action: PayloadAction<boolean>) => {
            state.isPaused = action.payload;
        },
        setAiMode: (state, action: PayloadAction<boolean>) => {
            state.aiMode = action.payload;
        },
        setAiStrategy: (state, action: PayloadAction<AIStrategy>) => {
            state.aiStrategy = action.payload;
        },
        toggleAiMode: (state) => {
            state.aiMode = !state.aiMode;
        },
        setShowSettings: (state, action: PayloadAction<boolean>) => {
            state.showSettings = action.payload;
        },
        setShowLeaderboard: (state, action: PayloadAction<boolean>) => {
            state.showLeaderboard = action.payload;
        },
        setDebugMode: (state, action: PayloadAction<boolean>) => {
            state.debugMode = action.payload;
        },
        resetUI: (state) => {
            state.isPlaying = false;
            state.isPaused = false;
            state.aiMode = false;
        },
    },
});

// Actions
export const {
    setPlaying,
    setPaused,
    setAiMode,
    setAiStrategy,
    toggleAiMode,
    setShowSettings,
    setShowLeaderboard,
    setDebugMode,
    resetUI,
} = uiSlice.actions;

// Selectors
export const selectIsPlaying = (state: RootState) => state.ui.isPlaying;
export const selectIsPaused = (state: RootState) => state.ui.isPaused;
export const selectAiMode = (state: RootState) => state.ui.aiMode;
export const selectAiStrategy = (state: RootState) => state.ui.aiStrategy;
export const selectShowSettings = (state: RootState) => state.ui.showSettings;
export const selectShowLeaderboard = (state: RootState) => state.ui.showLeaderboard;
export const selectDebugMode = (state: RootState) => state.ui.debugMode;

// Reducer
export default uiSlice.reducer;
