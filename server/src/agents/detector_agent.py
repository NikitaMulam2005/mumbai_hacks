"""Detector Agent – lifts structure, domains, and queries from raw claims.
Still fully deterministic: a set of heuristics extracts entities, domains,
structured claims, and search queries so downstream agents can work with a
clean, explainable representation.
"""

from __future__ import annotations
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Set
from loguru import logger

Domain = Literal["health", "politics", "travel", "disaster", "finance", "technology", "general"]

@dataclass
class StructuredClaim:
    subject: Optional[str] = None
    action: Optional[str] = None
    location: Optional[str] = None
    time: Optional[str] = None
    entities: List[str] = field(default_factory=list)
    
    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            "subject": self.subject,
            "action": self.action,
            "location": self.location,
            "time": self.time,
            "entities": self.entities,
        }

@dataclass
class DetectionResult:
    claim: str
    domain: Domain
    claim_type: str
    entities: List[str]
    keywords: List[str]
    structured_claim: StructuredClaim
    search_queries: List[str]
    risk_score: float
    confidence: float
    notes: str
    # New enhanced fields
    claim_complexity: str  # "simple", "moderate", "complex"
    supporting_evidence_types: List[str]  # ["official", "eyewitness", "statistical", etc.]
    temporal_indicators: List[str]  # Time-related phrases found
    quantitative_elements: List[str]  # Numbers, percentages, statistics
    
    def model_dump(self) -> Dict:
        return {
            "claim": self.claim,
            "domain": self.domain,
            "claim_type": self.claim_type,
            "entities": self.entities,
            "keywords": self.keywords,
            "structured_claim": self.structured_claim.as_dict(),
            "search_queries": self.search_queries,
            "risk_score": round(self.risk_score, 2),
            "confidence": round(self.confidence, 2),
            "notes": self.notes,
            "claim_complexity": self.claim_complexity,
            "supporting_evidence_types": self.supporting_evidence_types,
            "temporal_indicators": self.temporal_indicators,
            "quantitative_elements": self.quantitative_elements,
        }

