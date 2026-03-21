"""
generate_oap.py — Generator for OAP-Bench (Override and Plan)
Executive Functions Track — Google DeepMind AGI Hackathon 2026

Produces: data/executive_functions/oap_bench.jsonl  (45 items, 15 per subtask)

Subtasks:
  rule_reversal      — inhibitory control (suppress prepotent response)
  task_switching     — cognitive flexibility (detect and adapt to rule change)
  loaded_wm          — working memory under distractor load

Run: python src/generate_oap.py
"""

import json
import random
from pathlib import Path

SEED = 42
random.seed(SEED)


# ---------------------------------------------------------------------------
# Subtask 1: Rule Reversal (15 items)
#
# A high-frequency, well-practiced mapping is explicitly inverted.
# The prepotent response is the un-inverted answer.
# Correct performance requires suppressing that response.
#
# Paradigm basis: Stroop (1935), reverse Stroop variants
# ---------------------------------------------------------------------------

REVERSAL_SCHEMAS = [
    {
        "rule": "For this task, when asked for the OPPOSITE of a word, give its SYNONYM instead.",
        "items": [
            {"prompt": "What is the opposite of LARGE?",
             "correct": "BIG", "prepotent": "SMALL",
             "choices": ["BIG", "SMALL", "ROUND", "DARK"]},
            {"prompt": "What is the opposite of FAST?",
             "correct": "QUICK", "prepotent": "SLOW",
             "choices": ["QUICK", "SLOW", "BRIGHT", "HEAVY"]},
            {"prompt": "What is the opposite of HOT?",
             "correct": "WARM", "prepotent": "COLD",
             "choices": ["WARM", "COLD", "DRY", "LOUD"]},
            {"prompt": "What is the opposite of HAPPY?",
             "correct": "JOYFUL", "prepotent": "SAD",
             "choices": ["JOYFUL", "SAD", "TIRED", "QUIET"]},
            {"prompt": "What is the opposite of STRONG?",
             "correct": "POWERFUL", "prepotent": "WEAK",
             "choices": ["POWERFUL", "WEAK", "SOFT", "EMPTY"]},
        ]
    },
    {
        "rule": "For this task, when asked which number is GREATER, choose the LESSER instead.",
        "items": [
            {"prompt": "Which is greater: 7 or 3?",
             "correct": "3", "prepotent": "7",
             "choices": ["7", "3", "5", "10"]},
            {"prompt": "Which is greater: 15 or 42?",
             "correct": "15", "prepotent": "42",
             "choices": ["42", "15", "28", "50"]},
            {"prompt": "Which is greater: 100 or 99?",
             "correct": "99", "prepotent": "100",
             "choices": ["100", "99", "101", "98"]},
            {"prompt": "Which is greater: 0.5 or 0.8?",
             "correct": "0.5", "prepotent": "0.8",
             "choices": ["0.8", "0.5", "1.0", "0.3"]},
            {"prompt": "Which is greater: 6 or 6000?",
             "correct": "6", "prepotent": "6000",
             "choices": ["6000", "6", "600", "60"]},
        ]
    },
    {
        "rule": (
            "For this task, when asked to identify the COLOR of the text, "
            "report the WORD instead — and when asked to report the WORD, "
            "report the COLOR instead."
        ),
        "items": [
            {"prompt": "The word RED is written in blue ink. What color is the text?",
             "correct": "RED", "prepotent": "BLUE",
             "choices": ["RED", "BLUE", "GREEN", "YELLOW"]},
            {"prompt": "The word GREEN is written in red ink. What is the word?",
             "correct": "RED", "prepotent": "GREEN",
             "choices": ["RED", "GREEN", "BLUE", "BLACK"]},
            {"prompt": "The word BLUE is written in yellow ink. What color is the text?",
             "correct": "BLUE", "prepotent": "YELLOW",
             "choices": ["BLUE", "YELLOW", "RED", "GREEN"]},
            {"prompt": "The word BLACK is written in green ink. What is the word?",
             "correct": "GREEN", "prepotent": "BLACK",
             "choices": ["GREEN", "BLACK", "BLUE", "RED"]},
            {"prompt": "The word YELLOW is written in black ink. What color is the text?",
             "correct": "YELLOW", "prepotent": "BLACK",
             "choices": ["YELLOW", "BLACK", "RED", "GREEN"]},
        ]
    },
]


