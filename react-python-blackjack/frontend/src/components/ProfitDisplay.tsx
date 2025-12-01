import React from 'react';
import { Box, Paper, Typography, Chip } from '@mui/material';
import { TrendingUp, TrendingDown, Remove } from '@mui/icons-material';
import styles from '../styles/ProfitDisplay.module.scss';

interface ProfitDisplayProps {
    sessionProfit: number;
    handsPlayed: number;
    handsWon: number;
    handsLost: number;
    onResetSession?: () => void;
}

const ProfitDisplay: React.FC<ProfitDisplayProps> = ({
    sessionProfit,
    handsPlayed,
    handsWon,
    handsLost,
    onResetSession,
}) => {
    const isProfit = sessionProfit > 0;
    const isLoss = sessionProfit < 0;
    const isBreakEven = sessionProfit === 0;
    const winRate = handsPlayed > 0 ? ((handsWon / handsPlayed) * 100).toFixed(1): '0.0';

    return (
        <Paper className={styles.profitDisplay} elevation={3}>
            <Box className={styles.header}>
                <Typography variant="h6" className={styles.title}>
                    Session Stats
                </Typography>
            </Box>
            {/* Main Profit Display */}
            <Box className={`${styles.profitAmount} ${isProfit ? styles.profit : isLoss ? styles.loss : styles.breakeven}`}>
                <Box className={styles.iconWrapper}>
                    {isProfit && <TrendingUp className={styles.icon} />}
                    {isLoss && <TrendingDown className={styles.icon} />}
                    {isBreakEven && <Remove className={styles.icon} />}
                </Box>
                <Box className={styles.amountWrapper}>
                    <Typography variant="h4" className={styles.amount}>
                        {sessionProfit >= 0 ? '+' : ''}{sessionProfit > 0 ? '$' : sessionProfit < 0 ? '-$' : '$'}{Math.abs(sessionProfit)}
                    </Typography>
                    <Typography variant="caption" className={styles.label}>
                        {isProfit ? 'Profit' : isLoss ? 'Loss' : 'Break Even'}
                    </Typography>
                </Box>
            </Box>
            {/* Stats Grid */}
            <Box className={styles.statsGrid}>
                <Box className={styles.statItem}>
                    <Typography variant="body2" className={styles.statLabel}>
                        Hands Played
                    </Typography>
                    <Typography variant="h6" className={styles.statValue}>
                        {handsPlayed}
                    </Typography>
                </Box>
                <Box className={styles.statItem}>
                    <Typography variant="body2" className={styles.statLabel}>
                        Win Rate
                    </Typography>
                    <Typography variant="h6" className={styles.statValue}>
                        {winRate}%
                    </Typography>
                </Box>
                <Box className={styles.statItem}>
                    <Typography variant="body2" className={styles.statLabel}>
                        Lost
                    </Typography>
                    <Chip
                        label={handsLost}
                        color="error"
                        size="small"
                        className={styles.chip}
                    />
                </Box>
            </Box>
            {/* Reset Button */}
            {onResetSession && handsPlayed > 0 && (
                <Box className={styles.resetButton}>
                    <button onClick={onResetSession} className={styles.button}>
                        Reset Session Stats
                    </button>
                </Box>
            )}
        </Paper>
    );
};

export default ProfitDisplay;