class DetectorAgent:
    """Enhanced Detector Agent with comprehensive claim analysis capabilities."""
    
    # Domain classification keywords
    DOMAIN_KEYWORDS: Dict[Domain, set[str]] = {
        "health": {
            "virus", "covid", "pandemic", "vaccine", "mask", "outbreak", "hospital", 
            "fever", "infection", "symptom", "treatment", "patient", "doctor"
        },
        "politics": {
            "election", "minister", "president", "policy", "parliament", "government", 
            "vote", "campaign", "bill", "law", "diplomat", "ambassador"
        },
        "travel": {
            "airport", "flight", "train", "railway", "visa", "border", "airline", 
            "runway", "luggage", "passport", "tourism", "cruise"
        },
        "disaster": {
            "flood", "cyclone", "earthquake", "tsunami", "landslide", "storm", 
            "wildfire", "evacuation", "relief", "rescue", "damage"
        },
        "finance": {
            "stock", "market", "crore", "billion", "rupee", "dollar", "inflation", 
            "interest", "budget", "bank", "investment", "economy"
        },
        "technology": {
            "ai", "cyber", "hack", "malware", "data leak", "server", "chip", 
            "software", "app", "internet", "network", "gadget"
        },
        "general": set(),
    }
    
    # Emergency and urgency indicators
    EMERGENCY_WORDS = {
        "breaking", "urgent", "alert", "warning", "emergency", "crisis", "panic", 
        "chaos", "collapse", "failure", "disaster"
    }
    
    # Action patterns for structured extraction
    ACTION_PATTERNS = [
        "flight cancelled", "flight canceled", "airport closed", "airport shutdown",
        "school closed", "lockdown", "virus outbreak", "cases rising",
        "explosive spread", "power outage", "internet shutdown", "bank closed",
        "market crash", "train derailed", "bridge collapsed"
    ]
    
    # Common stopwords to filter out noise
    STOPWORDS = {
        "the", "and", "that", "this", "with", "from", "have", "been", "will",
        "about", "over", "into", "after", "before", "today", "news", "claims", 
        "claim", "says", "said", "according", "reports", "reported", "source"
    }
    
    # Entity extraction pattern
    ENTITY_PATTERN = re.compile(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b")
    
    # New: Quantitative patterns
    QUANTITATIVE_PATTERNS = [
        r"\b\d+(?:\.\d+)?%\s",  # Percentages: 75%, 12.5%
        r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:billion|million|thousand|crore|lakh)\b",  # Large numbers
        r"\b\d+\s*(?:cases?|deaths?|patients?|tests?|infections?)\b",  # Health metrics
        r"\b\d+\s*(?:people?|persons?|individuals?|victims?)\b",  # People counts
        r"\b\d+\s*(?:flights?|trains?|vehicles?|ships?)\b",  # Travel/transport
        r"\b\d+\s*(?:rupees?|dollars?|euros?)\b",  # Currency amounts
        r"\b\d+(?:\.\d+)?\s*(?:degrees?|°C|°F)\b"  # Temperature
    ]
    
    # New: Temporal indicators
    TEMPORAL_INDICATORS = {
        "immediate": {"breaking", "just now", "moments ago", "right now", "live"},
        "short_term": {
            "today", "tonight", "tomorrow", "yesterday", "this morning", 
            "this evening", "this week", "next few hours"
        },
        "medium_term": {
            "past 24 hours", "past few days", "last week", "recent", "this month",
            "past month", "next week"
        },
        "long_term": {
            "past year", "over the past", "several months", "this year", 
            "last year", "coming months"
        }
    }
    
    # New: Supporting evidence indicators
    SUPPORT_EVIDENCE_INDICATORS = {
        "official": {
            "official", "government", "authorities", "spokesperson", "statement", 
            "press release", "ministry", "agency", "department"
        },
        "statistical": {
            "study", "research", "data", "survey", "statistics", "figures", 
            "analysis", "report", "metrics", "numbers"
        },
        "eyewitness": {
            "resident", "witness", "local", "on the ground", "firsthand", 
            "eyewitness", "passerby", "neighbor"
        },
        "media": {
            "reported by", "according to", "sources say", "media reports", 
            "journalist", "correspondent", "broadcast"
        },
        "expert": {
            "expert", "scientist", "doctor", "professor", "analyst", 
            "specialist", "researcher"
        }
    }
    
    def detect(self, claim: str) -> DetectionResult:
        """Main detection method with comprehensive analysis."""
        clean_claim = (claim or "").strip()
        if len(clean_claim) < 8:
            raise ValueError("Claim must be at least 8 characters long")
        
        logger.info("DetectorAgent: analysing claim snippet='{}...'", clean_claim[:80])
        
        claim_lower = clean_claim.lower()
        
        # Core analysis
        claim_type = self._classify_claim(claim_lower)
        domain = self._detect_domain(claim_lower)
        entities = self._extract_entities(clean_claim)
        keywords = self._extract_keywords(claim_lower)
        structured = self._build_structured_claim(clean_claim, entities)
        queries = self._generate_search_queries(clean_claim, structured, entities, domain)
        risk = self._score_risk(clean_claim, claim_type)
        confidence = self._score_confidence(claim_type, risk, len(entities))
        notes = self._build_notes(claim_type, domain, entities, risk, structured)
        
        # Enhanced analysis
        complexity = self._assess_claim_complexity(clean_claim)
        supporting_types = self._identify_supporting_evidence_types(claim_lower)
        temporal_indicators = self._extract_temporal_indicators(claim_lower)
        quantitative_elements = self._extract_quantitative_elements(clean_claim)
        
        # Adjust confidence based on enhanced analysis
        evidence_bonus = self._calculate_evidence_confidence(supporting_types, temporal_indicators)
        adjusted_confidence = min(0.95, confidence + evidence_bonus)
        
        # Enhanced notes
        enhanced_notes = self._build_enhanced_notes(
            notes, complexity, supporting_types, temporal_indicators, 
            quantitative_elements, risk
        )
        
        # Generate contextual search queries
        contextual_queries = self._generate_contextual_search_queries(structured, supporting_types)
        all_queries = self._deduplicate_queries(queries + contextual_queries)[:8]
        
        result = DetectionResult(
            claim=clean_claim,
            domain=domain,
            claim_type=claim_type,
            entities=entities,
            keywords=keywords,
            structured_claim=structured,
            search_queries=all_queries,
            risk_score=risk,
            confidence=adjusted_confidence,
            notes=enhanced_notes,
            claim_complexity=complexity,
            supporting_evidence_types=supporting_types,
            temporal_indicators=temporal_indicators,
            quantitative_elements=quantitative_elements
        )
        
        logger.success(
            "DetectorAgent: domain={} type={} risk={:.2f} entities={} confidence={:.2f} complexity={}",
            domain, claim_type, risk, len(entities), adjusted_confidence, complexity
        )
        return result
    
    # Core analysis methods
    def _detect_domain(self, claim_lower: str) -> Domain:
        """Detect the domain of the claim."""
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(word in claim_lower for word in keywords):
                return domain
        return "general"
    
    def _classify_claim(self, claim_lower: str) -> str:
        """Classify the type of claim."""
        if "?" in claim_lower or claim_lower.startswith(("did", "is", "are", "can", "does", "has")):
            return "question"
        if re.search(r"\d", claim_lower):
            return "numerical_claim"
        if any(phrase in claim_lower for phrase in self.ACTION_PATTERNS):
            return "action_claim"
        return "narrative_claim"
    
    def _extract_entities(self, claim: str) -> List[str]:
        """Extract proper nouns and named entities."""
        matches = {m.group(0).strip() for m in self.ENTITY_PATTERN.finditer(claim)}
        # Sort by first occurrence and limit to top 5
        sorted_entities = []
        for entity in matches:
            try:
                index = claim.index(entity)
                sorted_entities.append((index, entity))
            except ValueError:
                continue
        sorted_entities.sort(key=lambda x: x[0])
        return [entity for _, entity in sorted_entities[:5]]
    
    def _extract_keywords(self, claim_lower: str) -> List[str]:
        """Extract meaningful keywords excluding stopwords."""
        tokens = re.split(r"[^\w@#]+", claim_lower)
        keywords = [
            tok for tok in tokens 
            if tok and len(tok) > 3 and tok not in self.STOPWORDS
        ]
        return keywords[:8]
    
    def _build_structured_claim(self, claim: str, entities: List[str]) -> StructuredClaim:
        """Build a structured representation of the claim."""
        claim_lower = claim.lower()
        subject = entities[0] if entities else None
        location = self._extract_location(claim, entities)
        time_phrase = self._extract_time_phrase(claim_lower)
        action = self._extract_action(claim_lower)
        return StructuredClaim(
            subject=subject,
            action=action,
            location=location,
            time=time_phrase,
            entities=entities
        )
    
    def _extract_location(self, claim: str, entities: List[str]) -> Optional[str]:
        """Extract location information from the claim."""
        # Look for location patterns
        patterns = [
            r"\b(?:in|at|near|from|to)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
            r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s+(?:airport|hospital|station|city)\b"
        ]
        for pattern in patterns:
            match = re.search(pattern, claim)
            if match:
                return match.group(1).strip()
        return entities[1] if len(entities) > 1 else None
    
    def _extract_time_phrase(self, claim_lower: str) -> Optional[str]:
        """Extract temporal information from the claim."""
        # Time patterns
        time_match = re.search(r"\b(\d{1,2}\s?(?:am|pm))\b", claim_lower)
        if time_match:
            return time_match.group(1)
        
        # Day/time keywords
        for token in ["morning", "evening", "tonight", "today", "tomorrow", "yesterday"]:
            if token in claim_lower:
                return token
        return None
    
    def _extract_action(self, claim_lower: str) -> Optional[str]:
        """Extract action verbs or phrases."""
        for phrase in self.ACTION_PATTERNS:
            if phrase in claim_lower:
                return phrase
        
        # Single word actions
        action_match = re.search(
            r"\b(shut\s+down|cancelled|canceled|closed|delay|postponed|confirmed|"
            r"declared|announced|reported|confirmed|denied|verified)\b", 
            claim_lower
        )
        if action_match:
            return action_match.group(1)
        return None
    
    # Enhanced analysis methods
    def _assess_claim_complexity(self, claim: str) -> str:
        """Assess the structural complexity of the claim."""
        word_count = len(claim.split())
        entity_count = len(self._extract_entities(claim))
        has_conjunctions = bool(re.search(r"\band\b|\bor\b", claim.lower()))
        has_multiple_clauses = bool(re.search(r"[,.]\s+[A-Z]", claim))
        has_quantitative = bool(self._extract_quantitative_elements(claim))
        
        if word_count <= 15 and entity_count <= 2 and not has_multiple_clauses and not has_quantitative:
            return "simple"
        elif word_count <= 40 and entity_count <= 4 and not has_conjunctions:
            return "moderate"
        else:
            return "complex"
    
    def _identify_supporting_evidence_types(self, claim_lower: str) -> List[str]:
        """Identify what types of supporting evidence are referenced."""
        evidence_types = []
        for evidence_type, indicators in self.SUPPORT_EVIDENCE_INDICATORS.items():
            if any(indicator in claim_lower for indicator in indicators):
                evidence_types.append(evidence_type)
        return evidence_types[:3]  # Limit to top 3 types
    
    def _extract_temporal_indicators(self, claim_lower: str) -> List[str]:
        """Extract temporal context from the claim."""
        temporal_phrases = []
        for category, indicators in self.TEMPORAL_INDICATORS.items():
            for indicator in indicators:
                if indicator in claim_lower:
                    temporal_phrases.append(indicator)
                    break  # Take first match per category
        return temporal_phrases[:3]  # Limit to top 3 indicators
    
    def _extract_quantitative_elements(self, claim: str) -> List[str]:
        """Extract quantitative information from the claim."""
        quantitative_elements = []
        for pattern in self.QUANTITATIVE_PATTERNS:
            matches = re.finditer(pattern, claim)
            for match in matches:
                quantitative_elements.append(match.group(0).strip())
        return quantitative_elements[:5]  # Limit to top 5 quantitative elements
    
    def _calculate_evidence_confidence(self, supporting_types: List[str], temporal_indicators: List[str]) -> float:
        """Calculate additional confidence based on evidence and temporal context."""
        confidence_bonus = 0.0
        
        # Official sources provide highest confidence
        if "official" in supporting_types:
            confidence_bonus += 0.15
        elif "statistical" in supporting_types:
            confidence_bonus += 0.10
        elif "expert" in supporting_types:
            confidence_bonus += 0.08
        
        # Multiple evidence types
        if len(supporting_types) > 1:
            confidence_bonus += 0.05 * (len(supporting_types) - 1)
        
        # Recent temporal indicators
        recent_indicators = self.TEMPORAL_INDICATORS["immediate"]
        if any(indicator in recent_indicators for indicator in temporal_indicators):
            confidence_bonus += 0.08
        elif any(indicator in self.TEMPORAL_INDICATORS["short_term"] for indicator in temporal_indicators):
            confidence_bonus += 0.04
        
        return min(0.25, confidence_bonus)  # Cap maximum bonus
    
    # Search query generation
    def _generate_search_queries(self, claim: str, structured: StructuredClaim, entities: List[str], domain: Domain) -> List[str]:
        """Generate base search queries."""
        queries: List[str] = [claim]
        
        # Subject-action combinations
        if structured.subject and structured.action:
            queries.append(f"{structured.subject} {structured.action}")
        
        # Location-based queries
        if structured.location and structured.action:
            queries.append(f"{structured.location} {structured.action}")
        if structured.location and structured.time:
            queries.append(f"{structured.location} {structured.time}")
        
        # Entity-action combinations
        for ent in entities[:2]:
            if structured.action:
                queries.append(f'"{ent}" {structured.action}')
        
        # Domain-specific queries
        domain_hints = {
            "health": ["official health update", "health ministry statement", "medical report"],
            "politics": ["fact check", "official statement", "government announcement"],
            "travel": ["status update", "travel advisory", "flight information"],
            "disaster": ["relief update", "emergency services", "damage assessment"],
            "finance": ["market news", "financial report", "economic update"],
            "technology": ["cyber alert", "security update", "tech news"],
        }
        
        if domain in domain_hints and structured.subject:
            for hint in domain_hints[domain][:2]:  # Take top 2 hints
                queries.append(f'"{structured.subject}" {hint}')
        
        return self._deduplicate_queries(queries)
    
    def _generate_contextual_search_queries(self, structured: StructuredClaim, supporting_types: List[str]) -> List[str]:
        """Generate additional search queries based on evidence types."""
        contextual_queries = []
        
        evidence_modifiers = {
            "official": ["official statement", "government confirmation", "press release", "authorities"],
            "statistical": ["study", "research", "official data", "statistics", "report"],
            "eyewitness": ["witness accounts", "resident reports", "firsthand accounts", "local sources"],
            "media": ["news report", "journalist account", "media coverage", "broadcast"],
            "expert": ["expert analysis", "specialist opinion", "professional assessment"]
        }
        
        for evidence_type in supporting_types:
            if evidence_type in evidence_modifiers and structured.subject:
                for modifier in evidence_modifiers[evidence_type][:2]:  # Top 2 modifiers
                    contextual_queries.append(f'"{structured.subject}" {modifier}')
        
        return contextual_queries
    
    def _deduplicate_queries(self, queries: List[str]) -> List[str]:
        """Remove duplicate queries while preserving order."""
        seen = set()
        ordered: List[str] = []
        for q in queries:
            normalized = q.strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(q.strip())
        return ordered
    
    # Scoring methods
    def _score_risk(self, claim: str, claim_type: str) -> float:
        """Calculate risk score based on claim characteristics."""
        risk = 0.3
        claim_lower = claim.lower()
        
        # Claim type risk
        if claim_type == "question":
            risk += 0.10
        elif claim_type == "numerical_claim":
            risk += 0.20
        elif claim_type == "action_claim":
            risk += 0.15
        
        # Emergency words increase risk
        if any(word in claim_lower for word in self.EMERGENCY_WORDS):
            risk += 0.25
        
        # Large numbers increase risk
        if re.search(r"\d{3,}", claim):
            risk += 0.15
        
        # Long claims might be less urgent
        if len(claim) > 240:
            risk -= 0.05
        
        # Quantitative elements increase risk
        if self._extract_quantitative_elements(claim):
            risk += 0.10
        
        return max(0.1, min(1.0, risk))
    
    def _score_confidence(self, claim_type: str, risk: float, entity_count: int) -> float:
        """Calculate base confidence score."""
        base = 0.55 if claim_type != "narrative_claim" else 0.4
        base += 0.08 * min(entity_count, 3)
        base += 0.10 * (risk - 0.3)
        return max(0.35, min(0.85, base))  # Cap base confidence
    
    # Note generation
    def _build_notes(self, claim_type: str, domain: Domain, entities: List[str], risk: float, structured: StructuredClaim) -> str:
        """Build basic analysis notes."""
        entity_str = ", ".join(entities[:3]) if entities else "no specific entities"
        action = structured.action or "unspecified action"
        return (
            f"Domain: {domain}. Classified as {claim_type.replace('_', ' ')} – {action}. "
            f"Entities: {entity_str}. Risk score {risk:.2f}."
        )
    
    def _build_enhanced_notes(
        self, base_notes: str, complexity: str, supporting_types: List[str], 
        temporal_indicators: List[str], quantitative_elements: List[str], risk: float
    ) -> str:
        """Build comprehensive analysis notes."""
        enhanced_parts = [base_notes]
        
        # Complexity
        enhanced_parts.append(f"Complexity: {complexity}.")
        
        # Evidence types
        if supporting_types:
            evidence_str = ", ".join(supporting_types)
            enhanced_parts.append(f"Evidence: {evidence_str}.")
        else:
            enhanced_parts.append("Evidence: none mentioned.")
        
        # Temporal context
        if temporal_indicators:
            time_str = ", ".join(temporal_indicators[:2])
            enhanced_parts.append(f"Temporal: {time_str}.")
        
        # Quantitative elements
        if quantitative_elements:
            quant_str = ", ".join(quantitative_elements[:2])
            enhanced_parts.append(f"Quantitative: {quant_str}.")
        
        # Risk assessment
        risk_level = "HIGH" if risk > 0.65 else "MEDIUM" if risk > 0.45 else "LOW"
        enhanced_parts.append(f"Priority: {risk_level}")
        
        return " | ".join(enhanced_parts)

# Create singleton instance
detector_agent = DetectorAgent()

if __name__ == "__main__":
    # Test cases
    test_claims = [
        "Breaking: WHO warns of a new virus outbreak in Mumbai hospitals with 150 cases reported today.",
        "Is the airport in Delhi really closed due to security threats?",
        "Stock market crashed by 12% this morning, experts predict recession.",
        "Local resident claims to have seen UFO near the power plant last night.",
        "Government announces new policy: all schools closed for next two weeks due to rising cases."
    ]
    
    for i, claim in enumerate(test_claims, 1):
        print(f"\n=== Test Case {i} ===")
        try:
            result = detector_agent.detect(claim)
            print(result.model_dump())
            print("-" * 80)
        except Exception as e:
            print(f"Error processing claim: {e}")