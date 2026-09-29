import logging
from app.services.pdf_table_parser import ParsedChunk
from app.services.vector_store import vector_store_service
from app.core.database import get_all_standards_db

logger = logging.getLogger(__name__)


def get_seed_chunks() -> list[ParsedChunk]:
    chunks = []

    # =========================================================================
    # 1. IS 14543: 2018 - Packaged Drinking Water
    # =========================================================================
    is14543_code = "IS 14543:2018"
    is14543_title = "Packaged Drinking Water (Other than Packaged Natural Mineral Water) - Specification"

    # Scope & Marking Text
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is14543_code} - {is14543_title}\n"
            f"PAGE: 1 | CLAUSE: Clause 1.0 Scope\n\n"
            f"This Indian Standard prescribes the requirements and methods of sampling and test for packaged drinking water "
            f"other than packaged natural mineral water. The water shall be derived from any source of potable water which may "
            f"be subjected to treatments, namely, decantation, filtration, combination of filtration, aerations, filtration with "
            f"membrane filter, depth filter, cartridge filter, activated carbon filtration, demineralization, remineralization, "
            f"reverse osmosis and pack after disinfection by ozonation or UV treatment."
        ),
        is_code=is14543_code,
        doc_title=is14543_title,
        clause="Clause 1.0 Scope",
        page_number=1,
        is_table=False
    ))

    # Table 1: Physical & Chemical Requirements
    tbl1_columns = ["Sl No.", "Characteristic", "Permissible Requirement / Limit", "Method of Test Ref"]
    tbl1_rows = [
        ["1", "Colour, Hazen Units", "Max 2", "IS 3025 (Part 4)"],
        ["2", "Odour & Taste", "Agreeable / Unobjectionable", "IS 3025 (Part 5)"],
        ["3", "Turbidity, NTU", "Max 2", "IS 3025 (Part 10)"],
        ["4", "pH Value", "6.5 to 8.5", "IS 3025 (Part 11)"],
        ["5", "Total Dissolved Solids (TDS)", "Max 500 mg/L", "IS 3025 (Part 16)"],
        ["6", "Total Hardness (as CaCO3)", "Max 200 mg/L", "IS 3025 (Part 21)"],
        ["7", "Calcium (as Ca)", "Max 75 mg/L", "IS 3025 (Part 40)"],
        ["8", "Magnesium (as Mg)", "Max 30 mg/L", "IS 3025 (Part 46)"],
        ["9", "Nitrate (as NO3)", "Max 45 mg/L", "IS 3025 (Part 34)"],
        ["10", "Sulphate (as SO4)", "Max 200 mg/L", "IS 3025 (Part 24)"]
    ]
    md_tbl1 = (
        "### Table 1: Physical and Chemical Requirements (IS 14543:2018 Clause 5.1)\n\n"
        "| Sl No. | Characteristic | Permissible Requirement / Limit | Method of Test Ref |\n"
        "| --- | --- | --- | --- |\n"
        "| 1 | Colour, Hazen Units | Max 2 | IS 3025 (Part 4) |\n"
        "| 2 | Odour & Taste | Agreeable / Unobjectionable | IS 3025 (Part 5) |\n"
        "| 3 | Turbidity, NTU | Max 2 | IS 3025 (Part 10) |\n"
        "| 4 | pH Value | 6.5 to 8.5 | IS 3025 (Part 11) |\n"
        "| 5 | Total Dissolved Solids (TDS) | Max 500 mg/L | IS 3025 (Part 16) |\n"
        "| 6 | Total Hardness (as CaCO3) | Max 200 mg/L | IS 3025 (Part 21) |\n"
        "| 7 | Calcium (as Ca) | Max 75 mg/L | IS 3025 (Part 40) |\n"
        "| 8 | Magnesium (as Mg) | Max 30 mg/L | IS 3025 (Part 46) |\n"
        "| 9 | Nitrate (as NO3) | Max 45 mg/L | IS 3025 (Part 34) |\n"
        "| 10 | Sulphate (as SO4) | Max 200 mg/L | IS 3025 (Part 24) |"
    )
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is14543_code} - {is14543_title}\n"
            f"PAGE: 2 | CLAUSE: Clause 5.1 Physical and Chemical Requirements\n\n"
            f"{md_tbl1}\n\n"
            f"Detailed Specifications:\n"
            f"- pH must be strictly maintained between 6.5 and 8.5.\n"
            f"- TDS permissible limit is 500 mg/L max to avoid mineral saturation.\n"
            f"- Turbidity must not exceed 2 NTU."
        ),
        is_code=is14543_code,
        doc_title=is14543_title,
        clause="Clause 5.1 (Table 1)",
        page_number=2,
        is_table=True,
        table_number="Table 1",
        table_title="Physical and Chemical Requirements",
        table_data={"columns": tbl1_columns, "rows": tbl1_rows, "markdown": md_tbl1}
    ))

    # Table 2: Requirements for Toxic Substances
    tbl2_columns = ["Sl No.", "Toxic Substance", "Permissible Limit (Max)", "Method of Test Ref"]
    tbl2_rows = [
        ["1", "Lead (as Pb)", "0.01 mg/L", "IS 3025 (Part 47)"],
        ["2", "Arsenic (as As)", "0.01 mg/L", "IS 3025 (Part 37)"],
        ["3", "Cadmium (as Cd)", "0.003 mg/L", "IS 3025 (Part 41)"],
        ["4", "Mercury (as Hg)", "0.001 mg/L", "IS 3025 (Part 48)"],
        ["5", "Chromium (as Cr)", "0.05 mg/L", "IS 3025 (Part 52)"],
        ["6", "Copper (as Cu)", "0.05 mg/L", "IS 3025 (Part 42)"],
        ["7", "Cyanide (as CN)", "0.05 mg/L", "IS 3025 (Part 27)"]
    ]
    md_tbl2 = (
        "### Table 2: Requirements for Toxic Substances (IS 14543:2018 Clause 5.2)\n\n"
        "| Sl No. | Toxic Substance | Permissible Limit (Max) | Method of Test Ref |\n"
        "| --- | --- | --- | --- |\n"
        "| 1 | Lead (as Pb) | 0.01 mg/L | IS 3025 (Part 47) |\n"
        "| 2 | Arsenic (as As) | 0.01 mg/L | IS 3025 (Part 37) |\n"
        "| 3 | Cadmium (as Cd) | 0.003 mg/L | IS 3025 (Part 41) |\n"
        "| 4 | Mercury (as Hg) | 0.001 mg/L | IS 3025 (Part 48) |\n"
        "| 5 | Chromium (as Cr) | 0.05 mg/L | IS 3025 (Part 52) |\n"
        "| 6 | Copper (as Cu) | 0.05 mg/L | IS 3025 (Part 42) |\n"
        "| 7 | Cyanide (as CN) | 0.05 mg/L | IS 3025 (Part 27) |"
    )
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is14543_code} - {is14543_title}\n"
            f"PAGE: 3 | CLAUSE: Clause 5.2 Toxic Substances\n\n"
            f"{md_tbl2}\n\n"
            f"Crucial Health Limits:\n"
            f"- Lead (Pb) limit is strictly 0.01 mg/L maximum. Any value above this constitutes critical contamination.\n"
            f"- Arsenic (As) limit is 0.01 mg/L max.\n"
            f"- Mercury (Hg) limit is 0.001 mg/L max."
        ),
        is_code=is14543_code,
        doc_title=is14543_title,
        clause="Clause 5.2 (Table 2)",
        page_number=3,
        is_table=True,
        table_number="Table 2",
        table_title="Requirements for Toxic Substances",
        table_data={"columns": tbl2_columns, "rows": tbl2_rows, "markdown": md_tbl2}
    ))

    # Clause 7: Marking and ISI Verification
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is14543_code} - {is14543_title}\n"
            f"PAGE: 5 | CLAUSE: Clause 7.0 Packaging, Marking and ISI Certification\n\n"
            f"7.1 Packing: Packaged drinking water shall be packed in clean, hygienic, colourless, transparent and tamperproof "
            f"containers conforming to IS 15410 or food-grade plastics conforming to IS 10146.\n\n"
            f"7.2 Marking: Each container shall bear legibly and indelibly the following:\n"
            f"a) Name of the product: 'Packaged Drinking Water'\n"
            f"b) Net volume in metric units\n"
            f"c) Name and address of the manufacturer with contact details\n"
            f"d) Batch number or code number\n"
            f"e) Date of manufacture and 'Best before' date\n"
            f"f) Standard BIS ISI Certification Mark with CM/L License Number (e.g. CM/L-XXXXXXXXXX)\n"
            f"7.3 Consumers can verify the 7 or 8-digit CM/L number through the BIS Care App."
        ),
        is_code=is14543_code,
        doc_title=is14543_title,
        clause="Clause 7.0 Marking and ISI Certification",
        page_number=5,
        is_table=False
    ))

    # =========================================================================
    # 2. IS 1786: 2008 - High Strength Deformed Steel Bars (TMT)
    # =========================================================================
    is1786_code = "IS 1786:2008"
    is1786_title = "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement - Specification"

    # Table 1: Chemical Composition
    tbl1786_chem_cols = ["Grade", "Carbon (Max %)", "Sulphur (Max %)", "Phosphorus (Max %)", "S + P (Max %)"]
    tbl1786_chem_rows = [
        ["Fe 415", "0.30", "0.060", "0.060", "0.110"],
        ["Fe 415D", "0.25", "0.045", "0.045", "0.085"],
        ["Fe 500", "0.30", "0.055", "0.055", "0.105"],
        ["Fe 500D", "0.25", "0.040", "0.040", "0.075"],
        ["Fe 550", "0.30", "0.055", "0.055", "0.100"],
        ["Fe 550D", "0.25", "0.040", "0.040", "0.075"],
        ["Fe 600", "0.30", "0.040", "0.040", "0.075"]
    ]
    md_chem_tmt = (
        "### Table 1: Chemical Composition (IS 1786:2008 Clause 4.2)\n\n"
        "| Grade | Carbon (Max %) | Sulphur (Max %) | Phosphorus (Max %) | S + P (Max %) |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Fe 415 | 0.30 | 0.060 | 0.060 | 0.110 |\n"
        "| Fe 415D | 0.25 | 0.045 | 0.045 | 0.085 |\n"
        "| Fe 500 | 0.30 | 0.055 | 0.055 | 0.105 |\n"
        "| Fe 500D | 0.25 | 0.040 | 0.040 | 0.075 |\n"
        "| Fe 550 | 0.30 | 0.055 | 0.055 | 0.100 |\n"
        "| Fe 550D | 0.25 | 0.040 | 0.040 | 0.075 |\n"
        "| Fe 600 | 0.30 | 0.040 | 0.040 | 0.075 |"
    )
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is1786_code} - {is1786_title}\n"
            f"PAGE: 2 | CLAUSE: Clause 4.2 Chemical Composition\n\n"
            f"{md_chem_tmt}\n\n"
            f"Key Chemical Requirements:\n"
            f"- 'D' grades (e.g. Fe 500D) designate enhanced ductility with lower Sulphur & Phosphorus (max 0.040% each) for earthquake zones.\n"
            f"- Maximum carbon content is restricted to 0.25% in 'D' grades to ensure superior weldability."
        ),
        is_code=is1786_code,
        doc_title=is1786_title,
        clause="Clause 4.2 (Table 1)",
        page_number=2,
        is_table=True,
        table_number="Table 1",
        table_title="Chemical Composition of TMT Rebars",
        table_data={"columns": tbl1786_chem_cols, "rows": tbl1786_chem_rows, "markdown": md_chem_tmt}
    ))

    # Table 3: Mechanical Properties
    tbl1786_mech_cols = ["Property / Grade", "Fe 415", "Fe 415D", "Fe 500", "Fe 500D", "Fe 550", "Fe 550D", "Fe 600"]
    tbl1786_mech_rows = [
        ["0.2% Proof Stress / Yield Strength (Min N/mm²)", "415.0", "415.0", "500.0", "500.0", "550.0", "550.0", "600.0"],
        ["Tensile Strength (TS) Min", "1.10 x YS (Min 485)", "1.12 x YS (Min 500)", "1.08 x YS (Min 545)", "1.10 x YS (Min 565)", "1.06 x YS (Min 585)", "1.08 x YS (Min 600)", "1.06 x YS (Min 660)"],
        ["Total Elongation (Min % on 5.65√A)", "14.5%", "18.0%", "12.0%", "16.0%", "10.0%", "14.5%", "10.0%"],
        ["Total Elongation at Max Force (Agt Min %)", "-", "5%", "-", "5%", "-", "5%", "-"]
    ]
    md_mech_tmt = (
        "### Table 3: Mechanical Properties of Deformed Bars (IS 1786:2008 Clause 8.1)\n\n"
        "| Property / Grade | Fe 415 | Fe 415D | Fe 500 | Fe 500D | Fe 550 | Fe 550D | Fe 600 |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| 0.2% Proof Stress / Yield Strength (Min N/mm²) | 415.0 | 415.0 | 500.0 | 500.0 | 550.0 | 550.0 | 600.0 |\n"
        "| Tensile Strength (TS) Min | 1.10 x YS | 1.12 x YS | 1.08 x YS | 1.10 x YS | 1.06 x YS | 1.08 x YS | 1.06 x YS |\n"
        "| Total Elongation (Min %) | 14.5% | 18.0% | 12.0% | 16.0% | 10.0% | 14.5% | 10.0% |\n"
        "| Total Elongation at Max Force (Agt) | - | 5% | - | 5% | - | 5% | - |"
    )
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is1786_code} - {is1786_title}\n"
            f"PAGE: 4 | CLAUSE: Clause 8.1 Mechanical Properties\n\n"
            f"{md_mech_tmt}\n\n"
            f"Structural Engineering Insights:\n"
            f"- Fe 500D rebar requires minimum 500 N/mm² yield strength and minimum 16% elongation.\n"
            f"- The TS/YS ratio for Fe 500D must not fall below 1.10 to prevent sudden brittle collapse under seismic stress."
        ),
        is_code=is1786_code,
        doc_title=is1786_title,
        clause="Clause 8.1 (Table 3)",
        page_number=4,
        is_table=True,
        table_number="Table 3",
        table_title="Mechanical Properties of TMT Rebars",
        table_data={"columns": tbl1786_mech_cols, "rows": tbl1786_mech_rows, "markdown": md_mech_tmt}
    ))

    # =========================================================================
    # 3. IS 4984: 2016 - High Density Polyethylene (HDPE) Pipes
    # =========================================================================
    is4984_code = "IS 4984:2016"
    is4984_title = "High Density Polyethylene (HDPE) Pipes for Water Supply - Specification"

    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is4984_code} - {is4984_title}\n"
            f"PAGE: 2 | CLAUSE: Clause 5.0 Material Requirements\n\n"
            f"5.1 Raw Material: The HDPE pipe material shall be designated as PE 63, PE 80, or PE 100 based on Minimum Required "
            f"Strength (MRS) of 6.3 MPa, 8.0 MPa, and 10.0 MPa respectively at 20°C for 50 years.\n"
            f"5.2 Density: The base density of virgin polymer at 27°C shall be between 940.0 kg/m³ and 958.0 kg/m³ when tested as per IS 7328.\n"
            f"5.3 Carbon Black Content: Black pipes shall contain 2.0% to 3.0% by mass of carbon black, uniformly dispersed (dispersion grade ≤ 3) "
            f"to guarantee UV resistance against sunlight degradation for outdoor municipal installations."
        ),
        is_code=is4984_code,
        doc_title=is4984_title,
        clause="Clause 5.0 Material Requirements",
        page_number=2,
        is_table=False
    ))

    # Table 4: Hydrostatic Strength Test
    tbl4984_cols = ["Designation", "Test Temp (°C)", "Duration (Hours)", "Induced Hoop Stress (MPa)"]
    tbl4984_rows = [
        ["PE 100", "20°C", "100 h", "12.4 MPa"],
        ["PE 100", "80°C", "165 h", "5.4 MPa"],
        ["PE 100", "80°C", "1000 h", "5.0 MPa"],
        ["PE 80", "20°C", "100 h", "10.0 MPa"],
        ["PE 80", "80°C", "165 h", "4.5 MPa"]
    ]
    md_hdpe = (
        "### Table 4: Hydrostatic Strength Test Requirements (IS 4984:2016 Clause 8.1)\n\n"
        "| Designation | Test Temp (°C) | Duration (Hours) | Induced Hoop Stress (MPa) |\n"
        "| --- | --- | --- | --- |\n"
        "| PE 100 | 20°C | 100 h | 12.4 MPa |\n"
        "| PE 100 | 80°C | 165 h | 5.4 MPa |\n"
        "| PE 100 | 80°C | 1000 h | 5.0 MPa |\n"
        "| PE 80 | 20°C | 100 h | 10.0 MPa |\n"
        "| PE 80 | 80°C | 165 h | 4.5 MPa |"
    )
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is4984_code} - {is4984_title}\n"
            f"PAGE: 5 | CLAUSE: Clause 8.1 Hydrostatic Internal Pressure Test\n\n"
            f"{md_hdpe}\n\n"
            f"Testing Criteria:\n"
            f"Pipes must not burst, weep, or show localized swelling during the 100-hour hydrostatic test at 20°C under 12.4 MPa hoop stress."
        ),
        is_code=is4984_code,
        doc_title=is4984_title,
        clause="Clause 8.1 (Table 4)",
        page_number=5,
        is_table=True,
        table_number="Table 4",
        table_title="Hydrostatic Strength Requirements",
        table_data={"columns": tbl4984_cols, "rows": tbl4984_rows, "markdown": md_hdpe}
    ))

    # =========================================================================
    # 4. IS 1293: 2019 - Plugs and Socket-Outlets
    # =========================================================================
    is1293_code = "IS 1293:2019"
    is1293_title = "Plugs and Socket-Outlets of Rated Voltage up to and including 250 V - Specification"

    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is1293_code} - {is1293_title}\n"
            f"PAGE: 3 | CLAUSE: Clause 6.0 Ratings and Safety Configurations\n\n"
            f"6.1 Standard Ratings: Plugs and socket-outlets shall have standard rated current of 6A or 16A at 250V AC 50Hz.\n"
            f"6.2 Shutters: All 6A and 16A socket-outlets for domestic household use shall be provided with integrated safety shutters "
            f"that automatically shield live contacts when the plug is withdrawn, preventing accidental child finger insertion.\n"
            f"6.3 Insulation Resistance: Shall be not less than 5 MΩ when measured with a 500V DC Megger between live parts and earth.\n"
            f"6.4 Temperature Rise: The terminal temperature rise shall not exceed 45°C during continuous operation under 1.1 times rated load."
        ),
        is_code=is1293_code,
        doc_title=is1293_title,
        clause="Clause 6.0 Ratings and Safety Configurations",
        page_number=3,
        is_table=False
    ))

    # =========================================================================
    # 5. IS 4151: 2015 - Protective Helmets for Two-Wheelers
    # =========================================================================
    is4151_code = "IS 4151:2015"
    is4151_title = "Protective Helmets for Two-Wheeler Riders - Specification"

    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is4151_code} - {is4151_title}\n"
            f"PAGE: 4 | CLAUSE: Clause 8.0 Impact Attenuation and Chin Strap Retention\n\n"
            f"8.1 Impact Test: When dropped onto flat and hemispherical steel anvils from a height giving an impact velocity of 7.0 m/s, "
            f"the peak acceleration recorded by the headform triaxial accelerometer shall NOT exceed 300g, and the cumulative time during "
            f"which acceleration exceeds 150g shall not exceed 5 milliseconds.\n"
            f"8.2 Retention System (Chin Strap): Under a dynamic drop mass of 10 kg from 750 mm height, the dynamic extension of the "
            f"strap shall not exceed 35 mm and residual displacement shall not exceed 25 mm.\n"
            f"8.3 Mandatory ISI Marking: As per Ministry of Road Transport & Highways (MoRTH) notification, all two-wheeler helmets sold in "
            f"India must carry non-detachable, tamper-evident ISI certification marks with CM/L number."
        ),
        is_code=is4151_code,
        doc_title=is4151_title,
        clause="Clause 8.0 Impact Attenuation and Chin Strap Retention",
        page_number=4,
        is_table=False
    ))

    # =========================================================================
    # 6. IS 2796: 2017 - Motor Gasoline (Petrol for Petrol Bunks & Retail Outlets)
    # =========================================================================
    is2796_code = "IS 2796:2017"
    is2796_title = "Motor Gasoline (Petrol) for Automotive Engines - Specification"

    tbl_petrol_cols = ["Sl No.", "Parameter / Characteristic", "BS-VI Standard Requirement", "Test Method Ref"]
    tbl_petrol_rows = [
        ["1", "Research Octane Number (RON)", "Min 91.0 (Regular) / Min 95.0 (Premium)", "IS 1448 [P:27]"],
        ["2", "Anti-Knock Index (AKI)", "Min 84.0", "IS 1448 [P:27]"],
        ["3", "Density at 15°C", "720.0 to 775.0 kg/m³", "IS 1448 [P:16]"],
        ["4", "Total Sulphur Content", "Max 10.0 mg/kg (BS-VI Clean Fuel Standard)", "IS 1448 [P:155]"],
        ["5", "Lead Content (as Pb)", "Max 0.005 g/L (Unleaded Gasoline)", "IS 1448 [P:38]"],
        ["6", "Benzene Content", "Max 1.0 % volume", "IS 1448 [P:154]"],
        ["7", "Ethanol Blending (E10/E20)", "Up to 10% (E10) / Up to 20% (E20) as marked", "IS 2796 Annex D"],
        ["8", "Reid Vapour Pressure (RVP)", "Max 60 kPa (Summer) / Max 70 kPa (Winter)", "IS 1448 [P:39]"]
    ]
    md_tbl_petrol = (
        "### Table 1: BS-VI Motor Gasoline Technical Requirements (IS 2796:2017 Clause 4.1)\n\n"
        "| Sl No. | Parameter / Characteristic | BS-VI Standard Requirement | Test Method Ref |\n"
        "| --- | --- | --- | --- |\n"
        "| 1 | Research Octane Number (RON) | Min 91.0 (Regular) / Min 95.0 (Premium) | IS 1448 [P:27] |\n"
        "| 2 | Anti-Knock Index (AKI) | Min 84.0 | IS 1448 [P:27] |\n"
        "| 3 | Density at 15°C | 720.0 to 775.0 kg/m³ | IS 1448 [P:16] |\n"
        "| 4 | Total Sulphur Content | Max 10.0 mg/kg (BS-VI Clean Fuel) | IS 1448 [P:155] |\n"
        "| 5 | Lead Content (as Pb) | Max 0.005 g/L (Unleaded) | IS 1448 [P:38] |\n"
        "| 6 | Benzene Content | Max 1.0 % volume | IS 1448 [P:154] |\n"
        "| 7 | Ethanol Blending (E10/E20) | Up to 10% / 20% by volume | IS 2796 Annex D |\n"
        "| 8 | Reid Vapour Pressure (RVP) | Max 60 kPa (Summer) | IS 1448 [P:39] |"
    )
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is2796_code} - {is2796_title}\n"
            f"PAGE: 2 | CLAUSE: Clause 4.0 Requirements and Regulatory Compliance for Petrol Pumps\n\n"
            f"{md_tbl_petrol}\n\n"
            f"Statutory Rules for Petrol Bunks and Retail Outlets:\n"
            f"- Certification Scheme: Scheme-I (ISI Mark Certification) under BIS Act 2016.\n"
            f"- Quality Control Order (QCO): Mandatory fuel quality enforcement under Ministry of Petroleum and Natural Gas (MoPNG).\n"
            f"- Co-requisite Clearances: Petroleum and Explosives Safety Organization (PESO) license for underground storage, "
            f"Legal Metrology Department stamping for fuel dispenser flow meter calibration, and OISD-141 safety compliance."
        ),
        is_code=is2796_code,
        doc_title=is2796_title,
        clause="Clause 4.1 (Table 1)",
        page_number=2,
        is_table=True,
        table_number="Table 1",
        table_title="BS-VI Motor Gasoline Technical Requirements",
        table_data={"columns": tbl_petrol_cols, "rows": tbl_petrol_rows, "markdown": md_tbl_petrol}
    ))

    # =========================================================================
    # 7. IS 1460: 2017 - Automotive Diesel Fuel (HSD for Commercial & Retail Bunks)
    # =========================================================================
    is1460_code = "IS 1460:2017"
    is1460_title = "Automotive Diesel Fuel (High Speed Diesel - HSD) - Specification"

    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is1460_code} - {is1460_title}\n"
            f"PAGE: 1 | CLAUSE: Clause 5.0 High Speed Diesel BS-VI Specifications\n\n"
            f"Mandatory Diesel Parameters for Retail Outlets and Industrial Consumers:\n"
            f"1. Cetane Number: Minimum 51.0 (measured via IS 1448 [P:9]).\n"
            f"2. Cetane Index: Minimum 46.0.\n"
            f"3. Density at 15°C: 820.0 to 845.0 kg/m³.\n"
            f"4. Sulphur Content: Maximum 10.0 mg/kg (BS-VI ultra-low sulphur diesel).\n"
            f"5. Flash Point (Abel): Minimum 35.0°C (prevents explosive vapour formation at ambient petrol pump temperature).\n"
            f"6. Kinematic Viscosity at 40°C: 2.00 to 4.50 cSt.\n"
            f"7. Water Content: Maximum 200 mg/kg.\n"
            f"8. Certification Scheme: Mandatory Scheme-I ISI Mark under MoPNG notification."
        ),
        is_code=is1460_code,
        doc_title=is1460_title,
        clause="Clause 5.0 High Speed Diesel Specifications",
        page_number=1,
        is_table=False
    ))

    # =========================================================================
    # 8. IS 269: 2015 - Ordinary Portland Cement (OPC 33, 43, 53 Grade)
    # =========================================================================
    is269_code = "IS 269:2015"
    is269_title = "Ordinary Portland Cement (33, 43 and 53 Grade) - Specification"

    tbl_cement_cols = ["Grade", "Min 3-Day Compressive Strength", "Min 7-Day Strength", "Min 28-Day Strength", "Soundness (Le-Chatelier)"]
    tbl_cement_rows = [
        ["OPC 33", "16 MPa", "22 MPa", "33 MPa", "Max 10 mm"],
        ["OPC 43", "23 MPa", "33 MPa", "43 MPa", "Max 10 mm"],
        ["OPC 53", "27 MPa", "37 MPa", "53 MPa", "Max 10 mm"]
    ]
    md_tbl_cement = (
        "### Table 1: Compressive Strength & Physical Requirements (IS 269:2015 Clause 6.1)\n\n"
        "| Grade | Min 3-Day Strength | Min 7-Day Strength | Min 28-Day Strength | Soundness (Le-Chatelier) |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| OPC 33 | 16 MPa | 22 MPa | 33 MPa | Max 10 mm |\n"
        "| OPC 43 | 23 MPa | 33 MPa | 43 MPa | Max 10 mm |\n"
        "| OPC 53 | 27 MPa | 37 MPa | 53 MPa | Max 10 mm |"
    )
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is269_code} - {is269_title}\n"
            f"PAGE: 3 | CLAUSE: Clause 6.0 Physical and Chemical Requirements for Cement Manufacturing\n\n"
            f"{md_tbl_cement}\n\n"
            f"Key Standards for Cement Industry:\n"
            f"- Initial Setting Time: Minimum 30 minutes.\n"
            f"- Final Setting Time: Maximum 600 minutes (10 hours).\n"
            f"- Total Loss on Ignition (LOI): Maximum 5.0% by mass.\n"
            f"- Insoluble Residue: Maximum 5.0% by mass.\n"
            f"- Statutory Scheme: Mandatory Scheme-I (ISI Mark) certification under the Cement (Quality Control) Order. No factory can sell cement in India without active BIS license."
        ),
        is_code=is269_code,
        doc_title=is269_title,
        clause="Clause 6.1 (Table 1)",
        page_number=3,
        is_table=True,
        table_number="Table 1",
        table_title="Cement Physical Requirements",
        table_data={"columns": tbl_cement_cols, "rows": tbl_cement_rows, "markdown": md_tbl_cement}
    ))

    # =========================================================================
    # 9. IS 13252 (Part 1): 2010 - IT & Electronics Safety (Scheme-II CRS)
    # =========================================================================
    is13252_code = "IS 13252 (Part 1):2010"
    is13252_title = "Information Technology Equipment - Safety - General Requirements"

    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is13252_code} - {is13252_title}\n"
            f"PAGE: 1 | CLAUSE: Clause 1.0 Scope and Scheme-II CRS Registration\n\n"
            f"Applies to: Mobile Phones, Laptops, Tablets, Power Banks, Adapters, Servers, Printers, Smart Watches, LED Displays.\n"
            f"Mandatory Certification Scheme: Scheme-II (Compulsory Registration Scheme - CRS) mandated by Ministry of Electronics and Information Technology (MeitY).\n"
            f"Key Requirements:\n"
            f"1. Electric Shock Hazard Prevention: Adequate creepage distance and clearance between primary and secondary circuits.\n"
            f"2. Fire Resistance: Enclosures must be constructed from flame-retardant polymers meeting UL 94 V-0 or V-1 ratings.\n"
            f"3. Battery Safety: Lithium-ion batteries inside IT equipment must independently conform to IS 16046 (Part 2):2018.\n"
            f"4. Marking: Self-declaration of conformity mark with standard logo, IS number, and Registration Number `R-XXXXXXXX`."
        ),
        is_code=is13252_code,
        doc_title=is13252_title,
        clause="Clause 1.0 Scope and CRS Requirements",
        page_number=1,
        is_table=False
    ))

    # =========================================================================
    # 10. IS 1417: 2016 - Gold and Gold Alloys Hallmarking & Fineness
    # =========================================================================
    is1417_code = "IS 1417:2016"
    is1417_title = "Gold and Gold Alloys, Jewellery/Artefacts - Fineness and Marking - Specification"

    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is1417_code} - {is1417_title}\n"
            f"PAGE: 2 | CLAUSE: Clause 4.0 Standard Grades and Mandatory 3-Symbol Hallmarking\n\n"
            f"Standard Gold Purity Grades Recognized under BIS Hallmarking Scheme:\n"
            f"1. 24K: 999 Fineness (99.9% Pure Gold)\n"
            f"2. 23K: 958 Fineness (95.8% Pure Gold)\n"
            f"3. 22K: 916 Fineness (91.6% Pure Gold - Most popular for Indian jewellery)\n"
            f"4. 20K: 833 Fineness (83.3% Pure Gold)\n"
            f"5. 18K: 750 Fineness (75.0% Pure Gold - Diamond and studded jewellery)\n"
            f"6. 14K: 585 Fineness (58.5% Pure Gold)\n"
            f"7. 9K: 375 Fineness (37.5% Pure Gold)\n\n"
            f"Mandatory 3-Symbol Hallmarking Structure on Every Article:\n"
            f"a) BIS Triangular Logo.\n"
            f"b) Purity & Fineness Mark (e.g., 22K916 or 18K750).\n"
            f"c) 6-digit alphanumeric HUID (Hallmark Unique Identification) code laser engraved by an Assaying & Hallmarking Centre (AHC).\n"
            f"Consumers can verify HUID authenticity instantaneously using the 'Verify HUID' feature in the BIS Care Mobile App."
        ),
        is_code=is1417_code,
        doc_title=is1417_title,
        clause="Clause 4.0 Gold Fineness and HUID Marking",
        page_number=2,
        is_table=False
    ))

    # =========================================================================
    # 11. IS 1374: 2007 - Poultry Feeds (Broiler & Layer)
    # =========================================================================
    is1374_code = "IS 1374:2007"
    is1374_title = "Poultry Feeds - Specification (Broiler Starter, Finisher & Layer Feeds)"

    tbl_poultry_cols = ["Parameter", "Broiler Starter", "Broiler Finisher", "Layer Feed", "Test Method Ref"]
    tbl_poultry_rows = [
        ["Crude Protein (Min)", "21.0% by mass", "19.0% by mass", "18.0% by mass", "IS 7874 (Part 1)"],
        ["Crude Fat (Min)", "3.0% by mass", "3.5% by mass", "3.0% by mass", "IS 7874 (Part 1)"],
        ["Crude Fibre (Max)", "5.0% by mass", "5.0% by mass", "7.0% by mass", "IS 7874 (Part 1)"],
        ["Aflatoxin B1 (Max)", "20 ppb (0.02 mg/kg)", "20 ppb", "20 ppb", "IS 13426"],
        ["Acid Insoluble Ash (Max)", "2.5% by mass", "2.5% by mass", "3.0% by mass", "IS 7874 (Part 1)"]
    ]
    md_tbl_poultry = (
        "### Table 1: Nutritional Requirements for Broiler and Layer Poultry Feeds (IS 1374:2007 Clause 4.1)\n\n"
        "| Parameter | Broiler Starter | Broiler Finisher | Layer Feed | Test Method Ref |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Crude Protein (Min) | 21.0% by mass | 19.0% by mass | 18.0% by mass | IS 7874 (Part 1) |\n"
        "| Crude Fat (Min) | 3.0% by mass | 3.5% by mass | 3.0% by mass | IS 7874 (Part 1) |\n"
        "| Crude Fibre (Max) | 5.0% by mass | 5.0% by mass | 7.0% by mass | IS 7874 (Part 1) |\n"
        "| Aflatoxin B1 (Max) | 20 ppb (0.02 mg/kg) | 20 ppb | 20 ppb | IS 13426 |\n"
        "| Acid Insoluble Ash (Max) | 2.5% by mass | 2.5% by mass | 3.0% by mass | IS 7874 (Part 1) |"
    )
    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is1374_code} - {is1374_title}\n"
            f"PAGE: 2 | CLAUSE: Clause 4.1 Nutritional & Chemical Requirements for Poultry Feeds\n\n"
            f"{md_tbl_poultry}\n\n"
            f"Statutory Requirements for Poultry Industry:\n"
            f"- Aflatoxin B1 must strictly NOT exceed 20 ppb (0.02 mg/kg) to prevent toxic contamination in chicken meat/eggs.\n"
            f"- Heavy metals: Lead max 5.0 mg/kg, Arsenic max 2.0 mg/kg.\n"
            f"- Mandatory Certification Scheme: Scheme-I (ISI Mark) under Animal Feed Quality Control Order."
        ),
        is_code=is1374_code,
        doc_title=is1374_title,
        clause="Clause 4.1 (Table 1)",
        page_number=2,
        is_table=True,
        table_number="Table 1",
        table_title="Nutritional Requirements for Broiler and Layer Poultry Feeds",
        table_data={"columns": tbl_poultry_cols, "rows": tbl_poultry_rows, "markdown": md_tbl_poultry}
    ))

    # =========================================================================
    # 12. IS 7049: 1973 - Poultry Processing & Retail Chicken Centres
    # =========================================================================
    is7049_code = "IS 7049:1973"
    is7049_title = "Code for Handling, Processing, Quality Evaluation and Storage of Poultry"

    chunks.append(ParsedChunk(
        text=(
            f"BIS STANDARD: {is7049_code} - {is7049_title}\n"
            f"PAGE: 1 | CLAUSE: Clause 5.0 Temperature Control & Hygienic Requirements for Chicken Centres\n\n"
            f"Mandatory Hygiene and Operational Standards for Retail Chicken Shops & Processing Units:\n"
            f"1. Cold Chain Temperature: Fresh dressed chicken carcasses must be immediately chilled to below 4°C within 4 hours of slaughter. Frozen chicken must be stored at -18°C or lower.\n"
            f"2. Water Quality: Potable water conforming strictly to IS 10500 must be used for scalding, evisceration, and carcass washing.\n"
            f"3. Evisceration & Sanitation: Separate clean and unclean zones. Stainless steel surfaces (SS 304) for all meat contact tables.\n"
            f"4. Inspection: Ante-mortem inspection to eliminate diseased birds (IS 1982) and post-mortem inspection for Salmonella/E. Coli absence.\n"
            f"5. Statutory Clearances: FSSAI Food Business License (Category 08: Meat and meat products) + Municipal Health Trade License."
        ),
        is_code=is7049_code,
        doc_title=is7049_title,
        clause="Clause 5.0 Temperature & Hygiene for Chicken Processing",
        page_number=1,
        is_table=False
    ))

    return chunks


def seed_database_if_empty():
    """Check if ChromaDB has the complete suite of national standards; if not, seed all missing standards."""
    standards = get_all_standards_db()
    existing_codes = {s["is_code"] for s in standards}
    seed_chunks = get_seed_chunks()
    
    # Group by standard
    standards_map = {}
    for chunk in seed_chunks:
        if chunk.is_code not in standards_map:
            standards_map[chunk.is_code] = []
        standards_map[chunk.is_code].append(chunk)

    missing_standards = [code for code in standards_map if code not in existing_codes]
    if missing_standards:
        logger.info(f"Seeding {len(missing_standards)} missing BIS standards into vector store: {missing_standards}...")
        for is_code in missing_standards:
            vector_store_service.add_chunks(standards_map[is_code])
        logger.info("Successfully updated BIS standards vector repository.")
    else:
        logger.info(f"Database already contains all {len(standards)} indexed BIS standards.")
