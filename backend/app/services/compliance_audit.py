import re
import uuid
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from app.models.schemas import (
    AuditRequest,
    AuditResponse,
    ParameterAuditResult,
    ComplianceStatus,
    OverallVerdict
)
from app.core.database import log_audit


# Knowledge base of standard clause limits for automated high-precision compliance verification
STANDARD_BENCHMARKS = {
    "IS 14543": {
        "title": "Packaged Drinking Water (Other than Natural Mineral Water)",
        "year": "2018",
        "parameters": {
            "ph": {
                "name": "pH Value",
                "min": 6.5,
                "max": 8.5,
                "unit": "",
                "clause": "Clause 5.1 (Table 1, Item 3)",
                "critical": True,
                "test_method": "IS 3025 (Part 11)"
            },
            "tds": {
                "name": "Total Dissolved Solids (TDS)",
                "min": 0,
                "max": 500.0,
                "unit": "mg/L",
                "clause": "Clause 5.1 (Table 1, Item 4)",
                "critical": False,
                "test_method": "IS 3025 (Part 16)"
            },
            "turbidity": {
                "name": "Turbidity",
                "min": 0,
                "max": 2.0,
                "unit": "NTU",
                "clause": "Clause 5.1 (Table 1, Item 2)",
                "critical": False,
                "test_method": "IS 3025 (Part 10)"
            },
            "lead": {
                "name": "Lead (as Pb)",
                "min": 0,
                "max": 0.01,
                "unit": "mg/L",
                "clause": "Clause 5.2 (Table 2 - Toxic Substances, Item 1)",
                "critical": True,
                "test_method": "IS 3025 (Part 47)"
            },
            "arsenic": {
                "name": "Arsenic (as As)",
                "min": 0,
                "max": 0.01,
                "unit": "mg/L",
                "clause": "Clause 5.2 (Table 2 - Toxic Substances, Item 2)",
                "critical": True,
                "test_method": "IS 3025 (Part 37)"
            },
            "nitrate": {
                "name": "Nitrate (as NO3)",
                "min": 0,
                "max": 45.0,
                "unit": "mg/L",
                "clause": "Clause 5.1 (Table 1, Item 9)",
                "critical": True,
                "test_method": "IS 3025 (Part 34)"
            },
            "ecoli": {
                "name": "Escherichia coli (E. coli)",
                "min": 0,
                "max": 0,
                "unit": "cfu/250ml",
                "clause": "Clause 5.3 (Table 3 - Microbiological, Item 1)",
                "critical": True,
                "test_method": "IS 15185"
            },
            "coliform": {
                "name": "Coliform Bacteria",
                "min": 0,
                "max": 0,
                "unit": "cfu/250ml",
                "clause": "Clause 5.3 (Table 3 - Microbiological, Item 2)",
                "critical": True,
                "test_method": "IS 15185"
            }
        }
    },
    "IS 1786": {
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
        "year": "2008",
        "parameters": {
            "carbon": {
                "name": "Carbon (C) Content",
                "min": 0,
                "max": 0.30,
                "unit": "% max",
                "clause": "Clause 4.2 (Table 1 - Chemical Composition)",
                "critical": True,
                "test_method": "IS 228"
            },
            "sulphur": {
                "name": "Sulphur (S) Content",
                "min": 0,
                "max": 0.060,
                "unit": "% max",
                "clause": "Clause 4.2 (Table 1 - Chemical Composition)",
                "critical": True,
                "test_method": "IS 228"
            },
            "phosphorus": {
                "name": "Phosphorus (P) Content",
                "min": 0,
                "max": 0.060,
                "unit": "% max",
                "clause": "Clause 4.2 (Table 1 - Chemical Composition)",
                "critical": True,
                "test_method": "IS 228"
            },
            "yield_strength": {
                "name": "0.2% Proof Stress / Yield Strength (Fe 500)",
                "min": 500.0,
                "max": 9999.0,
                "unit": "N/mm² (MPa)",
                "clause": "Clause 8.1 (Table 3 - Mechanical Properties)",
                "critical": True,
                "test_method": "IS 1608"
            },
            "elongation": {
                "name": "Elongation (Gauge Length 5.65√A)",
                "min": 14.5,
                "max": 100.0,
                "unit": "% min",
                "clause": "Clause 8.1 (Table 3 - Mechanical Properties)",
                "critical": True,
                "test_method": "IS 1608"
            },
            "tensile_ratio": {
                "name": "Tensile Strength to Yield Strength Ratio (TS/YS)",
                "min": 1.08,
                "max": 2.50,
                "unit": "ratio",
                "clause": "Clause 8.1 (Table 3, Grade Fe 500D)",
                "critical": True,
                "test_method": "IS 1608"
            }
        }
    },
    "IS 4984": {
        "title": "High Density Polyethylene (HDPE) Pipes for Water Supply",
        "year": "2016",
        "parameters": {
            "density": {
                "name": "Base Polymer Density at 27°C",
                "min": 940.0,
                "max": 958.0,
                "unit": "kg/m³",
                "clause": "Clause 5.1 (Table 1 - Material Properties)",
                "critical": True,
                "test_method": "IS 7328"
            },
            "mfi": {
                "name": "Melt Flow Index (190°C / 5 kg)",
                "min": 0.20,
                "max": 1.10,
                "unit": "g/10 min",
                "clause": "Clause 5.2 (Table 1)",
                "critical": False,
                "test_method": "IS 2530"
            },
            "carbon_black": {
                "name": "Carbon Black Content",
                "min": 2.0,
                "max": 3.0,
                "unit": "%",
                "clause": "Clause 5.3 (Table 1)",
                "critical": True,
                "test_method": "IS 2530"
            },
            "hydrostatic_100h": {
                "name": "Hydrostatic Strength (100h at 20°C, PE 100)",
                "min": 12.4,
                "max": 9999.0,
                "unit": "MPa hoop stress",
                "clause": "Clause 8.1 (Table 4 - Hydrostatic Test)",
                "critical": True,
                "test_method": "IS 4984 Clause 8.1.1"
            }
        }
    },
    "IS 1293": {
        "title": "Plugs and Socket-Outlets of Rated Voltage up to 250 V",
        "year": "2019",
        "parameters": {
            "insulation_resistance": {
                "name": "Insulation Resistance at 500V DC",
                "min": 5.0,
                "max": 99999.0,
                "unit": "MΩ min",
                "clause": "Clause 16.1 (Insulation Test)",
                "critical": True,
                "test_method": "IS 1293 Clause 16"
            },
            "temperature_rise": {
                "name": "Terminal Temperature Rise under Rated Current",
                "min": 0.0,
                "max": 45.0,
                "unit": "°C max",
                "clause": "Clause 19.1 (Temperature Rise Test)",
                "critical": True,
                "test_method": "IS 1293 Clause 19"
            },
            "breaking_capacity": {
                "name": "Breaking Capacity (250V AC, 1.25 In)",
                "min": 50.0,
                "max": 9999.0,
                "unit": "cycles",
                "clause": "Clause 20.1 (Switching Operations)",
                "critical": True,
                "test_method": "IS 1293 Clause 20"
            }
        }
    },
    "IS 10500": {
        "title": "Drinking Water Specification (Potable Water)",
        "year": "2012",
        "parameters": {
            "ph": {
                "name": "pH Value",
                "min": 6.5,
                "max": 8.5,
                "unit": "",
                "clause": "Clause 4 (Table 1, Item 1)",
                "critical": True,
                "test_method": "IS 3025 (Part 11)"
            },
            "tds": {
                "name": "Total Dissolved Solids (TDS)",
                "min": 0,
                "max": 500.0,
                "unit": "mg/L",
                "clause": "Clause 4 (Table 1, Item 3)",
                "critical": False,
                "test_method": "IS 3025 (Part 16)"
            },
            "turbidity": {
                "name": "Turbidity",
                "min": 0,
                "max": 1.0,
                "unit": "NTU",
                "clause": "Clause 4 (Table 1, Item 4)",
                "critical": False,
                "test_method": "IS 3025 (Part 10)"
            },
            "total_hardness": {
                "name": "Total Hardness (as CaCO3)",
                "min": 0,
                "max": 200.0,
                "unit": "mg/L",
                "clause": "Clause 4 (Table 1, Item 6)",
                "critical": False,
                "test_method": "IS 3025 (Part 21)"
            },
            "chloride": {
                "name": "Chlorides (as Cl)",
                "min": 0,
                "max": 250.0,
                "unit": "mg/L",
                "clause": "Clause 4 (Table 1, Item 8)",
                "critical": False,
                "test_method": "IS 3025 (Part 32)"
            },
            "fluoride": {
                "name": "Fluoride (as F)",
                "min": 0,
                "max": 1.0,
                "unit": "mg/L",
                "clause": "Clause 4 (Table 1, Item 11)",
                "critical": True,
                "test_method": "IS 3025 (Part 60)"
            },
            "lead": {
                "name": "Lead (as Pb)",
                "min": 0,
                "max": 0.01,
                "unit": "mg/L",
                "clause": "Clause 4 (Table 2 - Toxic, Item 1)",
                "critical": True,
                "test_method": "IS 3025 (Part 47)"
            },
            "arsenic": {
                "name": "Arsenic (as As)",
                "min": 0,
                "max": 0.01,
                "unit": "mg/L",
                "clause": "Clause 4 (Table 2 - Toxic, Item 2)",
                "critical": True,
                "test_method": "IS 3025 (Part 37)"
            },
            "ecoli": {
                "name": "Escherichia coli (E. coli)",
                "min": 0,
                "max": 0,
                "unit": "cfu/100ml",
                "clause": "Clause 4 (Table 3 - Microbiological, Item 1)",
                "critical": True,
                "test_method": "IS 15185"
            }
        }
    },
    "IS 269": {
        "title": "Ordinary Portland Cement (33, 43 and 53 Grade)",
        "year": "2015",
        "parameters": {
            "soundness": {
                "name": "Soundness (Le Chatelier)",
                "min": 0,
                "max": 10.0,
                "unit": "mm",
                "clause": "Clause 6 (Table 2 - Physical, Item 2)",
                "critical": True,
                "test_method": "IS 4031 (Part 3)"
            },
            "initial_setting": {
                "name": "Initial Setting Time",
                "min": 30.0,
                "max": 9999.0,
                "unit": "minutes",
                "clause": "Clause 6 (Table 2 - Physical, Item 3)",
                "critical": True,
                "test_method": "IS 4031 (Part 5)"
            },
            "final_setting": {
                "name": "Final Setting Time",
                "min": 0,
                "max": 600.0,
                "unit": "minutes",
                "clause": "Clause 6 (Table 2 - Physical, Item 4)",
                "critical": False,
                "test_method": "IS 4031 (Part 5)"
            },
            "compressive_strength_28d": {
                "name": "28-Day Compressive Strength",
                "min": 43.0,
                "max": 9999.0,
                "unit": "MPa",
                "clause": "Clause 6 (Table 2 - Physical, Item 5)",
                "critical": True,
                "test_method": "IS 4031 (Part 6)"
            },
            "insoluble_residue": {
                "name": "Insoluble Residue",
                "min": 0,
                "max": 5.0,
                "unit": "%",
                "clause": "Clause 5 (Table 1 - Chemical, Item 2)",
                "critical": False,
                "test_method": "IS 4032"
            },
            "magnesia": {
                "name": "Magnesia (MgO) Content",
                "min": 0,
                "max": 6.0,
                "unit": "%",
                "clause": "Clause 5 (Table 1 - Chemical, Item 3)",
                "critical": True,
                "test_method": "IS 4032"
            }
        }
    },
    "IS 4151": {
        "title": "Protective Helmets for Two-Wheeler Riders",
        "year": "2015",
        "parameters": {
            "impact_attenuation": {
                "name": "Peak Impact Attenuation Acceleration",
                "min": 0,
                "max": 300.0,
                "unit": "g",
                "clause": "Clause 9.2 (Table 2 - Impact)",
                "critical": True,
                "test_method": "IS 4151 Annex A"
            },
            "retention_dynamic": {
                "name": "Retention System Dynamic Extension",
                "min": 0,
                "max": 25.0,
                "unit": "mm",
                "clause": "Clause 9.3 (Retention System)",
                "critical": True,
                "test_method": "IS 4151 Annex B"
            },
            "retention_residual": {
                "name": "Retention System Residual Extension",
                "min": 0,
                "max": 15.0,
                "unit": "mm",
                "clause": "Clause 9.3.2 (Residual Extension)",
                "critical": False,
                "test_method": "IS 4151 Annex B"
            },
            "rigidity_deformation": {
                "name": "Lateral Rigidity Max Deformation",
                "min": 0,
                "max": 40.0,
                "unit": "mm",
                "clause": "Clause 9.4 (Rigidity Test)",
                "critical": True,
                "test_method": "IS 4151 Annex C"
            }
        }
    },
    "IS 16102": {
        "title": "Self-Ballasted LED Lamps for General Lighting Services",
        "year": "2012",
        "parameters": {
            "luminous_efficacy": {
                "name": "Luminous Efficacy",
                "min": 80.0,
                "max": 9999.0,
                "unit": "lm/W",
                "clause": "Clause 8.1 (Efficacy Benchmark)",
                "critical": True,
                "test_method": "IS 16102 (Part 2)"
            },
            "power_factor": {
                "name": "Power Factor",
                "min": 0.90,
                "max": 1.0,
                "unit": "",
                "clause": "Clause 7.2 (Electrical Characteristics)",
                "critical": True,
                "test_method": "IS 16102 (Part 1)"
            },
            "harmonics_thd": {
                "name": "Total Harmonic Distortion (THD)",
                "min": 0,
                "max": 30.0,
                "unit": "%",
                "clause": "Clause 7.4 (Harmonic Currents)",
                "critical": False,
                "test_method": "IS 16102 (Part 1)"
            },
            "insulation_resistance": {
                "name": "Insulation Resistance",
                "min": 2.0,
                "max": 9999.0,
                "unit": "MOhm",
                "clause": "Clause 9.1 (Safety - Dielectric)",
                "critical": True,
                "test_method": "IS 16102 (Part 1)"
            }
        }
    },
    "IS 1417": {
        "title": "Gold & Gold Alloys, Jewellery/Artefacts - Fineness & Hallmarking",
        "year": "2016",
        "parameters": {
            "gold_fineness_22k": {
                "name": "22 Karat Gold Fineness",
                "min": 916.0,
                "max": 1000.0,
                "unit": "ppt",
                "clause": "Clause 4.1 (Table 1 - Grades)",
                "critical": True,
                "test_method": "IS 1418 (Fire Assay Method)"
            },
            "gold_fineness_18k": {
                "name": "18 Karat Gold Fineness",
                "min": 750.0,
                "max": 1000.0,
                "unit": "ppt",
                "clause": "Clause 4.1 (Table 1 - Grades)",
                "critical": True,
                "test_method": "IS 1418 (Fire Assay Method)"
            },
            "toxic_cadmium": {
                "name": "Cadmium Toxicity in Soldering",
                "min": 0,
                "max": 200.0,
                "unit": "ppm",
                "clause": "Clause 5.2 (Prohibited Solder Elements)",
                "critical": True,
                "test_method": "IS 1417 Annex C"
            },
            "toxic_lead": {
                "name": "Lead Content Restriction",
                "min": 0,
                "max": 200.0,
                "unit": "ppm",
                "clause": "Clause 5.2 (Hazardous Metals)",
                "critical": True,
                "test_method": "IS 1417 Annex C"
            }
        }
    }
}


