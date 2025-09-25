"""
Analytics API Namespace

Provides advanced analytics, insights, and statistical analysis
of election data across all elections.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter
from flask import request
from flask_restx import Namespace, Resource
from app.core.responses import APIResponse
from app.core.exceptions import NotFoundError
from app.core.logging_config import get_logger
from app.api.models import (
    electoral_statistics_model,
    trend_analysis_model,
    demographic_analysis_model,
    api_response_model,
    error_response_model
)

# Create namespace
analytics_ns = Namespace(
    'analytics',
    description='📊 Election Analytics & Insights API\n\nAdvanced analytics, statistical insights, and trend analysis of Indian election data.'
)

logger = get_logger("rajniti.api.analytics")

def load_all_analytics_data() -> Dict[str, Any]:
    """Load all election data for analytics"""
    all_data = {}
    data_root = Path("app/data")
    
    election_paths = {
        "lok-sabha-2024": data_root / "lok_sabha" / "lok-sabha-2024" / "candidates.json",
        "delhi-assembly-2025": data_root / "vidhan_sabha" / "DL_2025_ASSEMBLY" / "candidates.json", 
        "maharashtra-assembly-2024": data_root / "vidhan_sabha" / "MH_2024" / "candidates.json"
    }
    
    for election_id, candidates_file in election_paths.items():
        try:
            if candidates_file.exists():
                with open(candidates_file, 'r', encoding='utf-8') as f:
                    candidates = json.load(f)
                    all_data[election_id] = candidates
        except Exception as e:
            logger.warning(f"Failed to load {election_id}", error=str(e))
    
    return all_data

def calculate_vote_share_analysis(candidates: List[Dict]) -> Dict[str, Any]:
    """Calculate vote share analysis for candidates"""
    party_votes = {}
    total_votes = 0
    
    for candidate in candidates:
        party = candidate.get('Party', candidate.get('party', 'Unknown'))
        votes = candidate.get('Votes', candidate.get('votes', 0))
        
        if votes and str(votes).replace(',', '').isdigit():
            vote_count = int(str(votes).replace(',', ''))
            party_votes[party] = party_votes.get(party, 0) + vote_count
            total_votes += vote_count
    
    # Calculate vote share percentages
    party_vote_share = {}
    for party, votes in party_votes.items():
        vote_share = (votes / total_votes) * 100 if total_votes > 0 else 0
        party_vote_share[party] = {
            'votes': votes,
            'vote_share': round(vote_share, 2)
        }
    
    return {
        'total_votes': total_votes,
        'party_performance': party_vote_share,
        'top_parties': sorted(party_vote_share.items(), key=lambda x: x[1]['vote_share'], reverse=True)[:10]
    }

def analyze_victory_margins(candidates: List[Dict]) -> Dict[str, Any]:
    """Analyze victory margins across constituencies"""
    margins = []
    constituency_margins = {}
    
    # Group by constituency
    by_constituency = {}
    for candidate in candidates:
        const_code = candidate.get('Constituency Code', candidate.get('constituency_code', ''))
        if const_code not in by_constituency:
            by_constituency[const_code] = []
        by_constituency[const_code].append(candidate)
    
    # Calculate margins for each constituency
    for const_code, const_candidates in by_constituency.items():
        if len(const_candidates) >= 2:
            const_candidates.sort(
                key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '') or 0),
                reverse=True
            )
            
            votes1 = int(str(const_candidates[0].get('Votes', const_candidates[0].get('votes', 0))).replace(',', '') or 0)
            votes2 = int(str(const_candidates[1].get('Votes', const_candidates[1].get('votes', 0))).replace(',', '') or 0)
            margin = votes1 - votes2
            
            total_constituency_votes = sum(
                int(str(c.get('Votes', c.get('votes', 0))).replace(',', '') or 0) 
                for c in const_candidates
            )
            
            margin_percentage = (margin / total_constituency_votes) * 100 if total_constituency_votes > 0 else 0
            
            margins.append(margin)
            constituency_margins[const_code] = {
                'margin': margin,
                'margin_percentage': round(margin_percentage, 2),
                'winner': const_candidates[0].get('Name', const_candidates[0].get('name', '')),
                'runner_up': const_candidates[1].get('Name', const_candidates[1].get('name', ''))
            }
    
    if not margins:
        return {'error': 'No margin data available'}
    
    return {
        'total_constituencies': len(constituency_margins),
        'average_margin': round(sum(margins) / len(margins), 2),
        'median_margin': sorted(margins)[len(margins) // 2],
        'highest_margin': max(margins),
        'lowest_margin': min(margins),
        'close_contests': [
            {'constituency': k, **v} for k, v in constituency_margins.items() 
            if v['margin'] <= 5000  # Contests decided by ≤5000 votes
        ],
        'landslide_victories': [
            {'constituency': k, **v} for k, v in constituency_margins.items() 
            if v['margin'] >= 100000  # Victories by ≥100,000 votes
        ]
    }

def calculate_demographic_insights(candidates: List[Dict]) -> Dict[str, Any]:
    """Calculate demographic insights from candidate data"""
    # This is simplified - in real scenario, we'd have more demographic data
    insights = {
        'party_diversity': {},
        'gender_analysis': {'Male': 0, 'Female': 0, 'Unknown': 0},
        'winning_patterns': {},
        'constituency_competition': {}
    }
    
    # Party diversity analysis
    party_counts = Counter(candidate.get('Party', candidate.get('party', 'Unknown')) for candidate in candidates)
    insights['party_diversity'] = dict(party_counts.most_common(20))
    
    # Winning patterns by party
    for candidate in candidates:
        if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
            party = candidate.get('Party', candidate.get('party', 'Unknown'))
            insights['winning_patterns'][party] = insights['winning_patterns'].get(party, 0) + 1
    
    # Constituency competition (number of candidates per constituency)
    const_competition = Counter()
    for candidate in candidates:
        const_code = candidate.get('Constituency Code', candidate.get('constituency_code', ''))
        const_competition[const_code] += 1
    
    insights['constituency_competition'] = {
        'average_candidates_per_constituency': round(sum(const_competition.values()) / len(const_competition), 2) if const_competition else 0,
        'most_contested': const_competition.most_common(5),
        'least_contested': const_competition.most_common()[-5:] if len(const_competition) >= 5 else const_competition.most_common()
    }
    
    return insights

@analytics_ns.route('/overview')
class AnalyticsOverview(Resource):
    @analytics_ns.doc('get_analytics_overview')
    @analytics_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        📊 Get comprehensive analytics overview
        
        Returns high-level analytics and insights across all elections
        including key statistics, trends, and comparative analysis.
        """
        try:
            all_data = load_all_analytics_data()
            
            if not all_data:
                return APIResponse.success(
                    data={'message': 'No election data available for analysis'},
                    message="No analytics data available"
                )
            
            overview_analytics = {
                'summary': {
                    'total_elections_analyzed': len(all_data),
                    'total_candidates': sum(len(candidates) for candidates in all_data.values()),
                    'data_coverage': '2024-2025'
                },
                'by_election': {},
                'comparative_insights': {},
                'key_findings': []
            }
            
            # Analyze each election
            for election_id, candidates in all_data.items():
                election_analytics = {
                    'total_candidates': len(candidates),
                    'total_winners': len([c for c in candidates if c.get('Status') == 'WON' or c.get('status') == 'won']),
                    'unique_parties': len(set(c.get('Party', c.get('party', 'Unknown')) for c in candidates)),
                    'vote_share': calculate_vote_share_analysis(candidates),
                    'margin_analysis': analyze_victory_margins(candidates),
                    'demographic_insights': calculate_demographic_insights(candidates)
                }
                
                overview_analytics['by_election'][election_id] = election_analytics
            
            # Comparative insights
            if len(all_data) > 1:
                # Compare party performance across elections
                all_parties = set()
                for candidates in all_data.values():
                    all_parties.update(c.get('Party', c.get('party', 'Unknown')) for c in candidates)
                
                party_comparison = {}
                for party in list(all_parties)[:10]:  # Top 10 parties
                    party_comparison[party] = {}
                    for election_id, candidates in all_data.items():
                        party_candidates = [c for c in candidates if c.get('Party', c.get('party', '')) == party]
                        party_wins = len([c for c in party_candidates if c.get('Status') == 'WON' or c.get('status') == 'won'])
                        
                        party_comparison[party][election_id] = {
                            'candidates': len(party_candidates),
                            'wins': party_wins,
                            'win_rate': round((party_wins / len(party_candidates)) * 100, 2) if party_candidates else 0
                        }
                
                overview_analytics['comparative_insights'] = party_comparison
            
            # Generate key findings
            key_findings = []
            
            # Find the most successful party overall
            all_winners = []
            for candidates in all_data.values():
                all_winners.extend([
                    c.get('Party', c.get('party', 'Unknown')) 
                    for c in candidates if c.get('Status') == 'WON' or c.get('status') == 'won'
                ])
            
            if all_winners:
                most_successful_party = Counter(all_winners).most_common(1)[0]
                key_findings.append(f"Most successful party overall: {most_successful_party[0]} with {most_successful_party[1]} total wins")
            
            # Find closest contest
            all_margins = []
            for election_id, candidates in all_data.items():
                margin_analysis = analyze_victory_margins(candidates)
                if 'lowest_margin' in margin_analysis:
                    all_margins.append((election_id, margin_analysis['lowest_margin']))
            
            if all_margins:
                closest_contest = min(all_margins, key=lambda x: x[1])
                key_findings.append(f"Closest contest: {closest_contest[1]} vote margin in {closest_contest[0]}")
            
            overview_analytics['key_findings'] = key_findings
            
            return APIResponse.success(
                data=overview_analytics,
                message="Analytics overview retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get analytics overview", error=str(e))
            return APIResponse.internal_error("Failed to retrieve analytics overview")

