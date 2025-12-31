export interface ApiGoal {
    name: string;
    minute: number;
}

export interface ApiMatch {
    team_a: string;
    team_b: string;
    team_a_code: string;
    team_b_code: string;
    score_a: number;
    score_b: number;
    goals: ApiGoal[];
    year: string;
    competition: string;
    id: number;
    date: string;
    stage: string;
}

export interface TeamGroupInfo {
    name: string;
    code: string;
}

export interface HeadToHeadStats {
    total_matches: number;
    wins_a: number;
    wins_b: number;
    draws: number;
    goals_a: number;
    goals_b: number;
    recent_matches: ApiMatch[];
}

export interface GoalStats {
    global: {
        goals_for: number;
        goals_against: number;
        matches_played: number;
        avg_goals_for: number;
        avg_goals_against: number;
        goal_difference: number;
    };
    by_competition: {
        [key: string]: {
            goals_for: number;
            goals_against: number;
            matches_played: number;
            avg_goals_for: number;
            avg_goals_against: number;
            goal_difference: number;
        };
    };
}

export interface StreakStats {
    current_streak: {
        type: 'W' | 'D' | 'L' | null;
        count: number;
    };
    longest_streaks: {
        W: number;
        D: number;
        L: number;
        Unbeaten: number;
    };
    transitions: {
        [key: string]: {
            W: number;
            D: number;
            L: number;
            sample_size: number;
        };
    };
    total_matches: number;
}

export interface HomeAwayStats {
    home: {
        matches_played: number;
        wins: number;
        draws: number;
        losses: number;
        goals_for: number;
        goals_against: number;
        win_percentage: number;
        avg_goals_for: number;
        avg_goals_against: number;
    };
    away: {
        matches_played: number;
        wins: number;
        draws: number;
        losses: number;
        goals_for: number;
        goals_against: number;
        win_percentage: number;
        avg_goals_for: number;
        avg_goals_against: number;
    };
}

export interface MomentumStats {
    current_momentum: number;
    history: {
        opponent: string;
        result: 'W' | 'D' | 'L';
        points: number;
        year: string;
        competition: string;
        momentum_score: number;
    }[];
}

export interface GraphStats {
    indirect_wins: {
        intermediate_team: string;
        indirect_victim: string;
        intermediate_code: string;
        indirect_victim_code: string;
    }[];
    total_indirect_wins: number;
}

export interface GoalPercentageStats {
    available: boolean;
    goals_per_match?: number;
    total_goals?: number;
    matches_played?: number;
    message?: string;
}

export interface EffectivenessStats {
    available: boolean;
    effectiveness_percentage?: number;
    message?: string;
}

export interface PossessionStats {
    available: boolean;
    possession_3rd_quarter_avg?: number;
    message?: string;
}
