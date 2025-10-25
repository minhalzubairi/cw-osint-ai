"""
Report Generator Utility
Generates insights and exports reports in various formats
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate reports from analysis results"""
    
    def generate_insights(self, analyses: List[Any]) -> Dict[str, Any]:
        """
        Generate insights from multiple analysis results
        
        Args:
            analyses: List of Analysis model instances
            
        Returns:
            Dictionary containing aggregated insights
        """
        if not analyses:
            return {}
        
        insights = {
            'total_analyses': len(analyses),
            'period': {
                'start': min(a.created_at for a in analyses).isoformat(),
                'end': max(a.created_at for a in analyses).isoformat()
            },
            'sentiment_distribution': self._calculate_sentiment_distribution(analyses),
            'top_trends': self._extract_top_trends(analyses),
            'key_insights': self._extract_key_insights(analyses),
            'activity_summary': self._summarize_activity(analyses),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return insights
    
    def _calculate_sentiment_distribution(self, analyses: List[Any]) -> Dict[str, Any]:
        """Calculate sentiment distribution across analyses"""
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for analysis in analyses:
            result = analysis.result
            if 'sentiment' in result:
                sentiment_data = result['sentiment']
                if isinstance(sentiment_data, dict):
                    sentiment = sentiment_data.get('overall', 'neutral')
                else:
                    sentiment = sentiment_data
                
                if sentiment in sentiments:
                    sentiments[sentiment] += 1
        
        total = sum(sentiments.values())
        if total > 0:
            percentages = {k: round((v / total) * 100, 2) for k, v in sentiments.items()}
        else:
            percentages = {k: 0 for k in sentiments}
        
        return {
            'counts': sentiments,
            'percentages': percentages
        }
    
    def _extract_top_trends(self, analyses: List[Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Extract top trends from analyses"""
        trends_map = {}
        
        for analysis in analyses:
            result = analysis.result
            if 'trends' in result:
                for trend in result['trends']:
                    topic = trend.get('topic')
                    if topic:
                        if topic not in trends_map:
                            trends_map[topic] = {
                                'topic': topic,
                                'total_mentions': 0,
                                'sentiment_scores': []
                            }
                        trends_map[topic]['total_mentions'] += trend.get('mentions', 1)
                        
                        sentiment = trend.get('sentiment', 'neutral')
                        score = 1 if sentiment == 'positive' else (-1 if sentiment == 'negative' else 0)
                        trends_map[topic]['sentiment_scores'].append(score)
        
        # Calculate average sentiment for each trend
        for trend in trends_map.values():
            scores = trend['sentiment_scores']
            if scores:
                avg_score = sum(scores) / len(scores)
                if avg_score > 0.3:
                    trend['overall_sentiment'] = 'positive'
                elif avg_score < -0.3:
                    trend['overall_sentiment'] = 'negative'
                else:
                    trend['overall_sentiment'] = 'neutral'
            else:
                trend['overall_sentiment'] = 'neutral'
            del trend['sentiment_scores']
        
        # Sort by mentions and return top N
        top_trends = sorted(
            trends_map.values(),
            key=lambda x: x['total_mentions'],
            reverse=True
        )[:limit]
        
        return top_trends
    
    def _extract_key_insights(self, analyses: List[Any]) -> List[str]:
        """Extract key insights from analyses"""
        insights = []
        
        for analysis in analyses:
            result = analysis.result
            
            # Extract from key_insights field
            if 'key_insights' in result:
                insights.extend(result['key_insights'])
            
            # Extract from recommendations
            if 'recommendations' in result:
                insights.extend(result['recommendations'])
            
            # Extract from key_points
            if 'key_points' in result:
                insights.extend(result['key_points'])
        
        # Deduplicate and return top insights
        unique_insights = list(set(insights))[:15]
        return unique_insights
    
    def _summarize_activity(self, analyses: List[Any]) -> Dict[str, Any]:
        """Summarize activity metrics"""
        analysis_types = {}
        
        for analysis in analyses:
            atype = analysis.analysis_type
            if atype not in analysis_types:
                analysis_types[atype] = 0
            analysis_types[atype] += 1
        
        return {
            'by_type': analysis_types,
            'total': len(analyses)
        }
    
    def generate_summary(self, insights: Dict[str, Any]) -> str:
        """
        Generate executive summary from insights
        
        Args:
            insights: Insights dictionary
            
        Returns:
            Summary text
        """
        total = insights.get('total_analyses', 0)
        sentiment = insights.get('sentiment_distribution', {})
        trends = insights.get('top_trends', [])
        
        summary_parts = [
            f"Analysis of {total} data points collected during the specified period.",
        ]
        
        # Sentiment summary
        if sentiment and 'percentages' in sentiment:
            pcts = sentiment['percentages']
            dominant = max(pcts.items(), key=lambda x: x[1])
            summary_parts.append(
                f"Overall sentiment is predominantly {dominant[0]} ({dominant[1]}%)."
            )
        
        # Trends summary
        if trends:
            top_3 = trends[:3]
            trend_names = [t['topic'] for t in top_3]
            summary_parts.append(
                f"Top trending topics include: {', '.join(trend_names)}."
            )
        
        return " ".join(summary_parts)
    
    def export_pdf(self, report: Any) -> bytes:
        """
        Export report as PDF
        
        Args:
            report: Report model instance
            
        Returns:
            PDF content as bytes
        """
        # Placeholder - implement with reportlab or similar
        logger.warning("PDF export not yet implemented")
        return b"PDF export not yet implemented"
    
    def export_html(self, report: Any) -> str:
        """
        Export report as HTML
        
        Args:
            report: Report model instance
            
        Returns:
            HTML content
        """
        insights = report.insights
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .metric {{ margin: 20px 0; padding: 15px; background: #f5f5f5; }}
                .trend {{ margin: 10px 0; padding: 10px; border-left: 3px solid #007bff; }}
            </style>
        </head>
        <body>
            <h1>{report.title}</h1>
            <p><strong>Period:</strong> {report.period_start} to {report.period_end}</p>
            <p><strong>Generated:</strong> {report.created_at}</p>
            
            <h2>Summary</h2>
            <p>{report.summary}</p>
            
            <h2>Sentiment Distribution</h2>
            <div class="metric">
                {self._render_sentiment_html(insights.get('sentiment_distribution', {}))}
            </div>
            
            <h2>Top Trends</h2>
            {self._render_trends_html(insights.get('top_trends', []))}
            
            <h2>Key Insights</h2>
            <ul>
                {''.join(f'<li>{insight}</li>' for insight in insights.get('key_insights', []))}
            </ul>
        </body>
        </html>
        """
        
        return html
    
    def _render_sentiment_html(self, sentiment: Dict[str, Any]) -> str:
        """Render sentiment distribution as HTML"""
        if not sentiment or 'percentages' not in sentiment:
            return "<p>No sentiment data available</p>"
        
        pcts = sentiment['percentages']
        return f"""
            <p>Positive: {pcts.get('positive', 0)}%</p>
            <p>Neutral: {pcts.get('neutral', 0)}%</p>
            <p>Negative: {pcts.get('negative', 0)}%</p>
        """
    
    def _render_trends_html(self, trends: List[Dict[str, Any]]) -> str:
        """Render trends as HTML"""
        if not trends:
            return "<p>No trends data available</p>"
        
        html = ""
        for trend in trends:
            html += f"""
            <div class="trend">
                <strong>{trend['topic']}</strong> - 
                {trend['total_mentions']} mentions 
                ({trend.get('overall_sentiment', 'neutral')} sentiment)
            </div>
            """
        
        return html