@analytics_ns.route('/vote-share')
class VoteShareAnalysis(Resource):
    @analytics_ns.doc('get_vote_share_analysis')
    @analytics_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        📈 Get detailed vote share analysis
        
        Returns comprehensive vote share analysis across all elections
        including party-wise performance and vote distribution patterns.
        """
        try:
            all_data = load_all_analytics_data()
            election_filter = request.args.get('election')
            
            vote_share_analysis = {}
            
            for election_id, candidates in all_data.items():
                if election_filter and election_id != election_filter:
                    continue
                    
                analysis = calculate_vote_share_analysis(candidates)
                vote_share_analysis[election_id] = analysis
            
            if not vote_share_analysis:
                return APIResponse.not_found("Vote share data", election_filter or "any election")
            
            # Aggregate analysis across elections
            if len(vote_share_analysis) > 1:
                aggregate_analysis = {
                    'total_elections': len(vote_share_analysis),
                    'combined_vote_share': {},
                    'consistency_analysis': {}
                }
                
                # Combine vote shares across elections
                all_party_votes = {}
                total_combined_votes = 0
                
                for election_data in vote_share_analysis.values():
                    total_combined_votes += election_data['total_votes']
                    for party, data in election_data['party_performance'].items():
                        if party not in all_party_votes:
                            all_party_votes[party] = 0
                        all_party_votes[party] += data['votes']
                
                # Calculate combined vote shares
                for party, votes in all_party_votes.items():
                    combined_share = (votes / total_combined_votes) * 100 if total_combined_votes > 0 else 0
                    aggregate_analysis['combined_vote_share'][party] = {
                        'votes': votes,
                        'vote_share': round(combined_share, 2)
                    }
                
                vote_share_analysis['aggregate'] = aggregate_analysis
            
            return APIResponse.success(
                data=vote_share_analysis,
                message="Vote share analysis retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get vote share analysis", error=str(e))
            return APIResponse.internal_error("Failed to retrieve vote share analysis")

@analytics_ns.route('/margins')
class MarginAnalysis(Resource):
    @analytics_ns.doc('get_margin_analysis')
    @analytics_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        ⚖️ Get detailed victory margin analysis
        
        Returns comprehensive analysis of victory margins including
        close contests, landslide victories, and margin distributions.
        """
        try:
            all_data = load_all_analytics_data()
            election_filter = request.args.get('election')
            
            margin_analysis = {}
            
            for election_id, candidates in all_data.items():
                if election_filter and election_id != election_filter:
                    continue
                    
                analysis = analyze_victory_margins(candidates)
                if 'error' not in analysis:
                    margin_analysis[election_id] = analysis
            
            if not margin_analysis:
                return APIResponse.success(
                    data={'message': 'No margin data available'},
                    message="No margin analysis data found"
                )
            
            # Cross-election margin insights
            if len(margin_analysis) > 1:
                all_margins = []
                all_close_contests = []
                all_landslides = []
                
                for election_data in margin_analysis.values():
                    if 'close_contests' in election_data:
                        all_close_contests.extend(election_data['close_contests'])
                    if 'landslide_victories' in election_data:
                        all_landslides.extend(election_data['landslide_victories'])
                
                cross_election_insights = {
                    'total_close_contests': len(all_close_contests),
                    'total_landslides': len(all_landslides),
                    'competitiveness_index': round((len(all_close_contests) / sum(
                        election_data.get('total_constituencies', 0) 
                        for election_data in margin_analysis.values()
                    )) * 100, 2) if margin_analysis else 0
                }
                
                margin_analysis['cross_election_insights'] = cross_election_insights
            
            return APIResponse.success(
                data=margin_analysis,
                message="Margin analysis retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get margin analysis", error=str(e))
            return APIResponse.internal_error("Failed to retrieve margin analysis")

