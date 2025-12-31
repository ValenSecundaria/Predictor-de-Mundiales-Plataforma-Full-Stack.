'use client';

import { Box, Img } from '@chakra-ui/react';
import { useRouter } from 'next/navigation';

// Custom Neon Colors
const NEON_PURPLE = '#a855f7';
const NEON_MAGENTA = '#d946ef';
const DEEP_PURPLE = '#581c87';

interface PlayerBannerProps {
    img: string;
    sport: string;
    targetUrl?: string; // Optional URL to navigate to
}

export default function PlayerBanner({ img, sport, targetUrl }: PlayerBannerProps) {
    const router = useRouter();

    const handleClick = () => {
        if (targetUrl) {
            router.push(targetUrl);
        }
    };

    return (
        <Box
            w="full"
            h={{ base: "300px", md: "400px" }}
            position="relative"
            filter={`drop-shadow(0 0 8px ${NEON_PURPLE})`}
            transition="all 0.4s ease-in-out"
            _hover={{ transform: 'translateY(-10px) scale(1.02)', filter: `drop-shadow(0 0 15px ${NEON_MAGENTA})` }}
            role="group"
            cursor={targetUrl ? "pointer" : "default"}
            onClick={handleClick}
        >
            {/* Jagged Container */}
            <Box
                w="full"
                h="full"
                // Deep purple textured background simulation
                bgGradient={`linear(to-b, ${DEEP_PURPLE}, black)`}
                // Jagged jagged clip-path for top and bottom
                clipPath="polygon(
          0% 5%, 10% 0%, 20% 5%, 30% 0%, 40% 5%, 50% 0%, 60% 5%, 70% 0%, 80% 5%, 90% 0%, 100% 5%, 
          100% 95%, 90% 100%, 80% 95%, 70% 100%, 60% 95%, 50% 100%, 40% 95%, 30% 100%, 20% 95%, 10% 100%, 0% 95%
        )"
                display="flex"
                alignItems="center"
                justifyContent="center"
                overflow="hidden"
                position="relative"
                _before={{
                    content: '""',
                    position: 'absolute',
                    inset: 0,
                    bgImage: 'radial-gradient(circle at center, rgba(168, 85, 247, 0.4) 0%, transparent 70%)',
                    opacity: 0.6,
                }}
            >
                {/* Player Silhouette */}
                <Img
                    src={`/${img}`}
                    alt={sport}
                    h="85%"
                    objectFit="contain"
                    zIndex={1}
                    filter="brightness(1.2) drop-shadow(0 0 10px rgba(217, 70, 239, 0.5))"
                    transition="transform 0.5s"
                    _groupHover={{ transform: 'scale(1.1)' }}
                />
            </Box>
        </Box>
    );
}
