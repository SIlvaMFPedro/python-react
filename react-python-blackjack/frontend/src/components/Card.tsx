import React from 'react';
import { Box } from '@mui/material';
import { type Card as CardType } from "../utils/utils.ts";
import styles from '../styles/Card.module.scss';

interface CardProps {
    card: CardType;
    faceDown?: boolean;
    animate?: boolean;
    delay?: number;
}

const renderCenterPattern = (rank: string, suit: string) => {
    /**
     * Render suit pattern based on rank
     */
    // Ace - large single suit
    if (rank === 'A') {
        return <span className={styles.largeSuit}>{suit}</span>;
    }
    // Face cards - show letter only
    if(['J', 'Q', 'K'].includes(rank)) {
        return <span className={styles.faceCard}>{rank}</span>;
    }
    // Number cards - show just center suits(s), not all
    const num = parseInt(rank);
    // For cards 2-10, show minimal center pattern
    if (num === 2 || num === 3) {
        return (
            <Box className={styles.suitPatternVertical}>
                {Array.from({ length: num }).map((_, i) => (
                    <span key={i} className={styles.mediumSuit}>{suit}</span>
                ))}
            </Box>
        );
    }
    // For 4-10, just show a center suit (keeps card clean)
    return <span className={styles.mediumSuit}>{suit}</span>
};

const Card: React.FC<CardProps> = ({ card, faceDown = false, animate = false, delay = 0 }) => {
    // const isRed = card.suit && CARD_COLORS.red.includes(card.suit);
    const isRed = card.suit && (card.suit === '♥' || card.suit === '♦');
    const isHidden = card.hidden || faceDown;

    return (
        <Box
            className={`${styles.card} ${isHidden ? styles.faceDown : styles.faceUp} ${animate ? styles.animate : ''}`}
            style={{ animationDelay: `${delay}ms` }}
        >
            {!isHidden ? (
                <Box className={`${styles.cardFront} ${isRed ? styles.red : styles.black}`}>
                    {/* Top left corner */}
                    <Box className={styles.corner}>
                        <Box className={styles.rank}>{card.rank}</Box>
                        <Box className={styles.suit}>{card.suit}</Box>
                    </Box>

                    {/* Center suit */}
                    <Box className={styles.centerSuit}>
                        {renderCenterPattern(card.rank, card.suit)}
                    </Box>

                    {/* Bottom right corner (upside down) */}
                    <Box className={`${styles.corner} ${styles.bottomRight}`}>
                        <Box className={styles.rank}>{card.rank}</Box>
                        <Box className={styles.suit}>{card.suit}</Box>
                    </Box>
                </Box>
            ) : (
                <Box className={styles.cardBack}>
                    <Box className={styles.backPattern} />
                </Box>
            )}
        </Box>
    );
};

export default Card;