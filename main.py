import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from typing import Union, Dict, Any, List
import math

# --- Configuration ---
DATA_FILE = "workout_data.json"
PULLUP_EXERCISE_NAME = "Pull-Up Variation"

# Define 1RM input fields
INPUT_SHEET_1RM_CELLS = {
    "Back Squat": "B3",
    "Deadlift": "B4",
    "Incline DB Press": "B5",
    "Overhead Press (OHP)": "B6",
}

# Default 1RM values (pre-filled)
DEFAULT_1RM_VALUES = {
    "Back Squat": 275,     # lbs
    "Deadlift": 140,       # kg
    "Incline DB Press": 80, # lbs
    "Overhead Press (OHP)": 155, # lbs
    PULLUP_EXERCISE_NAME: 8 # reps
}

# --- Program Parameters ---
MAIN_LIFT_SETS = {1: "3-4", 2: "3-4", 3: "3-4", 4: "3-4", 5: "3-4", 6: "2-3"}
MAIN_LIFT_REPS = {1: "8-10", 2: "8-10", 3: "5-6", 4: "5-6", 5: "3-5", 6: "6-8"}
MAIN_LIFT_1RM_PERCENT_WK1 = 0.625
PERCENTAGE_INCREMENT_ON_SUCCESS = 0.04
DELOAD_1RM_PERCENTAGE = 0.55

ACCESSORY_SETS = 3
ACCESSORY_REPS = "10-15"
ACCESSORY_DELOAD_SETS = 2
ACCESSORY_DELOAD_REPS = 12

PULLUP_SETS = 3
PULLUP_REPS = "8-10"
PULLUP_REPS_PER_SET_THRESHOLD = 10
PULLUP_INCREMENT = 5
PULLUP_DELOAD_SETS = 2

WEIGHT_ROUNDING = 5

MAIN_LIFT_NAMES = ["Back Squat", "Deadlift", "Incline DB Press", "Overhead Press (OHP)"]

