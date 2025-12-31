import { Box, Heading, Text, VStack } from '@chakra-ui/react';

export const VersusHeader = () => (
    <VStack spacing={2} textAlign="center" py={10}>
        <Heading
            as="h1"
            size="3xl"
            bgGradient="linear(to-r, #7F00FF, #FF0080)"
            bgClip="text"
            letterSpacing="tighter"
            fontWeight="extrabold"
        >
            VS
        </Heading>
        <Text color="gray.400" fontSize="lg" maxW="md">
            Comparador Histórico de Selecciones
        </Text>
    </VStack>
);
