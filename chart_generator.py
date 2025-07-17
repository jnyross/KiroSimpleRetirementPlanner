"""
Web-specific chart generation with Plotly for retirement calculator.

This module creates interactive Plotly charts optimized for web display,
including 10th, 50th, and 90th percentile visualizations with responsive
design and mobile-friendly rendering.
"""

import plotly.graph_objects as go
import plotly.utils
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Color palette for consistent chart styling
CHART_COLORS = {
    'percentile_90': 'rgba(0,100,80,0.3)',
    'percentile_10': 'rgba(0,100,80,0.3)', 
    'percentile_50': 'rgb(0,100,80)',
    'fill_area': 'rgba(0,100,80,0.1)',
    'portfolio_colors': [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Olive
        '#17becf'   # Cyan
    ]
}


@dataclass
class ChartConfig:
    """Configuration for chart generation."""
    height: int = 400
    show_legend: bool = True
    responsive: bool = True
    mobile_optimized: bool = True
    include_hover: bool = True
    show_grid: bool = True
    title_font_size: int = 16
    axis_font_size: int = 12


class WebChartGenerator:
    """
    Web-specific chart generator using Plotly for interactive visualizations.
    
    Creates JSON chart data optimized for web display with responsive design
    and mobile-friendly rendering.
    """
    
    def __init__(self, config: Optional[ChartConfig] = None):
        """
        Initialize the chart generator.
        
        Args:
            config: Chart configuration options
        """
        self.config = config or ChartConfig()
    
    def generate_portfolio_chart(self, result_data: Dict[str, Any]) -> str:
        """
        Generate interactive Plotly chart for a single portfolio's percentile projections.
        
        Args:
            result_data: Portfolio result data containing percentile information
            
        Returns:
            JSON string representation of Plotly figure
        """
        portfolio_name = result_data.get('portfolio_name', 'Unknown Portfolio')
        percentile_data = result_data.get('percentile_data', {})
        
        if not percentile_data:
            return self._create_empty_chart(f"No data available for {portfolio_name}")
        
        # Extract percentile arrays
        percentile_10 = percentile_data.get('10th', [])
        percentile_50 = percentile_data.get('50th', [])
        percentile_90 = percentile_data.get('90th', [])
        
        if not all([percentile_10, percentile_50, percentile_90]):
            return self._create_empty_chart(f"Incomplete data for {portfolio_name}")
        
        # Create years array
        years = list(range(len(percentile_50)))
        
        # Create figure
        fig = go.Figure()
        
        # Add 90th percentile (upper bound)
        fig.add_trace(go.Scatter(
            x=years,
            y=percentile_90,
            fill=None,
            mode='lines',
            line=dict(color=CHART_COLORS['percentile_90'], width=1),
            name='90th Percentile',
            showlegend=False,
            hovertemplate='<b>Year %{x}</b><br>90th Percentile: £%{y:,.0f}<extra></extra>'
        ))
        
        # Add 10th percentile with fill to previous trace
        fig.add_trace(go.Scatter(
            x=years,
            y=percentile_10,
            fill='tonexty',  # Fill to previous trace
            mode='lines',
            line=dict(color=CHART_COLORS['percentile_10'], width=1),
            fillcolor=CHART_COLORS['fill_area'],
            name='10th-90th Percentile Range',
            hovertemplate='<b>Year %{x}</b><br>10th Percentile: £%{y:,.0f}<extra></extra>'
        ))
        
        # Add median line (most prominent)
        fig.add_trace(go.Scatter(
            x=years,
            y=percentile_50,
            mode='lines',
            line=dict(color=CHART_COLORS['percentile_50'], width=3),
            name='Median (50th Percentile)',
            hovertemplate='<b>Year %{x}</b><br>Median: £%{y:,.0f}<extra></extra>'
        ))
        
        # Configure layout for web display
        self._configure_layout(
            fig,
            title=f'{portfolio_name} Portfolio Projection',
            xaxis_title='Years from Now',
            yaxis_title='Portfolio Value (£, today\'s money)'
        )
        
        return self._figure_to_json(fig)
    
    def generate_comparison_chart(self, results_data: List[Dict[str, Any]]) -> str:
        """
        Generate comparison chart showing median projections for all portfolios.
        
        Args:
            results_data: List of portfolio result data
            
        Returns:
            JSON string representation of Plotly figure
        """
        if not results_data:
            return self._create_empty_chart("No portfolio data available")
        
        fig = go.Figure()
        
        # Filter out portfolios without valid data
        valid_results = [
            r for r in results_data 
            if r.get('percentile_data', {}).get('50th') and r.get('retirement_age')
        ]
        
        if not valid_results:
            return self._create_empty_chart("No valid portfolio data for comparison")
        
        # Add trace for each portfolio
        for i, result in enumerate(valid_results):
            portfolio_name = result.get('portfolio_name', f'Portfolio {i+1}')
            percentile_50 = result['percentile_data']['50th']
            color = CHART_COLORS['portfolio_colors'][i % len(CHART_COLORS['portfolio_colors'])]
            
            years = list(range(len(percentile_50)))
            
            fig.add_trace(go.Scatter(
                x=years,
                y=percentile_50,
                mode='lines',
                line=dict(color=color, width=2),
                name=portfolio_name,
                hovertemplate=f'<b>{portfolio_name}</b><br>Year %{{x}}<br>Median: £%{{y:,.0f}}<extra></extra>'
            ))
        
        # Configure layout
        self._configure_layout(
            fig,
            title='Portfolio Comparison - Median Projections',
            xaxis_title='Years from Now',
            yaxis_title='Portfolio Value (£, today\'s money)',
            height=500
        )
        
        return self._figure_to_json(fig)
    
    def generate_success_rate_chart(self, results_data: List[Dict[str, Any]]) -> str:
        """
        Generate bar chart showing success rates for all portfolios.
        
        Args:
            results_data: List of portfolio result data
            
        Returns:
            JSON string representation of Plotly figure
        """
        if not results_data:
            return self._create_empty_chart("No portfolio data available")
        
        # Extract portfolio names and success rates
        portfolio_names = []
        success_rates = []
        retirement_ages = []
        colors = []
        
        for i, result in enumerate(results_data):
            name = result.get('portfolio_name', f'Portfolio {i+1}')
            success_rate = result.get('success_rate', 0) * 100  # Convert to percentage
            retirement_age = result.get('retirement_age')
            
            portfolio_names.append(name)
            success_rates.append(success_rate)
            retirement_ages.append(retirement_age if retirement_age else 'N/A')
            
            # Color based on success rate
            if success_rate >= 99:
                colors.append('#2ca02c')  # Green for high success
            elif success_rate >= 95:
                colors.append('#ff7f0e')  # Orange for moderate success
            else:
                colors.append('#d62728')  # Red for low success
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=portfolio_names,
            y=success_rates,
            marker_color=colors,
            text=[f'{rate:.1f}%<br>Age {age}' for rate, age in zip(success_rates, retirement_ages)],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Success Rate: %{y:.1f}%<br>Retirement Age: %{customdata}<extra></extra>',
            customdata=retirement_ages
        ))
        
        # Add target line at 99%
        fig.add_hline(
            y=99,
            line_dash="dash",
            line_color="red",
            annotation_text="99% Target",
            annotation_position="top right"
        )
        
        # Configure layout
        self._configure_layout(
            fig,
            title='Portfolio Success Rates (99% Confidence Target)',
            xaxis_title='Portfolio Allocation',
            yaxis_title='Success Rate (%)',
            height=400
        )
        
        # Customize y-axis for percentage
        fig.update_yaxes(range=[0, 105], ticksuffix='%')
        
        return self._figure_to_json(fig)
    
    def generate_retirement_age_chart(self, results_data: List[Dict[str, Any]]) -> str:
        """
        Generate bar chart showing retirement ages for successful portfolios.
        
        Args:
            results_data: List of portfolio result data
            
        Returns:
            JSON string representation of Plotly figure
        """
        if not results_data:
            return self._create_empty_chart("No portfolio data available")
        
        # Filter successful portfolios (99% success rate)
        successful_results = [
            r for r in results_data 
            if r.get('success_rate', 0) >= 0.99 and r.get('retirement_age')
        ]
        
        if not successful_results:
            return self._create_empty_chart("No portfolios achieve 99% success rate")
        
        # Sort by retirement age
        successful_results.sort(key=lambda x: x['retirement_age'])
        
        portfolio_names = [r['portfolio_name'] for r in successful_results]
        retirement_ages = [r['retirement_age'] for r in successful_results]
        success_rates = [r['success_rate'] * 100 for r in successful_results]
        
        # Color the earliest retirement differently
        colors = ['#2ca02c' if i == 0 else '#1f77b4' for i in range(len(retirement_ages))]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=portfolio_names,
            y=retirement_ages,
            marker_color=colors,
            text=[f'Age {age}' for age in retirement_ages],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Retirement Age: %{y}<br>Success Rate: %{customdata:.1f}%<extra></extra>',
            customdata=success_rates
        ))
        
        # Configure layout
        self._configure_layout(
            fig,
            title='Retirement Ages for Successful Portfolios (99% Confidence)',
            xaxis_title='Portfolio Allocation',
            yaxis_title='Retirement Age',
            height=400
        )
        
        return self._figure_to_json(fig)
    
    def generate_chart_selector_data(self, results_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate data for chart selector dropdown.
        
        Args:
            results_data: List of portfolio result data
            
        Returns:
            Dictionary with selector options and default selection
        """
        options = []
        default_selection = None
        
        # Find recommended portfolio (earliest retirement with 99% success)
        successful_results = [
            r for r in results_data 
            if r.get('success_rate', 0) >= 0.99 and r.get('retirement_age')
        ]
        
        if successful_results:
            recommended = min(successful_results, key=lambda x: x['retirement_age'])
            default_selection = recommended['portfolio_name']
        
        # Create options for all portfolios
        for result in results_data:
            name = result.get('portfolio_name', 'Unknown')
            success_rate = result.get('success_rate', 0) * 100
            retirement_age = result.get('retirement_age')
            
            label = f"{name}"
            if retirement_age:
                label += f" (Age {retirement_age}, {success_rate:.1f}%)"
            else:
                label += f" ({success_rate:.1f}% success)"
            
            options.append({
                'value': name,
                'label': label,
                'success_rate': success_rate,
                'retirement_age': retirement_age,
                'recommended': name == default_selection
            })
        
        return {
            'options': options,
            'default': default_selection or (options[0]['value'] if options else None)
        }
    
    def _configure_layout(self, fig: go.Figure, title: str, xaxis_title: str, 
                         yaxis_title: str, height: Optional[int] = None) -> None:
        """
        Configure standard layout for charts.
        
        Args:
            fig: Plotly figure to configure
            title: Chart title
            xaxis_title: X-axis title
            yaxis_title: Y-axis title
            height: Chart height (optional)
        """
        layout_config = {
            'title': {
                'text': title,
                'x': 0.5,
                'font': {'size': self.config.title_font_size}
            },
            'xaxis': {
                'title': xaxis_title,
                'showgrid': self.config.show_grid,
                'gridcolor': 'rgba(128,128,128,0.2)',
                'tickfont': {'size': self.config.axis_font_size}
            },
            'yaxis': {
                'title': yaxis_title,
                'showgrid': self.config.show_grid,
                'gridcolor': 'rgba(128,128,128,0.2)',
                'tickformat': '£,.0f',
                'tickfont': {'size': self.config.axis_font_size},
                'tickangle': 0,  # Keep ticks horizontal for better readability
                'automargin': True,  # Auto-adjust margin for tick labels
                'tickmode': 'auto',  # Let plotly choose optimal tick spacing
                'nticks': 8  # Limit number of ticks for cleaner display
            },
            'hovermode': 'x unified' if self.config.include_hover else False,
            'showlegend': self.config.show_legend,
            'margin': {'l': 80, 'r': 30, 't': 60, 'b': 60},
            'height': height or self.config.height,
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white'
        }
        
        # Configure legend for mobile
        if self.config.mobile_optimized:
            layout_config['legend'] = {
                'orientation': "h",
                'yanchor': "bottom",
                'y': 1.02,
                'xanchor': "right",
                'x': 1,
                'font': {'size': 10}
            }
        
        # Make responsive
        if self.config.responsive:
            layout_config['autosize'] = True
        
        fig.update_layout(**layout_config)
    
    def _figure_to_json(self, fig: go.Figure) -> str:
        """
        Convert Plotly figure to JSON string optimized for web transfer.
        
        Args:
            fig: Plotly figure to convert
            
        Returns:
            JSON string representation
        """
        # Remove template to reduce JSON size
        fig.layout.template = None
        
        # Convert to JSON with optimized settings
        return fig.to_json()
    
    def _create_empty_chart(self, message: str) -> str:
        """
        Create an empty chart with a message.
        
        Args:
            message: Message to display
            
        Returns:
            JSON string representation of empty chart
        """
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            font=dict(size=16, color="gray"),
            showarrow=False
        )
        
        fig.update_layout(
            title="Chart Not Available",
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=self.config.height,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return self._figure_to_json(fig)


def generate_all_charts(results_data: List[Dict[str, Any]], 
                       config: Optional[ChartConfig] = None) -> Dict[str, Any]:
    """
    Generate all charts for the web interface.
    
    Args:
        results_data: List of portfolio result data
        config: Chart configuration options
        
    Returns:
        Dictionary containing all chart data and selector information
    """
    generator = WebChartGenerator(config)
    
    charts = {}
    
    # Generate individual portfolio charts
    portfolio_charts = {}
    for result in results_data:
        portfolio_name = result.get('portfolio_name')
        if portfolio_name and result.get('percentile_data'):
            portfolio_charts[portfolio_name] = generator.generate_portfolio_chart(result)
    
    # Generate comparison charts
    comparison_chart = generator.generate_comparison_chart(results_data)
    success_rate_chart = generator.generate_success_rate_chart(results_data)
    retirement_age_chart = generator.generate_retirement_age_chart(results_data)
    
    # Generate selector data
    selector_data = generator.generate_chart_selector_data(results_data)
    
    return {
        'portfolio_charts': portfolio_charts,
        'comparison_chart': comparison_chart,
        'success_rate_chart': success_rate_chart,
        'retirement_age_chart': retirement_age_chart,
        'selector_data': selector_data,
        'chart_count': len(portfolio_charts),
        'has_successful_portfolios': any(
            r.get('success_rate', 0) >= 0.99 for r in results_data
        )
    }


def create_mobile_optimized_config() -> ChartConfig:
    """
    Create chart configuration optimized for mobile devices.
    
    Returns:
        Mobile-optimized chart configuration
    """
    return ChartConfig(
        height=300,
        show_legend=True,
        responsive=True,
        mobile_optimized=True,
        include_hover=True,
        show_grid=True,
        title_font_size=14,
        axis_font_size=10
    )


def create_desktop_config() -> ChartConfig:
    """
    Create chart configuration optimized for desktop devices.
    
    Returns:
        Desktop-optimized chart configuration
    """
    return ChartConfig(
        height=450,
        show_legend=True,
        responsive=True,
        mobile_optimized=False,
        include_hover=True,
        show_grid=True,
        title_font_size=18,
        axis_font_size=12
    )