import React from 'react';
import {
  Box,
  Heading,
  Text,
  Button,
  SimpleGrid,
  Container,
  Stack,
  Flex
} from '@chakra-ui/react';
import Link from 'next/link';

import SearchHeader from '../components/SearchHeader';
import PlayerBanner from '../components/PlayerBanner';

// Custom Neon Colors
const NEON_PURPLE = '#a855f7'; // Purple-500 equivalent
const NEON_MAGENTA = '#d946ef'; // Fuchsia-500 equivalent

export default function Page() {
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

        {/* HEADER (Client Component for Search) */}
        <SearchHeader />

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
            targetUrl="/equipo-ganador"
          />
          <PlayerBanner img="baseball.png" sport="Baseball" />
          <PlayerBanner img="voleyball.png" sport="Volleyball" />
          <PlayerBanner img="basketball.png" sport="Basketball" />
        </SimpleGrid>

        {/* CALL TO ACTION (FOOTER) */}
        <Flex justify="center" pb={10}>
          <Link href="/equipo-ganador">
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
            >
              Play Now!
            </Button>
          </Link>
        </Flex>

      </Container>
    </Box>
  );
}
