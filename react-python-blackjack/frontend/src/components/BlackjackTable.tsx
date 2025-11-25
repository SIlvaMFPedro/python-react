import React, { useEffect, useRef, useState } from "react";
import { Box, Container, Paper, Typography, Chip, Alert, Snackbar } from '@mui/material';
import { useAppDispatch, useAppSelector } from "../store/hook.ts";
import {
    updateGameState,
    setError,
    clearError,
    selectPlayerHands,
    selectDealerHand,
    selectGamePhase,
    selectPlayerChips,
    selectCurrentBet,
    selectCurrentHandIndex,
    selectCanHit,
    selectCanStand,
    selectCanDouble,
    selectCanSplit,
    selectCanInsure,
    selectLastError,
    selectCanSurrender,
} from '../store/slices/gameSlice';
import {
    setAiMode,
    setAiStrategy,
    setAiDescription,
    selectAiMode,
    selectAiStrategy,
    selectAiDescription,
} from '../store/slices/uiSlice';
import { setConnected, setConnection } from '../store/slices/webSocketSlice';
import type {ActionMessage, AIStrategy} from "../utils/utils";
import Card from "../components/Card";
import BettingControls from "../components/BettingControls";
import ActionButtons from "../components/ActionButtons";
import AIControls from "../components/AIControls";
import styles from '../styles/BlackjackTable.module.scss';


