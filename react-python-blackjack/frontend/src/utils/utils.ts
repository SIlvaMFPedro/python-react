// ============================================
//            Constants
// ============================================
export const CHIP_VALUES = [1, 5, 25, 100, 500] as const;
export const CARD_COLORS = { red: ['♥', '♦'], black: ['♣', '♠']} as const;  // color scheme for cards

// ============================================
//            Type Definitions
// ============================================

/**
 * Represents card suit
 */
export type Suit = '♥' | '♦' | '♣' | '♠';

/**
 * Represents card rank
 */
export type Rank = 'A' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '10' | 'J' | 'Q' | 'K';

/**
 * Represents game phase
 */
export type GamePhase = 'betting' | 'playing' | 'dealer_turn' | 'finished';

/**
 * Represents player actions
 */
export type PlayerAction = 'bet' | 'hit' | 'stand' | 'double' | 'split' | 'surrender' | 'insurance' | 'reset';

/**
 * Represents possible AI strategies
 */
export type AIStrategy = 'simple' | 'basic' | 'conservative';

/**
 * Represents card back design options
 */
export type CardBackDesign = 'blue' | 'red' | 'green' | 'purple';

/**
 * Represents chip value
 */
export type ChipValue = typeof CHIP_VALUES[number];

/**
 * Represents hand result
 */
export type HandResult = 'win' | 'lose' | 'push' | 'blackjack' | 'surrender';

// ============================================
//            Interfaces
// ============================================

/**
 * Represents card entity
 */
export interface Card {
    suit: Suit | '?';
    rank: Rank | '?';
    value: number;
    hidden?: boolean;
}

/**
 * Represents hand entity
 */
export interface Hand {
    cards: Card[];
    value: number;
    bet: number;
    is_blackjack: boolean;
    is_bust: boolean;
    is_soft: boolean;
    can_split: boolean;
    can_double: boolean;
    is_surrendered: boolean;
    is_insured: boolean;
}

/**
 * Represents the complete game state
 */
export interface GameState {
    player_hands: Hand[];
    dealer_hand: Hand;
    current_hand_index: number;
    game_phase: GamePhase;
    player_chips: number;
    current_bet: number;
    insurance_bet: number;
    deck_remaining: number;
}

/**
 * Action message sent to the backend
 */
export interface ActionMessage {
    action: PlayerAction;
    amount?: number;
}

/**
 * WebSocket message received from the backend
 */
export interface WebsocketMessage {
    type: 'game_state' | 'error' | 'info';
    state?: GameState;
    error?: string;
    message?: string;
}

/**
 * Represents chip stack values
 */
export interface ChipStack {
    value: ChipValue;
    count: number;
}

/**
 * Represents the complete game settings
 */
export interface GameSettings {
    numDecks: number;
    blackjackPayout: number; // 1.5 for 3:2, 1.2 for 6:5
    dealerHitsOnSoft17: boolean;
    allowSurrender: boolean;
    allowDoubleAfterSplit: boolean;
    maxSplits: number;
    minBet: number;
    maxBet: number;
    soundEnabled: boolean;
    animationSpeed: 'slow' | 'normal' | 'fast';
}

/**
 * Represents the complete player stats
 */
export interface PlayerStats {
    handsPlayed: number;
    handsWon: number;
    handsLost: number;
    handsPushed: number;
    blackjacks: number;
    busts: number;
    totalWagered: number;
    totalWon: number;
    biggestWin: number;
    currentStreak: number;
    longestWinStreak: number;
}

/**
 * Represents the complete hand history
 */
export interface HandHistory {
    handNumber: number;
    playerCards: Card[];
    dealerCards: Card[];
    playerValue: number;
    dealerValue: number;
    bet: number;
    result: HandResult;
    payout: number;
    timestamp: Date;
}

// ============================================
//      Utility Functions
// ============================================
/**
 * Get the WebSocket URL based on environment
 */
export function getWebSocketURL(gameId: string = 'default'): string {
    /*
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = process.env.NODE_ENV === 'production'
            ? window.location.host
            : 'localhost:8000';
        return `${protocol}//${host}/ws/game/${gameId}/`;
    */
    // For development, hardcode localhost
    // return `ws://127.0.0.1:8000/ws/game/${gameId}/`;
    return `ws://localhost:8000/ws/blackjack/${gameId}/`;
}