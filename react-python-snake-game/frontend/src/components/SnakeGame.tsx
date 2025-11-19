import React, { useEffect, useRef, useCallback } from "react";
import {
    type Position,
    type AIStrategy,
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
import {
    Box,
    Paper,
    Button,
    Typography,
    Chip,
    Stack,
    ButtonGroup
} from '@mui/material';
import {
    PlayArrow,
    Pause,
    Refresh,
    SmartToy
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from "../store/hooks.ts";
import { updateGameState, resetGame as resetGameState } from "../store/slices/gameSlice.ts";
import { setConnected, setConnectionError, setLastMessage, setConnection } from "../store/slices/websocketSlice.ts";
import { setPlaying, setPaused, setAiMode, setAiStrategy, resetUI } from "../store/slices/uiSlice.ts";
import styles from '../styles/SnakeGame.module.scss';

// ============================================
//         SNAKE GAME REACT COMPONENT
// ============================================
const SnakeGame: React.FC = () => {
    // Set state variables
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const containerRef = useRef<HTMLDivElement | null>(null);

    // Redux selectors
    const dispatch = useAppDispatch();
    const gameState = useAppSelector(state => state.game);
    const { isConnected, connection } = useAppSelector(state => state.websocket);
    const { isPlaying, aiMode, aiStrategy } = useAppSelector(state => state.ui);

    // Set game config
    const { CELL_SIZE, GRID_SIZE } = GAME_CONFIG;
    const CANVAS_SIZE = calculateCanvasSize(GRID_SIZE, CELL_SIZE);

    const sendAction = (message: ActionMessage) => {
        /**
         * Sends action message to websocket
         */
        if (connection && isConnected) {
            connection.send(JSON.stringify(message));
        }
    };

    const startGame = () => {
        /**
         * Sends message to start game
         */
        // console.log('Starting Game');
        sendAction({ action: 'start' });
        dispatch(setPlaying(true));
        // Focus container after starting
        setTimeout(() => containerRef.current?.focus(), 100);
    };

    const resetGame = (): void => {
        /**
         * Sends message to reset game
         */
        // console.log('Reset Game');
        sendAction({ action: 'reset' });
        dispatch(resetGameState());
        dispatch(resetUI());
    };

    const pauseGame = (): void => {
        /**
         * Sends message to pause game
         */
        // console.log('Paused Game');
        sendAction({ action: 'pause' });
        dispatch(setPaused(true));
        dispatch(setPlaying(false));
    };

    const toggleAI = (): void => {
        /**
         * Sends message to toggle ai mode
         */
        // console.log('Toggle AI');
        sendAction({ action: 'toggle_ai' });
    }

    const changeAIStrategy = (strategy: string): void => {
        /**
         * Sends message to change ai strategy
         */
        // console.log('Changing AI strategy to: ', strategy);
        sendAction({ action: 'set_ai_strategy', strategy: strategy as never });
    }

    const handleKeyPress = useCallback((event: KeyboardEvent): void => {
        // console.log('Key pressed:', event.key, 'Code:', event.code, 'Playing:', isPlaying, 'AI Mode:', aiMode);

        if (!isPlaying) {
            // console.log('Game not playing. Ignoring input...');
            return;
        }

        // Toggle AI with spacebar
        if (event.code === 'Space' || event.key === ' '){
            event.preventDefault();
            // console.log('Toggling AI');
            toggleAI();
            return;
        }

        // Only accept manual controls if AI is off
        if (aiMode) {
            // console.log('AI mode active. Ignoring manual controls...');
            return;
        }
        if (isDirectionKey(event.key)) {
            event.preventDefault(); // Prevent page scrolling
            const direction = KEYBOARD_CONTROLS[event.key];
            // console.log('Sending direction: ', direction);
            if (connection) {
                const message: ActionMessage = {
                    action: 'direction',
                    direction: direction
                };
                connection.send(JSON.stringify(message));
            }
        }

    }, [isPlaying, aiMode, connection, toggleAI]);

    // Handle websocket connection
    useEffect(() => {
        // Connect to WebSocket
        const ws = new WebSocket(getWebSocketURL());
        dispatch(setConnection(ws));

        ws.onopen = () => {
            console.log("WebSocket Connected");
            dispatch(setConnected(true));
        };

        ws.onmessage = (event: MessageEvent) => {
            const data: WebSocketMessage = JSON.parse(event.data);
            dispatch(setLastMessage(data));
            // Check game state message
            if (isGameStateMessage(data)) {
                dispatch(updateGameState(data.state));
                if (data.ai_mode !== undefined) {
                    dispatch(setAiMode(data.ai_mode));
                }
                if (data.ai_strategy) {
                    dispatch(setAiStrategy(data.ai_strategy));
                }
                else if (isAIStatusMessage(data)) {
                    dispatch(setAiMode(data.ai_mode));
                    if (data.strategy) {
                        dispatch(setAiStrategy(data.strategy));
                    }
                }
            }
        };

        ws.onclose = () => {
            console.log("WebSocket Disconnected");
            dispatch(setConnected(false));
        };

        ws.onerror = (error: Event) => {
            console.log("WebSocket Error: ", error);
            dispatch(setConnectionError('Connection Failed'));
        };

        return () => {
            ws.close();
            dispatch(setConnection(null));
        };
    }, [dispatch]);

    // Handle draw game logic
    useEffect(() => {
        // Draw game state
        if (!gameState.snake.length || !canvasRef.current) return;

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
        if (gameState.gameOver) {
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

    // Handle keyboard
    useEffect(() => {
        // Add keyboard event listener to document
        // console.log('Setting up keyboard listener, isPlaying: ', isPlaying, 'aiMode: ', aiMode);
        document.addEventListener('keydown', handleKeyPress);
        return () => {
            document.removeEventListener('keydown', handleKeyPress);
        };
    }, [handleKeyPress]);

    // Focus on mount and when game starts
    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.focus();
        }
    }, [isPlaying]);

    return (
        <Box
            ref={containerRef}
            tabIndex={0}
            className={styles.gameContainer}
            onClick={() => containerRef.current?.focus()}
        >
            <Typography variant="h2" className={styles.title}>
                🐍 Snake Game {aiMode && '🤖'}
            </Typography>

            {/* Debug Info */}
            <Paper className={styles.debugInfo} elevation={2}>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip
                        size="small"
                        label={isConnected ? 'Connected' : 'Disconnected'}
                        color={isConnected ? 'success' : 'error'}
                    />
                    <Chip
                        size="small"
                        label={isPlaying ? 'Playing' : 'Idle'}
                        color={isPlaying ? 'primary' : 'default'}
                    />
                    <Chip
                        size="small"
                        label={aiMode ? 'AI Active' : 'Manual'}
                        color={aiMode ? 'secondary' : 'default'}
                    />
                </Box>
            </Paper>

            {/* Info Panel */}
            <Paper className={styles.infoPanel} elevation={3}>
                <Box className={styles.statsRow}>
                    <Box className={styles.statItem}>
                        <Typography variant="body1" component="div">
                            Score: <strong>{gameState?.score || 0}</strong>
                        </Typography>
                    </Box>
                    <Box className={styles.statItem}>
                        <Typography variant="body1" component="div">
                            Moves: <strong>{gameState?.moves || 0}</strong>
                        </Typography>
                    </Box>
                    <Box className={styles.statItem}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" component="span">
                                Status:
                            </Typography>
                            <Chip
                                label={isConnected ? 'Connected' : 'Disconnected'}
                                color={isConnected ? 'success' : 'error'}
                                size="small"
                            />
                        </Box>
                    </Box>
                </Box>

                <Box className={`${styles.modeIndicator} ${aiMode ? styles.aiMode : styles.manual}`}>
                    <Box className={styles.modeContent}>
                        <Typography variant="body1" component="div">
                            Mode:{' '}
                            <strong className={aiMode ? styles.ai : styles.manual}>
                                {aiMode ? '🤖 AI Auto-Pilot' : '👤 Manual'}
                            </strong>
                        </Typography>
                        {aiMode && (
                            <Typography variant="body2" component="div" className={styles.strategyName}>
                                Strategy: {aiStrategy.toUpperCase()}
                            </Typography>
                        )}
                    </Box>
                </Box>
            </Paper>

            {/* Canvas */}
            <canvas
                ref={canvasRef}
                width={CANVAS_SIZE}
                height={CANVAS_SIZE}
                className={`${styles.canvas} ${aiMode ? styles.aiMode : ''}`}
                onClick={() => containerRef.current?.focus()}
            />

            {/* Control Buttons */}
            <Stack direction="row" spacing={2} className={styles.buttonContainer} flexWrap="wrap">
                <Button
                    variant="contained"
                    color="primary"
                    startIcon={<PlayArrow />}
                    onClick={startGame}
                    disabled={!isConnected || isPlaying}
                    className={styles.button}
                >
                    Start
                </Button>

                <Button
                    variant="contained"
                    color="warning"
                    startIcon={<Pause />}
                    onClick={pauseGame}
                    disabled={!isConnected || !isPlaying}
                    className={`${styles.button} ${styles.pauseButton}`}
                >
                    Pause
                </Button>

                <Button
                    variant="contained"
                    color="error"
                    startIcon={<Refresh />}
                    onClick={resetGame}
                    disabled={!isConnected}
                    className={`${styles.button} ${styles.resetButton}`}
                >
                    Reset
                </Button>

                <Button
                    variant="contained"
                    color={aiMode ? 'secondary' : 'info'}
                    startIcon={<SmartToy />}
                    onClick={toggleAI}
                    disabled={!isConnected || !isPlaying}
                    className={`${styles.button} ${styles.aiButton} ${aiMode ? styles.aiActive : ''}`}
                >
                    {aiMode ? 'AI ON' : 'AI OFF'}
                </Button>
            </Stack>

            {/* AI Strategy Selector */}
            {aiMode && (
                <Paper className={styles.strategySelector} elevation={3}>
                    <Typography variant="h6" className={styles.strategyTitle}>
                        AI Strategy
                    </Typography>
                    <ButtonGroup variant="contained" className={styles.strategyButtons}>
                        {(['simple', 'astar', 'safe'] as AIStrategy[]).map((strategy) => (
                            <Button
                                key={strategy}
                                onClick={() => changeAIStrategy(strategy)}
                                variant={aiStrategy === strategy ? 'contained' : 'outlined'}
                                color="secondary"
                            >
                                {formatStrategyName(strategy)}
                            </Button>
                        ))}
                    </ButtonGroup>
                </Paper>
            )}

            {/* Controls Info */}
            <Paper className={styles.controlsInfo} elevation={2}>
                <Typography variant="h6" className={styles.controlsTitle}>
                    Controls
                </Typography>
                <Box className={styles.controlsText}>
                    <Typography variant="body2" component="div">
                        🎮 Arrow Keys or WASD - Move snake
                    </Typography>
                    <Typography variant="body2" component="div" className={styles.aiControl}>
                        ⚡ SPACEBAR - Toggle AI Auto-Pilot
                    </Typography>
                </Box>
                <Typography variant="caption" component="div" className={styles.controlsTip}>
                    💡 Tip: Click anywhere to ensure keyboard focus
                </Typography>
            </Paper>

            {/* Strategy Info */}
            <Paper className={styles.strategyInfo} elevation={2}>
                <Typography variant="h6" className={styles.strategyInfoTitle}>
                    🤖 AI Strategies
                </Typography>
                <ul className={styles.strategyList}>
                    {(['simple', 'astar', 'safe'] as AIStrategy[]).map((strategy) => (
                        <li key={strategy}>
                            <strong>{formatStrategyName(strategy)}:</strong> {getStrategyDescription(strategy)}
                        </li>
                    ))}
                </ul>
            </Paper>
        </Box>
    );
};

export default SnakeGame;