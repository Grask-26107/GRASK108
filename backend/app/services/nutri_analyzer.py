import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.services.multilingual_translator import multilingual_translator, SUPPORTED_LANGUAGES
from app.services.domain_relevance_guard import domain_relevance_guard

logger = logging.getLogger(__name__)

# FSSAI Front-of-Pack Labelling & Indian Food Safety Reference Thresholds (Per 100g solid food)
THRESHOLDS = {
    "sodium_caution_mg": 400.0,      # > 400 mg/100g -> High Sodium (Caution)
    "sodium_harmful_mg": 800.0,      # > 800 mg/100g -> Very High / Harmful
    "trans_fat_max_g": 0.2,          # FSSAI strict ceiling: <= 0.2g / 100g
    "saturated_fat_caution_g": 5.0,  # > 5g / 100g -> High Saturated Fat
    "saturated_fat_harmful_g": 8.0,  # > 8g / 100g -> Excessive Saturated Fat
    "added_sugar_caution_g": 10.0,   # > 10g / 100g -> Moderate to High Sugar
    "added_sugar_harmful_g": 20.0,   # > 20g / 100g -> Very High Sugar / HFSS
}

# Extensive Dictionary of Hidden Added Sugars
HIDDEN_SUGAR_DATABASE = {
    "maltodextrin": {
        "name": "Maltodextrin",
        "description": "High Glycemic Index (GI 110-130) starch derivative; causes rapid blood glucose spikes higher than table sugar.",
        "risk_level": "HIGH",
        "category": "Hidden Fast-Spiking Carb"
    },
    "high fructose corn syrup": {
        "name": "High Fructose Corn Syrup (HFCS)",
        "description": "Cheap liquid sweetener linked directly to non-alcoholic fatty liver disease (NAFLD), visceral fat, and insulin resistance.",
        "risk_level": "CRITICAL",
        "category": "Industrial Fructose"
    },
    "hfcs": {
        "name": "HFCS (High Fructose Corn Syrup)",
        "description": "Industrial fructose syrup linked to severe metabolic dysregulation and fatty liver.",
        "risk_level": "CRITICAL",
        "category": "Industrial Fructose"
    },
    "invert sugar": {
        "name": "Invert Sugar / Invert Syrup",
        "description": "Hydrolyzed sucrose (split glucose + fructose); rapidly absorbed into bloodstream, common in commercial biscuits.",
        "risk_level": "HIGH",
        "category": "Hidden Liquid Sugar"
    },
    "invert syrup": {
        "name": "Invert Sugar Syrup",
        "description": "Concentrated liquid sugar syrup that enhances shelf-life while dramatically spiking calorie density.",
        "risk_level": "HIGH",
        "category": "Hidden Liquid Sugar"
    },
    "liquid glucose": {
        "name": "Liquid Glucose / Glucose Syrup",
        "description": "Refined concentrated glucose solution that causes severe post-prandial glycemic excursions.",
        "risk_level": "HIGH",
        "category": "Refined Sugar"
    },
    "glucose syrup": {
        "name": "Glucose Syrup",
        "description": "Refined corn/starch syrup with high caloric load and instant glycemic impact.",
        "risk_level": "HIGH",
        "category": "Refined Sugar"
    },
    "dextrose": {
        "name": "Dextrose (D-Glucose)",
        "description": "Pure simple sugar absorbed almost instantly; dangerous for individuals with prediabetes or diabetes.",
        "risk_level": "HIGH",
        "category": "Simple Sugar"
    },
    "malt extract": {
        "name": "Malt Extract / Barley Malt",
        "description": "Barley-derived sweetener containing maltose; also poses severe danger to celiac/gluten-sensitive individuals.",
        "risk_level": "MODERATE",
        "category": "Malt-Derived Sugar"
    },
    "corn syrup": {
        "name": "Corn Syrup / Corn Syrup Solids",
        "description": "Concentrated glucose and maltose polymer, adds empty calories with zero micronutrients.",
        "risk_level": "HIGH",
        "category": "Industrial Sweetener"
    },
    "maltose": {
        "name": "Maltose",
        "description": "Disaccharide with very high glycemic index (GI 105), spikes insulin faster than pure glucose.",
        "risk_level": "HIGH",
        "category": "High-GI Disaccharide"
    },
    "agave nectar": {
        "name": "Agave Nectar",
        "description": "Contains up to 85% free fructose; heavily promotes hepatic lipogenesis despite 'natural' marketing.",
        "risk_level": "MODERATE",
        "category": "Fructose-Heavy Sweetener"
    },
    "cane juice crystals": {
        "name": "Evaporated Cane Juice Crystals",
        "description": "Marketing euphemism for crystallized sucrose / refined sugar.",
        "risk_level": "MODERATE",
        "category": "Refined Sucrose"
    }
}

# Dangerous / Restricted Additives & E/INS Numbers
ADDITIVE_DATABASE = {
    "102": {
        "name": "INS 102 (Tartrazine)",
        "type": "Synthetic Azo Dye (Yellow 5)",
        "hazard": "Known to trigger severe hyperactivity in children (ADHD), asthma attacks, and urticaria. Requires warning label in EU.",
        "risk": "HIGH"
    },
    "110": {
        "name": "INS 110 (Sunset Yellow FCF)",
        "type": "Synthetic Coal-Tar Food Dye",
        "hazard": "Associated with allergic reactions, hyperactivity, abdominal pain, and hives; banned or restricted in several European countries.",
        "risk": "HIGH"
    },
    "122": {
        "name": "INS 122 (Carmoisine / Azorubine)",
        "type": "Red Azo Dye",
        "hazard": "Causes histamine release, intensifying asthma and skin dermatitis; flagged in Southampton child hyperactivity study.",
        "risk": "HIGH"
    },
    "124": {
        "name": "INS 124 (Ponceau 4R)",
        "type": "Synthetic Red Coloring",
        "hazard": "Suspected carcinogen in animal models; banned in USA and Canada; linked to intense allergic intolerance in aspirin-sensitive patients.",
        "risk": "CRITICAL"
    },
    "127": {
        "name": "INS 127 (Erythrosine)",
        "type": "Synthetic Red Dye",
        "hazard": "Contains iodine; evidence of thyroid tumor development in laboratory animal trials.",
        "risk": "CRITICAL"
    },
    "133": {
        "name": "INS 133 (Brilliant Blue FCF)",
        "type": "Synthetic Triarylmethane Color",
        "hazard": "Associated with allergic reactions and cellular toxicity in vulnerable children.",
        "risk": "MODERATE"
    },
    "171": {
        "name": "INS 171 (Titanium Dioxide)",
        "type": "Whitening Nanoparticle Pigment",
        "hazard": "BANNED by the European Commission in 2022 due to genotoxicity concerns (DNA damage & chromosomal aberrations).",
        "risk": "CRITICAL"
    },
    "621": {
        "name": "INS 621 (Monosodium Glutamate / MSG)",
        "type": "Excitotoxin & Flavor Enhancer",
        "hazard": "Can trigger headaches, flushing, numbness, and sweating (MSG symptom complex). Prohibited in infant food under FSSAI.",
        "risk": "MODERATE"
    },
    "627": {
        "name": "INS 627 (Disodium Guanylate)",
        "type": "Nucleotide Flavor Synergist",
        "hazard": "Metabolizes to purines; dangerous for consumers suffering from gout or kidney stones.",
        "risk": "MODERATE"
    },
    "631": {
        "name": "INS 631 (Disodium Inosinate)",
        "type": "Nucleotide Flavor Synergist",
        "hazard": "Often animal/fish derived; metabolizes into uric acid, exacerbating arthritis and gout.",
        "risk": "MODERATE"
    },
    "211": {
        "name": "INS 211 (Sodium Benzoate)",
        "type": "Chemical Preservative",
        "hazard": "In the presence of Ascorbic Acid (Vitamin C), reacts to synthesize Benzene, a confirmed Class-1 human carcinogen.",
        "risk": "HIGH"
    },
    "220": {
        "name": "INS 220 (Sulfur Dioxide)",
        "type": "Sulfite Preservative",
        "hazard": "Can trigger life-threatening bronchospasm in asthmatic individuals.",
        "risk": "HIGH"
    },
    "223": {
        "name": "INS 223 (Sodium Metabisulfite)",
        "type": "Sulfite Bleaching Agent",
        "hazard": "Destroys Thiamine (Vitamin B1) in foods and triggers acute allergic bronchial spasms.",
        "risk": "HIGH"
    },
    "249": {
        "name": "INS 249 / 250 (Sodium Nitrite)",
        "type": "Curing Preservative",
        "hazard": "Forms carcinogenic Nitrosamines when exposed to high heat in protein matrices.",
        "risk": "CRITICAL"
    },
    "250": {
        "name": "INS 250 (Sodium Nitrite)",
        "type": "Curing Preservative",
        "hazard": "Generates carcinogenic Nitrosamines; linked directly to colorectal cancer risks.",
        "risk": "CRITICAL"
    },
    "320": {
        "name": "INS 320 (BHA - Butylated Hydroxyanisole)",
        "type": "Synthetic Antioxidant",
        "hazard": "Classified as 'reasonably anticipated to be a human carcinogen' by the US National Toxicology Program; endocrine disruptor.",
        "risk": "HIGH"
    },
    "321": {
        "name": "INS 321 (BHT - Butylated Hydroxytoluene)",
        "type": "Synthetic Antioxidant",
        "hazard": "Endocrine disruptor linked to lung and liver tumor promotion in animal testing.",
        "risk": "HIGH"
    },
    "407": {
        "name": "INS 407 (Carrageenan)",
        "type": "Seaweed Polysaccharide Thickener",
        "hazard": "Degrades into poligeenan, triggering severe intestinal inflammation, ulcerations, and gut barrier permeability.",
        "risk": "MODERATE"
    },
    "466": {
        "name": "INS 466 (Sodium Carboxymethylcellulose)",
        "type": "Emulsifier & Thickener",
        "hazard": "Disrupts the intestinal mucus layer, promoting gut microbiome dysbiosis and colitis.",
        "risk": "MODERATE"
    },
    "950": {
        "name": "INS 950 (Acesulfame Potassium)",
        "type": "Non-Nutritive Artificial Sweetener",
        "hazard": "Contains methylene chloride impurities; disrupts gut microbiota composition.",
        "risk": "MODERATE"
    },
    "951": {
        "name": "INS 951 (Aspartame)",
        "type": "Artificial Sweetener",
        "hazard": "Classified as 'Possibly Carcinogenic to Humans' (Group 2B) by WHO IARC (2023). Dangerous for phenylketonuria (PKU) patients.",
        "risk": "HIGH"
    },
    "954": {
        "name": "INS 954 (Saccharin)",
        "type": "Synthetic Sweetener",
        "hazard": "High doses historically linked to bladder toxicity in animals; induces gut dysbiosis.",
        "risk": "MODERATE"
    },
    "955": {
        "name": "INS 955 (Sucralose)",
        "type": "Chlorinated Artificial Sweetener",
        "hazard": "When heated, generates toxic chloropropanols; decreases beneficial Bifidobacteria and Lactobacillus in gut.",
        "risk": "MODERATE"
    }
}

# Unhealthy Fats & Atherogenic Oils
PALM_OIL_KEYWORDS = [
    "palm oil", "palmolein", "refined palm oil", "fractionated palm oil",
    "palm kernel oil", "hydrogenated palm oil", "palm olein", "palmitic acid",
    "hydrogenated vegetable oil", "vanaspati", "interesterified vegetable fat",
    "margarine", "shortening"
]

