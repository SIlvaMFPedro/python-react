import React from 'react';
import { Box, Button, Stack, Tooltip } from '@mui/material';
import { PanTool, FrontHand, DoubleArrow, CallSplit, Flag, Security } from '@mui/icons-material';
import styles from '../styles/ActionButtons.module.scss';

interface ActionButtonsProps {
    canHit: boolean;
    canStand: boolean;
    canDouble: boolean;
    canSplit: boolean;
    canSurrender: boolean;
    canInsure: boolean;
    onHit: () => void;
    onStand: () => void;
    onDouble: () => void;
    onSplit: () => void;
    onSurrender: () => void;
    onInsurance: () => void;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({
    canHit,
    canStand,
    canDouble,
    canSplit,
    canSurrender,
    canInsure,
    onHit,
    onStand,
    onDouble,
    onSplit,
    onSurrender,
    onInsurance,
}) => {
    return (
        <Box className={styles.actionButtons}>
            <Stack direction="row" spacing={2} flexWrap="wrap" justifyContent="center">
                {/* HIT */}
                <Tooltip title="Take another card" arrow>
                    <span>
                        <Button
                            variant="contained"
                            color="primary"
                            size="large"
                            startIcon={<FrontHand />}
                            onClick={onHit}
                            disabled={!canHit}
                            className={styles.button}
                        >
                            Hit
                        </Button>
                    </span>
                </Tooltip>
                {/* STAND */}
                <Tooltip title="Keep your current hand" arrow>
                    <span>
                        <Button
                            variant="contained"
                            color="error"
                            size="large"
                            startIcon={<PanTool />}
                            onClick={onStand}
                            disabled={!canStand}
                            className={styles.button}
                        >
                            Stand
                        </Button>
                    </span>
                </Tooltip>
                {/* Double Down */}
                <Tooltip title="Double your bet and take one card" arrow>
                    <span>
                        <Button
                            variant="contained"
                            color="warning"
                            size="large"
                            startIcon={<DoubleArrow />}
                            onClick={onDouble}
                            disabled={!canDouble}
                            className={styles.button}
                        >
                            Double
                        </Button>
                    </span>
                </Tooltip>
                {/* Split */}
                {canSplit && (
                    <Tooltip title="Split pair into two hands" arrow>
                        <span>
                            <Button
                                variant="contained"
                                color="info"
                                size="large"
                                startIcon={<CallSplit/>}
                                onClick={onSplit}
                                disabled={!canSplit}
                                className={styles.button}
                            >
                                Split
                            </Button>
                        </span>
                    </Tooltip>
                )}
                {/* Surrender */}
                {canSurrender && (
                    <Tooltip title="Surrender and get half your bet back" arrow>
                        <span>
                            <Button
                                variant="contained"
                                color="secondary"
                                size="large"
                                startIcon={<Flag/>}
                                onClick={onSurrender}
                                disabled={!canSurrender}
                                className={styles.button}
                            >
                                Surrender
                            </Button>
                        </span>
                    </Tooltip>
                )}
                {/* Insurance */}
                {canInsure && (
                    <Tooltip title="Insure against dealer blackjack (costs half of your bet)" arrow>
                        <span>
                            <Button
                                variant="outlined"
                                color="success"
                                size="large"
                                startIcon={<Security/>}
                                onClick={onInsurance}
                                disabled={!canInsure}
                                className={styles.button}
                            ></Button>
                        </span>
                    </Tooltip>
                )}
            </Stack>
        </Box>
    );
};

export default ActionButtons;