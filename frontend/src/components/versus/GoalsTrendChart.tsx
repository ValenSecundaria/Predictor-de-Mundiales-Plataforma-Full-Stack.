import { Box, Flex, Text, Tooltip } from '@chakra-ui/react';
import { ApiMatch } from '../../types';

interface GoalsTrendChartProps {
    matches: ApiMatch[];
    teamA: { name: string; code: string };
    teamB: { name: string; code: string };
}

export const GoalsTrendChart = ({ matches, teamA, teamB }: GoalsTrendChartProps) => {
    // Deduplicate matches by ID and sort chronologically
    const uniqueMatches = matches.filter((m, index, self) =>
        index === self.findIndex((t) => t.id === m.id)
    );
    const sortedMatches = [...uniqueMatches].sort((a, b) => a.year.localeCompare(b.year) || (a.date || '').localeCompare(b.date || ''));

    if (sortedMatches.length === 0) return null;

    const maxGoals = Math.max(
        ...sortedMatches.map(m => Math.max(m.score_a, m.score_b)),
        1
    );

    // Generate Y-axis ticks (integers only)
    const yTicks = Array.from({ length: maxGoals + 1 }, (_, i) => i);

    return (
        <Box
            w="full"
            p={6}
            bg="rgba(10,10,10,0.4)"
            borderRadius="xl"
            border="1px solid"
            borderColor="gray.800"
            mt={8}
            position="relative"
        >
            <Text fontSize="md" fontWeight="bold" mb={6} color="gray.300">
                Tendencia de Goles por Partido
            </Text>

            <Flex position="relative" height="240px">
                {/* Y-Axis Labels & Grid Lines */}
                <Box position="absolute" left="0" top="0" bottom="30px" w="100%" pointerEvents="none" zIndex={1}>
                    {yTicks.map((tick) => (
                        <Box
                            key={tick}
                            position="absolute"
                            bottom={`${(tick / maxGoals) * 100}%`}
                            w="100%"
                            borderBottom={tick === 0 ? "1px solid" : "1px dashed"}
                            borderColor={tick === 0 ? "gray.600" : "rgba(255,255,255,0.05)"}
                        >
                            <Text
                                position="absolute"
                                left="-25px"
                                transform="translateY(50%)"
                                fontSize="xs"
                                color="gray.500"
                                w="20px"
                                textAlign="right"
                            >
                                {tick}
                            </Text>
                        </Box>
                    ))}
                    {/* Y-axis vertical line */}
                    <Box position="absolute" left="0" top="0" bottom="0" w="1px" bg="gray.600" />
                </Box>

                {/* Chart Area */}
                <Box ml={8} w="full" h="100%" overflowX="auto" sx={{ '&::-webkit-scrollbar': { height: '6px' }, '&::-webkit-scrollbar-thumb': { bg: 'gray.700', borderRadius: 'full' } }}>
                    <Flex
                        h="100%"
                        alignItems="flex-end"
                        justifyContent={sortedMatches.length > 5 ? "flex-start" : "center"} // Center if few items, Start if many (for scroll)
                        gap={12} // Increased Gap for separation
                        pb="30px" // Space for labels
                        px={4}
                        minW="fit-content"
                    >
                        {sortedMatches.map((m) => {
                            const isAHome = m.team_a_code.toLowerCase() === teamA.code.toLowerCase();
                            const goalsA = isAHome ? m.score_a : m.score_b;
                            const goalsB = isAHome ? m.score_b : m.score_a;

                            const hA = (goalsA / maxGoals) * 100;
                            const hB = (goalsB / maxGoals) * 100;

                            return (
                                <Tooltip key={m.id} label={`${m.year}: ${teamA.name} ${goalsA} - ${goalsB} ${teamB.name}`} hasArrow bg="gray.900" color="white">
                                    <Flex
                                        direction="column"
                                        justify="flex-end"
                                        h="100%"
                                        minW="40px"
                                        maxW="60px"
                                        position="relative"
                                        role="group"
                                    >
                                        <Flex justify="center" align="flex-end" h="100%" gap={1} w="full">
                                            {/* Bar A */}
                                            <Box
                                                w="40%"
                                                h={`${Math.max(hA, 0)}%`}
                                                bg={goalsA >= goalsB ? '#a855f7' : '#a855f7'}
                                                opacity={goalsA >= goalsB ? 1 : 0.6}
                                                borderTopRadius="sm"
                                                transition="all 0.3s"
                                                _groupHover={{ opacity: 1, filter: 'brightness(1.2)' }}
                                                position="relative"
                                            />
                                            {/* Bar B */}
                                            <Box
                                                w="40%"
                                                h={`${Math.max(hB, 0)}%`}
                                                bg={goalsB >= goalsA ? '#d946ef' : '#d946ef'}
                                                opacity={goalsB >= goalsA ? 1 : 0.6}
                                                borderTopRadius="sm"
                                                transition="all 0.3s"
                                                _groupHover={{ opacity: 1, filter: 'brightness(1.2)' }}
                                                position="relative"
                                            />
                                        </Flex>

                                        {/* X-Axis Label */}
                                        <Text
                                            position="absolute"
                                            bottom="-25px"
                                            left="0"
                                            right="0"
                                            fontSize="10px"
                                            color="gray.500"
                                            textAlign="center"
                                        >
                                            {m.year}
                                        </Text>
                                    </Flex>
                                </Tooltip>
                            );
                        })}
                    </Flex>
                </Box>
            </Flex>

            {/* Legend */}
            <Flex mt={6} justify="center" gap={6} fontSize="xs" color="gray.400">
                <Flex align="center" gap={2}>
                    <Box w="10px" h="10px" bg="#a855f7" borderRadius="sm" />
                    <Text>{teamA.name}</Text>
                </Flex>
                <Flex align="center" gap={2}>
                    <Box w="10px" h="10px" bg="#d946ef" borderRadius="sm" />
                    <Text>{teamB.name}</Text>
                </Flex>
            </Flex>
        </Box>
    );
};
