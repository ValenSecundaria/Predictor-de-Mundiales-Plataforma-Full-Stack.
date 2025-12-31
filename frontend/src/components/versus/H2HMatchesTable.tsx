import { Table, Thead, Tbody, Tr, Th, Td, Box, Text, Badge } from '@chakra-ui/react';
import { ApiMatch } from '../../types';

interface H2HMatchesTableProps {
    matches: ApiMatch[];
}

export const H2HMatchesTable = ({ matches }: H2HMatchesTableProps) => {
    return (
        <Box overflowX="auto" border="1px solid" borderColor="gray.800" borderRadius="xl" bg="rgba(0,0,0,0.4)">
            <Table variant="simple" size="sm">
                <Thead bg="whiteAlpha.100">
                    <Tr>
                        <Th color="gray.400" borderColor="gray.800" py={4}>Año</Th>
                        <Th color="gray.400" borderColor="gray.800">Instancia</Th>
                        <Th color="gray.400" borderColor="gray.800">Partido</Th>
                        <Th color="gray.400" isNumeric borderColor="gray.800">Score</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {matches.length === 0 ? (
                        <Tr>
                            <Td colSpan={4} textAlign="center" py={8} color="gray.500" borderColor="gray.800">
                                No hay partidos registrados
                            </Td>
                        </Tr>
                    ) : (
                        matches.map((m) => (
                            <Tr key={m.id} _hover={{ bg: 'whiteAlpha.50' }} transition="background 0.2s">
                                <Td color="gray.300" borderColor="gray.800" fontWeight="bold">{m.year}</Td>
                                <Td color="gray.500" fontSize="xs" borderColor="gray.800">{m.stage || m.competition}</Td>
                                <Td borderColor="gray.800">
                                    <Text color="gray.200" as="span">{m.team_a}</Text>
                                    <Text color="gray.600" as="span" mx={2} fontSize="xs">vs</Text>
                                    <Text color="gray.200" as="span">{m.team_b}</Text>
                                </Td>
                                <Td isNumeric fontWeight="bold" color="#a855f7" borderColor="gray.800" fontSize="md">
                                    {m.score_a} - {m.score_b}
                                </Td>
                            </Tr>
                        ))
                    )}
                </Tbody>
            </Table>
        </Box>
    );
};
