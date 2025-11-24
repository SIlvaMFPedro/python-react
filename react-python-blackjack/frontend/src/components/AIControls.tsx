import React from 'react';
import { Box, Paper, Typography, Switch, FormControlLabel, ButtonGroup, Button, Chip, Tooltip } from '@mui/material';
import { SmartToy, Psychology, Security, Speed } from '@mui/icons-material';
import styles from '../styles/AIControls.module.scss';

interface AIControlsProps {
    aiMode: boolean;
    aiStrategy: 'simple' | 'basic' | 'conservative';
    aiDescription: string;
    onToggleAI: () => void;
    onChangeStrategy: (strategy: 'simple' | 'basic' | 'conservative') => void;
    disabled?: boolean;
}

const AIControls: React.FC<AIControlsProps> = ({
    aiMode,
    aiStrategy,
    onToggleAI,
    onChangeStrategy,
    disabled = false
}) => {
    const strategies = [
        {
            value: 'simple' as const,
            label: 'Simple',
            icon: <Speed />,
            description: 'Hit on <17, stand on 17+. Good for learning.',
            winRate: '42%',
            color: '#4caf50',
        },
        {
            value: 'basic' as const,
            label: 'Basic Strategy',
            icon: <Psychology />,
            description: 'Mathematically optimal play. Best win rate!',
            winRate: '49.5%',
            color: '#2196f3',
        },
        {
            value: 'conservative' as const,
            label: 'Conservative',
            icon: <Security />,
            description: 'Risk-averse, focuses on not busting. Safest play.',
            winRate: '45%',
            color: '#ff9800',
        },
    ];
    const currentStrategy = strategies.find(s => s.value === aiStrategy);

    return (
        <Paper className={styles.aiControls} elevation={3}>
            <Box className={styles.header}>
                <SmartToy className={styles.icon}/>
                <Typography variant="h6" className={styles.title}>
                    AI Auto-Pilot
                </Typography>
                <Chip
                    label={aiMode ? 'ACTIVE' : 'INACTIVE'}
                    color={aiMode ? 'success' : 'default'}
                    size="small"
                    className={styles.statusChip}
                />
            </Box>
            <FormControlLabel
                control={
                    <Switch
                        checked={aiMode}
                        onChange={onToggleAI}
                        disabled={disabled}
                        color="primary"
                    />
                }
                label={aiMode ? 'AI is playing' : 'Play manually'}
                className={styles.toggle}
            />
            {aiMode && (
                <Box className={styles.strategySection}>
                    <Typography variant="subtitle2" className={styles.sectionTitle}>
                        Select Strategy
                    </Typography>
                    <ButtonGroup variant="outlined" fullWidth className={styles.strategyButtons}>
                        {strategies.map((strategy) => (
                            <Tooltip key={strategy.value} title={strategy.description} arrow>
                                <Button
                                    onClick={() => onChangeStrategy(strategy.value)}
                                    variant={aiStrategy === strategy.value ? 'contained' : 'outlined'}
                                    startIcon={strategy.icon}
                                    className={`${styles.strategyButton} ${
                                        aiStrategy === strategy.value ? styles.active : ''
                                    }`}
                                    style={{
                                        borderColor: aiStrategy === strategy.value ? strategy.color : undefined,
                                        backgroundColor: aiStrategy === strategy.value ? strategy.color : undefined,
                                    }}
                                >
                                    {strategy.label}
                                </Button>
                            </Tooltip>
                        ))}
                    </ButtonGroup>
                    {currentStrategy && (
                        <Box className={styles.strategyInfo}>
                            <Box className={styles.infoRow}>
                                <Typography variant="body2" className={styles.label}>
                                    Description:
                                </Typography>
                                <Typography variant="body2" className={styles.value}>
                                    {currentStrategy.description}
                                </Typography>
                            </Box>
                            <Box className={styles.infoRow}>
                                <Typography variant="body2" className={styles.label}>
                                    Win Rate:
                                </Typography>
                                <Chip
                                    label={currentStrategy.winRate}
                                    size="small"
                                    style={{ backgroundColor: currentStrategy.color, color: '#fff' }}
                                />
                            </Box>
                        </Box>
                    )}
                    <Box className={styles.aiStatus}>
                        <Typography variant="caption" color="text.secondary">
                            💡 AI will make betting and playing decisions automatically
                        </Typography>
                    </Box>
                </Box>
            )}
            {!aiMode && (
                <Box className={styles.manualMode}>
                    <Typography variant="body2" color="text.secondary" >
                        Enable AI to watch optimal blackjack strategy in action
                    </Typography>
                </Box>
            )}
        </Paper>
    );
};

export default AIControls;