def make_rule_reversal_items() -> list[dict]:
    items = []
    item_num = 0
    for schema in REVERSAL_SCHEMAS:
        rule = schema["rule"]
        for q in schema["items"]:
            item_num += 1
            choices = q["choices"][:]
            random.shuffle(choices)
            answer_letter = chr(65 + choices.index(q["correct"]))
            context = (
                f"IMPORTANT INSTRUCTION — read carefully before answering:\n\n"
                f"{rule}\n\n"
                f"This rule overrides your normal response. "
                f"Apply it to the following question."
            )
            items.append({
                "id": f"oap_rr_{item_num:03d}",
                "track": "executive_functions",
                "subtask": "rule_reversal",
                "difficulty": 2,
                "cognitive_ability": "inhibitory_control",
                "context": context,
                "question": q["prompt"],
                "choices": choices,
                "answer": answer_letter,
                "prepotent_response": q["prepotent"],
                "human_baseline_expected": 0.71,
                "contamination_safe": True,
                "seed": SEED,
                "notes": (
                    "Prepotent response is the un-inverted answer. "
                    "Correct performance requires active suppression."
                ),
            })
    return items


# ---------------------------------------------------------------------------
# Subtask 2: Task Switching (15 items)
#
# A sequence of items is presented under Rule A.
# A switch cue introduces Rule B mid-sequence.
# Model must detect the switch and abandon Rule A without perseveration.
#
# Paradigm basis: Wisconsin Card Sorting Test (WCST), Jersild (1927)
# ---------------------------------------------------------------------------

SWITCH_SEQUENCES = [
    {
        "rule_a": "Classify each number as ODD or EVEN.",
        "rule_b": "Classify each number as GREATER THAN 10 or LESS THAN OR EQUAL TO 10.",
        "switch_cue": "--- RULE CHANGE: Now classify by size, not parity. ---",
        "pre_switch": [
            {"q": "7", "a_correct": "ODD",   "b_correct": "LESS THAN OR EQUAL TO 10",
             "choices": ["ODD", "EVEN", "GREATER THAN 10", "LESS THAN OR EQUAL TO 10"]},
            {"q": "4", "a_correct": "EVEN",  "b_correct": "LESS THAN OR EQUAL TO 10",
             "choices": ["ODD", "EVEN", "GREATER THAN 10", "LESS THAN OR EQUAL TO 10"]},
            {"q": "11","a_correct": "ODD",   "b_correct": "GREATER THAN 10",
             "choices": ["ODD", "EVEN", "GREATER THAN 10", "LESS THAN OR EQUAL TO 10"]},
        ],
        "post_switch": [
            {"q": "8",  "correct": "LESS THAN OR EQUAL TO 10", "persev": "EVEN",
             "choices": ["ODD", "EVEN", "GREATER THAN 10", "LESS THAN OR EQUAL TO 10"]},
            {"q": "13", "correct": "GREATER THAN 10",          "persev": "ODD",
             "choices": ["ODD", "EVEN", "GREATER THAN 10", "LESS THAN OR EQUAL TO 10"]},
            {"q": "2",  "correct": "LESS THAN OR EQUAL TO 10", "persev": "EVEN",
             "choices": ["ODD", "EVEN", "GREATER THAN 10", "LESS THAN OR EQUAL TO 10"]},
            {"q": "25", "correct": "GREATER THAN 10",          "persev": "ODD",
             "choices": ["ODD", "EVEN", "GREATER THAN 10", "LESS THAN OR EQUAL TO 10"]},
            {"q": "6",  "correct": "LESS THAN OR EQUAL TO 10", "persev": "EVEN",
             "choices": ["ODD", "EVEN", "GREATER THAN 10", "LESS THAN OR EQUAL TO 10"]},
        ],
    },
    {
        "rule_a": "For each word, respond with the FIRST letter of the word.",
        "rule_b": "For each word, respond with the LAST letter of the word.",
        "switch_cue": "--- RULE CHANGE: Now report the final letter, not the first. ---",
        "pre_switch": [
            {"q": "BRIDGE", "a_correct": "B", "b_correct": "E",
             "choices": ["B", "E", "R", "G"]},
            {"q": "CLOCK",  "a_correct": "C", "b_correct": "K",
             "choices": ["C", "K", "L", "O"]},
            {"q": "STORM",  "a_correct": "S", "b_correct": "M",
             "choices": ["S", "M", "T", "O"]},
        ],
        "post_switch": [
            {"q": "FLOWER", "correct": "R", "persev": "F",
             "choices": ["F", "R", "L", "O"]},
            {"q": "GRANT",  "correct": "T", "persev": "G",
             "choices": ["G", "T", "R", "A"]},
            {"q": "BLANK",  "correct": "K", "persev": "B",
             "choices": ["B", "K", "L", "A"]},
            {"q": "CRISP",  "correct": "P", "persev": "C",
             "choices": ["C", "P", "R", "I"]},
            {"q": "DRAFT",  "correct": "T", "persev": "D",
             "choices": ["D", "T", "R", "A"]},
        ],
    },
    {
        "rule_a": "Sort the following item into: ANIMAL, PLANT, or OBJECT.",
        "rule_b": "Sort the following item into: LIVING or NON-LIVING.",
        "switch_cue": "--- RULE CHANGE: Now classify by living status only. ---",
        "pre_switch": [
            {"q": "FERN",     "a_correct": "PLANT",  "b_correct": "LIVING",
             "choices": ["ANIMAL", "PLANT", "OBJECT", "LIVING", "NON-LIVING"]},
            {"q": "HAMMER",   "a_correct": "OBJECT", "b_correct": "NON-LIVING",
             "choices": ["ANIMAL", "PLANT", "OBJECT", "LIVING", "NON-LIVING"]},
            {"q": "SPARROW",  "a_correct": "ANIMAL", "b_correct": "LIVING",
             "choices": ["ANIMAL", "PLANT", "OBJECT", "LIVING", "NON-LIVING"]},
        ],
        "post_switch": [
            {"q": "MUSHROOM", "correct": "LIVING",     "persev": "PLANT",
             "choices": ["ANIMAL", "PLANT", "OBJECT", "LIVING", "NON-LIVING"]},
            {"q": "CANDLE",   "correct": "NON-LIVING", "persev": "OBJECT",
             "choices": ["ANIMAL", "PLANT", "OBJECT", "LIVING", "NON-LIVING"]},
            {"q": "BEETLE",   "correct": "LIVING",     "persev": "ANIMAL",
             "choices": ["ANIMAL", "PLANT", "OBJECT", "LIVING", "NON-LIVING"]},
            {"q": "STONE",    "correct": "NON-LIVING", "persev": "OBJECT",
             "choices": ["ANIMAL", "PLANT", "OBJECT", "LIVING", "NON-LIVING"]},
            {"q": "MOSS",     "correct": "LIVING",     "persev": "PLANT",
             "choices": ["ANIMAL", "PLANT", "OBJECT", "LIVING", "NON-LIVING"]},
        ],
    },
]


