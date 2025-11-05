// ============================================
//            Type Definitions
// ============================================

/**
 * Represents a position on the game grid as [x, y] coordinates
 */
export type Position = [number, number];

/**
 * Valid directions for snake movement
 */
export type Direction = 'up' | 'down' | 'left' | 'right';

/**
 * Available AI agent strategy types
 */
export type AIStrategy = 'simple' | 'astar' | 'safe';

// ============================================
//            Interfaces
// ============================================

/**
 * Represents the complete game state
 */
export interface GameState {
    snake: Position[];
    food: Position;
    score: number;
    game_over: boolean;
    direction: Direction;
    moves: number;
    grid_size: number;
}

/**
 * WebSocket message received from the backend
 */
export interface WebSocketMessage {
    type: 'game_state' | 'ai_status';
    state?: GameState;
    ai_mode?: boolean;
    ai_strategy?: AIStrategy;
    strategy?: AIStrategy;
}

/**
 * Action message sent to the backend
 */
export interface ActionMessage {
    action: 'start' | 'pause' | 'reset' | 'direction' | 'toggle_ai' | 'set_ai_strategy';
    direction?: Direction;
    strategy?: AIStrategy;
}

// ============================================
//            Constants
// ============================================

/**
 * Game configuration constants
 */
export const GAME_CONFIG = {
    CELL_SIZE: 25,
    GRID_SIZE: 20,
    TICK_RATE: 150,     // milliseconds
} as const;

/**
 * Color scheme for the game
 */
export const COLORS = {
    background: '#1a1a2e',
    grid: '#16213e',
    food: '#ff6b6b',
    snakeHead: '#4ecdc4',
    snakeBody: '#45b7af',
    aiSnakeHead: '#9b59b6',
    aiSnakeBody: '#8e44ad',
    overlay: 'rgba(155, 89, 182, 0.2)',
    gameOver: 'rgba(0, 0, 0, 0.7)',
    text: '#fff',
} as const;

/**
 * Keyboard controls mapping
 */
export const KEYBOARD_CONTROLS: Record<string, Direction> = {
    'ArrowUp': 'up',
    'ArrowDown': 'down',
    'ArrowLeft': 'left',
    'ArrowRight': 'right',
    'w': 'up',
    's': 'down',
    'a': 'left',
    'd': 'right',
};

// ============================================
//          Utility Functions
// ============================================

/**
 * Check if a key press is a valid direction key
 */
export function isDirectionKey(key: string): key is keyof typeof KEYBOARD_CONTROLS {
    return key in KEYBOARD_CONTROLS;
}

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
    return `ws://localhost:8000/ws/game/${gameId}/`;
}

/**
 * Calculate the canvas size based on grid size and cell size
 */
export function calculateCanvasSize(gridSize: number, cellSize: number): number {
    return gridSize * cellSize;
}

/**
 * Format AI strategy name for display
 */
export function formatStrategyName(strategy: AIStrategy): string {
    const strategyNames: Record<AIStrategy, string> = {
        simple: 'Simple',
        astar: 'A* (Best Strategy)',
        safe: 'Safe',
    };
    return strategyNames[strategy];
}

/**
 * Get strategy description
 */
export function getStrategyDescription(strategy: AIStrategy): string {
    const descriptions: Record<AIStrategy, string> = {
        simple: 'Greedy approach, moves directly towards the food',
        astar: 'Optimal pathfinding with collision avoidance',
        safe: 'Prioritizes survival, checks for escape routes'
    };
    return descriptions[strategy];
}

// ============================================
//           Type Guards
// ============================================

/**
 * Type guard to check if message is a game state message
 */
export function isGameStateMessage(message: WebSocketMessage): message is WebSocketMessage & { state: GameState } {
    return message.type === 'game_state' && message.state !== undefined;
}

/**
 * Type guard to check if message is an AI status message
 */
export function isAIStatusMessage(message: WebSocketMessage): message is WebSocketMessage & { ai_mode: boolean } {
    return message.type === 'ai_status' && message.ai_mode !== undefined;
}

/**
 * Type guard to validate AI strategy
 */
export function isValidAIStrategy(strategy: string): strategy is AIStrategy {
    return ['simple', 'astar', 'safe'].includes(strategy);
}

// ============================================
//         Canvas Drawing Helpers
// ============================================

/**
 * Draw a cell on the canvas
 */
export function drawCell(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    cellSize: number,
    color: string,
    padding: number = 2
): void {
    ctx.fillStyle = color;
    ctx.fillRect(
        x * cellSize + padding,
        y * cellSize + padding,
        cellSize - padding * 2,
        cellSize - padding * 2
    );
}

/**
 * Draw a circle on the canvas
 */
export function drawCircle(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    radius: number,
    color: string
): void {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI, false);
    ctx.fill();
}

/**
 * Draw text on the canvas
 */
export function drawText(
    ctx: CanvasRenderingContext2D,
    text: string,
    x: number,
    y: number,
    options?: {
        font?: string;
        color?: string;
        align?: CanvasTextAlign;
    }
): void {
    ctx.font = options?.font || '20px Arial';
    ctx.fillStyle = options?.color || COLORS.text;
    ctx.textAlign = options?.align || 'left';
    ctx.fillText(text, x, y);
}

/**
 * Draw grid lines on the canvas
 */
export function drawGrid(
    ctx: CanvasRenderingContext2D,
    gridSize: number,
    cellSize: number,
    color: string = COLORS.grid
): void {
    const canvasSize = gridSize * cellSize;
    ctx.strokeStyle = color;

    for (let i = 0; i <= gridSize; i++) {
        // Vertical lines
        ctx.beginPath();
        ctx.moveTo(i * cellSize, 0);
        ctx.lineTo(i * cellSize, canvasSize);
        ctx.stroke();
        // Horizontal lines
        ctx.beginPath();
        ctx.moveTo(0, i * cellSize);
        ctx.lineTo(canvasSize, i * cellSize);
        ctx.stroke();
    }
}

/**
 * Clear the entire canvas
 */
export function clearCanvas(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    color: string = COLORS.background
): void {
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, width, height);
}