@analytics_ns.route('/trends')
class TrendAnalysis(Resource):
    @analytics_ns.doc('get_trend_analysis')
    @analytics_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        📊 Get electoral trends and patterns
        
        Returns trend analysis including party performance trends,
        constituency patterns, and emerging political dynamics.
        """
        try:
            all_data = load_all_analytics_data()
            
            # Since we have limited historical data (mostly 2024-2025), 
            # we'll focus on cross-election patterns and regional trends
            trend_analysis = {
                'temporal_trends': {},
                'regional_patterns': {},
                'party_momentum': {},
                'competitive_dynamics': {}
            }
            
            # Analyze party performance across different election types
            party_performance = {}
            
            for election_id, candidates in all_data.items():
                election_type = 'national' if 'lok-sabha' in election_id else 'state'
                
                for candidate in candidates:
                    party = candidate.get('Party', candidate.get('party', 'Unknown'))
                    
                    if party not in party_performance:
                        party_performance[party] = {
                            'national': {'contested': 0, 'won': 0},
                            'state': {'contested': 0, 'won': 0}
                        }
                    
                    party_performance[party][election_type]['contested'] += 1
                    
                    if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                        party_performance[party][election_type]['won'] += 1
            
            # Calculate performance ratios
            for party, performance in party_performance.items():
                national_rate = (performance['national']['won'] / performance['national']['contested']) if performance['national']['contested'] > 0 else 0
                state_rate = (performance['state']['won'] / performance['state']['contested']) if performance['state']['contested'] > 0 else 0
                
                performance['national_vs_state_ratio'] = round(national_rate / state_rate, 2) if state_rate > 0 else float('inf')
                performance['overall_consistency'] = abs(national_rate - state_rate)
            
            trend_analysis['party_momentum'] = {
                party: {
                    'national_performance': round((data['national']['won'] / data['national']['contested']) * 100, 2) if data['national']['contested'] > 0 else 0,
                    'state_performance': round((data['state']['won'] / data['state']['contested']) * 100, 2) if data['state']['contested'] > 0 else 0,
                    'consistency_score': round(100 - (data['overall_consistency'] * 100), 2)
                }
                for party, data in party_performance.items() 
                if data['national']['contested'] > 0 or data['state']['contested'] > 0
            }
            
            # Identify trending parties (those performing well across different contexts)
            trending_parties = []
            for party, momentum in trend_analysis['party_momentum'].items():
                if momentum['national_performance'] > 0 and momentum['state_performance'] > 0:
                    overall_score = (momentum['national_performance'] + momentum['state_performance']) / 2
                    trending_parties.append({
                        'party': party,
                        'overall_score': overall_score,
                        'consistency': momentum['consistency_score']
                    })
            
            trending_parties.sort(key=lambda x: x['overall_score'], reverse=True)
            trend_analysis['trending_parties'] = trending_parties[:10]
            
            # Regional patterns (simplified based on available data)
            regional_winners = {}
            for election_id, candidates in all_data.items():
                winners = [c for c in candidates if c.get('Status') == 'WON' or c.get('status') == 'won']
                party_wins = Counter(w.get('Party', w.get('party', 'Unknown')) for w in winners)
                
                if 'delhi' in election_id:
                    regional_winners['Delhi'] = dict(party_wins.most_common(5))
                elif 'maharashtra' in election_id:
                    regional_winners['Maharashtra'] = dict(party_wins.most_common(5))
                elif 'lok-sabha' in election_id:
                    regional_winners['National (Lok Sabha)'] = dict(party_wins.most_common(10))
            
            trend_analysis['regional_patterns'] = regional_winners
            
            return APIResponse.success(
                data=trend_analysis,
                message="Trend analysis retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get trend analysis", error=str(e))
            return APIResponse.internal_error("Failed to retrieve trend analysis")

@analytics_ns.route('/demographics')
class DemographicAnalysis(Resource):
    @analytics_ns.doc('get_demographic_analysis')
    @analytics_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        👥 Get demographic analysis and insights
        
        Returns demographic analysis including party diversity,
        candidate profiles, and representation patterns.
        """
        try:
            all_data = load_all_analytics_data()
            
            demographic_analysis = {}
            
            for election_id, candidates in all_data.items():
                insights = calculate_demographic_insights(candidates)
                demographic_analysis[election_id] = insights
            
            # Cross-election demographic insights
            if len(demographic_analysis) > 1:
                combined_insights = {
                    'overall_party_diversity': {},
                    'representation_patterns': {},
                    'competitive_landscape': {}
                }
                
                # Combine party diversity across elections
                all_party_counts = {}
                for election_data in demographic_analysis.values():
                    for party, count in election_data['party_diversity'].items():
                        all_party_counts[party] = all_party_counts.get(party, 0) + count
                
                combined_insights['overall_party_diversity'] = dict(
                    sorted(all_party_counts.items(), key=lambda x: x[1], reverse=True)[:20]
                )
                
                # Overall winning patterns
                all_winners = {}
                for election_data in demographic_analysis.values():
                    for party, wins in election_data['winning_patterns'].items():
                        all_winners[party] = all_winners.get(party, 0) + wins
                
                combined_insights['representation_patterns'] = dict(
                    sorted(all_winners.items(), key=lambda x: x[1], reverse=True)[:10]
                )
                
                demographic_analysis['combined_insights'] = combined_insights
            
            return APIResponse.success(
                data=demographic_analysis,
                message="Demographic analysis retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get demographic analysis", error=str(e))
            return APIResponse.internal_error("Failed to retrieve demographic analysis")

