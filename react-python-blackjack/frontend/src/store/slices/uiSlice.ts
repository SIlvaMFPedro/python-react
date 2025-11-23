import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../index.ts";
import type { AIStrategy} from "../../utils/utils.ts";

interface BlackJackUIState {
    aiMode: boolean;
    aiStrategy: AIStrategy;
    aiDescription: string;
    showSettings: boolean;
    showStats: boolean;
    showHelp: boolean;
    soundEnabled: boolean;
    animationSpeed: 'slow' | 'normal' | 'fast';
}

const initialState: BlackJackUIState = {
    aiMode: false,
    aiStrategy: 'basic',
    aiDescription: '',
    showSettings: false,
    showStats: false,
    showHelp: false,
    soundEnabled: true,
    animationSpeed: 'normal',
}

export const blackjackUISlice = createSlice({
    name: 'blackjackUI',
    initialState,
    reducers: {
        setAiMode: (state, action: PayloadAction<boolean>) => {
            state.aiMode = action.payload;
        },
        toggleAiMode: (state) => {
            state.aiMode = !state.aiMode;
        },
        setAiStrategy: (state, action: PayloadAction<AIStrategy>) => {
            state.aiStrategy = action.payload;
        },
        setAiDescription: (state, action: PayloadAction<string>) => {
            state.aiDescription = action.payload;
        },
        setShowSettings: (state, action: PayloadAction<boolean>) => {
            state.showSettings = action.payload;
        },
        setShowStats: (state, action: PayloadAction<boolean>) => {
            state.showStats = action.payload;
        },
        setShowHelp: (state, action: PayloadAction<boolean>) => {
            state.showHelp = action.payload;
        },
        setSoundEnabled: (state, action: PayloadAction<boolean>) => {
            state.soundEnabled = action.payload;
        },
        setAnimationSpeed: (state, action: PayloadAction<'slow' | 'normal' | 'fast'>) => {
            state.animationSpeed = action.payload;
        },
    },
});

// Actions
export const {
    setAiMode,
    toggleAiMode,
    setAiStrategy,
    setAiDescription,
    setShowSettings,
    setShowStats,
    setShowHelp,
    setSoundEnabled,
    setAnimationSpeed,
} = blackjackUISlice.actions;

// Selectors
export const selectAiMode = (state: RootState) => state.blackjackUI.aiMode;
export const selectAiStrategy = (state: RootState) => state.blackjackUI.aiStrategy;
export const selectAiDescription = (state: RootState) => state.blackjackUI.aiDescription;
export const selectShowSettings = (state: RootState) => state.blackjackUI.showSettings;
export const selectShowStats = (state: RootState) => state.blackjackUI.showStats;
export const selectShowHelp = (state: RootState) => state.blackjackUI.showHelp;
export const selectSoundEnabled = (state: RootState) => state.blackjackUI.soundEnabled;
export const selectAnimationSpeed = (state: RootState) => state.blackjackUI.animationSpeed;

// Reducer
export default blackjackUISlice.reducer;