def make_task_switching_items() -> list[dict]:
    items = []
    item_num = 0
    for seq in SWITCH_SEQUENCES:
        # Build the context: show pre-switch items as worked examples
        pre_lines = []
        for ex in seq["pre_switch"]:
            pre_lines.append(f"  Item: {ex['q']}  →  {ex['a_correct']}")

        for post_item in seq["post_switch"]:
            item_num += 1
            choices = post_item["choices"][:]
            random.shuffle(choices)
            answer_letter = chr(65 + choices.index(post_item["correct"]))

            context = (
                f"RULE A (active at start): {seq['rule_a']}\n\n"
                f"Examples under Rule A:\n"
                + "\n".join(pre_lines)
                + f"\n\n{seq['switch_cue']}\n\n"
                f"RULE B (now active): {seq['rule_b']}\n\n"
                f"Apply Rule B to the following item."
            )

            items.append({
                "id": f"oap_ts_{item_num:03d}",
                "track": "executive_functions",
                "subtask": "task_switching",
                "difficulty": 2,
                "cognitive_ability": "cognitive_flexibility",
                "context": context,
                "question": f"Item: {post_item['q']}",
                "choices": choices,
                "answer": answer_letter,
                "prepotent_response": post_item["persev"],
                "human_baseline_expected": 0.68,
                "contamination_safe": True,
                "seed": SEED,
                "notes": (
                    "Perseverative response is the Rule A answer. "
                    "Correct performance requires detecting the switch cue and abandoning Rule A."
                ),
            })
    return items


# ---------------------------------------------------------------------------
# Subtask 3: Loaded Working Memory (15 items)
#
# Model is given a tracking goal, then presented with a passage containing
# both goal-relevant and highly salient distractor content.
# Question tests goal tracking, not distractor recall.
#
# Paradigm basis: n-back, dual-task, Baddeley working memory model
# ---------------------------------------------------------------------------

