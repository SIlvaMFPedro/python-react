import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../index';
import type { Position, Direction, GameState } from '../../utils/utils';

interface GameStateSlice {
    snake: Position[];
    food: Position;
    score: number;
    moves: number;
    gameOver: boolean;
    direction: Direction;
    gridSize: number;
}

const initialState: GameStateSlice = {
    snake: [],
    food: [0, 0],
    score: 0,
    moves: 0,
    gameOver: false,
    direction: 'up',
    gridSize: 20,
};

export const gameSlice = createSlice({
    name: 'game',
    initialState,
    reducers: {
        updateGameState: (state, action: PayloadAction<GameState>) => {
            state.snake = action.payload.snake;
            state.food = action.payload.food;
            state.score = action.payload.score;
            state.moves = action.payload.moves;
            state.gameOver = action.payload.game_over;
            state.direction = action.payload.direction;
            state.gridSize = action.payload.grid_size;
        },
        resetGame: (state) => {
            state.snake = [];
            state.food = [0, 0];
            state.score = 0;
            state.moves = 0;
            state.gameOver = false;
            state.direction = 'up';
        },
        setDirection: (state, action: PayloadAction<Direction>) => {
            state.direction = action.payload;
        },
        incrementScore: (state, action: PayloadAction<number>) => {
            state.score += action.payload;
        },
    },
});

// Actions
export const { updateGameState, resetGame, setDirection, incrementScore } = gameSlice.actions;

// Selectors
export const selectGameState = (state: RootState) => state.game;
export const selectScore = (state: RootState) => state.game.score;
export const selectGameOver = (state: RootState) => state.game.gameOver;
export const selectSnake = (state: RootState) => state.game.snake;
export const selectFood = (state: RootState) => state.game.food;
export const selectMoves = (state: RootState) => state.game.moves;

// Reducer
export default gameSlice.reducer;