"""
Sequential Agent with a Minimal Callback

This example demonstrates a lead qualification pipeline with a minimal
before_agent_callback that only initializes state once at the beginning.
"""

from google.adk.agents import SequentialAgent

from .subagentss.analyzer.agent import analyzer_agent
from .subagentss.mathmaker.agent import math_agent

# Create the sequential agent with minimal callback
stock_agent = SequentialAgent(
    name="LeadQualificationPipeline",
    sub_agents=[analyzer_agent,math_agent],
    description="A pipeline that analyzes and do the math of a stock",
)