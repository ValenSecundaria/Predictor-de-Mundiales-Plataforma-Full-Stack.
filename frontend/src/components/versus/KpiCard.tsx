import { Box, Text, VStack } from '@chakra-ui/react';

interface KpiCardProps {
    label: string;
    value: string | number;
    subValue?: string;
    color?: string;
}

export const KpiCard = ({ label, value, subValue, color = "white" }: KpiCardProps) => (
    <Box
        bg="rgba(10,10,10,0.6)"
        border="1px solid"
        borderColor="gray.800"
        _hover={{ borderColor: '#7F00FF', boxShadow: '0 0 20px rgba(127, 0, 255, 0.15)' }}
        borderRadius="xl"
        p={6}
        textAlign="center"
        transition="all 0.3s"
        backdropFilter="blur(10px)"
    >
        <VStack spacing={1}>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="widest" fontWeight="semibold">{label}</Text>
            <Text fontSize="4xl" fontWeight="bold" color={color} style={{ fontVariantNumeric: 'tabular-nums' }}>{value}</Text>
            {subValue && <Text fontSize="xs" color="gray.500">{subValue}</Text>}
        </VStack>
    </Box>
);
