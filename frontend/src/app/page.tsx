'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Input,
  InputGroup,
  InputLeftElement,
  Button,
  Img,
  SimpleGrid,
  Container,
  HStack,
  Stack,
  Link as ChakraLink,
  List,
  ListItem,
} from '@chakra-ui/react';
import { useRouter } from 'next/navigation';
import { SearchIcon } from '@chakra-ui/icons';

// Custom Neon Colors
const NEON_PURPLE = '#a855f7'; // Purple-500 equivalent
const NEON_MAGENTA = '#d946ef'; // Fuchsia-500 equivalent
const DEEP_PURPLE = '#581c87';

interface Team {
  name: string;
  code: string;
}

const PlayerBanner = ({ img, sport, onClick }: { img: string, sport: string, onClick?: () => void }) => (
  <Box
    w="full"
    h={{ base: "300px", md: "400px" }}
    position="relative"
    filter={`drop-shadow(0 0 8px ${NEON_PURPLE})`}
    transition="all 0.4s ease-in-out"
    _hover={{ transform: 'translateY(-10px) scale(1.02)', filter: `drop-shadow(0 0 15px ${NEON_MAGENTA})` }}
    role="group"
    cursor="pointer"
    onClick={onClick}
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

export default function Page() {
  const router = useRouter();
  const [teams, setTeams] = useState<Team[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredTeams, setFilteredTeams] = useState<Team[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch teams for search
    fetch('http://localhost:8000/api/v1/teams')
      .then(res => res.json())
      .then(data => {
        setTeams(data);
      })
      .catch(err => console.error('Error fetching teams:', err));

    // Handle clicks outside dropdown to close it
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
    ).slice(0, 8); // Limit to 8 results for speed/clarity

    setFilteredTeams(filtered);
    setIsDropdownOpen(filtered.length > 0);
  };

  return (
    <Box
      minH="100vh"
      w="full"
      bg="black"
      bgImage="url('/assets/cosmic_bg.png')"
      bgSize="cover"
      bgPosition="center"
      bgRepeat="no-repeat"
      color="white"
      fontFamily="sans-serif"
      overflowX="hidden"
      position="relative"
    >
      {/* Overlay to darken background slightly if needed */}
      <Box position="absolute" inset="0" bg="blackAlpha.40" pointerEvents="none" />

      {/* Main Container */}
      <Container maxW="container.xl" position="relative" zIndex={2} pt={6} pb={20}>

        {/* HEADER */}
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
                      onClick={() => {
                        setSearchQuery(team.name);
                        setIsDropdownOpen(false);
                      }}
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

        {/* HERO SECTION */}
        <Stack spacing={4} textAlign="center" align="center" mb={16}>
          <Heading
            as="h1"
            fontSize={{ base: "4xl", md: "6xl", lg: "7xl" }}
            fontWeight="900"
            color="white"
            // Strong purple outer glow
            textShadow={`0 0 20px ${NEON_PURPLE}, 0 0 40px ${NEON_PURPLE}`}
            letterSpacing="wider"
            fontStyle="italic"
          >
            READY TO <Text as="span" color={NEON_MAGENTA}>PLAY.</Text>
          </Heading>
          <Text
            fontSize={{ base: "lg", md: "2xl" }}
            color="whiteAlpha.900"
            fontWeight="light"
            letterSpacing="wide"
          >
            All types of sports product available here!
          </Text>
        </Stack>

        {/* BANNERS */}
        <SimpleGrid
          columns={{ base: 1, sm: 2, lg: 4 }}
          spacing={8}
          mb={20}
          alignItems="center"
        >
          <PlayerBanner
            img="football.png"
            sport="Football"
            onClick={() => router.push('/equipo-ganador')}
          />
          <PlayerBanner img="baseball.png" sport="Baseball" />
          <PlayerBanner img="voleyball.png" sport="Volleyball" />
          <PlayerBanner img="basketball.png" sport="Basketball" />
        </SimpleGrid>

        {/* CALL TO ACTION (FOOTER) */}
        <Flex justify="center" pb={10}>
          <Button
            size="lg"
            px={16}
            py={8}
            fontSize="2xl"
            fontWeight="bold"
            borderRadius="full"
            bgGradient={`linear(to-r, ${NEON_PURPLE}, ${NEON_MAGENTA})`}
            color="white"
            border="2px solid white"
            boxShadow={`0 0 20px ${NEON_MAGENTA}, inset 0 0 10px white`}
            _hover={{
              transform: 'scale(1.05)',
              boxShadow: `0 0 30px ${NEON_MAGENTA}, inset 0 0 20px white`,
              bgGradient: `linear(to-r, ${NEON_MAGENTA}, ${NEON_PURPLE})`
            }}
            _active={{ transform: 'scale(0.95)' }}
            letterSpacing="1px"
            onClick={() => router.push('/equipo-ganador')}
          >
            Play Now!
          </Button>
        </Flex>

      </Container>
    </Box>
  );
}
