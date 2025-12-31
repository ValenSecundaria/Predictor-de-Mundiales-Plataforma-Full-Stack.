import { Box, Flex, Tooltip, Text } from '@chakra-ui/react';

interface H2HChartProps {
    winsA: number;
    draws: number;
    winsB: number;
    teamA: string;
    teamB: string;
}

export const H2HChart = ({ winsA, draws, winsB, teamA, teamB }: H2HChartProps) => {
    const total = winsA + draws + winsB;
    const pA = total > 0 ? (winsA / total) * 100 : 0;
    const pD = total > 0 ? (draws / total) * 100 : 0;
    const pB = total > 0 ? (winsB / total) * 100 : 0;

    return (
        <Box w="full" mt={8} p={6} bg="rgba(255,255,255,0.02)" borderRadius="xl" border="1px solid" borderColor="gray.800">
            <Flex justify="space-between" mb={4} fontSize="sm" fontWeight="bold">
                <Text color="#7F00FF">{teamA.toUpperCase()} ({winsA})</Text>
                <Text color="gray.500">EMPATES ({draws})</Text>
                <Text color="#FF0080">{teamB.toUpperCase()} ({winsB})</Text>
            </Flex>
            <Flex h="32px" w="full" borderRadius="md" overflow="hidden" bg="gray.900" position="relative">
                {total === 0 ? (
                    <Box w="100%" bg="gray.800" display="flex" alignItems="center" justifyContent="center">
                        <Text fontSize="xs" color="gray.600">Sin datos</Text>
                    </Box>
                ) : (
                    <>
                        {pA > 0 && (
                            <Tooltip label={`${teamA}: ${winsA} (${pA.toFixed(1)}%)`}>
                                <Box w={`${pA}%`} bgGradient="linear(to-r, #6A00D6, #7F00FF)" transition="width 0.5s" />
                            </Tooltip>
                        )}
                        {pD > 0 && (
                            <Tooltip label={`Empates: ${draws} (${pD.toFixed(1)}%)`}>
                                <Box w={`${pD}%`} bg="gray.700" transition="width 0.5s" borderLeft="1px solid #000" borderRight="1px solid #000" />
                            </Tooltip>
                        )}
                        {pB > 0 && (
                            <Tooltip label={`${teamB}: ${winsB} (${pB.toFixed(1)}%)`}>
                                <Box w={`${pB}%`} bgGradient="linear(to-r, #FF0080, #D6006A)" transition="width 0.5s" />
                            </Tooltip>
                        )}
                    </>
                )}
            </Flex>
        </Box>
    );
};