# Gluten Keywords
GLUTEN_KEYWORDS = [
    "wheat", "refined wheat flour", "maida", "atta", "durum wheat", "semolina",
    "suji", "rava", "barley", "malt", "malt extract", "rye", "spelt", "triticale",
    "wheat gluten", "vital gluten", "hydrolyzed wheat protein"
]

# Beneficial Ingredients (Fiber, Whole Grains, Seeds, Healthy Fats)
BENEFICIAL_KEYWORDS = [
    "whole wheat", "oats", "rolled oats", "ragi", "millet", "jowar", "bajra",
    "flaxseed", "chia seeds", "almonds", "walnuts", "olive oil", "cold pressed",
    "dietary fiber", "whey protein isolate", "pea protein", "quinoa", "lentils"
]

# Comprehensive Knowledge Base of Extracted Ingredients, Categories & Health Effects
INGREDIENT_KNOWLEDGE_BASE = {
    # Whole Grains & Traditional Flours
    "whole wheat flour": {
        "category": "Whole Grain Flour",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Rich in dietary fiber, B-vitamins, and magnesium. Supports digestion, sustained energy release, and healthy cholesterol.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "whole wheat": {
        "category": "Whole Grain",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Unrefined wheat retaining bran and germ; rich in complex carbs and gut-friendly prebiotic fiber.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "atta": {
        "category": "Whole Grain Flour",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Traditional Indian stone-ground whole wheat flour containing natural bran fiber, iron, and minerals.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "wheat flour": {
        "category": "Grain Flour",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Standard staple grain providing complex carbohydrates and protein. Wholesome and easily digestible.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "refined wheat flour": {
        "category": "Refined Grain / Starch",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Maida stripped of bran and germ fibers; high glycemic index (~75) causing rapid insulin surges and low satiety.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "maida": {
        "category": "Refined Grain / Starch",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Finely milled and refined wheat starch with minimal micronutrients; rapid digestion leads to glycemic spikes.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "oats": {
        "category": "Whole Grain Cereal",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Abundant in Beta-Glucan soluble fiber; clinically proven to reduce LDL cholesterol and stabilize blood sugar.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "rolled oats": {
        "category": "Whole Grain Cereal",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Minimally processed oat flakes high in prebiotic fiber, phosphorus, and plant protein.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ragi": {
        "category": "Nutrient-Dense Millet",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Super-millet extremely high in calcium (344mg/100g), iron, and essential amino acids; builds bone density.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "finger millet": {
        "category": "Nutrient-Dense Millet",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Calcium and polyphenol-rich ancient grain; aids slow glucose release and diabetes management.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "jowar": {
        "category": "Ancient Millet",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "High-fiber, gluten-free grain packed with antioxidant phytochemicals that combat cellular oxidation.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "bajra": {
        "category": "Ancient Millet",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Rich in iron, magnesium, and resistant starch; improves gut microbiota and satiety.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "besan": {
        "category": "Legume Flour",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Chickpea/gram flour rich in plant protein, folate, and potassium; low glycemic index.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "gram flour": {
        "category": "Legume Flour",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Protein-dense chickpea flour with high satiety index and low glycemic impact.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "semolina": {
        "category": "Coarse Wheat (Suji)",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Purified wheat middlings; good source of energy and protein, naturally low in fat.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "suji": {
        "category": "Coarse Wheat",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Light on digestion; healthy staple for upma, halwa, or idli when combined with vegetables.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "rava": {
        "category": "Coarse Wheat",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Wheat semolina staple; versatile complex carbohydrate source.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "corn flour": {
        "category": "Refined Starch",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Starch powder derived from corn endosperm; high glycemic index, acts as caloric binder.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "corn starch": {
        "category": "Refined Starch",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Refined carbohydrate texturizer; quickly converts to glucose in digestion.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "rice flour": {
        "category": "Gluten-Free Grain Flour",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Gentle on sensitive digestive tracts and naturally gluten-free; moderate glycemic index.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },

    # Oils and Fats
    "mustard oil": {
        "category": "Traditional Cold-Pressed Oil",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Rich in heart-friendly MUFA (oleic acid) and Omega-3 (ALA); strong natural antibacterial ally.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "kachi ghani": {
        "category": "Cold-Pressed Mustard Oil",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Unrefined expeller-pressed oil retaining natural antioxidants and natural pungency.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "groundnut oil": {
        "category": "Traditional Cooking Oil",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "High smoke point, rich in oleic acid and resveratrol; protects cardiovascular endothelium.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "peanut oil": {
        "category": "Traditional Cooking Oil",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Rich in monounsaturated fats and Vitamin E; stable for high-temperature home cooking.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "sesame oil": {
        "category": "Traditional Cooking Oil",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Loaded with sesamol and sesaminol antioxidants; helps regulate systolic blood pressure.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "til oil": {
        "category": "Traditional Cooking Oil",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Cardioprotective sesame oil with natural anti-inflammatory polyphenols.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ghee": {
        "category": "Clarified Butter Fat",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Provides butyrate for colon epithelial health, fat-soluble vitamins (A, D, E, K); safe in moderate daily home amounts (1-2 tsp).",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "clarified butter": {
        "category": "Clarified Dairy Fat",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Lactose-free natural dairy fat supporting fat-soluble nutrient absorption when used moderately.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "butter": {
        "category": "Dairy Fat",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Natural dairy fat; harmless in culinary moderation (10-15g/day), excessive amounts add saturated fat.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "sunflower oil": {
        "category": "Refined Seed Oil",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "High in Vitamin E and Polyunsaturated Fatty Acids (PUFA); safe for everyday cooking in moderate amounts.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "soybean oil": {
        "category": "Refined Seed Oil",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Source of polyunsaturated Omega-6 fats; safe in moderate rotation with MUFA-rich oils.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "coconut oil": {
        "category": "Traditional Cooking Oil",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Contains Medium Chain Triglycerides (MCTs) like lauric acid; healthy in traditional culinary moderation.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "olive oil": {
        "category": "Cold-Pressed Fruit Oil",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Highest concentration of Oleic acid and polyphenols; recognized gold standard for cardiovascular protection.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "palm oil": {
        "category": "Atherogenic Industrial Fat",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "High in Palmitic acid (~44%); significantly raises atherogenic LDL cholesterol and arterial stiffness.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "palmolein": {
        "category": "Industrial Palm Fraction",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Liquid fraction of palm oil widely used in ultra-processed snacks; high saturated fat load and arterial risk.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "hydrogenated vegetable oil": {
        "category": "Industrial Trans Fat Source",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Produces harmful Trans Fatty Acids; drastically lowers protective HDL while hiking dangerous LDL cholesterol.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "vanaspati": {
        "category": "Partially Hydrogenated Fat",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Industrial hardened fat with severe atherogenic and inflammatory cardiovascular consequences.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "margarine": {
        "category": "Processed Emulsified Fat",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Chemically modified fat substitute often containing synthetic trans-isomers and emulsifiers.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "interesterified vegetable fat": {
        "category": "Modified Industrial Fat",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Chemically rearranged triglycerides; impairs postprandial glucose metabolism and insulin secretion.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },

    # Sugars & Sweeteners
    "sugar": {
        "category": "Refined Disaccharide",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Empty calorie sweetener; harmless in small home quantities (1-2 tsp/day), but causes metabolic risk in large industrial doses.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "white sugar": {
        "category": "Refined Sucrose",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Bleached sucrose lacking all micronutrients; rapid glycemic absorption.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "jaggery": {
        "category": "Unrefined Cane Sugar",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Traditional unrefined sweetener retaining potassium, iron, and magnesium; healthier than white sugar but still calorie dense.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "gur": {
        "category": "Traditional Cane Sweetener",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Natural sweetener with mineral content; aids digestion when taken in small post-meal amounts.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "honey": {
        "category": "Natural Floral Sweetener",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Contains enzymes, antioxidants, and antimicrobial compounds; soothing for throat and gut.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "maltodextrin": {
        "category": "Hidden High-GI Starch",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Extreme Glycemic Index (110-130); triggers sudden insulin surges and promotes visceral fat accumulation.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "invert sugar": {
        "category": "Industrial Hydrolyzed Sugar",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Chemically split glucose and fructose; accelerates absorption and increases empty calorie density.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "invert sugar syrup": {
        "category": "Industrial Liquid Sweetener",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Liquid sugar formulation engineered for extended commercial shelf-life and intense palatability.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "liquid glucose": {
        "category": "Industrial Refined Starch Syrup",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Highly concentrated glucose solution; causes acute postprandial glucose spikes.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "glucose syrup": {
        "category": "Refined Industrial Sweetener",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Concentrated simple sugar offering zero micronutrients; high glycemic burden.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "high fructose corn syrup": {
        "category": "Industrial Fructose",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Enzymatically processed syrup linked directly to non-alcoholic fatty liver disease (NAFLD) and insulin resistance.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "dextrose": {
        "category": "Simple Monosaccharide",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Pure D-glucose absorbed almost instantly; rapid blood sugar elevation.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },

    # Salts, Spices, Seasonings
    "iodised salt": {
        "category": "Fortified Essential Mineral",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Essential for fluid balance, nerve transmission, and thyroid health (prevents goiter). Harmless in home use (< 5g/day).",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "salt": {
        "category": "Essential Mineral",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Vital physiological electrolyte. Safe in home cooking; becomes hazardous only in ultra-processed snacks with mega-doses.",
        "harmlessness_level": "🟡 Usual Everyday Use (Moderate)"
    },
    "rock salt": {
        "category": "Natural Mineral Salt",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Sendha namak containing 84 natural trace minerals; lower sodium density and gentle on blood pressure.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "sendha namak": {
        "category": "Himalayan Pink Salt",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Pure unrefined mineral salt aiding cellular hydration and digestive enzyme function.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "black salt": {
        "category": "Therapeutic Mineral Salt",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Kala namak rich in hydrogen sulfide minerals; traditionally proven digestive and carminative stimulant.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "turmeric": {
        "category": "Medicinal Botanical Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Abundant in Curcumin; extraordinary natural anti-inflammatory, antioxidant, and immunomodulatory properties.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "haldi": {
        "category": "Medicinal Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Traditional healing spice; reduces systemic inflammation and protects cellular DNA.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "cumin": {
        "category": "Digestive Botanical Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Rich in thymol and essential oils; stimulates pancreatic enzymes, relieving gas and indigestion.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "jeera": {
        "category": "Digestive Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Digestive catalyst rich in non-heme iron and gut-soothing bioactives.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "black pepper": {
        "category": "Bioenhancing Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Contains Piperine, which enhances nutrient absorption (curcumin by 2000%) and fires digestive metabolism.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "kali mirch": {
        "category": "Bioenhancing Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Stimulates digestive hydrochloric acid secretion; potent antimicrobial and respiratory decongestant.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "coriander": {
        "category": "Antioxidant Herb / Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Rich in linalool, dietary fiber, and vitamin C; aids cholesterol management and gastric comfort.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "dhaniya": {
        "category": "Aromatic Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Natural cooling spice with diuretic and digestive benefits.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ginger": {
        "category": "Medicinal Rhizome",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Contains Gingerols; natural anti-inflammatory, speeds gastric emptying, and relieves nausea.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "adrak": {
        "category": "Digestive Rhizome",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Powerful digestive stimulant, alleviates joint stiffness and respiratory phlegm.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "cardamom": {
        "category": "Aromatic Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Cardioprotective and carminative spice with cineole terpene antioxidants; natural oral cleanser.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "cinnamon": {
        "category": "Metabolic Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Rich in cinnamaldehyde; naturally enhances insulin sensitivity and lowers fasting blood sugar.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "clove": {
        "category": "Medicinal Flower Bud",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Highest ORAC antioxidant rating among common spices; rich in eugenol for antimicrobial defense.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "laung": {
        "category": "Medicinal Spice",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Eugenol-rich flower bud supporting oral hygiene and gastric barrier protection.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "chilli powder": {
        "category": "Capsaicin Spice",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Contains capsaicin; boosts thermogenesis and metabolic rate; safe in typical culinary amounts.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "red chilli": {
        "category": "Capsaicin Spice",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Stimulates salivary flow and metabolism; harmless in home cooking moderation.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },

    # Dairy, Protein, Leaveners & Household Additives
    "milk solids": {
        "category": "Dairy Protein & Calcium",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Provides complete biological value protein, bioavailable calcium, and vitamin B2 (riboflavin).",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "skimmed milk powder": {
        "category": "Low-Fat Dairy Protein",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Concentrated milk protein and bone-building minerals with minimal fat content.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "cocoa solids": {
        "category": "Plant Flavanol Source",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Abundant in flavanols and theobromine; enhances vascular elasticity and cognitive alertness.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "cocoa powder": {
        "category": "Plant Flavanol Source",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Antioxidant-dense botanical powder supporting cardiovascular nitric oxide synthesis.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "baking soda": {
        "category": "Household Leavening Agent",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Pure Sodium Bicarbonate (INS 500ii); decomposes into water, CO2 and sodium in baking. Completely harmless in home culinary use.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "sodium bicarbonate": {
        "category": "Food Leavener",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Standard kitchen leavener for dough rising; decomposes cleanly during baking; contributes mildly to sodium.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ins 500": {
        "category": "Food Leavening Salt",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Sodium carbonate / bicarbonate; standard food-grade baking salt with safe metabolic clearance.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ins 500(ii)": {
        "category": "Baking Soda (Sodium Bicarbonate)",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Household baking soda; safe and benign leavener used universally in home and bakery recipes.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ins 503": {
        "category": "Baker's Ammonia (Ammonium Carbonate)",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Traditional biscuit leavener that evaporates completely during high-temperature oven baking; harmless in finished food.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ins 503(ii)": {
        "category": "Ammonium Bicarbonate",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Crisp biscuit leavener; releases ammonia and CO2 gas completely during baking, leaving no toxic residue.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "citric acid": {
        "category": "Organic Fruit Acid",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Natural acid found in citrus fruits (nimbu sat); harmless natural acidulant, pH balancer, and antioxidant protector.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ins 330": {
        "category": "Citric Acid",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Naturally occurring fruit acid used safely across global food science for flavor and freshness.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "soya lecithin": {
        "category": "Plant Phospholipid Emulsifier",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Natural source of choline and cellular phospholipids derived from soybean; completely safe and non-toxic.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "ins 322": {
        "category": "Lecithin Emulsifier",
        "health_effect": "SAFE_NEUTRAL",
        "health_advantage_or_risk": "Natural phospholipid aiding even fat blending; safe for everyday digestion.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },
    "yeast": {
        "category": "Natural Fermentation Culture",
        "health_effect": "BENEFICIAL",
        "health_advantage_or_risk": "Active living culture synthesizing natural B-complex vitamins, enzymes, and prebiotic beta-glucans.",
        "harmlessness_level": "🟢 Safe & Beneficial"
    },

    # Harmful Synthetic Additives
    "ins 102": {
        "category": "Synthetic Azo Dye (Tartrazine)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Coal-tar dye linked to hyperactivity (ADHD) in children, asthma aggravation, and urticaria; restricted in Europe.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "tartrazine": {
        "category": "Synthetic Food Dye",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Artificial yellow colorant; neurobehavioral and allergic trigger in susceptible children.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 110": {
        "category": "Synthetic Coal-Tar Dye (Sunset Yellow)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Azo colorant banned in several Nordic countries; linked to allergies, hives, and hyperactivity.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "sunset yellow": {
        "category": "Synthetic Food Color",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Artificial petroleum dye associated with abdominal discomfort and histamine release.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 122": {
        "category": "Red Azo Dye (Carmoisine)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Causes allergic reactions and asthma triggers; flagged in Southampton child hyperactivity study.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "carmoisine": {
        "category": "Synthetic Red Color",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Artificial red dye linked to skin dermatitis and behavioral agitation in children.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 124": {
        "category": "Synthetic Color (Ponceau 4R)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Suspected carcinogen in animal models; banned in USA; dangerous for aspirin-sensitive individuals.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 127": {
        "category": "Synthetic Color (Erythrosine)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Contains iodine; evidence of thyroid tumor development in laboratory animal trials.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 171": {
        "category": "Nanoparticle Whitener (Titanium Dioxide)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "BANNED by the European Commission due to genotoxicity concerns (DNA damage and chromosomal aberrations).",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "titanium dioxide": {
        "category": "Nanoparticle Pigment",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Accumulates in organs and damages cellular DNA; declared unsafe by European Food Safety Authority (EFSA).",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 621": {
        "category": "Excitotoxin (Monosodium Glutamate / MSG)",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Glutamate flavor booster; can provoke headaches and palpitations; strictly prohibited in infant food by FSSAI.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "monosodium glutamate": {
        "category": "Excitotoxin Flavor Enhancer",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Over-stimulates neural receptors; linked to Chinese Restaurant Syndrome and forbidden in infant formulas.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "msg": {
        "category": "Flavor Enhancer",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Neuro-sensory enhancer inducing hyper-palatability; regulated under Indian food standards.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 211": {
        "category": "Chemical Preservative (Sodium Benzoate)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Reacts with Vitamin C (ascorbic acid) to synthesize carcinogenic Benzene; irritates gastric mucosal barrier.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "sodium benzoate": {
        "category": "Chemical Food Preservative",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Chemical antimicrobial capable of forming carcinogenic Benzene when paired with acidic fruit juices.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 320": {
        "category": "Synthetic Antioxidant (BHA)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Classified as reasonably anticipated human carcinogen; endocrine disruptor that promotes fat rancidity resistance.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "bha": {
        "category": "Synthetic Chemical Preservative",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Petrochemical preservative disrupting cellular endocrine pathways; restricted globally.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 321": {
        "category": "Synthetic Preservative (BHT)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Endocrine disruptor linked to liver enlargement and metabolic changes in toxicological animal studies.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "bht": {
        "category": "Synthetic Antioxidant",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Synthetic chemical compound associated with organ burden and hormonal alterations.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 407": {
        "category": "Seaweed Gum (Carrageenan)",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Degrades into inflammatory poligeenan in stomach acid; induces intestinal inflammation and gut barrier leakage.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "carrageenan": {
        "category": "Inflammatory Thickener",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Polysaccharide linked to colitis and mucosal inflammation in sensitive gastrointestinal systems.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 466": {
        "category": "Emulsifier (Carboxymethylcellulose)",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Thins the protective gut mucus layer, triggering microbiome dysbiosis and low-grade systemic inflammation.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "carboxymethylcellulose": {
        "category": "Synthetic Gelling Emulsifier",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Industrial polymer altering intestinal barrier integrity and promoting metabolic syndrome.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "ins 951": {
        "category": "Artificial Sweetener (Aspartame)",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "Classified as Possibly Carcinogenic to Humans (Group 2B) by WHO IARC (2023); hazard for phenylketonuria.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "aspartame": {
        "category": "Synthetic Intense Sweetener",
        "health_effect": "HARMFUL",
        "health_advantage_or_risk": "WHO IARC Group 2B possible carcinogen; breaks down into phenylalanine, aspartic acid, and methanol.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    },
    "sucralose": {
        "category": "Chlorinated Artificial Sweetener",
        "health_effect": "MODERATE_CAUTION",
        "health_advantage_or_risk": "Synthetically chlorinated sucrose; degrades beneficial gut Bifidobacteria and generates chloropropanols under heat.",
        "harmlessness_level": "🔴 Harmful / Ultra-Processed Risk"
    }
}

# Everyday Household Staples: Harmlessness Level vs Packaged Food Risks
USUAL_HOUSEHOLD_ITEMS = [
    {
        "item_name": "Table Salt (Iodised Salt)",
        "everyday_use_context": "Standard seasoning in daily home cooking (curries, dals, rotis, rice, sambar).",
        "harmlessness_verdict": "🟢 100% Safe & Harmless in Everyday Home Use",
        "safe_daily_limit": "Up to 5 grams total salt (approx. 2000 mg Sodium) per person daily (WHO & ICMR).",
        "processed_food_risk": "In home cooking, salt is evenly distributed with water and fiber. In ultra-processed packaged snacks (chips, noodles), sodium is mega-concentrated (800-1200mg/100g) with zero moisture, causing vascular strain and hypertension."
    },
    {
        "item_name": "White Sugar (Table Sugar / Sucrose)",
        "everyday_use_context": "Added in home kitchens to tea, coffee, homemade desserts, and festive sweets.",
        "harmlessness_verdict": "🟡 Harmless in Small Culinary Amounts (Moderate)",
        "safe_daily_limit": "Maximum 20 to 25 grams (4 to 5 level teaspoons) total added sugar per day (WHO recommendation).",
        "processed_food_risk": "A cup of home tea uses ~4g sugar. In contrast, a single packaged soft drink or pack of biscuits conceals 25 to 40 grams of sugar or industrial HFCS, directly driving visceral fat, diabetes, and fatty liver disease."
    },
    {
        "item_name": "Traditional Cooking Oils (Mustard, Groundnut, Sesame & Ghee)",
        "everyday_use_context": "Daily tadka, vegetable sautéing, dal tempering, and shallow pan cooking.",
        "harmlessness_verdict": "🟢 Safe, Cardioprotective & Wholesome in Daily Moderation",
        "safe_daily_limit": "20 to 25 grams (approx. 4 to 5 teaspoons) visible fats per person per day (ICMR-NIN).",
        "processed_food_risk": "Home cooking uses fresh, unheated traditional oils. Packaged food manufacturers use cheap refined palm olein or hydrogenated fat (vanaspati) subjected to repeated industrial deep-frying, generating trans fats and oxidized free radicals."
    },
    {
        "item_name": "Whole Wheat Atta vs Refined Maida",
        "everyday_use_context": "Whole wheat atta for daily rotis/chapatis; Maida for occasional home puris or parathas.",
        "harmlessness_verdict": "Atta: 🟢 Highly Beneficial | Maida: 🟡 Harmless in Occasional Home Treats",
        "safe_daily_limit": "No restriction on whole grain Atta; limit refined Maida to occasional consumption.",
        "processed_food_risk": "Commercial packaged biscuits, breads, and noodles use 100% refined maida stripped of fiber and germ, resulting in rapid digestion, severe insulin spikes (GI ~75-80), and low satiety."
    },
    {
        "item_name": "Turmeric (Haldi) & Cumin (Jeera)",
        "everyday_use_context": "Essential daily home cooking base for Indian curries, dals, and vegetable dishes.",
        "harmlessness_verdict": "🟢 100% Safe, Healing & Medically Beneficial",
        "safe_daily_limit": "1 to 3 grams daily of pure ground botanical spices.",
        "processed_food_risk": "Pure kitchen spices are natural antioxidants and anti-inflammatories. Packaged foods frequently replace pure spices with synthetic chemical colorings (INS 102 Tartrazine, INS 110 Sunset Yellow) and artificial flavouring compounds."
    },
    {
        "item_name": "Baking Soda (INS 500ii) & Citric Acid (INS 330)",
        "everyday_use_context": "Baking soda used for dhokla, idli fermentation, and chana boiling; Citric acid / nimbu sat for sourness.",
        "harmlessness_verdict": "🟢 Harmless Food-Grade Leavener & Acidity Regulator",
        "safe_daily_limit": "Pinch quantities (< 1-2g across an entire family meal batch).",
        "processed_food_risk": "Pure baking soda and citric acid are non-toxic mineral/fruit compounds that decompose cleanly. Packaged food danger comes from synthetic industrial preservatives (BHA, BHT, Sodium Benzoate) rather than pure household leaveners."
    }
]


class NutriAnalyzerService:
    """
    FSSAI Nutri-Score & Hidden Ingredient Decrypter Service.
    Parses nutrition tables and ingredient lists to detect hidden sugars, high sodium,
    trans fats, palm oil, and harmful additives with custom persona safety alerts.
    """

    def __init__(self):
        pass

    def analyze(
        self,
        text: Optional[str] = None,
        image_base64: Optional[str] = None,
        persona: Optional[str] = "general",
        language: Optional[str] = "en"
    ) -> Dict[str, Any]:
        """
        Executes end-to-end nutrition and ingredient safety auditing with
        strict multimodal topic relevance guards and error correction.
        """
        raw_text = text or ""
        product_name = "Packaged Consumer Food Item"
        extracted_facts: Dict[str, Any] = {}
        detected_subject = "Packaged Food"
        corrected_text_summary = ""

        # 1. Clean grammatical and spelling mistakes in text if provided
        if raw_text.strip():
            corr_result = domain_relevance_guard.clean_and_correct_text(raw_text, "nutri_score")
            raw_text = corr_result["corrected_text"]
            corrected_text_summary = raw_text

        # 2. If Image provided, inspect using multimodal DomainRelevanceGuard FIRST
        if image_base64:
            inspection = domain_relevance_guard.inspect_image_for_feature(
                image_base64=image_base64,
                feature="nutri_score",
                extra_text=raw_text
            )
            detected_subject = inspection.get("detected_subject", "Unidentified Image")

            if not inspection.get("is_relevant", False):
                logger.info(f"Nutri-analyzer rejected image: {inspection.get('relevance_reason')}")
                return {
                    "status": "IRRELEVANT_DATA",
                    "is_relevant": False,
                    "relevance_reason": inspection.get("relevance_reason", "Uploaded image does not show a food package or nutrition label."),
                    "detected_subject": detected_subject,
                    "corrected_text": corrected_text_summary,
                    "product_name": "Irrelevant Visual Media",
                    "verdict": "IRRELEVANT",
                    "verdict_badge": "IRRELEVANT",
                    "nutri_score_grade": "N/A",
                    "nutri_score_points": 0,
                    "score_breakdown": None,
                    "summary_verdict": f"Irrelevant Data Detected: {inspection.get('relevance_reason')}",
                    "spoken_summary": f"Irrelevant image detected. {inspection.get('relevance_reason')}",
                    "spoken_language": language or "en",
                    "sodium_mg": None,
                    "sodium_level": "N/A",
                    "trans_fat_g": None,
                    "trans_fat_status": "N/A",
                    "saturated_fat_g": None,
                    "added_sugar_g": None,
                    "added_sugar_level": "N/A",
                    "has_palm_oil": False,
                    "palm_oil_details": None,
                    "hidden_sugars": [],
                    "harmful_additives": [],
                    "beneficial_ingredients": [],
                    "persona_alerts": [],
                    "fssai_compliance_notes": ["Please upload a clear photograph of a packaged food label or nutritional information table."],
                    "raw_extracted_ingredients": [],
                    "nutrition_table": {},
                    "all_ingredients_analysis": [],
                    "govt_limit_comparison": [],
                    "usual_items_summary": []
                }

            if inspection.get("extracted_data"):
                ext = inspection["extracted_data"]
                if ext.get("product_name"):
                    product_name = ext["product_name"]
                if ext.get("extracted_facts"):
                    extracted_facts = ext["extracted_facts"]
                if ext.get("ingredients_list"):
                    raw_text = (raw_text + "\nIngredients: " + ", ".join(ext["ingredients_list"])).strip()
            if inspection.get("raw_text") and not raw_text:
                raw_text = inspection["raw_text"]

        # 3. If no image provided, check text relevance
        elif raw_text.strip():
            is_rel, rel_reason, _ = domain_relevance_guard.check_text_relevance(raw_text, "nutri_score")
            if not is_rel:
                logger.info(f"Nutri-analyzer rejected text: {rel_reason}")
                return {
                    "status": "IRRELEVANT_DATA",
                    "is_relevant": False,
                    "relevance_reason": rel_reason,
                    "detected_subject": "unrelated text",
                    "corrected_text": corrected_text_summary,
                    "product_name": "Irrelevant Text Input",
                    "verdict": "IRRELEVANT",
                    "verdict_badge": "IRRELEVANT",
                    "nutri_score_grade": "N/A",
                    "nutri_score_points": 0,
                    "score_breakdown": None,
                    "summary_verdict": f"Irrelevant Data Detected: {rel_reason}",
                    "spoken_summary": f"Irrelevant text detected. {rel_reason}",
                    "spoken_language": language or "en",
                    "sodium_mg": None,
                    "sodium_level": "N/A",
                    "trans_fat_g": None,
                    "trans_fat_status": "N/A",
                    "saturated_fat_g": None,
                    "added_sugar_g": None,
                    "added_sugar_level": "N/A",
                    "has_palm_oil": False,
                    "palm_oil_details": None,
                    "hidden_sugars": [],
                    "harmful_additives": [],
                    "beneficial_ingredients": [],
                    "persona_alerts": [],
                    "fssai_compliance_notes": ["Please enter food ingredients or a nutrition facts table to analyze."],
                    "raw_extracted_ingredients": [],
                    "nutrition_table": {},
                    "all_ingredients_analysis": [],
                    "govt_limit_comparison": [],
                    "usual_items_summary": []
                }

        # 4. If neither image nor text provided, or both empty
        if not raw_text.strip() and not extracted_facts:
            return {
                "status": "IRRELEVANT_DATA",
                "is_relevant": False,
                "relevance_reason": "No food ingredients or nutritional information was detected in the input.",
                "detected_subject": "empty input",
                "corrected_text": "",
                "product_name": "No Input Data",
                "verdict": "IRRELEVANT",
                "verdict_badge": "IRRELEVANT",
                "nutri_score_grade": "N/A",
                "nutri_score_points": 0,
                "score_breakdown": None,
                "summary_verdict": "No food ingredients or nutrition facts provided.",
                "spoken_summary": "Please provide an image or text of food nutrition facts.",
                "spoken_language": language or "en",
                "sodium_mg": None,
                "sodium_level": "N/A",
                "trans_fat_g": None,
                "trans_fat_status": "N/A",
                "saturated_fat_g": None,
                "added_sugar_g": None,
                "added_sugar_level": "N/A",
                "has_palm_oil": False,
                "palm_oil_details": None,
                "hidden_sugars": [],
                "harmful_additives": [],
                "beneficial_ingredients": [],
                "persona_alerts": [],
                "fssai_compliance_notes": ["No input provided."],
                "raw_extracted_ingredients": [],
                "nutrition_table": {},
                "all_ingredients_analysis": [],
                "govt_limit_comparison": [],
                "usual_items_summary": []
            }

        # 5. Parse nutrition values from text if not populated by vision
        nutri_table = self._parse_nutrition_table(raw_text, extracted_facts)

        # 6. Parse ingredient list from text
        ingredients_list = self._extract_ingredients(raw_text)

        # 4. Decrypt Hidden Sugars
        hidden_sugars = self._detect_hidden_sugars(raw_text, ingredients_list)

        # 5. Decrypt Unhealthy Fats & Palm Oil
        has_palm_oil, palm_details = self._detect_palm_oil(raw_text)

        # 6. Decrypt Harmful Additives & E-Numbers
        harmful_additives = self._detect_additives(raw_text)

        # 7. Identify Beneficial Ingredients
        beneficial = self._detect_beneficial(raw_text)

        # 8. All Ingredients Analysis (Extract every ingredient, health effect, advantage/risk, harmlessness level)
        all_ingredients_analysis = self._analyze_all_ingredients(raw_text, ingredients_list)

        # 9. Government Recommended Limits Comparison (Check parameters vs FSSAI & WHO/ICMR safe limits with exceed %)
        govt_limit_comparison = self._compute_govt_limit_comparison(nutri_table, harmful_additives, raw_text)

        # 10. Household Usual Items Harmlessness Breakdown (Staple foods harmlessness vs processed food risk)
        usual_items_summary = self._build_usual_items_summary(ingredients_list, raw_text)

        # 11. Check persona specific risk factors (kept for backwards compatibility)
        persona_alerts = self._check_persona_risks(
            persona=persona or "general",
            nutri_table=nutri_table,
            raw_text=raw_text,
            hidden_sugars=hidden_sugars,
            has_palm_oil=has_palm_oil,
            harmful_additives=harmful_additives
        )

        # 12. Calculate FSSAI Nutri-Score (Grade A to E)
        nutri_grade, nutri_points, score_breakdown = self._compute_nutri_score(
            nutri_table=nutri_table,
            has_palm_oil=has_palm_oil,
            hidden_sugars_count=len(hidden_sugars),
            critical_additives_count=sum(1 for a in harmful_additives if a.get("risk") == "CRITICAL")
        )

        # 13. Generate Definitive Verdict (HARMFUL / CAUTION / SECURE)
        verdict, verdict_badge, summary_verdict, compliance_notes = self._determine_verdict(
            nutri_grade=nutri_grade,
            nutri_table=nutri_table,
            has_palm_oil=has_palm_oil,
            hidden_sugars=hidden_sugars,
            harmful_additives=harmful_additives,
            persona_alerts=persona_alerts,
            persona=persona or "general"
        )

        # 14. Multilingual Localization of Response Fields
        target_lang = (language or "en").lower()
        if target_lang != "en" and target_lang in SUPPORTED_LANGUAGES:
            summary_verdict = multilingual_translator.translate_text(summary_verdict, target_lang)
            if palm_details:
                palm_details = multilingual_translator.translate_text(palm_details, target_lang)

            localized_persona_alerts = []
            for a in persona_alerts:
                localized_persona_alerts.append({
                    "persona": multilingual_translator.translate_text(a.get("persona", ""), target_lang),
                    "severity": a.get("severity", "WARNING"),
                    "message": multilingual_translator.translate_text(a.get("message", ""), target_lang)
                })
            persona_alerts = localized_persona_alerts

            compliance_notes = [
                multilingual_translator.translate_text(note, target_lang)
                for note in compliance_notes
            ]

            localized_hidden_sugars = []
            for s in hidden_sugars:
                localized_hidden_sugars.append({
                    "name": s.get("name", ""),
                    "description": multilingual_translator.translate_text(s.get("description", ""), target_lang),
                    "risk_level": s.get("risk_level", "HIGH"),
                    "category": multilingual_translator.translate_text(s.get("category", ""), target_lang)
                })
            hidden_sugars = localized_hidden_sugars

            localized_additives = []
            for a in harmful_additives:
                localized_additives.append({
                    "code": a.get("code", ""),
                    "name": a.get("name", ""),
                    "type": multilingual_translator.translate_text(a.get("type", ""), target_lang),
                    "hazard": multilingual_translator.translate_text(a.get("hazard", ""), target_lang),
                    "risk": a.get("risk", "HIGH")
                })
            harmful_additives = localized_additives

        # 15. Generate Spoken Multilingual Summary
        spoken_summary, spoken_lang = self._generate_spoken_verdict(
            verdict=verdict,
            product_name=product_name,
            nutri_grade=nutri_grade,
            nutri_table=nutri_table,
            has_palm_oil=has_palm_oil,
            hidden_sugars=hidden_sugars,
            harmful_additives=harmful_additives,
            persona_alerts=persona_alerts,
            language=target_lang
        )

        return {
            "status": "SUCCESS",
            "is_relevant": True,
            "relevance_reason": "Relevant food nutrition label analyzed successfully.",
            "detected_subject": detected_subject,
            "corrected_text": corrected_text_summary,
            "product_name": product_name,
            "verdict": verdict,
            "verdict_badge": verdict_badge,
            "nutri_score_grade": nutri_grade,
            "nutri_score_points": nutri_points,
            "score_breakdown": score_breakdown,
            "summary_verdict": summary_verdict,
            "spoken_summary": spoken_summary,
            "spoken_language": spoken_lang,
            "sodium_mg": nutri_table.get("sodium_mg"),
            "sodium_level": self._classify_sodium(nutri_table.get("sodium_mg")),
            "trans_fat_g": nutri_table.get("trans_fat_g"),
            "trans_fat_status": "HIGH / DANGEROUS" if (nutri_table.get("trans_fat_g") or 0) > THRESHOLDS["trans_fat_max_g"] else "ZERO / COMPLIANT",
            "saturated_fat_g": nutri_table.get("saturated_fat_g"),
            "added_sugar_g": nutri_table.get("added_sugar_g") if nutri_table.get("added_sugar_g") is not None else nutri_table.get("total_sugar_g"),
            "added_sugar_level": self._classify_sugar(nutri_table.get("added_sugar_g") or nutri_table.get("total_sugar_g")),
            "has_palm_oil": has_palm_oil,
            "palm_oil_details": palm_details,
            "hidden_sugars": hidden_sugars,
            "harmful_additives": harmful_additives,
            "beneficial_ingredients": beneficial,
            "persona_alerts": persona_alerts,
            "all_ingredients_analysis": all_ingredients_analysis,
            "govt_limit_comparison": govt_limit_comparison,
            "usual_items_summary": usual_items_summary,
            "fssai_compliance_notes": compliance_notes,
            "raw_extracted_ingredients": ingredients_list[:30],
            "nutrition_table": nutri_table
        }

    def _inspect_image_with_vision(self, image_base64: str) -> Optional[Dict[str, Any]]:
        """Uses Gemini Vision (if configured) to read nutrition label and ingredients accurately."""
        if not settings.GEMINI_API_KEY:
            return None

        try:
            import google.generativeai as genai
            import json
            import base64

            # Clean base64 header and detect mime type
            clean_b64 = image_base64
            mime_type = "image/jpeg"
            if "data:" in clean_b64 and ";base64," in clean_b64:
                parts = clean_b64.split(";base64,")
                detected_mime = parts[0].replace("data:", "").strip()
                if detected_mime:
                    mime_type = detected_mime
                clean_b64 = parts[1]
            elif "base64," in clean_b64:
                clean_b64 = clean_b64.split("base64,")[1]

            image_bytes = base64.b64decode(clean_b64)
            from app.core.gemini_manager import gemini_manager

            prompt = (
                "You are an expert FSSAI Food Safety and Nutrition Inspector. "
                "Analyze this food packaging image and extract:\n"
                "1. Product or Brand Name\n"
                "2. Complete Ingredients List (exact text)\n"
                "3. Nutritional Information per 100g or per serving (Energy kcal, Protein g, Carbohydrate g, "
                "Total Sugar g, Added Sugar g, Total Fat g, Saturated Fat g, Trans Fat g, Sodium mg, Dietary Fiber g)\n\n"
                "Return ONLY a valid JSON object with the following structure (no backticks, no markdown):\n"
                "{\n"
                '  "product_name": "Product Name",\n'
                '  "raw_text": "Extracted text of ingredients and nutrition facts",\n'
                '  "extracted_facts": {\n'
                '    "energy_kcal": 450.0,\n'
                '    "protein_g": 6.5,\n'
                '    "carbs_g": 68.0,\n'
                '    "total_sugar_g": 24.0,\n'
                '    "added_sugar_g": 22.0,\n'
                '    "total_fat_g": 18.0,\n'
                '    "saturated_fat_g": 8.5,\n'
                '    "trans_fat_g": 0.1,\n'
                '    "sodium_mg": 780.0,\n'
                '    "fiber_g": 2.0\n'
                "  }\n"
                "}"
            )

            raw_resp, _ = gemini_manager.generate_with_fallback([
                prompt,
                {"mime_type": mime_type, "data": image_bytes}
            ])
            if not raw_resp:
                return None
            # Clean markdown codeblocks if present
            if raw_resp.startswith("```json"):
                raw_resp = raw_resp[7:]
            if raw_resp.startswith("```"):
                raw_resp = raw_resp[3:]
            if raw_resp.endswith("```"):
                raw_resp = raw_resp[:-3]
            raw_resp = raw_resp.strip()

            data = json.loads(raw_resp)
            return data
        except Exception as e:
            logger.warning(f"Nutri-Analyzer Gemini Vision failed, falling back to local extractor: {e}")
            return None

    def _parse_nutrition_table(self, text: str, initial_facts: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts nutritional values per 100g/serving using high-precision regex."""
        facts = dict(initial_facts)
        clean_text = text.lower()

        # Helper regex parser
        def extract_num(patterns: List[str]) -> Optional[float]:
            for pat in patterns:
                m = re.search(pat, clean_text, re.IGNORECASE)
                if m:
                    try:
                        val = float(m.group(1).replace(",", "."))
                        return val
                    except Exception:
                        continue
            return None

        if "energy_kcal" not in facts or facts["energy_kcal"] is None:
            facts["energy_kcal"] = extract_num([
                r'energy\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*k?cal',
                r'calories\s*[:\-]?\s*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*k?cal'
            ])

        if "protein_g" not in facts or facts["protein_g"] is None:
            facts["protein_g"] = extract_num([
                r'protein\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'protein\s+(\d+(?:\.\d+)?)'
            ])

        if "carbs_g" not in facts or facts["carbs_g"] is None:
            facts["carbs_g"] = extract_num([
                r'carbohydrates?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'total\s+carbs?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'carbs?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
            ])

        if "total_sugar_g" not in facts or facts["total_sugar_g"] is None:
            facts["total_sugar_g"] = extract_num([
                r'total\s+sugars?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'sugars?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
            ])

        if "added_sugar_g" not in facts or facts["added_sugar_g"] is None:
            facts["added_sugar_g"] = extract_num([
                r'added\s+sugars?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'of\s+which\s+added\s+sugar\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
            ])

        if "total_fat_g" not in facts or facts["total_fat_g"] is None:
            facts["total_fat_g"] = extract_num([
                r'total\s+fat\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'fat\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
            ])

        if "saturated_fat_g" not in facts or facts["saturated_fat_g"] is None:
            facts["saturated_fat_g"] = extract_num([
                r'saturated\s+fat(?:ty\s+acids)?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'sat(?:urated)?\s+fat\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
            ])

        if "trans_fat_g" not in facts or facts["trans_fat_g"] is None:
            facts["trans_fat_g"] = extract_num([
                r'trans\s+fat(?:ty\s+acids)?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'trans\s+fat\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
            ])

        if "sodium_mg" not in facts or facts["sodium_mg"] is None:
            # Check mg first
            s_mg = extract_num([
                r'sodium\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*mg',
                r'na\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*mg'
            ])
            if s_mg is not None:
                facts["sodium_mg"] = s_mg
            else:
                # Check sodium in grams (multiply by 1000) or salt in grams (salt * 400 = sodium mg)
                s_g = extract_num([
                    r'sodium\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
                ])
                if s_g is not None:
                    facts["sodium_mg"] = s_g * 1000.0
                else:
                    salt_g = extract_num([
                        r'salt\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
                    ])
                    if salt_g is not None:
                        facts["sodium_mg"] = salt_g * 393.4  # FSSAI conversion: 1g salt ~ 393mg sodium

        if "fiber_g" not in facts or facts["fiber_g"] is None:
            facts["fiber_g"] = extract_num([
                r'dietary\s+fib(?:er|re)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g',
                r'fib(?:er|re)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*g'
            ])

        return facts

    def _extract_ingredients(self, text: str) -> List[str]:
        """Separates ingredient strings delimited by commas or parentheses."""
        match = re.search(r'ingredients?\s*[:\-]?\s*(.*?)(?:nutrition|nutritional|contains|allergens|mfg|best\s+before|$)', text, re.IGNORECASE | re.DOTALL)
        target_text = match.group(1) if match else text

        raw_tokens = re.split(r'[,;\n•]+', target_text)
        cleaned = []
        for t in raw_tokens:
            item = re.sub(r'[\(\)\[\]\{\}]', '', t).strip()
            if len(item) > 2 and not item.lower().startswith("per 100") and not item.lower().startswith("table"):
                cleaned.append(item)
        return cleaned

    def _detect_hidden_sugars(self, text: str, ingredients_list: List[str]) -> List[Dict[str, str]]:
        """Identifies hidden sugars, maltodextrins, syrups, and high-GI sweeteners."""
        detected = []
        lower_text = text.lower()

        for key, info in HIDDEN_SUGAR_DATABASE.items():
            pattern = rf'\b{re.escape(key)}\b'
            if re.search(pattern, lower_text):
                # Avoid duplicate names
                if not any(d["name"] == info["name"] for d in detected):
                    detected.append({
                        "name": info["name"],
                        "description": info["description"],
                        "risk_level": info["risk_level"],
                        "category": info["category"]
                    })
        return detected

    def _detect_palm_oil(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detects presence of Palm Oil, Palmolein, or Hydrogenated Fats."""
        lower_text = text.lower()
        found_types = []

        for p in PALM_OIL_KEYWORDS:
            if re.search(rf'\b{re.escape(p)}\b', lower_text):
                found_types.append(p.title())

        if found_types:
            unique_types = list(set(found_types))
            details = f"Detected: {', '.join(unique_types)}. Palm oils have a high Palmitic acid ratio (~44%) and atherogenic index, contributing to LDL cholesterol and arterial plaque."
            return True, details
        return False, None

    def _detect_additives(self, text: str) -> List[Dict[str, str]]:
        """Identifies synthetic colors, preservatives, and flavor enhancers by INS / E numbers or names."""
        lower_text = text.lower()
        detected = []

        # 1. INS / E-Number match (e.g. INS 102, E102, 102, INS102(i))
        for code, info in ADDITIVE_DATABASE.items():
            pattern = rf'\b(?:ins|e)?[ -]?{code}(?:\([a-z0-9]+\))?\b'
            if re.search(pattern, lower_text):
                detected.append({
                    "code": f"INS {code}",
                    "name": info["name"],
                    "type": info["type"],
                    "hazard": info["hazard"],
                    "risk": info["risk"]
                })
            else:
                # Name matching (e.g. Tartrazine, Monosodium glutamate, BHA, Aspartame)
                keywords = []
                if "tartrazine" in info["name"].lower():
                    keywords.append("tartrazine")
                if "sunset yellow" in info["name"].lower():
                    keywords.append("sunset yellow")
                if "carmoisine" in info["name"].lower():
                    keywords.append("carmoisine")
                if "monosodium glutamate" in info["name"].lower():
                    keywords.extend(["monosodium glutamate", "msg"])
                if "titanium dioxide" in info["name"].lower():
                    keywords.append("titanium dioxide")
                if "aspartame" in info["name"].lower():
                    keywords.append("aspartame")
                if "sucralose" in info["name"].lower():
                    keywords.append("sucralose")
                if "sodium benzoate" in info["name"].lower():
                    keywords.append("sodium benzoate")

                for kw in keywords:
                    if re.search(rf'\b{re.escape(kw)}\b', lower_text):
                        if not any(d["name"] == info["name"] for d in detected):
                            detected.append({
                                "code": f"INS {code}",
                                "name": info["name"],
                                "type": info["type"],
                                "hazard": info["hazard"],
                                "risk": info["risk"]
                            })
                        break

        return detected

    def _detect_beneficial(self, text: str) -> List[str]:
        """Detects whole grains, millets, fiber, and clean health ingredients."""
        lower_text = text.lower()
        found = []
        for b in BENEFICIAL_KEYWORDS:
            if re.search(rf'\b{re.escape(b)}\b', lower_text):
                found.append(b.title())
        return list(set(found))

    def _check_persona_risks(
        self,
        persona: str,
        nutri_table: Dict[str, Any],
        raw_text: str,
        hidden_sugars: List[Dict[str, str]],
        has_palm_oil: bool,
        harmful_additives: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Applies specialized clinical and allergic safety checks based on user health persona."""
        alerts = []
        lower_text = raw_text.lower()
        sugar_val = nutri_table.get("added_sugar_g") or nutri_table.get("total_sugar_g") or 0.0
        sodium_val = nutri_table.get("sodium_mg") or 0.0
        trans_fat = nutri_table.get("trans_fat_g") or 0.0

        # Persona 1: Diabetic
        if persona in ["diabetic", "all"]:
            reasons = []
            if sugar_val > 5.0:
                reasons.append(f"Sugar content ({sugar_val}g/100g) exceeds the safe threshold for blood sugar regulation.")
            if hidden_sugars:
                names = [s["name"] for s in hidden_sugars]
                reasons.append(f"Contains high-GI hidden sweeteners ({', '.join(names)}) which rapidly spike blood glucose and glycated hemoglobin (HbA1c).")
            if "refined wheat flour" in lower_text or "maida" in lower_text:
                reasons.append("Contains Refined Wheat Flour (Maida) with high glycemic index (~75) causing rapid insulin surges.")

            if reasons:
                alerts.append({
                    "persona": "Diabetic Alert",
                    "severity": "CRITICAL" if sugar_val > 15.0 or any(s["name"] == "Maltodextrin" for s in hidden_sugars) else "WARNING",
                    "message": " ".join(reasons)
                })

        # Persona 2: Gluten Allergic / Celiac Disease
        if persona in ["gluten_free", "celiac", "all"]:
            found_gluten = []
            for g in GLUTEN_KEYWORDS:
                if re.search(rf'\b{re.escape(g)}\b', lower_text):
                    found_gluten.append(g.title())
            if found_gluten:
                alerts.append({
                    "persona": "Gluten & Celiac Alert",
                    "severity": "CRITICAL",
                    "message": f"Contains Gluten-bearing grains: {', '.join(set(found_gluten))}. NOT SAFE for Celiac disease or gluten intolerance."
                })

        # Persona 3: Infants & Young Children (< 2 years / kids)
        if persona in ["infant", "child", "all"]:
            infant_flags = []
            # Check MSG
            if any("621" in a.get("code", "") for a in harmful_additives):
                infant_flags.append("Contains Monosodium Glutamate (MSG / INS 621), strictly prohibited in infant food formulations under FSSAI regulations.")
            # Check Artificial Colors
            synth_colors = [a["name"] for a in harmful_additives if "color" in a.get("type", "").lower() or "dye" in a.get("type", "").lower()]
            if synth_colors:
                infant_flags.append(f"Contains synthetic azo dyes ({', '.join(synth_colors)}) linked to ADHD hyperactivity and behavioral disorders in children.")
            # Check Artificial Sweeteners
            sweeteners = [a["name"] for a in harmful_additives if "sweetener" in a.get("type", "").lower()]
            if sweeteners:
                infant_flags.append(f"Contains non-nutritive artificial sweeteners ({', '.join(sweeteners)}) prohibited for infants and toddlers.")
            # Check Sodium for infants (RDA is very low: < 200mg/day)
            if sodium_val > 200.0:
                infant_flags.append(f"Sodium level of {sodium_val}mg is excessively high for immature infant kidneys.")

            if infant_flags:
                alerts.append({
                    "persona": "Infant & Child Safety Alert",
                    "severity": "CRITICAL",
                    "message": " ".join(infant_flags)
                })

        # Persona 4: Heart & Hypertension
        if persona in ["heart", "hypertension", "all"]:
            heart_flags = []
            if sodium_val > THRESHOLDS["sodium_caution_mg"]:
                heart_flags.append(f"Sodium content of {sodium_val}mg/100g contributes to elevated blood pressure and vascular strain.")
            if trans_fat > THRESHOLDS["trans_fat_max_g"]:
                heart_flags.append(f"Trans Fat ({trans_fat}g/100g) exceeds FSSAI limits; increases atherogenic LDL and lowers protective HDL.")
            if has_palm_oil:
                heart_flags.append("Contains high-palmitic palm oil / palmolein, elevating arterial stiffness and coronary disease risks.")

            if heart_flags:
                alerts.append({
                    "persona": "Cardiovascular & Blood Pressure Alert",
                    "severity": "CRITICAL" if sodium_val > 800.0 or trans_fat > 0.2 else "WARNING",
                    "message": " ".join(heart_flags)
                })

        return alerts

    def _compute_nutri_score(
        self,
        nutri_table: Dict[str, Any],
        has_palm_oil: bool,
        hidden_sugars_count: int,
        critical_additives_count: int
    ) -> Tuple[str, int, Dict[str, int]]:
        """
        FSSAI-aligned Front-of-Pack Nutri-Score calculation (Grades A to E).
        Calculates negative points (N) and positive points (P).
        Net Score = N - P.
        """
        energy = nutri_table.get("energy_kcal") or 0.0
        sat_fat = nutri_table.get("saturated_fat_g") or 0.0
        sugars = nutri_table.get("added_sugar_g") or nutri_table.get("total_sugar_g") or 0.0
        sodium = nutri_table.get("sodium_mg") or 0.0
        trans_fat = nutri_table.get("trans_fat_g") or 0.0
        fiber = nutri_table.get("fiber_g") or 0.0
        protein = nutri_table.get("protein_g") or 0.0

        # Negative Points Calculation (N)
        n_points = 0

        # Energy (kcal per 100g)
        if energy > 800: n_points += 10
        elif energy > 670: n_points += 8
        elif energy > 500: n_points += 6
        elif energy > 335: n_points += 4
        elif energy > 160: n_points += 2

        # Saturated Fat (g)
        if sat_fat > 10.0: n_points += 10
        elif sat_fat > 7.0: n_points += 7
        elif sat_fat > 4.0: n_points += 4
        elif sat_fat > 2.0: n_points += 2
        elif sat_fat > 1.0: n_points += 1

        # Sugars (g)
        if sugars > 30.0: n_points += 10
        elif sugars > 20.0: n_points += 7
        elif sugars > 13.0: n_points += 5
        elif sugars > 9.0: n_points += 3
        elif sugars > 4.5: n_points += 1

        # Sodium (mg)
        if sodium > 900.0: n_points += 10
        elif sodium > 720.0: n_points += 8
        elif sodium > 540.0: n_points += 6
        elif sodium > 360.0: n_points += 4
        elif sodium > 180.0: n_points += 2
        elif sodium > 90.0: n_points += 1

        # Penalty additions for palm oil and industrial chemicals
        if has_palm_oil:
            n_points += 3
        if trans_fat > 0.2:
            n_points += 6
        n_points += min(hidden_sugars_count * 2, 6)
        n_points += min(critical_additives_count * 3, 9)

        # Positive Points Calculation (P)
        p_points = 0

        # Fiber (g)
        if fiber > 4.5: p_points += 5
        elif fiber > 3.0: p_points += 3
        elif fiber > 1.5: p_points += 2
        elif fiber > 0.7: p_points += 1

        # Protein (g)
        if protein > 8.0: p_points += 5
        elif protein > 6.0: p_points += 4
        elif protein > 4.0: p_points += 3
        elif protein > 2.0: p_points += 2
        elif protein > 1.0: p_points += 1

        net_score = n_points - p_points

        # Grade Mapping
        if net_score <= -1:
            grade = "A"
        elif net_score <= 2:
            grade = "B"
        elif net_score <= 10:
            grade = "C"
        elif net_score <= 18:
            grade = "D"
        else:
            grade = "E"

        breakdown = {
            "negative_points": n_points,
            "positive_points": p_points,
            "net_score": net_score
        }

        return grade, net_score, breakdown

    def _determine_verdict(
        self,
        nutri_grade: str,
        nutri_table: Dict[str, Any],
        has_palm_oil: bool,
        hidden_sugars: List[Dict[str, str]],
        harmful_additives: List[Dict[str, str]],
        persona_alerts: List[Dict[str, str]],
        persona: str
    ) -> Tuple[str, str, str, List[str]]:
        """
        Determines the definitive 3-tier verdict:
        - 🚨 HARMFUL (HIGH RISK)
        - ⚠️ CAUTION (MODERATE RISK)
        - 🛡️ SECURE (SAFE & COMPLIANT)
        """
        sodium = nutri_table.get("sodium_mg") or 0.0
        trans_fat = nutri_table.get("trans_fat_g") or 0.0
        added_sugar = nutri_table.get("added_sugar_g") or nutri_table.get("total_sugar_g") or 0.0
        sat_fat = nutri_table.get("saturated_fat_g") or 0.0

        critical_reasons = []
        caution_reasons = []
        compliance_notes = []

        # 1. Trans fat check
        if trans_fat > THRESHOLDS["trans_fat_max_g"]:
            critical_reasons.append(f"Trans Fat ({trans_fat}g/100g) breaches FSSAI statutory cap of 0.2g/100g.")
        else:
            compliance_notes.append("Trans Fat compliant with FSSAI limits (<= 0.2g / 100g).")

        # 2. Sodium check
        if sodium >= THRESHOLDS["sodium_harmful_mg"]:
            critical_reasons.append(f"Excessive Sodium ({sodium}mg/100g), exceeding 40% of WHO/ICMR daily allowance in a single serving.")
        elif sodium >= THRESHOLDS["sodium_caution_mg"]:
            caution_reasons.append(f"Elevated Sodium ({sodium}mg/100g) classified as High in Fat/Sugar/Salt (HFSS).")
        else:
            compliance_notes.append(f"Sodium content ({sodium}mg/100g) is within healthy bounds (< 400mg).")

        # 3. Added sugar check
        if added_sugar >= THRESHOLDS["added_sugar_harmful_g"]:
            critical_reasons.append(f"Dangerous Added Sugar level ({added_sugar}g/100g), promoting metabolic syndrome and diabetes.")
        elif added_sugar >= THRESHOLDS["added_sugar_caution_g"]:
            caution_reasons.append(f"Moderate to High Sugar ({added_sugar}g/100g).")

        # 4. Saturated fat & Palm oil
        if has_palm_oil and sat_fat > THRESHOLDS["saturated_fat_harmful_g"]:
            critical_reasons.append("High Saturated Fat combined with Palm Oil / Palmolein promotes arterial cholesterol accumulation.")
        elif has_palm_oil:
            caution_reasons.append("Contains Palm Oil / Palmolein; consider switching to healthier cold-pressed oils.")

        # 5. Dangerous Additives
        crit_add = [a for a in harmful_additives if a.get("risk") == "CRITICAL"]
        if crit_add:
            for c in crit_add:
                critical_reasons.append(f"Contains hazardous chemical additive {c['name']} ({c['hazard']}).")

        # 6. Persona specific critical alerts
        for alert in persona_alerts:
            if alert.get("severity") == "CRITICAL":
                critical_reasons.append(f"{alert['persona']}: {alert['message']}")
            elif alert.get("severity") == "WARNING":
                caution_reasons.append(f"{alert['persona']}: {alert['message']}")

        # 7. Nutri-Score Grade override
        if nutri_grade == "E":
            critical_reasons.append("Nutri-Score Grade E denotes ultra-processed HFSS product with poor nutritional density.")

        # Final Verdict Decision
        if critical_reasons:
            verdict = "HARMFUL"
            badge = "🚨 HARMFUL (HIGH RISK)"
            summary = "This product contains hazardous components or severe health risk triggers: " + " ".join(critical_reasons[:3])
        elif caution_reasons or nutri_grade == "D":
            verdict = "CAUTION"
            badge = "⚠️ CAUTION (MODERATE RISK)"
            summary = "Consume with caution in moderation: " + " ".join(caution_reasons[:3])
        else:
            verdict = "SECURE"
            badge = "🛡️ SECURE (SAFE & COMPLIANT)"
            summary = "This food item meets healthy FSSAI nutritional standards with low sodium, zero trans fats, and no toxic hidden additives."

        return verdict, badge, summary, compliance_notes

    def _generate_spoken_verdict(
        self,
        verdict: str,
        product_name: str,
        nutri_grade: str,
        nutri_table: Dict[str, Any],
        has_palm_oil: bool,
        hidden_sugars: List[Dict[str, str]],
        harmful_additives: List[Dict[str, str]],
        persona_alerts: List[Dict[str, str]],
        language: str
    ) -> Tuple[str, str]:
        """Generates a clear 2-3 sentence spoken summary and translates it into the user's native language."""
        sodium = nutri_table.get("sodium_mg") or 0.0
        sugar = nutri_table.get("added_sugar_g") or nutri_table.get("total_sugar_g") or 0.0

        if verdict == "HARMFUL":
            reasons = []
            if sodium > 800:
                reasons.append(f"very high sodium of {int(sodium)} milligrams")
            if sugar > 20:
                reasons.append(f"high added sugar of {int(sugar)} grams")
            if has_palm_oil:
                reasons.append("palm oil")
            if hidden_sugars:
                reasons.append(hidden_sugars[0]["name"])
            if harmful_additives:
                reasons.append(harmful_additives[0]["name"])

            cause_str = ", ".join(reasons[:3]) if reasons else "unhealthy nutritional levels"
            eng_text = (
                f"Safety Analysis Result: HARMFUL. FSSAI Nutri-Score Grade is {nutri_grade}. "
                f"This product is flagged as high risk due to {cause_str}. "
                f"Regular consumption is not recommended as it breaches recommended government health limits."
            )
        elif verdict == "CAUTION":
            eng_text = (
                f"Safety Analysis Result: CAUTION. FSSAI Nutri-Score Grade is {nutri_grade}. "
                f"This product has moderate levels of fat, sugar, or sodium. "
                f"Consume only in limited moderation."
            )
        else:
            eng_text = (
                f"Safety Analysis Result: SECURE and Healthy. FSSAI Nutri-Score Grade is {nutri_grade}. "
                f"This product is verified compliant with Indian food standards, with low sodium and no dangerous trans fats."
            )

        target_lang = (language or "en").lower()
        if target_lang != "en" and target_lang in SUPPORTED_LANGUAGES:
            # Deterministic native speech templates for 100% reliability
            native_speech_map = {
                "hi": {
                    "HARMFUL": f"सुरक्षा विश्लेषण परिणाम: हानिकारक। FSSAI न्यूट्री-स्कोर ग्रेड {nutri_grade} है। उच्च सोडियम, ट्रांस फैट या हानिकारक एडिटिव्स के कारण यह स्वास्थ्य के लिए जोखिम भरा है। इसका नियमित सेवन न करें।",
                    "CAUTION": f"सुरक्षा विश्लेषण परिणाम: सावधानी। FSSAI न्यूट्री-स्कोर ग्रेड {nutri_grade} है। इसमें वसा, चीनी या नमक की मात्रा मध्यम है। केवल सीमित मात्रा में सेवन करें।",
                    "SECURE": f"सुरक्षा विश्लेषण परिणाम: सुरक्षित और स्वस्थ। FSSAI न्यूट्री-स्कोर ग्रेड {nutri_grade} है। यह उत्पाद भारतीय खाद्य सुरक्षा मानकों के अनुरूप है और कम सोडियम वाला है।"
                },
                "te": {
                    "HARMFUL": f"భద్రతా విశ్లేషణ ఫలితం: హానికరం. FSSAI న్యూట్రి-స్కోర్ గ్రేడ్ {nutri_grade}. అధిక సోడియం, ట్రాన్స్ ఫ్యాట్ లేదా హానికరమైన పదార్థాల వల్ల ఇది ఆరోగ్యానికి ప్రమాదకరం. క్రమం తప్పకుండా తీసుకోవడం మంచిది కాదు.",
                    "CAUTION": f"భద్రతా విశ్లేషణ ఫలితం: జాగ్రత్త. FSSAI న్యూట్రి-స్కోర్ గ్రేడ్ {nutri_grade}. ఇందులో కొవ్వు, చక్కెర లేదా ఉప్పు మధ్యస్థంగా ఉన్నాయి. మితంగా మాత్రమే తినండి.",
                    "SECURE": f"భద్రతా విశ్లేషణ ఫలితం: సురక్షితం మరియు ఆరోగ్యకరం. FSSAI న్యూట్రి-స్కోర్ గ్రేడ్ {nutri_grade}. ఈ ఆహారం భారతీయ ఆహార భద్రతా ప్రమాణాలకు అనుగుణంగా ఉంది."
                },
                "ta": {
                    "HARMFUL": f"பாதுகாப்பு பகுப்பாய்வு முடிவு: தீங்கு விளைவிக்கக்கூடியது. FSSAI நியூட்ரி-ஸ்கோர் தரம் {nutri_grade}. அதிக சோடியம் அல்லது டிரான்ஸ் கொழுப்பு காரணமாக இது ஆபத்தானது.",
                    "CAUTION": f"பாதுகாப்பு பகுப்பாய்வு முடிவு: எச்சரிக்கை. FSSAI நியூட்ரி-ஸ்கோர் தரம் {nutri_grade}. மிதமான அளவில் மட்டுமே உட்கொள்ளுங்கள்.",
                    "SECURE": f"பாதுகாப்பு பகுப்பாய்வு முடிவு: பாதுகாப்பானது மற்றும் ஆரோக்கியமானது. FSSAI நியூட்ரி-ஸ்கோர் தரம் {nutri_grade}. இந்த உணவு இந்திய உணவு பாதுகாப்பு தரநிலைகளுக்கு இணங்குகிறது."
                },
                "mr": {
                    "HARMFUL": f"सुरक्षा विश्लेषण निकाल: हानिकारक. FSSAI न्यूट्री-स्कोअर ग्रेड {nutri_grade} आहे. जास्त सोडियम किंवा हानिकारक घटकांमुळे हे आरोग्यासाठी घातक आहे.",
                    "CAUTION": f"सुरक्षा विश्लेषण निकाल: काळजीपूर्वक वापरा. FSSAI न्यूट्री-स्कोअर ग्रेड {nutri_grade} आहे. मर्यादित प्रमाणात सेवन करा.",
                    "SECURE": f"सुरक्षा विश्लेषण निकाल: सुरक्षित आणि पौष्टिक. FSSAI न्यूट्री-स्कोअर ग्रेड {nutri_grade} आहे. हे उत्पादन भारतीय अन्न सुरक्षा मानकांनुसार योग्य आहे."
                },
                "bn": {
                    "HARMFUL": f"সুরক্ষা বিশ্লেষণ ফলাফল: ক্ষতিকারক। FSSAI নিউট্রি-স্কোর গ্রেড {nutri_grade}। উচ্চ সোডিয়াম বা ক্ষতিকারক উপাদানের কারণে এটি স্বাস্থ্যের জন্য ঝুঁকিপূর্ণ।",
                    "CAUTION": f"সুরক্ষা বিশ্লেষণ ফলাফল: সতর্কতা। FSSAI নিউট্রি-স্কোর গ্রেড {nutri_grade}। পরিমিত পরিমাণে গ্রহণ করুন।",
                    "SECURE": f"সুরক্ষা বিশ্লেষণ ফলাফল: নিরাপদ এবং স্বাস্থ্যকর। FSSAI নিউট্রি-স্কোর গ্রেড {nutri_grade}। এই খাদ্য ভারতীয় খাদ্য নিরাপত্তা মান মেনে তৈরি।"
                }
            }
            if target_lang in native_speech_map and verdict in native_speech_map[target_lang]:
                return native_speech_map[target_lang][verdict], target_lang

            try:
                translated_text = multilingual_translator.translate_text(eng_text, target_lang)
                clean_spoken = re.sub(r'[#\*`_>\[\]]', '', translated_text).strip()
                return clean_spoken, target_lang
            except Exception as e:
                logger.warning(f"Voice translation failed: {e}")

        return eng_text, "en"

    def _analyze_all_ingredients(self, text: str, ingredients_list: List[str]) -> List[Dict[str, str]]:
        """
        Extracts all ingredients, classifies their category, determines their health effect
        (BENEFICIAL, SAFE_NEUTRAL, MODERATE_CAUTION, HARMFUL), physiological advantage/risk,
        and everyday harmlessness rating.
        """
        analyzed = []
        seen_names = set()

        all_candidates = list(ingredients_list)
        if not all_candidates and text:
            match = re.search(r'ingredients?\s*[:\-]?\s*(.*?)(?:nutrition|nutritional|contains|allergens|mfg|best\s+before|$)', text, re.IGNORECASE | re.DOTALL)
            target_text = match.group(1) if match else text
            tokens = re.split(r'[,;\n•]+', target_text)
            for t in tokens:
                clean_t = re.sub(r'[\(\)\[\]\{\}]', '', t).strip()
                if len(clean_t) > 2:
                    all_candidates.append(clean_t)

        kb_keys = sorted(INGREDIENT_KNOWLEDGE_BASE.keys(), key=len, reverse=True)

        for candidate in all_candidates:
            clean_item = re.sub(r'[\(\)\[\]\{\}:]', '', candidate).strip()
            lower_item = clean_item.lower()
            if len(clean_item) < 2 or lower_item in ["and", "or", "contains", "ingredients", "allergen", "added", "contain"]:
                continue

            matched_entry = None
            for key in kb_keys:
                if key in lower_item or re.search(rf'\b{re.escape(key)}\b', lower_item):
                    matched_entry = INGREDIENT_KNOWLEDGE_BASE[key]
                    break

            item_display_name = clean_item.title()
            if item_display_name.lower() in seen_names:
                continue
            seen_names.add(item_display_name.lower())

            if matched_entry:
                analyzed.append({
                    "name": item_display_name,
                    "category": matched_entry["category"],
                    "health_effect": matched_entry["health_effect"],
                    "health_advantage_or_risk": matched_entry["health_advantage_or_risk"],
                    "harmlessness_level": matched_entry["harmlessness_level"]
                })
            else:
                cat = "Food Component"
                effect = "SAFE_NEUTRAL"
                advantage = "Standard food constituent; contributes to matrix structure and satiety in balanced dietary intake."
                harmlessness = "🟢 Safe & Beneficial"

                if any(w in lower_item for w in ["flavor", "flavour", "aroma"]):
                    cat = "Flavoring Substance"
                    effect = "SAFE_NEUTRAL"
                    advantage = "Sensory aromatic compound used to enhance palatability and fragrance; safe within regulated limits."
                    harmlessness = "🟢 Safe & Beneficial"
                elif any(w in lower_item for w in ["gum", "pectin", "cellulose", "thickener"]):
                    cat = "Plant Hydrocolloid / Stabilizer"
                    effect = "SAFE_NEUTRAL"
                    advantage = "Soluble dietary texturizer providing smooth mouthfeel and emulsion stability."
                    harmlessness = "🟢 Safe & Beneficial"
                elif any(w in lower_item for w in ["vitamin", "mineral", "iron", "zinc", "calcium", "folate"]):
                    cat = "Nutritional Fortificant"
                    effect = "BENEFICIAL"
                    advantage = "Added micronutrient supporting physiological adequacy and preventing clinical deficiencies."
                    harmlessness = "🟢 Safe & Beneficial"
                elif any(w in lower_item for w in ["color", "colour", "dye"]):
                    cat = "Coloring Agent"
                    effect = "MODERATE_CAUTION"
                    advantage = "Added for visual appearance; synthetic variants warrant moderation, especially for children."
                    harmlessness = "🔴 Harmful / Ultra-Processed Risk"
                elif any(w in lower_item for w in ["preservative", "benzoate", "sorbate", "propionate"]):
                    cat = "Chemical Preservative"
                    effect = "MODERATE_CAUTION"
                    advantage = "Inhibits microbial degradation and extends retail shelf-life; prefer fresh whole foods where possible."
                    harmlessness = "🔴 Harmful / Ultra-Processed Risk"

                analyzed.append({
                    "name": item_display_name,
                    "category": cat,
                    "health_effect": effect,
                    "health_advantage_or_risk": advantage,
                    "harmlessness_level": harmlessness
                })

        return analyzed

    def _compute_govt_limit_comparison(
        self,
        nutri_table: Dict[str, Any],
        harmful_additives: List[Dict[str, str]],
        raw_text: str
    ) -> List[Dict[str, Any]]:
        """
        Compares food parameters against statutory Indian FSSAI Front-of-Pack thresholds
        and WHO/ICMR recommended safe daily ceilings.
        Calculates exact exceedance percentages and provides actionable public guidance.
        """
        comparisons = []

        # 1. Added Sugar (FSSAI cutoff: 10g/100g; WHO daily limit: 25g/day)
        sugar_val = nutri_table.get("added_sugar_g")
        if sugar_val is None:
            sugar_val = nutri_table.get("total_sugar_g")
        if sugar_val is not None:
            if sugar_val > 10.0:
                pct_exceed = int(((sugar_val - 10.0) / 10.0) * 100)
                status = "CRITICAL_EXCESS" if sugar_val > 20.0 else "EXCEEDS_RECOMMENDED_LIMIT"
                daily_pct = min(100, int((sugar_val / 25.0) * 100))
                comparisons.append({
                    "parameter": "Added / Total Sugar",
                    "found_value": f"{sugar_val} g / 100g",
                    "govt_recommended_limit": "<= 10.0 g / 100g (FSSAI Cutoff) | Max 25g/day (WHO)",
                    "status": status,
                    "exceed_percentage": f"+{pct_exceed}%",
                    "warning_or_guidance": f"Exceeds FSSAI safe threshold by {pct_exceed}%. Consuming 100g uses {daily_pct}% of WHO's total daily sugar ceiling. Promotes insulin resistance and metabolic fatty liver."
                })
            else:
                comparisons.append({
                    "parameter": "Added / Total Sugar",
                    "found_value": f"{sugar_val} g / 100g",
                    "govt_recommended_limit": "<= 10.0 g / 100g (FSSAI Cutoff) | Max 25g/day (WHO)",
                    "status": "SAFE_WITHIN_LIMIT",
                    "exceed_percentage": "0% (Compliant)",
                    "warning_or_guidance": "Sugar level is within healthy FSSAI front-of-pack benchmark and WHO dietary guidelines."
                })

        # 2. Sodium / Salt (FSSAI cutoff: 500mg/100g; WHO daily limit: 2,000mg/day)
        sodium_val = nutri_table.get("sodium_mg")
        if sodium_val is not None:
            if sodium_val > 500.0:
                pct_exceed = int(((sodium_val - 500.0) / 500.0) * 100)
                status = "CRITICAL_EXCESS" if sodium_val > 800.0 else "EXCEEDS_RECOMMENDED_LIMIT"
                daily_pct = min(100, int((sodium_val / 2000.0) * 100))
                comparisons.append({
                    "parameter": "Sodium (Salt Equivalent)",
                    "found_value": f"{sodium_val} mg / 100g",
                    "govt_recommended_limit": "<= 500.0 mg / 100g (FSSAI Cutoff) | Max 2,000mg/day (WHO)",
                    "status": status,
                    "exceed_percentage": f"+{pct_exceed}%",
                    "warning_or_guidance": f"Exceeds FSSAI safe sodium threshold by {pct_exceed}%. A 100g serving consumes {daily_pct}% of WHO's daily recommended ceiling, elevating hypertension and stroke risk."
                })
            else:
                comparisons.append({
                    "parameter": "Sodium (Salt Equivalent)",
                    "found_value": f"{sodium_val} mg / 100g",
                    "govt_recommended_limit": "<= 500.0 mg / 100g (FSSAI Cutoff) | Max 2,000mg/day (WHO)",
                    "status": "SAFE_WITHIN_LIMIT",
                    "exceed_percentage": "0% (Compliant)",
                    "warning_or_guidance": "Sodium is well within healthy FSSAI limits (< 500mg/100g)."
                })

        # 3. Saturated Fat (FSSAI cutoff: 5.0g/100g; ICMR daily limit: <= 20g/day)
        sat_fat = nutri_table.get("saturated_fat_g")
        if sat_fat is not None:
            if sat_fat > 5.0:
                pct_exceed = int(((sat_fat - 5.0) / 5.0) * 100)
                status = "CRITICAL_EXCESS" if sat_fat > 8.0 else "EXCEEDS_RECOMMENDED_LIMIT"
                comparisons.append({
                    "parameter": "Saturated Fat",
                    "found_value": f"{sat_fat} g / 100g",
                    "govt_recommended_limit": "<= 5.0 g / 100g (FSSAI HFSS Standard) | <= 20g/day (ICMR)",
                    "status": status,
                    "exceed_percentage": f"+{pct_exceed}%",
                    "warning_or_guidance": f"Breaches FSSAI safe threshold by {pct_exceed}%. Excessive saturated fat stimulates hepatic LDL cholesterol synthesis and arterial narrowing."
                })
            else:
                comparisons.append({
                    "parameter": "Saturated Fat",
                    "found_value": f"{sat_fat} g / 100g",
                    "govt_recommended_limit": "<= 5.0 g / 100g (FSSAI HFSS Standard) | <= 20g/day (ICMR)",
                    "status": "SAFE_WITHIN_LIMIT",
                    "exceed_percentage": "0% (Compliant)",
                    "warning_or_guidance": "Saturated fat complies with FSSAI healthy benchmarks (<= 5g/100g)."
                })

        # 4. Trans Fat (FSSAI statutory ceiling: 0.2g/100g; Target: 0g)
        trans_fat = nutri_table.get("trans_fat_g")
        if trans_fat is not None:
            if trans_fat > 0.2:
                pct_exceed = int(((trans_fat - 0.2) / 0.2) * 100)
                comparisons.append({
                    "parameter": "Trans Fatty Acids",
                    "found_value": f"{trans_fat} g / 100g",
                    "govt_recommended_limit": "<= 0.2 g / 100g (Statutory FSSAI Mandatory Cap)",
                    "status": "CRITICAL_EXCESS",
                    "exceed_percentage": f"+{pct_exceed}%",
                    "warning_or_guidance": f"STATUTORY BREACH: Exceeds India's legal FSSAI trans-fat limit by {pct_exceed}%. Industrial trans fats have ZERO safe intake and directly cause coronary artery disease."
                })
            else:
                comparisons.append({
                    "parameter": "Trans Fatty Acids",
                    "found_value": f"{trans_fat} g / 100g",
                    "govt_recommended_limit": "<= 0.2 g / 100g (Statutory FSSAI Mandatory Cap)",
                    "status": "SAFE_WITHIN_LIMIT",
                    "exceed_percentage": "0% (Compliant)",
                    "warning_or_guidance": "Compliant with FSSAI statutory trans-fat regulations (<= 0.2g/100g)."
                })

        # 5. Chemical Additives & E-Numbers
        crit_add = [a for a in harmful_additives if a.get("risk") == "CRITICAL"]
        high_add = [a for a in harmful_additives if a.get("risk") == "HIGH"]
        if crit_add:
            names = [a["name"] for a in crit_add]
            comparisons.append({
                "parameter": "High-Risk Chemical Additives",
                "found_value": f"{len(crit_add)} Hazardous Additive(s) ({', '.join(names)})",
                "govt_recommended_limit": "Zero Banned / Genotoxic / Carcinogenic Additives (EU / WHO)",
                "status": "CRITICAL_EXCESS",
                "exceed_percentage": "UNACCEPTABLE RISK",
                "warning_or_guidance": f"Contains additives restricted or banned in international jurisdictions due to genotoxicity or severe health hazards ({', '.join(names)})."
            })
        elif high_add:
            names = [a["name"] for a in high_add]
            comparisons.append({
                "parameter": "Synthetic Dyes & Preservatives",
                "found_value": f"{len(high_add)} Synthetic Additive(s) ({', '.join(names)})",
                "govt_recommended_limit": "Minimal / Clean Label (No Synthetic Azo Dyes)",
                "status": "EXCEEDS_RECOMMENDED_LIMIT",
                "exceed_percentage": "ELEVATED RISK",
                "warning_or_guidance": f"Contains synthetic food dyes or preservatives ({', '.join(names)}) linked to behavioral hyperactivity in children and hypersensitivity."
            })
        else:
            comparisons.append({
                "parameter": "Chemical Additives & Clean Label",
                "found_value": "Zero Hazardous Additives Detected",
                "govt_recommended_limit": "Clean Label Standard",
                "status": "SAFE_WITHIN_LIMIT",
                "exceed_percentage": "0% (Clean)",
                "warning_or_guidance": "No banned synthetic colors, petrochemical antioxidants (BHA/BHT), or genotoxic whiteners detected."
            })

        return comparisons

    def _build_usual_items_summary(self, ingredients_list: List[str], raw_text: str) -> List[Dict[str, str]]:
        """
        Generates citizen-friendly clarity on the safety and harmlessness of usual household staples
        we use every day at home vs their risks in industrial packaged food.
        """
        return list(USUAL_HOUSEHOLD_ITEMS)

    def _classify_sodium(self, sodium_mg: Optional[float]) -> str:
        if sodium_mg is None: return "UNKNOWN"
        if sodium_mg >= 800.0: return "CRITICAL"
        if sodium_mg >= 400.0: return "HIGH"
        if sodium_mg >= 150.0: return "MODERATE"
        return "LOW (HEALTHY)"

    def _classify_sugar(self, sugar_g: Optional[float]) -> str:
        if sugar_g is None: return "UNKNOWN"
        if sugar_g >= 20.0: return "VERY HIGH (HFSS)"
        if sugar_g >= 10.0: return "HIGH"
        if sugar_g >= 5.0: return "MODERATE"
        return "LOW (HEALTHY)"


nutri_analyzer_service = NutriAnalyzerService()
