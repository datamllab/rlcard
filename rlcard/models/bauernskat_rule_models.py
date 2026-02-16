'''
    File name: rlcard/models/bauernskat_rule_models.py
    Author: Oliver Czerwinski
    Date created: 08/15/2025
    Date last modified: 02/16/2026
    Python Version: 3.9+
'''

from rlcard.models.model import Model
from rlcard.agents.bauernskat.rule_agents import (
    BauernskatRandomRuleAgent,
    BauernskatFrugalRuleAgent,
    BauernskatLookaheadRuleAgent,
    BauernskatSHOTAlphaBetaRuleAgent
)

class BauernskatRandomRuleModelV1(Model):
    """
    A model that uses the RandomRuleAgent for both players in Bauernskat.
    """
    def __init__(self):
        """Load rule agent"""
        self.rule_agents = [BauernskatRandomRuleAgent() for _ in range(2)]

    @property
    def agents(self):
        """Get a list of agents for each position in a game."""
        return self.rule_agents

class BauernskatFrugalRuleModelV1(Model):
    """
    A model that uses the FrugalRuleAgent for both players in Bauernskat.
    """
    def __init__(self):
        """Load rule agent"""
        self.rule_agents = [BauernskatFrugalRuleAgent() for _ in range(2)]

    @property
    def agents(self):
        """Get a list of agents for each position in a game."""
        return self.rule_agents

class BauernskatLookaheadRuleModelV1(Model):
    """A model that uses the LookaheadRuleAgent for both players in Bauernskat."""
    def __init__(self):
        """Load rule agent"""
        self.rule_agents = [BauernskatLookaheadRuleAgent() for _ in range(2)]

    @property
    def agents(self):
        """Get a list of agents for each position in a game."""
        return self.rule_agents

class BauernskatSHOTAlphaBetaRuleModelV1(Model):
    """A model that uses the SHOT+AlphaBeta agent for both players in Bauernskat."""
    def __init__(self):
        """Load rule agent"""
        self.rule_agents = [BauernskatSHOTAlphaBetaRuleAgent() for _ in range(2)]

    @property
    def agents(self):
        """Get a list of agents for each position in a game."""
        return self.rule_agents