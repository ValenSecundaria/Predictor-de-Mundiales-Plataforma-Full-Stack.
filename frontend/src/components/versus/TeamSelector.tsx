import React, { useState, useEffect, useRef } from 'react';
import { Box, Input, List, ListItem, Text, InputGroup, InputLeftElement } from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';

interface Team {
    name: string;
    code: string;
}

interface TeamSelectorProps {
    teams: Team[];
    selected: Team | null;
    onSelect: (team: Team) => void;
    placeholder?: string;
    exclude?: Team | null;
}

export const TeamSelector = ({ teams, selected, onSelect, placeholder, exclude }: TeamSelectorProps) => {
    const [query, setQuery] = useState('');
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef<HTMLDivElement>(null);

    // Update query when selection changes
    useEffect(() => {
        if (selected) {
            setQuery(selected.name);
        } else {
            setQuery('');
        }
    }, [selected]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
                setIsOpen(false);
                // Reset query to selection if clicked outside without selecting
                if (selected) {
                    if (document.activeElement !== wrapperRef.current?.querySelector('input')) {
                        setQuery(selected.name);
                    }
                } else {
                    // if (!query) setQuery(''); 
                }
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [selected, query]);

    const filtered = teams.filter(t =>
        (t.name.toLowerCase().includes(query.toLowerCase()) || t.code.toLowerCase().includes(query.toLowerCase())) &&
        (exclude ? t.code !== exclude.code : true)
    );

    const handleSelect = (t: Team) => {
        onSelect(t);
        setQuery(t.name);
        setIsOpen(false);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setQuery(e.target.value);
        setIsOpen(true);
        // If user clears input, treat as de-select? Maybe not automatically, let them search matching "nothing" (all)
    };

    return (
        <Box position="relative" ref={wrapperRef} w="full">
            <InputGroup>
                <InputLeftElement pointerEvents="none">
                    <SearchIcon color="gray.500" />
                </InputLeftElement>
                <Input
                    placeholder={placeholder}
                    value={query} // Always controlled
                    onChange={handleInputChange}
                    onFocus={() => {
                        setIsOpen(true);
                        // Optional: Clear on focus if it matches selected to allow easy new search?
                        // For now keep it simple.
                    }}
                    bg="rgba(15,15,15,0.8)"
                    border="1px solid"
                    borderColor={selected ? "#a855f7" : "gray.800"}
                    color="white"
                    _placeholder={{ color: 'gray.600' }}
                    _focus={{ borderColor: '#a855f7', boxShadow: '0 0 0 1px #a855f7', bg: 'black' }}
                    height="50px"
                    fontSize="lg"
                    borderRadius="lg"
                />
            </InputGroup>
            {isOpen && filtered.length > 0 && (
                <List
                    position="absolute"
                    top="100%"
                    left={0}
                    right={0}
                    bg="#0a0a0a"
                    border="1px solid"
                    borderColor="gray.800"
                    borderRadius="lg"
                    mt={2}
                    zIndex={50}
                    maxH="300px"
                    overflowY="auto"
                    boxShadow="dark-lg"
                    css={{
                        '&::-webkit-scrollbar': {
                            width: '4px',
                        },
                        '&::-webkit-scrollbar-track': {
                            width: '6px',
                        },
                        '&::-webkit-scrollbar-thumb': {
                            background: '#333',
                            borderRadius: '24px',
                        },
                    }}
                >
                    {filtered.map(t => (
                        <ListItem
                            key={t.code}
                            px={4}
                            py={3}
                            borderBottom="1px solid"
                            borderColor="gray.900"
                            _last={{ borderBottom: 'none' }}
                            _hover={{ bg: '#151515', cursor: 'pointer', color: '#7F00FF' }}
                            onClick={() => handleSelect(t)}
                        >
                            <Text color="gray.200" fontWeight="medium">{t.name}</Text>
                        </ListItem>
                    ))}
                </List>
            )}
        </Box>
    );
};
