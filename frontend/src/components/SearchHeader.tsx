'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Flex,
    Text,
    Input,
    InputGroup,
    InputLeftElement,
    HStack,
    Link as ChakraLink,
    List,
    ListItem,
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
import { useRouter } from 'next/navigation';

// Custom Neon Colors
const NEON_PURPLE = '#a855f7';
const NEON_MAGENTA = '#d946ef';
const DEEP_PURPLE = '#581c87';

interface Team {
    name: string;
    code: string;
}

export default function SearchHeader() {
    const router = useRouter();
    const [teams, setTeams] = useState<Team[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [filteredTeams, setFilteredTeams] = useState<Team[]>([]);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetch('http://localhost:8000/api/v1/teams')
            .then(res => res.json())
            .then(data => setTeams(data))
            .catch(err => console.error('Error fetching teams:', err));

        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSearch = (query: string) => {
        setSearchQuery(query);
        if (!query.trim()) {
            setFilteredTeams([]);
            setIsDropdownOpen(false);
            return;
        }

        const filtered = teams.filter(team =>
            team.name.toLowerCase().includes(query.toLowerCase()) ||
            team.code.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 8);

        setFilteredTeams(filtered);
        setIsDropdownOpen(filtered.length > 0);
    };

    const handleSelectTeam = (team: Team) => {
        setSearchQuery(team.name);
        setIsDropdownOpen(false);
        // Optional: Navigate to team details or prediction page if needed
        // router.push(`/analisis/${team.code}`); 
    };

    return (
        <Flex
            as="header"
            align="center"
            justify="space-between"
            wrap="wrap"
            gap={6}
            mb={16}
        >
            {/* Logo */}
            <Flex align="center">
                <Box
                    w="80px"
                    h="80px"
                    borderRadius="full"
                    border={`3px solid ${NEON_PURPLE}`}
                    boxShadow={`0 0 15px ${NEON_PURPLE}, inset 0 0 10px ${NEON_PURPLE}`}
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    bg="blackAlpha.800"
                    cursor="pointer"
                    onClick={() => router.push('/')}
                >
                    <Text
                        fontWeight="bold"
                        textAlign="center"
                        lineHeight="1.2"
                        fontSize="sm"
                        textShadow={`0 0 5px ${NEON_PURPLE}`}
                    >
                        SPORTS<br />HUB
                    </Text>
                </Box>
            </Flex>

            {/* Search Bar */}
            <Box flex={1} maxW="500px" position="relative" ref={dropdownRef} zIndex={50}>
                <InputGroup size="lg">
                    <InputLeftElement pointerEvents="none">
                        <SearchIcon color="white" />
                    </InputLeftElement>
                    <Input
                        type="text"
                        placeholder="search country..."
                        value={searchQuery}
                        onChange={(e) => handleSearch(e.target.value)}
                        onFocus={() => searchQuery.trim() && setIsDropdownOpen(true)}
                        borderRadius="full"
                        borderColor={NEON_PURPLE}
                        borderWidth="2px"
                        bg="blackAlpha.800"
                        color="white"
                        boxShadow={`0 0 10px ${NEON_PURPLE}`}
                        _hover={{ borderColor: NEON_MAGENTA, boxShadow: `0 0 15px ${NEON_MAGENTA}` }}
                        _focus={{ borderColor: NEON_MAGENTA, boxShadow: `0 0 20px ${NEON_MAGENTA}`, outline: 'none' }}
                        _placeholder={{ color: 'gray.300', fontStyle: 'italic' }}
                    />
                </InputGroup>

                {/* Dropdown Results */}
                {isDropdownOpen && (
                    <Box
                        position="absolute"
                        top="100%"
                        left="0"
                        right="0"
                        mt={2}
                        bg="#0a0a0a"
                        border={`2px solid ${NEON_PURPLE}`}
                        borderRadius="xl"
                        overflow="hidden"
                        zIndex={100}
                        boxShadow={`0 10px 30px rgba(0,0,0,0.8), 0 0 20px ${NEON_PURPLE}`}
                        backdropFilter="blur(15px)"
                    >
                        <List spacing={0}>
                            {filteredTeams.map((team) => (
                                <ListItem
                                    key={team.code}
                                    px={4}
                                    py={3}
                                    cursor="pointer"
                                    transition="all 0.2s"
                                    _hover={{ bg: DEEP_PURPLE, color: NEON_MAGENTA }}
                                    onClick={() => handleSelectTeam(team)}
                                >
                                    <Flex align="center">
                                        <Text fontWeight="bold">{team.name}</Text>
                                        <Text ml={3} fontSize="xs" color="gray.400" border="1px solid" borderColor="gray.600" px={1} borderRadius="sm">
                                            {team.code}
                                        </Text>
                                    </Flex>
                                </ListItem>
                            ))}
                        </List>
                    </Box>
                )}
            </Box>

            {/* Navigation */}
            <HStack spacing={8} display={{ base: 'none', md: 'flex' }}>
                {['MAIN', 'OFFERS', 'PRODUCTS', 'ABOUT'].map((item) => (
                    <ChakraLink
                        key={item}
                        href="#"
                        fontSize="lg"
                        fontWeight="semibold"
                        color="gray.100"
                        _hover={{ color: NEON_MAGENTA, textDecoration: 'none', textShadow: `0 0 8px ${NEON_MAGENTA}` }}
                        transition="all 0.3s"
                    >
                        {item}
                    </ChakraLink>
                ))}
            </HStack>
        </Flex>
    );
}
