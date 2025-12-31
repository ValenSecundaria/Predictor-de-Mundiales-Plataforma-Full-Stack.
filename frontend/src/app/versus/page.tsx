'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Box, Container, Grid, Text, Spinner, Flex, useToast, Heading } from '@chakra-ui/react';
import { VersusHeader } from '../../components/versus/VersusHeader';
import { TeamSelector } from '../../components/versus/TeamSelector';
import { KpiCard } from '../../components/versus/KpiCard';
import { H2HChart } from '../../components/versus/H2HChart';
import { GoalsTrendChart } from '../../components/versus/GoalsTrendChart';
import { H2HMatchesTable } from '../../components/versus/H2HMatchesTable';
import { ApiMatch } from '../../types';

interface Team { name: string; code: string; }

export default function VersusPage() {
    const [allMatches, setAllMatches] = useState<ApiMatch[]>([]);
    const [teams, setTeams] = useState<Team[]>([]);
    const [teamA, setTeamA] = useState<Team | null>(null);
    const [teamB, setTeamB] = useState<Team | null>(null);
    const [loading, setLoading] = useState(true);
    const toast = useToast();

    // Init: Fetch all matches to build team list
    useEffect(() => {
        async function init() {
            try {
                // Initial fetch
                const res = await fetch('http://localhost:8000/api/v1/matches?page=1&pageSize=100');
                if (!res.ok) throw new Error('Failed to load matches');
                const json = await res.json();
                let allData = json.data as ApiMatch[];
                const totalPages = json.meta.totalPages;

                if (totalPages > 1) {
                    const promises = [];
                    for (let p = 2; p <= totalPages; p++) {
                        promises.push(
                            fetch(`http://localhost:8000/api/v1/matches?page=${p}&pageSize=100`)
                                .then(r => r.json())
                                .then(d => d.data)
                        );
                    }
                    const results = await Promise.all(promises);
                    results.forEach(chunk => {
                        if (chunk) allData = allData.concat(chunk);
                    });
                }

                setAllMatches(allData);

                // Extract teams
                const teamMap = new Map<string, string>();
                allData.forEach(m => {
                    if (m.team_a_code && m.team_a) teamMap.set(m.team_a_code, m.team_a);
                    if (m.team_b_code && m.team_b) teamMap.set(m.team_b_code, m.team_b);
                });

                const teamList = Array.from(teamMap.entries()).map(([code, name]) => ({ code, name }));
                teamList.sort((a, b) => a.name.localeCompare(b.name));
                setTeams(teamList);
            } catch (e) {
                toast({ title: 'Error cargando datos', description: 'No se pudieron obtener los equipos.', status: 'error' });
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        init();
    }, [toast]);

    // Derived State
    const filteredMatches = useMemo(() => {
        if (!teamA || !teamB) return [];
        return allMatches.filter(m =>
            (m.team_a_code.toLowerCase() === teamA.code.toLowerCase() && m.team_b_code.toLowerCase() === teamB.code.toLowerCase()) ||
            (m.team_a_code.toLowerCase() === teamB.code.toLowerCase() && m.team_b_code.toLowerCase() === teamA.code.toLowerCase())
        ).sort((a, b) => {
            if (b.year !== a.year) return b.year.localeCompare(a.year);
            return (b.date || '').localeCompare(a.date || '');
        });
    }, [allMatches, teamA, teamB]);

    const stats = useMemo(() => {
        if (!teamA || !teamB) return null;
        let winsA = 0;
        let winsB = 0;
        let draws = 0;
        let goalsA = 0;
        let goalsB = 0;

        filteredMatches.forEach(m => {
            // Determine who is A in this specific match
            const isAHome = m.team_a_code.toLowerCase() === teamA.code.toLowerCase();
            const scoreA = isAHome ? m.score_a : m.score_b;
            const scoreB = isAHome ? m.score_b : m.score_a;

            goalsA += scoreA;
            goalsB += scoreB;

            if (scoreA > scoreB) winsA++;
            else if (scoreB > scoreA) winsB++;
            else draws++;
        });

        return { winsA, winsB, draws, goalsA, goalsB, total: filteredMatches.length };
    }, [filteredMatches, teamA, teamB]);

    return (
        <Box minH="100vh" bg="#050505" color="white" pb={20}>
            <Container maxW="container.xl">
                <VersusHeader />

                <Grid templateColumns={{ base: '1fr', md: '1fr 1fr' }} gap={8} mb={10}>
                    <TeamSelector
                        teams={teams}
                        selected={teamA}
                        onSelect={setTeamA}
                        placeholder="Seleccionar Equipo A"
                        exclude={teamB}
                    />
                    <TeamSelector
                        teams={teams}
                        selected={teamB}
                        onSelect={setTeamB}
                        placeholder="Seleccionar Equipo B"
                        exclude={teamA}
                    />
                </Grid>

                {loading && <Flex justify="center" py={20}><Spinner color="#a855f7" size="xl" /></Flex>}

                {!loading && teamA && teamB && stats && (
                    <Box animation="fadeIn 0.5s" sx={{ '@keyframes fadeIn': { from: { opacity: 0 }, to: { opacity: 1 } } }}>
                        {/* Summary KPIs */}
                        <Grid templateColumns={{ base: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(5, 1fr)' }} gap={4} mb={8}>
                            <KpiCard label="Partidos" value={stats.total} color="white" />
                            <KpiCard label={`Victorias ${teamA.name}`} value={stats.winsA} color="#a855f7" />
                            <KpiCard label="Empates" value={stats.draws} color="gray.400" />
                            <KpiCard label={`Victorias ${teamB.name}`} value={stats.winsB} color="#d946ef" />
                            <KpiCard label="Goles Totales" value={stats.goalsA + stats.goalsB} subValue={stats.total > 0 ? `Promedio: ${((stats.goalsA + stats.goalsB) / stats.total).toFixed(2)}` : '0.00'} />
                        </Grid>

                        {/* Chart */}
                        <H2HChart winsA={stats.winsA} draws={stats.draws} winsB={stats.winsB} teamA={teamA.name} teamB={teamB.name} />

                        <GoalsTrendChart matches={filteredMatches} teamA={teamA} teamB={teamB} />

                        {/* Matches List */}
                        <Box mt={12}>
                            <Text fontSize="2xl" fontWeight="bold" mb={6} borderLeft="4px solid #7F00FF" pl={3}>Historial de Partidos</Text>
                            <H2HMatchesTable matches={filteredMatches} />
                        </Box>

                        {stats.total === 0 && (
                            <Text textAlign="center" color="gray.500" mt={4} fontSize="sm">
                                No se encontraron partidos registrados entre {teamA.name} y {teamB.name} en la base de datos de Mundiales.
                            </Text>
                        )}

                        <Text textAlign="center" color="gray.800" fontSize="xs" mt={20}>
                            Database contains {allMatches.length} matches.
                        </Text>
                    </Box>
                )}

                {!loading && (!teamA || !teamB) && (
                    <Box textAlign="center" py={20} border="1px dashed" borderColor="gray.800" borderRadius="xl" bg="rgba(255,255,255,0.02)">
                        <Text color="gray.500" fontSize="lg">Selecciona dos equipos para ver la comparativa</Text>
                    </Box>
                )}
            </Container>
        </Box>
    );
}