WM_ITEMS = [
    {
        "goal": "Count the total number of times the word 'blue' appears in the passage below.",
        "passage": (
            "The captain gave the order to raise the red flag. Crew members scrambled "
            "across the deck as storm clouds gathered. A blue lantern swung from the mast. "
            "The first mate shouted about the cargo — three crates of silk, five barrels "
            "of grain, and a locked chest no one had seen opened. Lightning struck the water "
            "to the east. A second blue flash lit the sky, followed by a blue streak along "
            "the horizon. The ship lurched. The captain seized a rope and pulled hard. "
            "By morning, the red dawn revealed calm seas and a distant coast."
        ),
        "correct": "3",
        "distractor_answer": "The captain, the first mate, and the crew",
        "choices": ["2", "3", "4", "5"],
        "human_baseline": 0.72,
    },
    {
        "goal": "Track how many different cities are mentioned in the passage below.",
        "passage": (
            "The conference opened in Geneva with delegates from forty nations. "
            "A side session in Zurich addressed climate funding, while the main "
            "resolution was drafted simultaneously in the Geneva committee room. "
            "Protests erupted outside the building — police estimated two thousand "
            "participants carrying signs in six languages. Late in the afternoon, "
            "news arrived that a parallel summit in Brussels had reached its own "
            "agreement, potentially superseding the Geneva draft. Delegates from "
            "Nairobi and Jakarta called for an emergency plenary. The session "
            "closed without consensus. Most delegates flew home via Frankfurt."
        ),
        "correct": "5",
        "distractor_answer": "Climate funding and the Geneva resolution",
        "choices": ["3", "4", "5", "6"],
        "human_baseline": 0.69,
    },
    {
        "goal": "Count the number of times a number (digit or written) appears in the passage.",
        "passage": (
            "Maria had worked at the lab for eleven years when the accident occurred. "
            "It was 3 a.m. on a Tuesday. A beaker containing 500 milliliters of solvent "
            "had been left too close to the heating element. The night shift had two "
            "technicians on duty. Neither noticed the temperature gauge reading 94 degrees. "
            "By the time the alarm sounded, the room was already filling with smoke. "
            "The fire department arrived in seven minutes. No one was injured. "
            "The lab sustained roughly $40,000 in damages."
        ),
        "correct": "8",
        "distractor_answer": "Maria and the two technicians",
        "choices": ["6", "7", "8", "9"],
        "human_baseline": 0.58,
    },
    {
        "goal": "Track how many distinct animals are mentioned in the passage below.",
        "passage": (
            "The wildlife survey covered three river basins over six weeks. Observers "
            "logged fourteen species of bird, including the kingfisher and two types of "
            "heron. Mammal sightings were rarer: a single otter at the northern bend, "
            "evidence of beaver activity near the dam, and one confirmed wolf track in "
            "the eastern basin. Invertebrate counts were not included in the primary "
            "dataset. The team's most surprising find was a grass snake at an elevation "
            "previously considered too high for the species. Funding for a follow-up "
            "survey has been requested."
        ),
        "correct": "6",
        "distractor_answer": "Fourteen species of bird across three river basins",
        "choices": ["4", "5", "6", "7"],
        "human_baseline": 0.64,
    },
    {
        "goal": (
            "Your task: remember the FIRST word of the passage. "
            "Answer only with that word at the end."
        ),
        "passage": (
            "Rainfall totals for the month exceeded historical averages by nearly "
            "thirty percent. The reservoir, which had been at fifty-two percent "
            "capacity in April, rose to eighty-one percent by the end of May. "
            "Engineers revised their flood risk projections upward. Three downstream "
            "communities received precautionary advisories. Local officials held a "
            "press conference on Thursday afternoon to address public concerns. "
            "The weather service forecast continued precipitation through the weekend. "
            "Sandbag distribution began Friday morning at six locations."
        ),
        "correct": "RAINFALL",
        "distractor_answer": "RESERVOIR",
        "choices": ["RAINFALL", "RESERVOIR", "ENGINEERS", "FLOOD"],
        "human_baseline": 0.81,
    },
    {
        "goal": "Count the number of times the word 'the' appears in the first sentence only.",
        "passage": (
            "The discovery of the artifact beneath the old market square stunned the "
            "archaeological team. Dating tests placed its origin at roughly 800 BCE. "
            "The object — a small bronze disc engraved with symbols — did not match "
            "any known regional style. Experts from four institutions were flown in. "
            "The debate over its origin continued for months. Some argued it was "
            "trade goods from a distant culture; others believed it was locally made "
            "using imported techniques. The disc is now held in a climate-controlled "
            "storage facility pending further analysis."
        ),
        "correct": "4",
        "distractor_answer": "The disc is held in a climate-controlled storage facility",
        "choices": ["3", "4", "5", "6"],
        "human_baseline": 0.66,
    },
    {
        "goal": "Track the running total of all explicit dollar amounts mentioned in the passage.",
        "passage": (
            "The city council approved a $2 million allocation for road repairs. "
            "A separate line item of $750,000 was earmarked for park maintenance. "
            "Council member Tran proposed adding $500,000 for library hours, but "
            "the motion failed by a narrow vote. The approved budget also included "
            "a contingency reserve of $250,000. Critics argued the total was "
            "insufficient given that preliminary engineering estimates had placed "
            "road repair costs alone at $3.1 million. The mayor signed the budget "
            "without amendment."
        ),
        "correct": "$3,500,000",
        "distractor_answer": "$3,100,000",
        "choices": ["$3,000,000", "$3,500,000", "$3,750,000", "$2,750,000"],
        "human_baseline": 0.55,
    },
    {
        "goal": "Count how many questions are asked (sentences ending in '?') in the passage.",
        "passage": (
            "The detective looked at the evidence again. Who had been in the room? "
            "The lock showed no signs of forced entry. Had someone used a key? "
            "She examined the window — latched from the inside. The timeline was "
            "impossible. Or was it? A second officer entered. 'Anything new?' "
            "she asked. 'Not yet,' the detective replied. She picked up the logbook. "
            "Every entry was in the same handwriting. Was that significant? "
            "She wrote her own name in the margin and stepped outside."
        ),
        "correct": "5",
        "distractor_answer": "The detective found no signs of forced entry",
        "choices": ["3", "4", "5", "6"],
        "human_baseline": 0.61,
    },
    {
        "goal": "Remember the third word in the passage and report it at the end.",
        "passage": (
            "After the merger, restructuring began immediately. The executive team "
            "announced layoffs affecting approximately twelve percent of the workforce. "
            "Offices in four cities were consolidated into two regional hubs. "
            "Employees received a sixty-day notice. Union representatives called "
            "for an emergency meeting. The company's stock rose three percent on "
            "the news, a reaction that angered laid-off workers. The CEO issued "
            "a statement citing market pressures and long-term strategic goals."
        ),
        "correct": "MERGER",
        "distractor_answer": "RESTRUCTURING",
        "choices": ["AFTER", "MERGER", "RESTRUCTURING", "IMMEDIATELY"],
        "human_baseline": 0.74,
    },
    {
        "goal": "Count how many people (named or referred to by role) are mentioned in the passage.",
        "passage": (
            "Judge Harlow called the courtroom to order at nine o'clock. "
            "The prosecutor outlined the charges in a twenty-minute opening statement. "
            "Defense counsel objected twice, both times overruled. The first witness, "
            "a forensic accountant, testified for three hours. The defendant sat "
            "motionless throughout. During the afternoon recess, a reporter outside "
            "interviewed a juror who had been dismissed earlier in the week. "
            "The bailiff asked everyone to return. Court adjourned at five."
        ),
        "correct": "7",
        "distractor_answer": "Three hours",
        "choices": ["5", "6", "7", "8"],
        "human_baseline": 0.59,
    },
    {
        "goal": "Track how many times a color word appears anywhere in the passage.",
        "passage": (
            "The autumn market stretched along the canal. Vendors in green aprons "
            "arranged their stalls before dawn. A woman in a red coat purchased "
            "three jars of honey. By midmorning the crowd had thickened. A blue "
            "delivery van blocked one end of the street for nearly an hour. "
            "Children pointed at the yellow and orange kites someone had strung "
            "between the lamp posts. A green flag at the far end marked the "
            "food stalls. By noon the red coat woman was gone."
        ),
        "correct": "7",
        "distractor_answer": "The market was held along a canal",
        "choices": ["5", "6", "7", "8"],
        "human_baseline": 0.60,
    },
    {
        "goal": "Count how many times a day of the week is mentioned in the passage.",
        "passage": (
            "The schedule was revised twice. Monday's session was moved to Wednesday "
            "after the venue flooded over the weekend. Saturday's keynote remained "
            "unchanged. Several attendees had already booked travel for Tuesday, "
            "creating a conflict. The organizing committee met Thursday evening and "
            "agreed to send updated invitations by Friday morning. No one mentioned "
            "Sunday."
        ),
        "correct": "7",
        "distractor_answer": "The venue flooded over the weekend",
        "choices": ["5", "6", "7", "8"],
        "human_baseline": 0.67,
    },
    {
        "goal": "Track the total number of items listed across all lists in the passage.",
        "passage": (
            "The packing list included: a sleeping bag, two changes of clothes, "
            "a water filter, and sunscreen. The supply cache at the midpoint "
            "contained: energy bars, a first aid kit, and a spare tarp. "
            "At the summit, the team logged: wind speed, temperature, "
            "barometric pressure, and visibility. No other measurements were taken."
        ),
        "correct": "10",
        "distractor_answer": "Three lists were present in the passage",
        "choices": ["8", "9", "10", "11"],
        "human_baseline": 0.62,
    },
    {
        "goal": "Remember the last word of the passage and report it.",
        "passage": (
            "The treaty was signed on a cold December morning. Dignitaries from "
            "eleven nations gathered in the main hall. Cameras recorded every "
            "handshake. Outside, a small protest was underway — thirty people "
            "holding signs calling the agreement insufficient. Inside, champagne "
            "was poured. The lead negotiator, visibly exhausted after months of "
            "talks, gave a brief statement to the press. The cameras switched off. "
            "The hall emptied. Someone left an umbrella."
        ),
        "correct": "UMBRELLA",
        "distractor_answer": "CAMERAS",
        "choices": ["CAMERAS", "STATEMENT", "HALL", "UMBRELLA"],
        "human_baseline": 0.78,
    },
    {
        "goal": "Count how many times the word 'and' appears in the passage.",
        "passage": (
            "The team arrived early and set up the equipment. Rain delayed the start "
            "and several participants left. By noon the clouds had cleared and the "
            "trials resumed. The results were logged and sent to the central database. "
            "Analysts reviewed the data and filed a preliminary report. The lead "
            "scientist and her assistant presented findings at the evening briefing."
        ),
        "correct": "6",
        "distractor_answer": "The team filed a preliminary report",
        "choices": ["4", "5", "6", "7"],
        "human_baseline": 0.63,
    },
]