@analytics_ns.route('/competitiveness')
class CompetitinenessIndex(Resource):
    @analytics_ns.doc('get_competitiveness_index')
    @analytics_ns.marshal_with(api_response_model, code=200)  
    def get(self):
        """
        🏆 Get electoral competitiveness index
        
        Returns competitiveness metrics including constituency competitiveness,
        party balance, and electoral dynamics indicators.
        """
        try:
            all_data = load_all_analytics_data()
            
            competitiveness_analysis = {}
            
            for election_id, candidates in all_data.items():
                # Calculate various competitiveness metrics
                
                # 1. Average candidates per constituency
                by_constituency = {}
                for candidate in candidates:
                    const_code = candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                    if const_code not in by_constituency:
                        by_constituency[const_code] = []
                    by_constituency[const_code].append(candidate)
                
                avg_candidates = sum(len(candidates_list) for candidates_list in by_constituency.values()) / len(by_constituency) if by_constituency else 0
                
                # 2. Party fragmentation (number of parties winning seats vs total parties)
                total_parties = len(set(c.get('Party', c.get('party', 'Unknown')) for c in candidates))
                winning_parties = len(set(c.get('Party', c.get('party', 'Unknown')) for c in candidates if c.get('Status') == 'WON' or c.get('status') == 'won'))
                
                # 3. Margin distribution
                margin_analysis = analyze_victory_margins(candidates)
                close_contest_ratio = len(margin_analysis.get('close_contests', [])) / margin_analysis.get('total_constituencies', 1)
                
                # 4. Vote distribution (how concentrated are votes among top parties)
                vote_share = calculate_vote_share_analysis(candidates)
                top_2_parties = sorted(vote_share['party_performance'].items(), key=lambda x: x[1]['vote_share'], reverse=True)[:2]
                top_2_share = sum(party[1]['vote_share'] for party in top_2_parties)
                
                competitiveness_metrics = {
                    'average_candidates_per_constituency': round(avg_candidates, 2),
                    'total_parties': total_parties,
                    'winning_parties': winning_parties,
                    'party_success_rate': round((winning_parties / total_parties) * 100, 2) if total_parties > 0 else 0,
                    'close_contest_ratio': round(close_contest_ratio, 3),
                    'top_2_party_dominance': round(top_2_share, 2),
                    'competitiveness_score': 0  # Will calculate below
                }
                
                # Calculate overall competitiveness score (0-100)
                # Higher score = more competitive
                score = 0
                score += min(avg_candidates / 10 * 20, 20)  # More candidates = more competitive (max 20 points)
                score += min((1 - close_contest_ratio) * 30, 30)  # More close contests = more competitive (max 30 points) 
                score += min((winning_parties / total_parties) * 25, 25)  # More parties winning = more competitive (max 25 points)
                score += min((100 - top_2_share) / 100 * 25, 25)  # Less concentration = more competitive (max 25 points)
                
                competitiveness_metrics['competitiveness_score'] = round(score, 2)
                
                # Classification
                if score >= 75:
                    competitiveness_metrics['classification'] = 'Highly Competitive'
                elif score >= 50:
                    competitiveness_metrics['classification'] = 'Moderately Competitive'
                elif score >= 25:
                    competitiveness_metrics['classification'] = 'Low Competitiveness'
                else:
                    competitiveness_metrics['classification'] = 'Low Competitiveness'
                
                competitiveness_analysis[election_id] = competitiveness_metrics
            
            # Overall competitiveness comparison
            if len(competitiveness_analysis) > 1:
                comparison = {
                    'most_competitive': max(competitiveness_analysis.items(), key=lambda x: x[1]['competitiveness_score']),
                    'least_competitive': min(competitiveness_analysis.items(), key=lambda x: x[1]['competitiveness_score']),
                    'average_score': round(sum(data['competitiveness_score'] for data in competitiveness_analysis.values()) / len(competitiveness_analysis), 2)
                }
                competitiveness_analysis['comparison'] = comparison
            
            return APIResponse.success(
                data=competitiveness_analysis,
                message="Competitiveness analysis retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get competitiveness analysis", error=str(e))
            return APIResponse.internal_error("Failed to retrieve competitiveness analysis")