class ComplianceAuditEngine:
    def __init__(self):
        pass

    def _normalize_key(self, name: str) -> str:
        s = name.lower()
        s = re.sub(r'[^a-z0-9]', '', s)
        return s

    def _find_matching_benchmark(self, standard_code: str, param_name: str) -> Tuple[Optional[Dict[str, Any]], str]:
        # Normalize standard code (e.g., "IS 14543:2018", "IS-14543", "IS14543" -> "is14543")
        norm_req = self._normalize_key(standard_code)
        matched_std_key = None
        for k in STANDARD_BENCHMARKS.keys():
            norm_k = self._normalize_key(k)
            if norm_k in norm_req or norm_req in norm_k:
                matched_std_key = k
                break

        if not matched_std_key:
            return None, "IS Standard"

        std_info = STANDARD_BENCHMARKS[matched_std_key]
        p_norm = self._normalize_key(param_name)

        alias_map = {
            "tds": "tds",
            "totaldissolvedsolids": "tds",
            "ph": "ph",
            "phvalue": "ph",
            "turbidity": "turbidity",
            "pb": "lead",
            "lead": "lead",
            "as": "arsenic",
            "arsenic": "arsenic",
            "no3": "nitrate",
            "nitrate": "nitrate",
            "ecoli": "ecoli",
            "escherichiacoli": "ecoli",
            "coliform": "coliform",
            "coliformbacteria": "coliform",
            "hardness": "total_hardness",
            "totalhardness": "total_hardness",
            "chloride": "chloride",
            "chlorides": "chloride",
            "fluoride": "fluoride",
            "carbon": "carbon",
            "sulphur": "sulphur",
            "sulfur": "sulphur",
            "phosphorus": "phosphorus",
            "yieldstrength": "yield_strength",
            "proofstress": "yield_strength",
            "02proofstress": "yield_strength",
            "tensilestrength": "tensile_ratio",
            "tensileratio": "tensile_ratio",
            "tsys": "tensile_ratio",
            "tsysratio": "tensile_ratio",
            "elongation": "elongation",
            "density": "density",
            "mfi": "mfi",
            "meltflowindex": "mfi",
            "carbonblack": "carbon_black",
            "hydrostaticstrength": "hydrostatic_100h",
            "insulationresistance": "insulation_resistance",
            "temperaturerise": "temperature_rise",
            "terminaltemperaturerise": "temperature_rise",
            "breakingcapacity": "breaking_capacity",
            "compressivestrength": "compressive_strength_28d",
            "compressivestrength28d": "compressive_strength_28d",
            "initialsetting": "initial_setting",
            "initialsettingtime": "initial_setting",
            "finalsetting": "final_setting",
            "finalsettingtime": "final_setting",
            "soundness": "soundness"
        }

        mapped_key = alias_map.get(p_norm)
        if mapped_key and mapped_key in std_info["parameters"]:
            return std_info["parameters"][mapped_key], std_info["title"]

        for p_key, p_val in std_info["parameters"].items():
            if p_key in p_norm or self._normalize_key(p_val["name"]) in p_norm or p_norm in self._normalize_key(p_val["name"]):
                return p_val, std_info["title"]

        return None, std_info["title"]

    def perform_audit(self, request: AuditRequest) -> AuditResponse:
        audit_id = f"BIS-AUD-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        results: List[ParameterAuditResult] = []
        passed_count = 0
        failed_count = 0
        warning_count = 0
        critical_failure = False
        std_title = "Bureau of Indian Standards Specification"

        for p_input in request.parameters:
            bm, found_title = self._find_matching_benchmark(request.standard_is_code, p_input.parameter_name)
            if found_title != "IS Standard":
                std_title = found_title

            # Parse numeric or qualitative tested value
            val_str = p_input.tested_value.strip()
            num_match = re.search(r'[-+]?\d*\.?\d+', val_str)
            is_zero_qualitative = any(w in val_str.lower() for w in ["nil", "absent", "not detected", "zero", "none", "nd", "negative"])
            
            if bm and (num_match or is_zero_qualitative):
                if num_match:
                    tested_num = float(num_match.group())
                else:
                    tested_num = 0.0
                min_lim = bm["min"]
                max_lim = bm["max"]
                unit = bm["unit"] or p_input.unit
                clause = bm["clause"]
                is_crit = bm.get("critical", False)
                
                # Format limit string
                if max_lim == 0 and min_lim == 0:
                    limit_str = f"Nil / Absent ({unit})"
                elif max_lim >= 9999.0:
                    limit_str = f"Min {min_lim} {unit}"
                elif min_lim == 0:
                    limit_str = f"Max {max_lim} {unit}"
                else:
                    limit_str = f"{min_lim} to {max_lim} {unit}"

                # Evaluate compliance
                is_pass = (tested_num >= min_lim) and (tested_num <= max_lim)
                
                if is_pass:
                    status = ComplianceStatus.PASS
                    passed_count += 1
                    deviation = "0.00% (Within Limits)"
                    remarks = f"Complies with {clause}. Tested value {tested_num} conforms to standard requirements."
                else:
                    status = ComplianceStatus.FAIL
                    failed_count += 1
                    if is_crit:
                        critical_failure = True
                    
                    if tested_num > max_lim:
                        diff = round(((tested_num - max_lim) / max_lim) * 100, 2) if max_lim > 0 else 100.0
                        deviation = f"+{diff}% Exceedance"
                    else:
                        diff = round(((min_lim - tested_num) / min_lim) * 100, 2) if min_lim > 0 else 0.0
                        deviation = f"-{diff}% Deficit"

                    remarks = f"NON-COMPLIANT with {clause}. Permissible bound: {limit_str}. Test Method: {bm.get('test_method', 'Standard')}"

                results.append(ParameterAuditResult(
                    parameter_name=bm["name"],
                    tested_value=f"{tested_num} {unit}".strip(),
                    standard_limit=limit_str,
                    unit=unit,
                    clause_reference=clause,
                    status=status,
                    deviation=deviation,
                    remarks=remarks
                ))
            else:
                # Custom or qualitative parameter
                status = ComplianceStatus.PASS if "pass" in val_str.lower() or "nil" in val_str.lower() or "absent" in val_str.lower() else ComplianceStatus.CONDITIONAL
                if status == ComplianceStatus.PASS:
                    passed_count += 1
                else:
                    warning_count += 1

                results.append(ParameterAuditResult(
                    parameter_name=p_input.parameter_name,
                    tested_value=val_str,
                    standard_limit="Specified in Standard / Conforming",
                    unit=p_input.unit,
                    clause_reference="Standard Specification Clause",
                    status=status,
                    deviation="N/A",
                    remarks=f"Evaluated against specification guidelines. {p_input.notes or ''}"
                ))

        total = len(results)
        compliance_pct = round((passed_count / total * 100), 1) if total > 0 else 0.0

        if failed_count == 0:
            verdict = OverallVerdict.CONFORMING
            summary = (
                f"Batch {request.batch_number} of {request.product_name} manufactured by {request.manufacturer_name} "
                f"fully CONFORMS to all audited clauses of {request.standard_is_code}. "
                f"All {passed_count} parameters satisfy the mandatory tolerance and safety thresholds."
            )
        elif critical_failure:
            verdict = OverallVerdict.NON_CONFORMING
            summary = (
                f"CRITICAL NON-CONFORMANCE DETECTED: Batch {request.batch_number} of {request.product_name} "
                f"FAILS mandatory safety/toxic substance clauses of {request.standard_is_code}. "
                f"{failed_count} parameter(s) exceeded statutory limits. Product cannot be granted or maintain ISI Mark certification."
            )
        else:
            verdict = OverallVerdict.CONDITIONAL_COMPLIANCE
            summary = (
                f"Batch {request.batch_number} exhibits minor non-critical variances. "
                f"Corrective Action Report (CAR) required within 14 working days."
            )

        report_url = f"/api/v1/audit/report/{audit_id}"

        # Save to SQLite database
        log_audit(
            audit_id=audit_id,
            standard_is_code=request.standard_is_code,
            standard_title=std_title,
            product_name=request.product_name,
            manufacturer_name=request.manufacturer_name,
            batch_number=request.batch_number,
            testing_lab=request.testing_lab,
            overall_verdict=verdict.value,
            passed_count=passed_count,
            failed_count=failed_count,
            warning_count=warning_count,
            total_count=total,
            compliance_score=compliance_pct,
            summary=summary,
            parameter_results=[r.dict() for r in results]
        )

        return AuditResponse(
            audit_id=audit_id,
            standard_is_code=request.standard_is_code,
            standard_title=std_title,
            product_name=request.product_name,
            manufacturer_name=request.manufacturer_name,
            batch_number=request.batch_number,
            testing_lab=request.testing_lab,
            overall_verdict=verdict,
            passed_count=passed_count,
            failed_count=failed_count,
            warning_count=warning_count,
            total_count=total,
            compliance_score_percent=compliance_pct,
            summary=summary,
            parameter_results=results,
            report_download_url=report_url,
            created_at=datetime.utcnow().strftime("%d-%b-%Y %H:%M UTC")
        )


compliance_audit_engine = ComplianceAuditEngine()
