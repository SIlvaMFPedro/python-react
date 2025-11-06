import React, {useEffect, useRef, useCallback, useState } from "react";
import {
    type Position,
    type AIStrategy,
    type GameState,
    type WebSocketMessage,
    type ActionMessage,
    GAME_CONFIG,
    COLORS,
    KEYBOARD_CONTROLS,
    isDirectionKey,
    getWebSocketURL,
    calculateCanvasSize,
    formatStrategyName,
    getStrategyDescription,
    isGameStateMessage,
    isAIStatusMessage,
    drawCell,
    drawCircle,
    drawText,
    drawGrid,
    clearCanvas
} from "../utils/utils.ts";

// ============================================
//         SNAKE GAME REACT COMPONENT
// ============================================
const SnakeGame: React.FC = () => {
    // Set state variables
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const containerRef = useRef<HTMLDivElement | null>(null);
    const [gameState, setGameState] = useState<GameState | null>(null);
    const [isConnected, setIsConnected] = useState<boolean>(false);
    const [isPlaying, setIsPlaying] = useState<boolean>(false);
    const [aiMode, setAIMode] = useState<boolean>(false);
    const [aiStrategy, setAIStrategy] = useState<AIStrategy>('astar');

    // Set game config
    const { CELL_SIZE, GRID_SIZE } = GAME_CONFIG;
    const CANVAS_SIZE = calculateCanvasSize(GRID_SIZE, CELL_SIZE);

    const sendAction = (message: ActionMessage) => {
        /**
         * Sends action message to websocket
         */
        if (wsRef.current && isConnected) {
            wsRef.current.send(JSON.stringify(message));
        }
    };

    const startGame = () => {
        /**
         * Sends message to start game
         */
        console.log('Starting Game');
        sendAction({ action: 'start' });
        setIsPlaying(true);
        // Focus container after starting
        setTimeout(() => {
            if (containerRef.current) {
                containerRef.current.focus();
            }
        }, 100);
    };

    const resetGame = (): void => {
        /**
         * Sends message to reset game
         */
        console.log('Reset Game');
        sendAction({ action: 'reset' });
        setIsPlaying(false);
        setAIMode(false);
    };

    const pauseGame = (): void => {
        /**
         * Sends message to pause game
         */
        console.log('Paused Game');
        sendAction({ action: 'pause' });
        setIsPlaying(false);
    };

    const toggleAI = (): void => {
        /**
         * Sends message to toggle ai mode
         */
        console.log('Toggle AI');
        sendAction({ action: 'toggle_ai' });
    }

    const changeAIStrategy = (strategy: AIStrategy): void => {
        /**
         * Sends message to change ai strategy
         */
        console.log('Changing AI strategy to: ', strategy);
        sendAction({ action: 'set_ai_strategy', strategy});
    }

    const handleKeyPress = useCallback((event: KeyboardEvent): void => {
        console.log('Key pressed:', event.key, 'Code:', event.code, 'Playing:', isPlaying, 'AI Mode:', aiMode);

        if (!isPlaying) {
            console.log('Game not playing. Ignoring input...');
            return;
        }

        // Toggle AI with spacebar
        if (event.code === 'Space' || event.key === ' '){
            event.preventDefault();
            console.log('Toggling AI');
            toggleAI();
            return;
        }

        // Only accept manual controls if AI is off
        if (aiMode) {
            console.log('AI mode active. Ignoring manual controls...');
            return;
        }
        if (isDirectionKey(event.key)) {
            event.preventDefault(); // Prevent page scrolling
            const direction = KEYBOARD_CONTROLS[event.key];
            console.log('Sending direction: ', direction);
            if (wsRef.current) {
                const message: ActionMessage = {
                    action: 'direction',
                    direction: direction
                };
                wsRef.current.send(JSON.stringify(message));
            }
        }

    }, [isPlaying, aiMode, toggleAI]);

    // Handle websocket connection
    useEffect(() => {
        // Connect to WebSocket
        const ws = new WebSocket(getWebSocketURL());
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("WebSocket Connected");
            setIsConnected(true);
        };

        ws.onmessage = (event: MessageEvent) => {
            const data: WebSocketMessage = JSON.parse(event.data);
            // Check game state message
            if (isGameStateMessage(data)) {
                setGameState(data.state);
                if (data.ai_mode !== undefined) {
                    setAIMode(data.ai_mode);
                }
                if (data.ai_strategy) {
                    setAIStrategy(data.ai_strategy);
                }
                else if (isAIStatusMessage(data)) {
                    setAIMode(data.ai_mode);
                    if (data.strategy) {
                        setAIStrategy(data.strategy);
                    }
                }
            }
        };

        ws.onclose = () => {
            console.log("WebSocket Disconnected");
            setIsConnected(false);
        };

        ws.onerror = (error: Event) => {
            console.log("WebSocket Error: ", error);
        };

        return () => {
            ws.close();
        };
    }, []);

    // Handle keyboard
    useEffect(() => {
        // Add keyboard event listener to document
        console.log('Setting up keyboard listener, isPlaying: ', isPlaying, 'aiMode: ', aiMode);
        document.addEventListener('keydown', handleKeyPress);

        return () => {
            document.removeEventListener('keydown', handleKeyPress);
        };
    }, [aiMode, handleKeyPress, isPlaying]);

    // Handle draw game logic
    useEffect(() => {
        // Draw game state
        if (!gameState || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear canvas
        clearCanvas(ctx, CANVAS_SIZE, CANVAS_SIZE);

        // Draw grid
        drawGrid(ctx, GRID_SIZE, CELL_SIZE);

        // Draw food
        const [foodX, foodY] = gameState.food;
        drawCircle(
            ctx,
            foodX * CELL_SIZE + CELL_SIZE / 2,
            foodY * CELL_SIZE + CELL_SIZE / 2,
            CELL_SIZE / 2 - 2,
            COLORS.food
        );

        // Draw snake
        gameState.snake.forEach((segment: Position, index: number) => {
            const [x, y] = segment;
            // Different colors for AI mode
            const color = index == 0
                ? (aiMode ? COLORS.aiSnakeHead : COLORS.snakeHead)
                : (aiMode ? COLORS.aiSnakeBody : COLORS.snakeBody);
            drawCell(ctx, x, y, CELL_SIZE, color);
            // Draw eyes on the head
            if (index === 0) {
                ctx.fillStyle = COLORS.text;
                ctx.fillRect(x * CELL_SIZE + 8, y * CELL_SIZE + 8, 4, 4);
                ctx.fillRect(x * CELL_SIZE + 13, y * CELL_SIZE + 8, 4, 4);
            }
        });

        // Draw AI indicator overlay
        if (aiMode) {
            ctx.fillStyle = COLORS.overlay;
            ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
            drawText(ctx, '🤖 AI AUTO-PILOT', 10, 30, {
                font: 'bold 20px Arial',
                color: COLORS.aiSnakeHead,
            });
        }

        // Draw game over overlay
        if (gameState.game_over) {
            ctx.fillStyle = COLORS.gameOver;
            ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

            drawText(ctx, 'Game Over!', CANVAS_SIZE / 2, CANVAS_SIZE / 2 - 20, {
                font: 'bold 40px Arial',
                color: COLORS.text,
                align: 'center',
            });
            drawText(ctx, `Score: ${gameState.score}`, CANVAS_SIZE / 2, CANVAS_SIZE / 2 + 20, {
                font: '20px Arial',
                color: COLORS.text,
                align: 'center',
            });
            if (aiMode) {
                drawText(ctx, `AI Strategy: ${aiStrategy}`, CANVAS_SIZE / 2, CANVAS_SIZE / 2 + 50, {
                    font: '20px Arial',
                    color: COLORS.text,
                    align: 'center',
                });

            }
        }
    }, [gameState, aiMode, aiStrategy, CANVAS_SIZE, CELL_SIZE, GRID_SIZE]);

    // Focus on mount and when game starts
    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.focus();
        }
    }, [isPlaying]);

    return (
        <div
            ref={containerRef}
            tabIndex={0}
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '20px',
                padding: '20px',
                backgroundColor: '#0f0f1e',
                minHeight: '100vh',
                outline: 'none',
            }}
            onClick={() => containerRef.current?.focus()}
        >
            <h1 style={{ color: COLORS.snakeHead, margin: 0}}>🐍 Snake Game {aiMode && '🤖'}</h1>
            {/* Debug Info */}
            <div style={{
                backgroundColor: '#2c3e50',
                padding: '10px',
                borderRadius: '5px',
                color: '#fff',
                fontSize: '12px',
                fontFamily: 'monospace'
            }}>
                Debug: Connected={isConnected ? '✅' : '❌'} | Playing={isPlaying ? '✅' : '❌'} | AI={aiMode ? '✅' : '❌'}
            </div>
            <div style={{
               backgroundColor: COLORS.grid,
               padding: '20px',
               borderRadius: '10px',
               color: COLORS.text,
               minWidth: '500px'
            }}>
                <div style={{ display: 'flex', gap: '30px', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <div>
                        Score: <strong style={{ color: COLORS.snakeHead}}>{gameState?.score || 0}</strong>
                    </div>
                    <div>
                        Moves: <strong>{gameState?.moves || 0}</strong>
                    </div>
                    <div>
                        Status: <strong style={{ color: isConnected ? COLORS.snakeHead : COLORS.food}}>{isConnected ? 'Connected' : 'Disconnected'}</strong>
                    </div>
                </div>
                <div style={{
                    padding: '10px',
                    backgroundColor: aiMode ? COLORS.overlay : 'transparent',
                    borderRadius: '5px',
                    border: aiMode ? `2px solid ${COLORS.aiSnakeHead}` : 'none',
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>
                              Mode: <strong style={{ color: aiMode ? COLORS.aiSnakeHead : COLORS.snakeHead }}>
                                {aiMode ? '🤖 AI Auto-Pilot' : '👤 Manual'}
                              </strong>
                        </span>
                        {aiMode && (
                            <span style={{ fontSize: '14px', color: COLORS.aiSnakeHead }}>
                                Strategy: {aiStrategy.toUpperCase()}
                            </span>
                        )}
                    </div>
                </div>
            </div>
            <canvas
                ref={canvasRef}
                width={CANVAS_SIZE}
                height={CANVAS_SIZE}
                style={{
                    border: aiMode ? `3px solid ${COLORS.aiSnakeHead}` : `3px solid ${COLORS.snakeHead}`,
                    borderRadius: '10px',
                    boxShadow: aiMode
                        ? '0 0 20px rgba(155, 89, 182, 0.5)'
                        : '0 0 20px rgba(78, 205, 196, 0.3)',
                    cursor: 'pointer',
                }}
                onClick={() => containerRef.current?.focus()}
            />
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', justifyContent: 'center'}}>
                <button
                    onClick={startGame}
                    disabled={!isConnected || isPlaying}
                    style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        backgroundColor: COLORS.snakeHead,
                        color: '#0f0f1e',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: isConnected && !isPlaying ? 'pointer' : 'not-allowed',
                        fontWeight: 'bold',
                        opacity: isConnected && !isPlaying ? 1 : 0.5
                    }}
                >
                    ▶ Start
                </button>
                <button
                    onClick={pauseGame}
                    disabled={!isConnected || !isPlaying}
                    style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        backgroundColor: '#ffd93d',
                        color: '#0f0f1e',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: isConnected && isPlaying ? 'pointer' : 'not-allowed',
                        fontWeight: 'bold',
                        opacity: isConnected && isPlaying ? 1 : 0.5
                    }}
                >
                    ⏸ Pause
                </button>
                <button
                    onClick={resetGame}
                    disabled={!isConnected}
                    style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        backgroundColor: COLORS.food,
                        color: COLORS.text,
                        border: 'none',
                        borderRadius: '5px',
                        cursor: isConnected ? 'pointer' : 'not-allowed',
                        fontWeight: 'bold',
                        opacity: isConnected ? 1 : 0.5
                    }}
                >
                    🔄 Reset
                </button>
                <button
                    onClick={toggleAI}
                    disabled={!isConnected || !isPlaying}
                    style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        backgroundColor: aiMode ? COLORS.aiSnakeHead : '#3498db',
                        color: COLORS.text,
                        border: 'none',
                        borderRadius: '5px',
                        cursor: isConnected && isPlaying ? 'pointer' : 'not-allowed',
                        fontWeight: 'bold',
                        opacity: isConnected && isPlaying ? 1 : 0.5
                    }}
                >
                    {aiMode ? '🤖 AI ON' : '🤖 AI OFF'}
                </button>
            </div>
            {/* AI Strategy Selector */}
            {aiMode && (
                <div style={{
                    backgroundColor: COLORS.grid,
                    padding: '15px',
                    borderRadius: '10px',
                    color: COLORS.text,
                    border: '2px solid ${COLORS.aiSnakeHead}`'
                }}>
                    <div style={{ marginBottom: '10px', fontWeight: 'bold' }}>AI Strategy:</div>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        {(['simple', 'astar', 'safe'] as AIStrategy[]).map((strategy) => (
                            <button
                                key={strategy}
                                onClick={() => changeAIStrategy(strategy)}
                                style={{
                                    padding: '8px 16px',
                                    backgroundColor: aiStrategy === strategy ? COLORS.aiSnakeHead : '#2c3e50',
                                    color: COLORS.text,
                                    border: 'none',
                                    borderRadius: '5px',
                                    cursor: 'pointer',
                                    fontSize: '14px'
                                }}
                            >
                                {formatStrategyName(strategy)}
                            </button>
                        ))}
                    </div>
                </div>
            )}
            <div style={{
                backgroundColor: COLORS.grid,
                padding: '15px',
                borderRadius: '10px',
                color: COLORS.text,
                maxWidth: '500px',
                textAlign: 'center'
            }}>
                <strong>Controls:</strong>
                <div style={{ marginTop: '8px', fontSize: '14px' }}>
                    🎮 Arrow Keys or WASD - Move snake<br/>
                    <span style={{ color: COLORS.aiSnakeHead }}>⚡ SPACEBAR - Toggle AI Auto-Pilot</span>
                </div>
            </div>
            <div style={{
                backgroundColor: '#2c3e50',
                padding: '15px',
                borderRadius: '10px',
                color: COLORS.text,
                maxWidth: '500px'
            }}>
                <strong style={{ color: COLORS.aiSnakeHead }}>🤖 AI Strategies:</strong>
                <ul style={{ marginTop: '10px', fontSize: '14px', lineHeight: '1.6'}}>
                    {(['simple', 'astar', 'safe'] as AIStrategy[]).map((strategy) => (
                        <li key={strategy}>
                            <strong>{formatStrategyName(strategy)}:</strong> {getStrategyDescription(strategy)}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default SnakeGame;