import React, { useState } from 'react';
import { Box, Button, Typography, Stack } from '@mui/material';
import { Casino, Clear, Done } from '@mui/icons-material';
import { CHIP_VALUES, type ChipValue } from "../utils/utils.ts";
import styles from "../styles/BettingControls.module.scss";

interface BettingControlsProps {
    playerChips: number;
    currentBet: number;
    onBet: (amount: number) => void;
    onDeal: () => void;
    disabled?: boolean;
}

const BettingControls: React.FC<BettingControlsProps> = ({
    playerChips,
    currentBet,
    onBet,
    onDeal,
    disabled = false,
}) => {
    const [selectedBet, setSelectedBet] = useState(0);

    const handleChipClick = (value: ChipValue) => {
        if (disabled) return;
        const newBet = selectedBet + value;
        if (newBet <= playerChips) {
            setSelectedBet(newBet);
        }
    };

    const handleClearBet = () => {
        setSelectedBet(0);
    };

    const handlePlaceBet = () => {
        if (selectedBet > 0 && selectedBet <= playerChips) {
            onBet(selectedBet);
            setSelectedBet(0);
        }
    };

    const handleDeal = () => {
        if (currentBet > 0) {
            onDeal();
        }
    };

    const getChipColor = (value: ChipValue): string => {
        const colors: Record<ChipValue, string> = {
            1: '#ffffff',
            5: '#ff5252',
            25: '#4caf50',
            100: '#000000',
            500: '#9c27b0',
        };
        return colors[value];
    }

    return (
        <Box className={styles.bettingControls}>
            <Box className={styles.chipDisplay}>
                <Typography variant="h6" className={styles.title}>
                    💰 Your Chips: ${playerChips}
                </Typography>
                <Typography variant="body1" className={styles.betAmount}>
                    Current Bet: ${currentBet}
                </Typography>
                {selectedBet > 0 && (
                    <Typography variant="body2" className={styles.selectedBet}>
                        Selected Bet: ${selectedBet}
                    </Typography>
                )}
            </Box>
            <Stack direction="row" spacing={2} className={styles.chipStack} flexWrap="wrap">
                {CHIP_VALUES.map((value) => (
                    <Box
                        key={value}
                        className={`${styles.chip} ${playerChips < value ? styles.disabled : ''}`}
                        onClick={() => handleChipClick(value)}
                        style={{
                            backgroundColor: getChipColor(value),
                            color: value === 1 || value === 100 ? '#000' : '#fff',
                        }}
                    >
                        <Box className={styles.chipInner}>
                            <Typography variant="body2" className={styles.chipValue}>
                                ${value}
                            </Typography>
                        </Box>
                    </Box>
                ))}
            </Stack>
            <Stack direction="row" spacing={2} className={styles.actionButtons}>
                <Button
                    variant="outlined"
                    color="error"
                    startIcon={<Clear/>}
                    onClick={handleClearBet}
                    disabled={disabled || selectedBet === 0}
                >
                    Clear
                </Button>
                {currentBet === 0 ? (
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<Casino/>}
                        onClick={handlePlaceBet}
                        disabled={disabled || selectedBet === 0 || selectedBet > playerChips}
                        fullWidth
                    >
                        Place Bet
                    </Button>
                ) : (
                    <Button
                        variant="contained"
                        color="success"
                        startIcon={<Done/>}
                        onClick={handleDeal}
                        disabled={disabled}
                        fullWidth
                    >
                        Deal Cards
                    </Button>
                )}
            </Stack>
            {selectedBet > playerChips && (
                <Typography variant="caption" color="error" className={styles.error}>
                    Insufficient Chips
                </Typography>
            )}
        </Box>
    )
};

export default BettingControls;