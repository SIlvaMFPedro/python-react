// frontend/src/store/slices/blackjackSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from '../index';
import type {GameState, Hand, GamePhase} from "../../utils/utils";

interface BlackjackState {
    playerHands: Hand[];
    dealerHand: Hand | null;
    currentHandIndex: number;
    gamePhase: GamePhase;
    playerChips: number;
    currentBet: number;
    insuranceBet: number;
    deckRemaining: number;
    lastError: string | null;
    lastMessage: string | null;
    startingChips: number;
    sessionProfit: number;
    handsPlayed: number;
    handsWon: number;
    handsLost: number;
}

const initialState: BlackjackState = {
    playerHands: [],
    dealerHand: null,
    currentHandIndex: 0,
    gamePhase: 'betting',
    playerChips: 1000,
    currentBet: 0,
    insuranceBet: 0,
    deckRemaining: 312, // 6 decks
    lastError: null,
    lastMessage: null,
    startingChips: 1000,
    sessionProfit: 0,
    handsPlayed: 0,
    handsWon: 0,
    handsLost: 0,
};

export const blackjackSlice = createSlice({
    name: 'blackjack',
    initialState,
    reducers: {
        updateGameState: (state, action: PayloadAction<GameState>) => {
            const previousChips = state.playerChips;
            const previousPhase = state.gamePhase;

            state.playerHands = action.payload.player_hands;
            state.dealerHand = action.payload.dealer_hand;
            state.currentHandIndex = action.payload.current_hand_index;
            state.gamePhase = action.payload.game_phase;
            state.playerChips = action.payload.player_chips;
            state.currentBet = action.payload.current_bet;
            state.insuranceBet = action.payload.insurance_bet;
            state.deckRemaining = action.payload.deck_remaining;
            state.lastError = null;

            // Update session stats when you finish your hand
            if (previousPhase !== 'finished' && action.payload.game_phase === 'finished') {
                state.handsPlayed += 1;
                const chipDifference = state.playerChips - previousChips;
                if (chipDifference > 0) {
                    state.handsWon += 1;
                }
                else if (chipDifference < 0) {
                    state.handsLost += 1;
                }
            }

            // Calculate current session profit
            state.sessionProfit = state.playerChips - state.startingChips;
        },
        setError: (state, action: PayloadAction<string>) => {
            state.lastError = action.payload;
        },
        setMessage: (state, action: PayloadAction<string>) => {
            state.lastMessage = action.payload;
        },
        clearError: (state) => {
            state.lastError = null;
        },
        clearMessage: (state) => {
            state.lastMessage = null;
        },
        resetGame: (state) => {
            state.playerHands = [];
            state.dealerHand = null;
            state.currentHandIndex = 0;
            state.gamePhase = 'betting';
            state.currentBet = 0;
            state.insuranceBet = 0;
        },
        resetSession: (state) => {
            state.startingChips = state.playerChips;
            state.sessionProfit = 0;
            state.handsPlayed = 0;
            state.handsWon = 0;
            state.handsLost = 0;
        },
    },
});

// Actions
export const {
    updateGameState,
    setError,
    setMessage,
    clearError,
    clearMessage,
    resetGame,
    resetSession,
} = blackjackSlice.actions;

// Selectors
export const selectPlayerHands = (state: RootState) => state.blackjack.playerHands;
export const selectDealerHand = (state: RootState) => state.blackjack.dealerHand;
export const selectCurrentHandIndex = (state: RootState) => state.blackjack.currentHandIndex;
export const selectCurrentHand = (state: RootState) =>
    state.blackjack.playerHands[state.blackjack.currentHandIndex];
export const selectGamePhase = (state: RootState) => state.blackjack.gamePhase;
export const selectPlayerChips = (state: RootState) => state.blackjack.playerChips;
export const selectCurrentBet = (state: RootState) => state.blackjack.currentBet;
export const selectInsuranceBet = (state: RootState) => state.blackjack.insuranceBet;
export const selectDeckRemaining = (state: RootState) => state.blackjack.deckRemaining;
export const selectLastError = (state: RootState) => state.blackjack.lastError;
export const selectLastMessage = (state: RootState) => state.blackjack.lastMessage;
export const selectSessionProfit = (state: RootState) => state.blackjack.sessionProfit;
export const selectHandsPlayed = (state: RootState) => state.blackjack.handsPlayed;
export const selectHandsWon = (state: RootState) => state.blackjack.handsWon;
export const selectHandsLost = (state: RootState) => state.blackjack.handsLost;
export const selectStartingChips = (state: RootState) => state.blackjack.startingChips;

// Computed selectors
export const selectCanBet = (state: RootState) =>
    state.blackjack.gamePhase === 'betting' && state.blackjack.playerChips > 0;

export const selectCanHit = (state: RootState) => {
    const phase = state.blackjack.gamePhase;
    const currentHand = state.blackjack.playerHands[state.blackjack.currentHandIndex];
    return phase === 'playing' && currentHand && !currentHand.is_bust && !currentHand.is_blackjack;
};

export const selectCanStand = (state: RootState) =>
    state.blackjack.gamePhase === 'playing';

export const selectCanDouble = (state: RootState) => {
    const phase = state.blackjack.gamePhase;
    const currentHand = state.blackjack.playerHands[state.blackjack.currentHandIndex];
    const chips = state.blackjack.playerChips;
    return phase === 'playing' && currentHand && currentHand.can_double && chips >= currentHand.bet;
};

export const selectCanSplit = (state: RootState) => {
    const phase = state.blackjack.gamePhase;
    const currentHand = state.blackjack.playerHands[state.blackjack.currentHandIndex];
    const chips = state.blackjack.playerChips;
    return phase === 'playing' && currentHand && currentHand.can_split && chips >= currentHand.bet;
};

export const selectCanSurrender = (state: RootState) => {
    const phase = state.blackjack.gamePhase;
    const currentHand = state.blackjack.playerHands[state.blackjack.currentHandIndex];
    return phase === 'playing' && currentHand && currentHand.cards.length === 2 && state.blackjack.currentHandIndex === 0;
};

export const selectCanInsure = (state: RootState) => {
    const phase = state.blackjack.gamePhase;
    const dealerHand = state.blackjack.dealerHand;
    const chips = state.blackjack.playerChips;
    const bet = state.blackjack.currentBet;
    return phase === 'playing' &&
        dealerHand &&
        dealerHand.cards[0]?.rank === 'A' &&
        chips >= bet / 2 &&
        !state.blackjack.insuranceBet;
};

// Reducer
export default blackjackSlice.reducer;