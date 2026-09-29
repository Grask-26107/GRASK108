"""
BIS Standards Knowledge Graph (StandardsGraphService)
Enables cross-standard relationship mapping, dependency tracking,
and regulatory cross-referencing for Indian Standards (IS Codes).
"""

import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class StandardsGraphService:
    """
    In-memory Statutory Knowledge Graph for Indian Standards.
    Models relationships:
      - [Standard] --MANDATES_TEST--> [Testing Standard]
      - [Standard] --REGULATED_BY--> [Quality Control Order / Ministry]
      - [Standard] --CERTIFICATION_SCHEME--> [Scheme I/II/IV/FMCS/Hallmarking]
      - [Standard] --RELATED_TO--> [Companion / Sibling Standards]
    """

    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
        self._build_initial_graph()

    def _build_initial_graph(self):
        """Initializes the core Bureau of Indian Standards statutory ontology."""
        
        # 1. Add Core Standards Nodes
        standards = [
            {
                "id": "IS 14543",
                "code": "IS 14543:2018",
                "title": "Packaged Drinking Water (Other than Natural Mineral Water)",
                "category": "Food & Agriculture (FAD 14)",
                "scheme": "Scheme-I (Mandatory ISI Mark)",
                "ministry": "Ministry of Consumer Affairs, Food & Public Distribution",
                "qco": "Packaged Drinking Water (Quality Control) Order",
                "penalties": "Section 29, BIS Act 2016 (Fine up to Rs. 5 Lakhs or 2 years imprisonment)"
            },
            {
                "id": "IS 13428",
                "code": "IS 13428:2005",
                "title": "Packaged Natural Mineral Water",
                "category": "Food & Agriculture (FAD 14)",
                "scheme": "Scheme-I (Mandatory ISI Mark)",
                "ministry": "Ministry of Consumer Affairs / FSSAI",
                "qco": "Packaged Drinking Water (Quality Control) Order",
                "penalties": "Section 29, BIS Act 2016"
            },
            {
                "id": "IS 10500",
                "code": "IS 10500:2012",
                "title": "Drinking Water (Potable Domestic Water Supply)",
                "category": "Food & Agriculture (FAD 14)",
                "scheme": "Voluntary / Jal Jeevan Mission Statutory Benchmark",
                "ministry": "Ministry of Jal Shakti",
                "qco": "National Drinking Water Guidelines",
                "penalties": "Municipal Quality Standard"
            },
            {
                "id": "IS 1786",
                "code": "IS 1786:2008",
                "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement (TMT Fe 415, Fe 500, Fe 550D)",
                "category": "Civil Engineering & Metallurgy (CED 54 / MTD 4)",
                "scheme": "Scheme-I (Mandatory ISI Mark)",
                "ministry": "Ministry of Steel",
                "qco": "Steel and Steel Products (Quality Control) Order",
                "penalties": "Section 16 & 29, BIS Act 2016"
            },
            {
                "id": "IS 269",
                "code": "IS 269:2015",
                "title": "Ordinary Portland Cement (33, 43 and 53 Grade) - Specification",
                "category": "Civil Engineering (CED 2)",
                "scheme": "Scheme-I (Mandatory ISI Mark)",
                "ministry": "DPIIT, Ministry of Commerce & Industry",
                "qco": "Cement (Quality Control) Order",
                "penalties": "Mandatory ISI Certification under Essential Commodities Act & BIS Act"
            },
            {
                "id": "IS 2796",
                "code": "IS 2796:2017",
                "title": "Motor Gasoline (Petrol) for Automotive Engines - Specification",
                "category": "Petroleum, Coal and Related Products (PCD 3)",
                "scheme": "Scheme-I (ISI Mark) / BS-VI Statutory Fuel Norms",
                "ministry": "Ministry of Petroleum and Natural Gas (MoPNG) & PESO",
                "qco": "Motor Gasoline (Quality Control) Order",
                "penalties": "Motor Spirit and High Speed Diesel (Regulation of Supply and Distribution and Prevention of Malpractices) Order"
            },
            {
                "id": "IS 1460",
                "code": "IS 1460:2017",
                "title": "Automotive Diesel Fuel (High Speed Diesel - HSD) - Specification",
                "category": "Petroleum, Coal and Related Products (PCD 3)",
                "scheme": "Scheme-I (ISI Mark) / BS-VI Statutory Fuel Norms",
                "ministry": "Ministry of Petroleum and Natural Gas (MoPNG)",
                "qco": "High Speed Diesel (Quality Control) Order",
                "penalties": "Section 29, BIS Act 2016"
            },
            {
                "id": "IS 13252",
                "code": "IS 13252 (Part 1):2010",
                "title": "Information Technology Equipment - Safety - General Requirements",
                "category": "Electronics & Information Technology (LITD 07)",
                "scheme": "Scheme-II (Compulsory Registration Scheme - CRS)",
                "ministry": "Ministry of Electronics and Information Technology (MeitY)",
                "qco": "Electronics and Information Technology Goods (Requirement for Compulsory Registration) Order",
                "penalties": "Prohibition of customs import and sale without valid BIS R-Number (R-XXXXXXXX)"
            },
            {
                "id": "IS 16046",
                "code": "IS 16046 (Part 2):2018",
                "title": "Secondary Cells and Batteries Containing Alkaline or Other Non-Acid Electrolytes (Lithium-ion Batteries)",
                "category": "Electrotechnical (ETD 11 / LITD 07)",
                "scheme": "Scheme-II (Compulsory Registration Scheme - CRS)",
                "ministry": "Ministry of Electronics and Information Technology (MeitY)",
                "qco": "Electronics & IT Goods Mandatory CRS Order",
                "penalties": "Section 29, BIS Act 2016"
            },
            {
                "id": "IS 1417",
                "code": "IS 1417:2016",
                "title": "Gold and Gold Alloys, Jewellery/Artefacts - Fineness and Marking",
                "category": "Precious Metals & Hallmarking (CHD 26)",
                "scheme": "Mandatory BIS Hallmarking with 6-Digit HUID",
                "ministry": "Department of Consumer Affairs",
                "qco": "Hallmarking of Gold Jewellery and Gold Artefacts Order",
                "penalties": "Section 29, BIS Act 2016 (Fine up to 5x value of gold or 1 yr imprisonment)"
            }
        ]

        for s in standards:
            self._nodes[s["id"]] = s

        # 2. Add Test Method Standards
        test_methods = [
            {
                "id": "IS 3025",
                "code": "IS 3025 (Parts 1 to 60)",
                "title": "Methods of Sampling and Test (Physical and Chemical) for Water and Wastewater",
                "category": "Testing Methodology",
                "type": "Mandatory NABL Test Method"
            },
            {
                "id": "IS 1608",
                "code": "IS 1608 (Part 1):2018 / ISO 6892-1",
                "title": "Metallic Materials - Tensile Testing - Method of Test at Room Temperature",
                "category": "Mechanical Testing Methodology",
                "type": "Mandatory Tensile & Yield Strength Test Method"
            },
            {
                "id": "IS 228",
                "code": "IS 228 (Parts 1 to 24)",
                "title": "Methods for Chemical Analysis of Steels",
                "category": "Chemical Testing Methodology",
                "type": "Mandatory Carbon, Sulphur, Phosphorus Determination Method"
            },
            {
                "id": "IS 1599",
                "code": "IS 1599:2019 / ISO 7438",
                "title": "Metallic Materials - Bend Test",
                "category": "Mechanical Testing Methodology",
                "type": "Mandatory Bend and Rebend Test Method"
            },
            {
                "id": "IS 4031",
                "code": "IS 4031 (Parts 1 to 15)",
                "title": "Methods of Physical Tests for Hydraulic Cement",
                "category": "Civil Testing Methodology",
                "type": "Mandatory Compressive Strength & Setting Time Test Method"
            },
            {
                "id": "IS 1448",
                "code": "IS 1448 (Parts 1 to 160)",
                "title": "Methods of Test for Petroleum and Its Products",
                "category": "Petrochemical Testing Methodology",
                "type": "Mandatory Octane, Cetane, Sulphur, Distillation Test Method"
            }
        ]

        for tm in test_methods:
            self._nodes[tm["id"]] = tm

        # 3. Add Relationships (Edges)
        self._add_edge("IS 14543", "IS 3025", "MANDATES_TEST_METHOD", "Physical and Chemical Water Testing (pH, TDS, Heavy Metals, Turbidity)")
        self._add_edge("IS 14543", "IS 10500", "STANDARDIZATION_BASELINE", "Raw water intake must comply with potable water quality limits")
        self._add_edge("IS 14543", "IS 13428", "SIBLING_STANDARD", "Differentiated by mineral enrichment vs naturally occurring source minerals")

        self._add_edge("IS 1786", "IS 1608", "MANDATES_TEST_METHOD", "Tensile strength, 0.2% Proof Stress/Yield Stress, and Elongation %")
        self._add_edge("IS 1786", "IS 228", "MANDATES_TEST_METHOD", "Chemical analysis of Carbon, Sulphur, and Phosphorus contents")
        self._add_edge("IS 1786", "IS 1599", "MANDATES_TEST_METHOD", "Mandatory cold bend and rebend tests around standard mandrel")

        self._add_edge("IS 269", "IS 4031", "MANDATES_TEST_METHOD", "Fineness, Soundness, Initial/Final Setting Time, and 28-day Compressive Strength")

        self._add_edge("IS 2796", "IS 1448", "MANDATES_TEST_METHOD", "Research Octane Number (RON), Sulphur content (XRF/UVF), and Distillation parameters")
        self._add_edge("IS 1460", "IS 1448", "MANDATES_TEST_METHOD", "Cetane Index, Flash Point (Abel), Kinematic Viscosity, and Sulphur content")

        self._add_edge("IS 13252", "IS 16046", "MANDATES_COMPONENT_CERT", "Embedded lithium batteries in IT equipment must independently hold valid BIS CRS registration")

    def _add_edge(self, source_id: str, target_id: str, relation: str, description: str):
        self._edges.append({
            "source": source_id,
            "target": target_id,
            "relation": relation,
            "description": description
        })

    def get_related_standards(self, is_code_or_text: str) -> List[Dict[str, Any]]:
        """Finds all cross-referenced testing methods, statutory orders, and sibling standards."""
        if not is_code_or_text:
            return []

        matched_keys = set()
        for node_id in self._nodes.keys():
            if node_id.lower() in is_code_or_text.lower():
                matched_keys.add(node_id)

        # Look for digits e.g. "1786" or "14543"
        digits = re.findall(r"\b\d{3,5}\b", is_code_or_text)
        for d in digits:
            key = f"IS {d}"
            if key in self._nodes:
                matched_keys.add(key)

        results = []
        for key in matched_keys:
            node = self._nodes.get(key, {})
            
            # Find outbound edges (test methods, siblings)
            connections = []
            for edge in self._edges:
                if edge["source"] == key:
                    target_node = self._nodes.get(edge["target"], {})
                    connections.append({
                        "relation": edge["relation"],
                        "target_code": target_node.get("code", edge["target"]),
                        "target_title": target_node.get("title", ""),
                        "details": edge["description"]
                    })
                elif edge["target"] == key:
                    source_node = self._nodes.get(edge["source"], {})
                    connections.append({
                        "relation": f"REFERENCED_BY ({edge['relation']})",
                        "target_code": source_node.get("code", edge["source"]),
                        "target_title": source_node.get("title", ""),
                        "details": edge["description"]
                    })

            results.append({
                "standard": node,
                "connections": connections
            })

        return results

    def format_graph_context(self, is_code_or_text: str) -> str:
        """Formats graph dependencies into a structured context block for RAG prompting."""
        related = self.get_related_standards(is_code_or_text)
        if not related:
            return ""

        lines = ["\n[KNOWLEDGE GRAPH: STATUTORY CROSS-REFERENCES & TEST METHODS]"]
        for item in related:
            std = item["standard"]
            lines.append(f"• Standard: {std.get('code', std.get('id'))} - {std.get('title')}")
            if "scheme" in std:
                lines.append(f"  - Statutory Certification: {std['scheme']}")
            if "qco" in std:
                lines.append(f"  - Mandatory QCO: {std['qco']} ({std.get('ministry', 'Govt of India')})")
            
            for conn in item["connections"]:
                lines.append(f"  - Link [{conn['relation']}]: {conn['target_code']} ({conn['target_title']}) -> {conn['details']}")

        return "\n".join(lines)


standards_graph_service = StandardsGraphService()