// ============================================
//       BLACKJACK TABLE COMPONENT
// ============================================
const BlackJackTable: React.FC = () => {
    const dispatch = useAppDispatch();
    const wsRef = useRef<WebSocket | null>(null);
    const [infoMessage, setInfoMessage] = useState<string | null>(null);

    const playerHands = useAppSelector(selectPlayerHands);
    const dealerHand = useAppSelector(selectDealerHand);
    const gamePhase = useAppSelector(selectGamePhase);
    const playerChips = useAppSelector(selectPlayerChips);
    const currentBet = useAppSelector(selectCurrentBet);
    const currentHandIndex = useAppSelector(selectCurrentHandIndex);
    const lastError = useAppSelector(selectLastError);
    // const lastMessage = useAppSelector(selectLastMessage);

    const aiMode = useAppSelector(selectAiMode);
    const aiStrategy = useAppSelector(selectAiStrategy);
    const aiDescription = useAppSelector(selectAiDescription);

    const canHit = useAppSelector(selectCanHit);
    const canStand = useAppSelector(selectCanStand);
    const canDouble = useAppSelector(selectCanDouble);
    const canSplit = useAppSelector(selectCanSplit);
    const canSurrender = useAppSelector(selectCanSurrender);
    const canInsure = useAppSelector(selectCanInsure);

    const isConnected = useAppSelector(state => state.websocket.isConnected);

    // Handler Functions

    const sendAction = (action: ActionMessage) => {
        if (wsRef.current && isConnected) {
            wsRef.current.send(JSON.stringify(action));
        }
    };

    const handleToggleAI = () => {
        sendAction({ action: 'toggle_ai' as never });
    };

    const handleChangeAIStrategy = (strategy: AIStrategy) => {
        sendAction({ action: 'set_ai_strategy' as never, strategy } as never);
    };

    const handleBet = (amount: number) => {
        sendAction({ action: 'bet', amount });
    };

    const handleDeal = () => {
        sendAction({ action: 'deal' as never });
    };

    const handleHit = () => {
        sendAction({ action: 'hit' });
    };

    const handleStand = () => {
        sendAction({ action: 'stand' });
    };

    const handleDouble = () => {
        sendAction({ action: 'double' });
    };

    const handleSplit = () => {
        sendAction({ action: 'split' });
    };

    const handleSurrender = () => {
        sendAction({ action: 'surrender' });
    };

    const handleInsurance = () => {
        sendAction({ action: 'insurance' });
    };

    const handleNewGame = () => {
        sendAction({ action: 'reset' });
    }

    // Websocket setup
    useEffect(() => {
        const ws = new WebSocket("ws://127.0.0.1:8080/ws/blackjack/default/");
        wsRef.current = ws;
        dispatch(setConnection(ws));

        ws.onopen = () => {
            console.log('WebSocket Connected');
            dispatch(setConnected(true));
        };

        ws.onmessage = (event: MessageEvent) => {
            const data = JSON.parse(event.data);
            // Check message type
            if (data.type === 'game_state') {
                dispatch(updateGameState(data.state));
                if (data.ai_mode !== undefined) {
                    dispatch(setAiMode(data.ai_mode));
                }
                if (data.ai_strategy) {
                    dispatch(setAiStrategy(data.ai_strategy));
                }
            } else if (data.type === 'error') {
                dispatch(setError(data.error));
            } else if (data.type === 'info') {
                setInfoMessage(data.message);
                setTimeout(() => setInfoMessage(null), 3000);
            } else if (data.type === 'ai_status') {
                if (data.ai_mode !== undefined) {
                    dispatch(setAiMode(data.ai_mode));
                }
                if (data.ai_strategy) {
                    dispatch(setAiStrategy(data.strategy));
                }
                if (data.description) {
                    dispatch(setAiDescription(data.description));
                }
            }
        };

        ws.onclose = () => {
            console.log("WebSocket Disconnected");
            dispatch(setConnected(false));
        };

        ws.onerror = (error: Event) => {
            console.error('WebSocket Error:', error);
        };

        return () => {
            ws.close();
            dispatch(setConnection(null));
        };
    }, [dispatch]);

    return (
        <Container maxWidth="lg" className={styles.tabContainer}>
            <Box className={styles.table}>
                {/* Header */}
                <Box className={styles.header}>
                    <Typography variant="h3" className={styles.title}>
                        🎰 Blackjack
                    </Typography>
                    <Box className={styles.headerRight}>
                        <Chip
                            label={isConnected ? 'Connected' : 'Disconnected'}
                            color={isConnected ? 'success' : 'error'}
                            size="small"
                        />
                        {aiMode && (
                            <Chip
                                icon={<span>🤖</span>}
                                label={`AI: ${aiStrategy.toUpperCase()}`}
                                color="secondary"
                                size="small"
                                className={styles.aiChip}
                            />
                        )}
                    </Box>
                </Box>
                {/* Main Game Area */}
                <Box className={styles.gameArea}>
                    {/* Dealer Section */}
                    <Paper className={styles.dealerSection} elevation={3}>
                        <Typography variant="h6" className={styles.sectionTitle}>
                            Dealer {dealerHand && !dealerHand.cards[0]?.hidden && `- ${dealerHand.value}`}
                        </Typography>
                        <Box className={styles.handArea}>
                            {dealerHand && dealerHand.cards.length > 0 ? (
                                dealerHand.cards.map((card, index) => (
                                    <Card
                                        key={index}
                                        card={card}
                                        faceDown={card.hidden}
                                        animate={true}
                                        delay={index * 200}
                                    />
                                ))
                            ) : (
                                <Typography variant="body2" color="text.secondary">
                                    Waiting for bets...
                                </Typography>
                            )}
                        </Box>
                        {dealerHand && dealerHand.is_blackjack && gamePhase === 'finished' && (
                            <Chip label="Blackjack!" color="error" className={styles.resultChip} />
                        )}
                        {dealerHand && dealerHand.is_bust && (
                            <Chip label="Bust!" color="success" className={styles.resultChip} />
                        )}
                    </Paper>

                    {/* Player Section */}
                    <Paper className={styles.playerSection} elevation={3}>
                        <Typography variant="h6" className={styles.sectionTitle}>
                            Your Hand{playerHands.length > 1 ? 's' : ''}
                        </Typography>
                        <Box className={styles.handsContainer}>
                            {playerHands.map((hand, handIndex) => (
                                <Box
                                    key={handIndex}
                                    className={`${styles.handWrapper} ${
                                        handIndex === currentHandIndex ? styles.activeHand : ''
                                    }`}
                                >
                                    <Box className={styles.handArea}>
                                        {hand.cards.map((card, cardIndex) => (
                                            <Card
                                                key={cardIndex}
                                                card={card}
                                                animate={true}
                                                delay={cardIndex * 200 + 400}
                                            />
                                        ))}
                                    </Box>
                                    <Box className={styles.handInfo}>
                                        <Typography variant="body1">
                                            Value: {hand.value} {hand.is_soft && '(Soft)'}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Bet: ${hand.bet}
                                        </Typography>
                                        {hand.is_blackjack && (
                                            <Chip label="Blackjack!" color="success" size="small" />
                                        )}
                                        {hand.is_bust && <Chip label="Bust" color="error" size="small" />}
                                        {hand.is_surrendered && (
                                            <Chip label="Surrendered" color="warning" size="small" />
                                        )}
                                    </Box>
                                </Box>
                            ))}
                        </Box>
                    </Paper>
                </Box>
                {/* Controls Area */}
                <Box className={styles.controlsArea}>
                    {/* AI Controls */}
                    <AIControls
                        aiMode={aiMode}
                        aiStrategy={aiStrategy}
                        aiDescription={aiDescription}
                        onToggleAI={handleToggleAI}
                        onChangeStrategy={handleChangeAIStrategy}
                        disabled={!isConnected}
                    />

                    {/* Game Controls */}
                    <Box className={styles.gameControls}>
                        {gamePhase === 'betting' || gamePhase === 'finished' ? (
                            <BettingControls
                                playerChips={playerChips}
                                currentBet={currentBet}
                                onBet={handleBet}
                                onDeal={handleDeal}
                                disabled={!isConnected || aiMode}
                            />
                        ) : (
                            <ActionButtons
                                canHit={canHit}
                                canStand={canStand}
                                canDouble={canDouble}
                                canSplit={canSplit}
                                canSurrender={canSurrender}
                                canInsure={canInsure}
                                onHit={handleHit}
                                onStand={handleStand}
                                onDouble={handleDouble}
                                onSplit={handleSplit}
                                onSurrender={handleSurrender}
                                onInsurance={handleInsurance}
                            />
                        )}
                    </Box>
                </Box>

                {/* New Game Button */}
                {gamePhase === 'finished' && currentBet === 0 && !aiMode && (
                    <Box className={styles.newGameButton}>
                        <button onClick={handleNewGame} className={styles.dealButton}>
                            New Game
                        </button>
                    </Box>
                )}

                {/* Info Message Snackbar */}
                <Snackbar
                    open={!!infoMessage}
                    autoHideDuration={3000}
                    onClose={() => setInfoMessage(null)}
                    anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
                >
                    <Alert severity="info" onClose={() => setInfoMessage(null)}>
                        {infoMessage}
                    </Alert>
                </Snackbar>

                {/* Error Snackbar */}
                <Snackbar
                    open={!!lastError}
                    autoHideDuration={4000}
                    onClose={() => dispatch(clearError())}
                    anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
                >
                    <Alert severity="error" onClose={() => dispatch(clearError())}>
                        {lastError}
                    </Alert>
                </Snackbar>
            </Box>
        </Container>
    );
};

export default BlackJackTable;