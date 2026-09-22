TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_overall_kpis",
            "description": (
                "Get overall manufacturing KPIs including "
                "production, efficiency, failures, downtime, "
                "quality inspections, defects, and quality score."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_machine_summary",
            "description": (
                "Get production, efficiency, failure count, "
                "and basic information for one machine or "
                "all machines."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "machine_id": {
                        "type": ["string", "null"],
                        "description": (
                            "Machine ID such as "
                            "MCH-001-01-01. Use null "
                            "to retrieve all machines."
                        ),
                    }
                },
                "required": ["machine_id"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_factory_summary",
            "description": (
                "Get production and average efficiency "
                "for each factory."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_machine_sensor_readings",
            "description": (
                "Get recent temperature, vibration, and "
                "pressure readings for a specific machine."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "machine_id": {
                        "type": "string",
                        "description": "Machine ID.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": (
                            "Maximum number of readings "
                            "to return."
                        ),
                        "default": 20,
                    },
                },
                "required": ["machine_id"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_machine_failures",
            "description": (
                "Get failure history for one machine "
                "or all machines."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "machine_id": {
                        "type": ["string", "null"],
                        "description": (
                            "Machine ID or null for "
                            "all machine failures."
                        ),
                    }
                },
                "required": ["machine_id"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_machine_downtime",
            "description": (
                "Get downtime history for one machine "
                "or total downtime statistics for all machines."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "machine_id": {
                        "type": ["string", "null"],
                        "description": (
                            "Machine ID or null for "
                            "all machines."
                        ),
                    }
                },
                "required": ["machine_id"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_quality_summary",
            "description": (
                "Get overall quality inspection count, "
                "defect count, and average quality score."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "search_manufacturing_knowledge",
            "description": (
                "Search the manufacturing knowledge base "
                "for maintenance, troubleshooting, production, "
                "or quality guidance."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Manufacturing question or "
                            "search query."
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": (
                            "Number of knowledge results "
                            "to return."
                        ),
                        "default": 3,
                    },
                },
                "required": ["query"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "predict_machine_failure",
            "description": (
                "Use the machine failure ML model to "
                "estimate failure probability from "
                "temperature, vibration, and pressure."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "temperature_celsius": {
                        "type": "number",
                    },
                    "vibration_mm_s": {
                        "type": "number",
                    },
                    "pressure_psi": {
                        "type": "number",
                    },
                },
                "required": [
                    "temperature_celsius",
                    "vibration_mm_s",
                    "pressure_psi",
                ],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "investigate_machine",
            "description": (
                "Perform a combined investigation of a "
                "specific machine using its summary, recent "
                "sensor readings, failure history, downtime "
                "history, and relevant manufacturing knowledge."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "machine_id": {
                        "type": "string",
                        "description": (
                            "Machine ID to investigate."
                        ),
                    }
                },
                "required": ["machine_id"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_machine_attention_signals",
            "description": (
                "Return objective evidence for all machines "
                "that can help identify machines deserving "
                "further investigation. Includes production, "
                "efficiency, failure count, recent failure, "
                "downtime, latest sensor readings, historical "
                "sensor averages, and deviations of the latest "
                "sensor readings from each machine's own average. "
                "This tool does not determine that a machine is "
                "unsafe or guaranteed to fail."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]