# --- Program Structure ---
program_structure: List[List[Dict[str, Any]]] = [
    # Week 1
    [
        {'day_name': "Monday (UA)", 'exercises': [
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter OHP day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Barbell Row", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Triceps Pushdown", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Tuesday (LA)", 'exercises': [
            {'name': "Back Squat", 'sets': 0, 'reps': 0, 'rest': "3-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift"},
            {'name': "Romanian Deadlift (RDL)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Leg Press", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hamstring Curl", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Plank", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]},
        {'day_name': "Thursday (UB)", 'exercises': [
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter Incline day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Lat Pulldown", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Dumbbell Bench Press", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Friday (LB)", 'exercises': [
            {'name': "Deadlift", 'sets': 0, 'reps': 0, 'rest': "4-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift (1 top set)"},
            {'name': "Front Squat", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Glute Bridge/Hip Thrust", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Standing Calf Raise", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hanging Leg Raise", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]}
    ],
    # Week 2
    [
        {'day_name': "Monday (UA)", 'exercises': [
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter OHP day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Barbell Row", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Triceps Pushdown", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Tuesday (LA)", 'exercises': [
            {'name': "Back Squat", 'sets': 0, 'reps': 0, 'rest': "3-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift"},
            {'name': "Romanian Deadlift (RDL)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Leg Press", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hamstring Curl", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Plank", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]},
        {'day_name': "Thursday (UB)", 'exercises': [
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter Incline day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Lat Pulldown", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Dumbbell Bench Press", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Friday (LB)", 'exercises': [
            {'name': "Deadlift", 'sets': 0, 'reps': 0, 'rest': "4-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift (1 top set)"},
            {'name': "Front Squat", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Glute Bridge/Hip Thrust", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Standing Calf Raise", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hanging Leg Raise", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]}
    ],
    # Week 3
    [
        {'day_name': "Monday (UA)", 'exercises': [
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter OHP day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Barbell Row", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Triceps Pushdown", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Tuesday (LA)", 'exercises': [
            {'name': "Back Squat", 'sets': 0, 'reps': 0, 'rest': "3-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift"},
            {'name': "Romanian Deadlift (RDL)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Leg Press", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hamstring Curl", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Weighted Plank", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]},
        {'day_name': "Thursday (UB)", 'exercises': [
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter Incline day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Lat Pulldown", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Dumbbell Bench Press", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Friday (LB)", 'exercises': [
            {'name': "Deadlift", 'sets': 0, 'reps': 0, 'rest': "4-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift (1 top set)"},
            {'name': "Front Squat", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Glute Bridge/Hip Thrust", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Standing Calf Raise", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Weighted Hanging Leg Raise", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]}
    ],
    # Week 4
    [
        {'day_name': "Monday (UA)", 'exercises': [
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter OHP day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Barbell Row", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Triceps Pushdown", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Tuesday (LA)", 'exercises': [
            {'name': "Back Squat", 'sets': 0, 'reps': 0, 'rest': "3-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift"},
            {'name': "Romanian Deadlift (RDL)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Leg Press", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hamstring Curl", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Weighted Plank", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]},
        {'day_name': "Thursday (UB)", 'exercises': [
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter Incline day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Lat Pulldown", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Dumbbell Bench Press", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Friday (LB)", 'exercises': [
            {'name': "Deadlift", 'sets': 0, 'reps': 0, 'rest': "4-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift (1 top set)"},
            {'name': "Front Squat", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Glute Bridge/Hip Thrust", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Standing Calf Raise", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Weighted Hanging Leg Raise", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]}
    ],
    # Week 5
    [
        {'day_name': "Monday (UA)", 'exercises': [
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter OHP day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Barbell Row", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Triceps Pushdown", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Tuesday (LA)", 'exercises': [
            {'name': "Back Squat", 'sets': 0, 'reps': 0, 'rest': "3-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift"},
            {'name': "Romanian Deadlift (RDL)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Leg Press", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hamstring Curl", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Weighted Plank", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]},
        {'day_name': "Thursday (UB)", 'exercises': [
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter Incline day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Lat Pulldown", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Dumbbell Bench Press", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Friday (LB)", 'exercises': [
            {'name': "Deadlift", 'sets': 0, 'reps': 0, 'rest': "4-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift (1 top set)"},
            {'name': "Front Squat", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Glute Bridge/Hip Thrust", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Standing Calf Raise", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Weighted Hanging Leg Raise", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]}
    ],
    # Week 6
    [
        {'day_name': "Monday (UA)", 'exercises': [
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter OHP day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Barbell Row", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Triceps Pushdown", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Tuesday (LA)", 'exercises': [
            {'name': "Back Squat", 'sets': 0, 'reps': 0, 'rest': "3-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift"},
            {'name': "Romanian Deadlift (RDL)", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Leg Press", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hamstring Curl", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Plank", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]},
        {'day_name': "Thursday (UB)", 'exercises': [
            {'name': "Overhead Press (OHP)", 'sets': 0, 'reps': 0, 'rest': "3-4", 'rpe': 0, 'type': 'main_upper', 'notes': "Main Lift"},
            {'name': "Incline DB Press", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Lighter Incline day"},
            {'name': PULLUP_EXERCISE_NAME, 'sets': 0, 'reps': 0, 'rest': "See T2", 'rpe': 0, 'type': 'pullup', 'notes': "Follow specific progression"},
            {'name': "Lat Pulldown", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Dumbbell Bench Press", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"}
        ]},
        {'day_name': "Friday (LB)", 'exercises': [
            {'name': "Deadlift", 'sets': 0, 'reps': 0, 'rest': "4-5", 'rpe': 0, 'type': 'main_lower', 'notes': "Main Lift (1 top set)"},
            {'name': "Front Squat", 'sets': 0, 'reps': 0, 'rest': "2-3", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Glute Bridge/Hip Thrust", 'sets': 0, 'reps': 0, 'rest': "1.5-2", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Standing Calf Raise", 'sets': 0, 'reps': 0, 'rest': "1-1.5", 'rpe': 0, 'type': 'accessory', 'notes': "Accessory"},
            {'name': "Hanging Leg Raise", 'sets': 0, 'reps': 0, 'rest': "1", 'rpe': 0, 'type': 'core', 'notes': "Core"}
        ]}
    ],
]

# Helper Functions
def round_to_nearest(value: float, base: float) -> float:
    if base <= 0: return value
    return round(value / base) * base

def get_target_reps(reps_value: Union[int, str]) -> int:
    if isinstance(reps_value, str) and '-' in reps_value:
        try: return int(reps_value.split('-')[0])
        except ValueError: return 0
    elif isinstance(reps_value, int): return reps_value
    elif isinstance(reps_value, str):
        try: return int(reps_value)
        except ValueError: return 0
    else: return 0

def get_numeric_sets(sets_value: Union[int, str]) -> int:
    if isinstance(sets_value, int): return sets_value
    elif isinstance(sets_value, str):
        try:
            if '-' in sets_value: return int(sets_value.split('-')[0])
            return int(sets_value)
        except ValueError: return 0
    return 0

def safe_float(value: Any, default: float = 0.0) -> float:
    try: return float(value) if value is not None else default
    except (ValueError, TypeError): return default

def safe_int(value: Any, default: int = 0) -> int:
    try: return int(float(value)) if value is not None else default
    except (ValueError, TypeError): return default

# Pull-Up Suggestion Logic
def get_pullup_suggestion_new(
    current_week_num: int,
    max_reps_input: int,
    prev_week_actual_weight: float = 0.0,
    prev_week_actual_reps: int = 0
) -> Dict[str, Any]:
    if current_week_num == 6:  # Deload Week
        deload_sets = PULLUP_DELOAD_SETS
        deload_reps, deload_weight, deload_notes = "50% Wk 5", 0, "Deload: ~50% of Week 5 reps/intensity"
        if prev_week_actual_weight > 0:
            if prev_week_actual_weight <= PULLUP_INCREMENT * 2:
                deload_weight = 0
                deload_notes = f"Deload: Bodyweight Focus (~50% Wk5 reps: {prev_week_actual_reps})"
            else:
                deload_weight = round_to_nearest(prev_week_actual_weight * DELOAD_1RM_PERCENTAGE, WEIGHT_ROUNDING)
                deload_notes = f"Deload: Use ~{DELOAD_1RM_PERCENTAGE*100:.0f}% of Week 5 weight ({prev_week_actual_weight} lbs)"
            deload_reps = 5
        elif prev_week_actual_reps > 0:
            reps_calc = max(1, prev_week_actual_reps // 2)
            reps_per_set = max(3, reps_calc // deload_sets) if deload_sets > 0 else 3
            deload_reps = f"~{reps_per_set}"
            deload_notes = f"Deload: ~50% of Week 5 total reps ({prev_week_actual_reps} reps)"
        else:
            deload_reps, deload_notes = "Light", "Deload: Light effort"
        return {"sets": deload_sets, "reps": deload_reps, "weight": deload_weight, "notes": deload_notes}

    target_sets, target_reps, base_notes = PULLUP_SETS, PULLUP_REPS, "Aim for reps."
    next_target_weight, progression_note = 0.0, ""

    if current_week_num > 1:
        estimated_reps_per_set = (prev_week_actual_reps / PULLUP_SETS) if PULLUP_SETS > 0 else 0
        if estimated_reps_per_set > PULLUP_REPS_PER_SET_THRESHOLD:
            next_target_weight = prev_week_actual_weight + PULLUP_INCREMENT
            progression_note = f"Add {PULLUP_INCREMENT} lbs (Avg >{PULLUP_REPS_PER_SET_THRESHOLD} reps/set Wk{current_week_num-1})"
        else:
            next_target_weight = prev_week_actual_weight
            progression_note = (f"Repeat {prev_week_actual_weight} lbs (Avg reps/set <= {PULLUP_REPS_PER_SET_THRESHOLD} Wk{current_week_num-1})"
                               if prev_week_actual_weight > 0 else f"Repeat BW (Avg reps/set <= {PULLUP_REPS_PER_SET_THRESHOLD} Wk{current_week_num-1})")
    elif max_reps_input >= 8:
        progression_note = "Start Bodyweight"

    if max_reps_input == 0:
        target_sets, target_reps, next_target_weight, base_notes, progression_note = "3-5", "3-5 Negatives", 0, "Focus on Negatives (3-5 sec lowering)", ""
    elif 1 <= max_reps_input <= 7:
        target_sets, target_reps, next_target_weight, base_notes, progression_note = "Multiple", "1-3", 0, f"Accumulate reps via low-rep sets (Max: {max_reps_input})", ""

    final_notes = f"{base_notes} {progression_note}".strip().replace(" .", ".")
    return {"sets": target_sets, "reps": target_reps, "weight": next_target_weight, "notes": final_notes}

# Kivy App
class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Enter Your 1RM Values", font_size=20))

        self.inputs = {}
        for exercise in INPUT_SHEET_1RM_CELLS.keys():
            row = BoxLayout(orientation='horizontal', spacing=10)
            row.add_widget(Label(text=exercise))
            input_field = TextInput(text=str(DEFAULT_1RM_VALUES.get(exercise, "")), multiline=False)
            self.inputs[exercise] = input_field
            row.add_widget(input_field)
            layout.add_widget(row)

        row = BoxLayout(orientation='horizontal', spacing=10)
        row.add_widget(Label(text=PULLUP_EXERCISE_NAME))
        pullup_input = TextInput(text=str(DEFAULT_1RM_VALUES.get(PULLUP_EXERCISE_NAME, "")), multiline=False)
        self.inputs[PULLUP_EXERCISE_NAME] = pullup_input
        row.add_widget(pullup_input)
        layout.add_widget(row)

        save_button = Button(text="Save and Continue", size_hint=(1, 0.2))
        save_button.bind(on_press=self.save_inputs)
        layout.add_widget(save_button)

        self.add_widget(layout)

    def save_inputs(self, instance):
        data = {"1RM": {}, "logs": {}, "new_1RM": {}}
        for exercise, input_field in self.inputs.items():
            try:
                value = float(input_field.text)
                data["1RM"][exercise] = value
            except ValueError:
                data["1RM"][exercise] = DEFAULT_1RM_VALUES.get(exercise, 0)
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
        self.manager.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Strength Training Tracker", font_size=20))

        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.2))
        input_button = Button(text="Edit 1RMs")
        input_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'input'))
        button_layout.add_widget(input_button)
        new_1rm_button = Button(text="New 1RM Calc")
        new_1rm_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'new_1rm'))
        button_layout.add_widget(new_1rm_button)
        layout.add_widget(button_layout)

        self.week_buttons = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.8))
        scroll = ScrollView()
        for week in range(1, 7):
            btn = Button(text=f"Week {week}", size_hint_y=None, height=50)
            btn.bind(on_press=lambda instance, w=week: self.show_week(w))
            self.week_buttons.add_widget(btn)
        scroll.add_widget(self.week_buttons)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def show_week(self, week_num):
        self.manager.get_screen('week').week_num = week_num
        self.manager.current = 'week'

class WeekScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.week_num = 1
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(self.layout)

    def on_enter(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text=f"Week {self.week_num}", font_size=20))
        back_button = Button(text="Back", size_hint=(1, 0.1))
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        self.layout.add_widget(back_button)

        scroll = ScrollView()
        content = GridLayout(cols=1, spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        week_data = program_structure[self.week_num-1]
        for day_idx, day_data in enumerate(week_data):
            day_label = Label(text=day_data['day_name'], size_hint_y=None, height=40, font_size=18)
            content.add_widget(day_label)
            for ex_idx, ex_data in enumerate(day_data['exercises']):
                ex_name = ex_data['name']
                ex_type = ex_data['type']
                sets, reps, rest, rpe = ex_data['sets'], ex_data['reps'], ex_data['rest'], ex_data['rpe']
                notes = ex_data['notes']

                target_weight = 0
                if ex_type == 'main_lift':
                    one_rm = data["1RM"].get(ex_name, DEFAULT_1RM_VALUES.get(ex_name, 0))
                    if self.week_num == 1:
                        target_weight = round_to_nearest(one_rm * MAIN_LIFT_1RM_PERCENT_WK1, WEIGHT_ROUNDING)
                        notes += f" (Wk1 Target: {MAIN_LIFT_1RM_PERCENT_WK1*100:.1f}% 1RM)"
                    elif 1 < self.week_num < 6:
                        prev_week = self.week_num - 1
                        log_key = f"Week{prev_week}_Day{day_idx}_Ex{ex_idx}"
                        prev_log = data["logs"].get(log_key, {})
                        prev_actual_wt = prev_log.get("actual_weight", 0)
                        prev_actual_reps = prev_log.get("actual_reps", 0)
                        if not prev_actual_wt:
                            prev_actual_wt = one_rm * MAIN_LIFT_1RM_PERCENT_WK1
                        prev_target_total_reps = get_numeric_sets(program_structure[prev_week-1][day_idx]['exercises'][ex_idx]['sets']) * get_target_reps(program_structure[prev_week-1][day_idx]['exercises'][ex_idx]['reps'])
                        if prev_actual_reps >= prev_target_total_reps and prev_target_total_reps > 0:
                            target_weight = round_to_nearest(prev_actual_wt * (1 + PERCENTAGE_INCREMENT_ON_SUCCESS), WEIGHT_ROUNDING)
                            notes += f" (Target based on Wk{prev_week} Actuals. Increase by {PERCENTAGE_INCREMENT_ON_SUCCESS*100:.0f}% if reps >= {prev_target_total_reps})"
                        else:
                            target_weight = round_to_nearest(prev_actual_wt, WEIGHT_ROUNDING)
                            notes += f" (Target based on Wk{prev_week} Actuals)"
                    elif self.week_num == 6:
                        target_weight = round_to_nearest(one_rm * DELOAD_1RM_PERCENTAGE, WEIGHT_ROUNDING)
                        notes += f" (Deload Target: {DELOAD_1RM_PERCENTAGE*100:.0f}% 1RM)"
                elif ex_type == 'pullup':
                    max_reps = data["1RM"].get(PULLUP_EXERCISE_NAME, DEFAULT_1RM_VALUES.get(PULLUP_EXERCISE_NAME, 0))
                    prev_week = self.week_num - 1 if self.week_num > 1 else 1
                    log_key = f"Week{prev_week}_Day{day_idx}_Ex{ex_idx}"
                    prev_log = data["logs"].get(log_key, {})
                    prev_wt = prev_log.get("actual_weight", 0)
                    prev_reps = prev_log.get("actual_reps", 0)
                    suggestion = get_pullup_suggestion_new(self.week_num, max_reps, prev_wt, prev_reps)
                    sets, reps, target_weight, notes = suggestion['sets'], suggestion['reps'], suggestion['weight'], suggestion['notes']
                elif ex_type in ['accessory', 'core']:
                    target_weight = "User Choice"
                    notes += f" (Increase wt ~2-3% when hitting {ACCESSORY_REPS.split('-')[-1]} reps)" if self.week_num < 6 else " (Deload)"

                log_key = f"Week{self.week_num}_Day{day_idx}_Ex{ex_idx}"
                log_data = data["logs"].get(log_key, {"actual_weight": 0, "actual_reps": 0})
                actual_weight = log_data["actual_weight"]
                actual_reps = log_data["actual_reps"]
                if self.week_num == 1 and ex_type in ['main_lift', 'pullup']:
                    actual_weight = target_weight
                    notes += " (Actual Wt pre-filled w/ Target)"

                ex_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=150, spacing=5)
                ex_layout.add_widget(Label(text=f"{ex_name}: {sets} sets, {reps} reps, Rest: {rest}, RPE: {rpe}", size_hint_y=None, height=30))
                ex_layout.add_widget(Label(text=f"Target Weight: {target_weight}", size_hint_y=None, height=30))
                actual_row = BoxLayout(orientation='horizontal', spacing=5)
                actual_row.add_widget(Label(text="Actual Wt:", size_hint_x=0.3))
                wt_input = TextInput(text=str(actual_weight), multiline=False, size_hint_x=0.3)
                actual_row.add_widget(wt_input)
                actual_row.add_widget(Label(text="Actual Reps:", size_hint_x=0.2))
                reps_input = TextInput(text=str(actual_reps), multiline=False, size_hint_x=0.2)
                actual_row.add_widget(reps_input)
                save_btn = Button(text="Save", size_hint_x=0.2)
                save_btn.bind(on_press=lambda instance, wk=self.week_num, d=day_idx, e=ex_idx, wt=wt_input, r=reps_input: self.save_log(wk, d, e, wt.text, r.text))
                actual_row.add_widget(save_btn)
                ex_layout.add_widget(actual_row)
                ex_layout.add_widget(Label(text=f"Notes: {notes}", size_hint_y=None, height=30))
                content.add_widget(ex_layout)

        scroll.add_widget(content)
        self.layout.add_widget(scroll)

    def save_log(self, week_num, day_idx, ex_idx, actual_weight, actual_reps):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        log_key = f"Week{week_num}_Day{day_idx}_Ex{ex_idx}"
        data["logs"][log_key] = {
            "actual_weight": safe_float(actual_weight, 0.0),
            "actual_reps": safe_int(actual_reps, 0)
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
        self.on_enter()  # Refresh the screen

class New1RMScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="New 1RM Calculation (After Week 5)", font_size=20))
        back_button = Button(text="Back", size_hint=(1, 0.1))
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_button)

        scroll = ScrollView()
        content = GridLayout(cols=1, spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        exercises_for_1rm = ["Back Squat", "Deadlift", "Incline DB Press", "Overhead Press (OHP)", PULLUP_EXERCISE_NAME]
        self.inputs = {}
        for ex_name in exercises_for_1rm:
            ex_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=120, spacing=5)
            ex_layout.add_widget(Label(text=ex_name, size_hint_y=None, height=30))
            row1 = BoxLayout(orientation='horizontal', spacing=5)
            row1.add_widget(Label(text="Wk 5 Weight:", size_hint_x=0.4))
            weight_input = TextInput(multiline=False, size_hint_x=0.6)
            row1.add_widget(weight_input)
            ex_layout.add_widget(row1)
            row2 = BoxLayout(orientation='horizontal', spacing=5)
            row2.add_widget(Label(text="Wk 5 Reps:", size_hint_x=0.4))
            reps_input = TextInput(multiline=False, size_hint_x=0.6)
            row2.add_widget(reps_input)
            ex_layout.add_widget(row2)
            result_label = Label(text="New 1RM: N/A", size_hint_y=None, height=30)
            ex_layout.add_widget(result_label)
            self.inputs[ex_name] = (weight_input, reps_input, result_label)
            content.add_widget(ex_layout)

        calc_button = Button(text="Calculate New 1RMs", size_hint_y=None, height=40)
        calc_button.bind(on_press=self.calculate_new_1rm)
        content.add_widget(calc_button)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def calculate_new_1rm(self, instance):
        for ex_name, (weight_input, reps_input, result_label) in self.inputs.items():
            try:
                weight = float(weight_input.text)
                reps = int(reps_input.text)
                if ex_name != PULLUP_EXERCISE_NAME:
                    new_1rm = round_to_nearest(weight * (1 + reps / 30), WEIGHT_ROUNDING)
                    result_label.text = f"New 1RM: {new_1rm}"
                else:
                    result_label.text = "New 1RM: Calculate manually"
            except ValueError:
                result_label.text = "New 1RM: Invalid input"

class StrengthApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(InputScreen(name='input'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(WeekScreen(name='week'))
        sm.add_widget(New1RMScreen(name='new_1rm'))
        return sm

    def on_start(self):
        if not os.path.exists(DATA_FILE):
            data = {"1RM": DEFAULT_1RM_VALUES, "logs": {}, "new_1RM": {}}
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f)

if __name__ == '__main__':
    StrengthApp().run()