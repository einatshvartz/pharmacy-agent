# app/db.py

USERS = [
    {
        "user_id": "u001",
        "name": "Einat Shvartz",
        # List of medication names (must match MEDICATIONS[*]["name"])
        "prescriptions": ["Amoxicillin", "Metformin"],
    },
    {
        "user_id": "u002",
        "name": "Guy Lurya",
        "prescriptions": [],
    },
    {
        "user_id": "u003",
        "name": "Noa Kasher",
        "prescriptions": ["Amoxicillin"],
    },
    {
        "user_id": "u004",
        "name": "Amit Wiez",
        "prescriptions": [],
    },
    {
        "user_id": "u005",
        "name": "Lea London",
        "prescriptions": ["Metformin"],
    },
    {
        "user_id": "u006",
        "name": "Maya Rubin",
        "prescriptions": [],
    },
    {
        "user_id": "u007",
        "name": "Tamar Levi",
        "prescriptions": ["Amoxicillin"],
    },
    {
        "user_id": "u008",
        "name": "Tair Cohen",
        "prescriptions": [],
    },
    {
        "user_id": "u009",
        "name": "Nicole Kaplan",
        "prescriptions": ["Metformin"],
    },
    {
        "user_id": "u010",
        "name": "Omri Paz",
        "prescriptions": [],
    },
]

MEDICATIONS = [
    {
        "name": "Paracetamol",
        "active_ingredient": "Acetaminophen",
        "requires_prescription": False,

        # Structured label-style dosage instruction
        "dosage_instruction": {
            "dose_amount": "500 mg",
            "frequency": "every 4–6 hours",
            "max_daily": "Do not exceed 4,000 mg in 24 hours (label guidance).",
        },

        # Free-text label-style usage instructions
        "usage_instructions": "Take with water. Follow the package directions.",

        # Free-text label-style safety instructions
        "safety_instructions": (
            "Do not use if you are allergic to acetaminophen. "
            "Avoid combining with other products containing acetaminophen. "
            "Follow the label and consult a healthcare professional for personal medical advice."
        ),

        "stock": 42,
    },
    {
        "name": "Ibuprofen",
        "active_ingredient": "Ibuprofen",
        "requires_prescription": False,

        "dosage_instruction": {
            "dose_amount": "200–400 mg",
            "frequency": "every 6–8 hours",
            "max_daily": "Do not exceed 1,200 mg in 24 hours unless directed by a clinician (label guidance).",
        },

        "usage_instructions": "Take with food or milk to reduce stomach upset. Follow the package directions.",

        "safety_instructions": (
            "Do not use if you are allergic to ibuprofen/NSAIDs. "
            "May increase risk of stomach bleeding; follow label warnings. "
            "Consult a healthcare professional for pregnancy/medical conditions or personal medical advice."
        ),

        "stock": 18,
    },
    {
        "name": "Amoxicillin",
        "active_ingredient": "Amoxicillin",
        "requires_prescription": True,

        "dosage_instruction": {
            "dose_amount": "As prescribed",
            "frequency": "As prescribed",
            "max_daily": "As prescribed",
        },

        "usage_instructions": "Prescription-only. Take exactly as prescribed. Complete the full course if instructed.",

        "safety_instructions": (
            "Do not use if you have a penicillin allergy. "
            "Follow the prescriber’s directions and consult a healthcare professional for side effects or concerns."
        ),

        "stock": 10,
    },
    {
        "name": "Cetirizine",
        "active_ingredient": "Cetirizine",
        "requires_prescription": False,

        "dosage_instruction": {
            "dose_amount": "10 mg",
            "frequency": "once daily",
            "max_daily": "Do not exceed 10 mg in 24 hours (label guidance).",
        },

        "usage_instructions": "May be taken with or without food. Follow the package directions.",

        "safety_instructions": (
            "Do not use if you are allergic to cetirizine. "
            "May cause drowsiness in some people; follow label warnings. "
            "Consult a healthcare professional for pregnancy/breastfeeding or personal medical advice."
        ),

        "stock": 0,
    },
    {
        "name": "Metformin",
        "active_ingredient": "Metformin",
        "requires_prescription": True,

        "dosage_instruction": {
            "dose_amount": "As prescribed",
            "frequency": "As prescribed",
            "max_daily": "As prescribed",
        },

        "usage_instructions": "Prescription-only. Take with meals as prescribed to reduce stomach upset.",

        "safety_instructions": (
            "Do not use if you are allergic to metformin. "
            "Follow the prescriber’s directions and consult a healthcare professional for side effects or concerns."
        ),

        "stock": 6,
    },
]