def make_loaded_wm_items() -> list[dict]:
    items = []
    for i, item in enumerate(WM_ITEMS):
        choices = item["choices"][:]
        random.shuffle(choices)
        answer_letter = chr(65 + choices.index(item["correct"]))
        context = (
            f"TRACKING GOAL — hold this in mind throughout:\n"
            f"{item['goal']}\n\n"
            f"--- Passage ---\n{item['passage']}\n\n"
            f"Answer the tracking goal, not any other question about the passage."
        )
        items.append({
            "id": f"oap_wm_{i+1:03d}",
            "track": "executive_functions",
            "subtask": "loaded_working_memory",
            "difficulty": 3,
            "cognitive_ability": "working_memory",
            "context": context,
            "question": item["goal"].split(".")[0].replace("Your task: remember", "What was") + "?",
            "choices": choices,
            "answer": answer_letter,
            "prepotent_response": item["distractor_answer"],
            "human_baseline_expected": item["human_baseline"],
            "contamination_safe": True,
            "seed": SEED,
            "notes": (
                "Correct answer requires tracking the stated goal. "
                "Prepotent response reflects engagement with salient distractor content."
            ),
        })
    return items


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_oap_bench() -> list[dict]:
    items = []
    items.extend(make_rule_reversal_items())
    items.extend(make_task_switching_items())
    items.extend(make_loaded_wm_items())
    return items


if __name__ == "__main__":
    random.seed(SEED)
    items = generate_oap_bench()

    out_path = Path("data/executive_functions/oap_bench.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for item in items:
            f.write(json.dumps(item) + "\n")

    print(f"Generated {len(items)} OAP-Bench items → {out_path}")
    subtask_counts = {}
    for item in items:
        st = item["subtask"]
        subtask_counts[st] = subtask_counts.get(st, 0) + 1
    for st, count in subtask_counts.items():
        print(f"  {st}: {count} items")
