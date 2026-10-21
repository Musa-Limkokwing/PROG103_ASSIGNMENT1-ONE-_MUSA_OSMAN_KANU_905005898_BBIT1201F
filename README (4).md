# 🐄 Livestock Health & Tracking System

> PROG211 Object-Oriented Programming 1 · Individual Assignment · *Real-World Solutions under DPG Standards*
> **Domain:** Agriculture · **System:** Livestock Health & Tracking · **Python 3, standard library only**

Livestock are often a rural family's biggest savings, and one sick animal can spread disease to the whole herd. This command-line tool lets a farmer group, a community animal health worker or a vet officer keep a **digital herd register**. They can record vaccinations, illnesses, treatments and recoveries, follow each animal's weight, and see straight away **which animals need attention**.

> ⚠️ Vaccine lists, healthy weight ranges and feed estimates in this program are simplified examples for a programming assignment. They are **not** veterinary advice.

---

## Contents

1. [Quick start](#1-quick-start)
2. [What it does](#2-what-it-does)
3. [How it is built](#3-how-it-is-built)
4. [Assignment tasks](#4-assignment-tasks)
5. [Digital Public Goods alignment](#5-digital-public-goods-alignment)
6. [Example usage](#6-example-usage)
7. [Tests](#7-tests)
8. [Future work](#8-future-work)
9. [Licence](#9-licence)

---

## 1. Quick start

You only need Python 3.8 or newer. Nothing else needs to be installed.

```bash
git clone https://github.com/<your-username>/livestock-health-tracker.git
cd livestock-health-tracker

python livestock_tracker.py          # interactive menu (starts with a sample herd)
python livestock_tracker.py --demo   # automatic walk-through of every requirement
python livestock_tracker.py --test   # run the 10 unit tests
```

## 2. What it does

| Key | Menu option | Description |
|:---:|---|---|
| 1 | Herd register | Table of every animal: tag, species, breed, sex, age, weight, status and health score |
| 2 | Register a new animal | Gives the animal an automatic ear tag (`CT-`, `GT-` or `SH-` + number); every answer is checked as it is typed |
| 3 | Record a health event | Vaccination, Illness, Treatment, Recovery or Check-up. Illness → **Sick**, Treatment → **Under treatment**, Recovery → **Healthy** |
| 4 | Update weight | Records a new weighing and shows the gain or loss |
| 5 | Animal health card | Full profile: weight check, feed estimate, status, score, missing vaccines and full health history |
| 6 | **Remove an animal** | For animals that are sold or have died. Removes the animal and its history after you type **YES** |
| 7 | **Search the herd** | By tag, species, breed or farm code, in any case |
| 8 | **Healthiest animal** | The animal with the highest health score (the "top scorer") |
| 9 | **Species report** | For cattle, goats and sheep: count, average weight, how many are fully vaccinated, and the heaviest animal |
| 10 | **Animals needing attention** | Every animal that is sick, under treatment, missing a vaccine or outside its healthy weight, with the reasons |
| 11 | Herd summary | Totals, plus each species' required vaccines and healthy weight range |
| 0 | Exit | |

**Health score (0–100):** each animal starts at 100 and loses points for these problems:
- **−40** if it is Sick;
- **−20** if it is Under treatment;
- **−10** for each required vaccine it is missing;
- **−15** if its weight is outside the healthy range for its species.

## 3. How it is built

Everything is in **one file**, `livestock_tracker.py`, split into lettered parts:

| Part | Contents |
|---|---|
| A | Fixed reference data in **tuples**: `EVENT_TYPES`, `STATUS_CHANGES`, `SEXES` |
| B | Classes: `Animal` (base class) → `Cattle`, `Goat`, `Sheep` (subclasses), and `HealthEvent` |
| C | Herd functions that work on the **list**: `add_animal()`, `find_animal()`, `remove_animal()`, `display_herd()`, `search_herd()` |
| D | `load_sample_herd()`: fictional animals and events |
| E | One "screen" function per menu option, plus safe input helpers |
| F | The menu (`run_menu()`), the demonstration (`run_demo()`) and start-up |
| G | Unit tests (`unittest`) |

### Class diagram

```
                 +---------------------------+
                 |          Animal           |   base class
                 +---------------------------+
                 | tag_id, breed, sex,       |
                 | birth_year, weight_kg,    |
                 | farm_code, status,        |
                 | health_events : list      |
                 +---------------------------+
                 | update_weight()           |
                 | add_event()               |
                 | health_score()            |
                 | daily_feed_kg()           |<---- overridden by each subclass
                 | create()   @classmethod   |
                 | from_text() @classmethod  |
                 | find_healthiest() @static |
                 +-------------+-------------+
          +--------------------+--------------------+
   +------+------+      +------+------+      +------+------+
   |   Cattle    |      |    Goat     |      |    Sheep    |
   | prefix CT   |      | prefix GT   |      | prefix SH   |
   +-------------+      +-------------+      +-------------+

   HealthEvent --(belongs to)--> Animal
   (event_id, event_type, event_date, details, officer_code)
```

## 4. Assignment tasks

### Task 1 – Classes, attributes and objects

The program has **five classes**. `Cattle`, `Goat` and `Sheep` **inherit** from `Animal`. Each subclass sets its own class attributes (`species`, `tag_prefix`, `healthy_weight`, `required_vaccines`) and **overrides** `daily_feed_kg()`. This is polymorphism: the same method call gives a different answer for each species.

**How the objects interact:**
- A `HealthEvent` object stores the `Animal` object it belongs to.
- When the event is created, it calls `animal.add_event(self)`.
- That call adds the event to the animal's history and updates the animal's `status` (for example, an *Illness* event makes the animal *Sick*).
- `health_score()` then uses the animal's status, its events and its species' rules.

```python
cow = Cattle.create("N'Dama", "Female", 2021, 310, "FARM-01")      # object creation
HealthEvent(cow, "Illness", "2026-09-20", "Coughing", "VO-02")      # interaction
print(cow.status)   # -> Sick
```

### Task 2 – Data structure: a list

The brief allows a list *or* a dictionary. This project uses **only lists** to store objects:

```python
herd = [<Cattle CT-001>, <Cattle CT-002>, <Goat GT-003>, ...]
animal.health_events = [<HealthEvent E001>, <HealthEvent E002>, ...]
```

A list suits a herd register well:
- it keeps animals in the order they were registered;
- every report naturally loops through the whole herd;
- finding one animal is a simple loop that compares ear tags.

**Add** and **display** functions, as the task requires:

```python
def add_animal(herd, animal):
    """Add an animal to the herd list (duplicate tags are refused)."""
    for existing in herd:
        if existing.tag_id == animal.tag_id:
            raise ValueError(f"Tag {animal.tag_id} is already in the herd.")
    herd.append(animal)
    return animal

def display_herd(herd):
    """Display every animal in the herd list."""
    ...
    for animal in herd:
        animal.display_row()
```

`find_animal()`, `remove_animal()` (which uses `herd.remove()`) and `search_herd()` also work on the list.

**Optional tuples (bonus):** tuples hold data that must never change:
- **Fixed data:** `EVENT_TYPES`, `STATUS_CHANGES` (pairs of event and new status), `SEXES` and `SPECIES_CLASSES`.
- **Species rules:** each species' `healthy_weight = (min, max)` and `required_vaccines`.
- **The menu.**
- **Returned tuples:** `vaccines_received()`, `missing_vaccines()` and `herd_statistics()`. The last returns `(count, average, heaviest, vaccinated)`.

All of them are read with tuple unpacking, e.g. `low, high = self.healthy_weight`.

### Task 3 – Methods

| Kind | Method | Purpose |
|---|---|---|
| Instance | `update_weight()` | Records a new weight and shows the change |
| Instance | `add_event()` | Stores a health event and updates the animal's status |
| Instance | `health_score()` | Works out the 0–100 score |
| Instance | `missing_vaccines()` | Required vaccines not yet given (returns a tuple) |
| Instance (overridden) | `daily_feed_kg()` | Different calculation for cattle, goats and sheep |
| Class | `Animal.create()` | Creates an animal of the class it is called on, with an automatic tag (`Goat.create(...)` → `GT-007`) |
| Class | `Animal.from_text()` | Builds the right subclass from text such as `"Sheep, Djallonke, Male, 2025, 22, FARM-03"` |
| Class | `Cattle.herd_statistics(herd)` | Statistics for one species only (uses `cls`) |
| Class | `HealthEvent.from_text()` | Builds an event from one line of text |
| Class | `get_total_animals()`, `record_removal()` | Read and update the shared counters |
| Static | `Animal.is_valid_sex()`, `Animal.is_valid_birth_year()` | Input checks that need no object |
| Static | `Animal.find_healthiest(herd)` | Finds the top-scoring animal |
| Static | `HealthEvent.parse_date()`, `HealthEvent.normalise_type()` | Check dates (no future dates) and event types |

## 5. Digital Public Goods alignment

| Principle | How it is met |
|---|---|
| **Open-source** | Public GitHub repository under the **MIT licence**. It uses only the Python standard library, so it is free to run, study, copy and improve. |
| **Inclusive & accessible** | Works in any text terminal on a low-cost laptop, fully offline, which suits rural areas. The numbered menu uses plain English, and every prompt shows an example. Species, sex, tags and event types are accepted in any case. Each answer is checked straight away and the user is asked again, so the program never crashes on a typing mistake. Status is shown in words, not colours. Removing an animal needs a typed **YES**. |
| **Privacy-respecting** | Only **animals** are recorded. Farms appear only as codes (`FARM-01`) and vet officers only as codes (`VO-01`). **No** farmer names, phone numbers, addresses, GPS locations, national IDs or financial details are stored. Data stays on the local machine. Removing an animal also removes its history. All sample data is fictional. |
| **Modular & reusable** | Clearly separated parts (data, classes, list functions, screens, menu, tests). **Adding a new species** (for example, pigs) only needs a new subclass with its own tag prefix, weight range and vaccines, plus one entry in `SPECIES_CLASSES`. The classes can be reused in a web, mobile or database-backed system. |

## 6. Example usage

### Registering an animal: every answer is checked

```
  Select: 2
  Species (Cattle/Goat/Sheep): camel
  ! please type Cattle/Goat/Sheep.
  Species (Cattle/Goat/Sheep): goat
  Breed (or press Enter if unknown):
  Sex (Male/Female): unknown
  ! please type Male or Female.
  Sex (Male/Female): female
  Birth year (e.g. 2024): 1990
  ! please type a year from 2000 to 2026.
  Birth year (e.g. 2024): 2025
  Weight in kg (e.g. 25.5): heavy
  ! please type a number above 0.
  Weight in kg (e.g. 25.5): 21.5
  Farm code (e.g. FARM-01): farm-03
  OK - registered with ear tag GT-006.
```

### Recording health events: status changes automatically

```
  Select: 3
  Ear tag (e.g. GT-003): gt-003
  Event types: Vaccination, Illness, Treatment, Recovery, Check-up
  Event type: party
  ! please type one of the event types shown.
  Event type: vaccination
  Required for Goat: PPR, Anthrax
  Date (YYYY-MM-DD): 2099-01-01
  ! please type a past date like 2026-09-30.
  Date (YYYY-MM-DD): 2026-10-10
  Details (vaccine name, illness or medicine): Anthrax
  Vet officer code (e.g. VO-01): VO-03
  OK - saved E013. GT-003 is now: Healthy.

  Select: 3
  Ear tag (e.g. GT-003): CT-001
  ...
  Event type: illness
  ...
  OK - saved E014. CT-001 is now: Sick.
```

### Animal health card (option 5)

```
+----------------------------------------------------------------+
|                       ANIMAL HEALTH CARD                       |
+----------------------------------------------------------------+
  Tag / species : CT-002  Cattle (N'Dama)
  Sex / age     : Male, 4 year(s) (born 2022)
  Farm          : FARM-01
  Weight        : 158.0 kg (healthy range 150-600 kg)
  Daily feed    : about 4.0 kg (estimate)
  Status        : Under treatment
  Health score  : 60 / 100
  Missing jabs  : Blackleg, FMD
  Health history:
    E005  2026-02-10  Vaccination Anthrax                   by VO-01
    E006  2026-09-20  Illness     Diarrhoea and weight loss by VO-02
    E007  2026-09-21  Treatment   Dewormer given            by VO-02
+----------------------------------------------------------------+
```

### Removing an animal (option 6)

```
  Select: 6
  Ear tag of the animal to remove: sh-005
  SH-005 (Sheep, Djallonke)  -  2 health event(s) on record
  Type YES to remove it (e.g. sold or died): YES
  OK - SH-005 and its health history were removed. 4 animal(s) remain.
```

Typing anything other than YES shows `Cancelled - nothing was removed.`

### Healthiest animal, species report and attention list (options 8–10)

```
  HEALTHIEST ANIMAL IN THE HERD
  --------------------------------------------
  CT-001 (Cattle, N'Dama)  on FARM-01
  Health score 100/100, 310.0 kg, status Healthy
  Vaccines: Anthrax, Blackleg, FMD

  SPECIES REPORT
  --------------------------------------------------------------
  Species   Count   Avg kg  Vaccinated   Heaviest
  --------------------------------------------------------------
  Cattle        2    225.0      1 of 2    CT-001 (310.0 kg)
  Goat          2     27.5      1 of 2    GT-004 (31.0 kg)
  Sheep         1     34.0      0 of 1    SH-005 (34.0 kg)

  ANIMALS NEEDING ATTENTION
  --------------------------------------------------------------
  CT-002  Cattle  under treatment; needs Blackleg, FMD; weight 140.0 kg out of range
  GT-003  Goat    needs Anthrax
  SH-005  Sheep   sick; needs Anthrax
  3 animal(s) need attention.
```

### Searching (option 7)

```
  Select: 7
  Search for (tag, species, breed or farm): goat
  GT-003  Goat    West African Dwarf    FARM-02  Healthy
  GT-004  Goat    West African Dwarf    FARM-02  Healthy
```

## 7. Tests

```
$ python livestock_tracker.py --test
...
Ran 10 tests in 0.002s

OK
```

The tests cover:
- inheritance, automatic tags and overridden feed calculations;
- `from_text()` choosing the right subclass;
- invalid sex, birth year and species being rejected;
- the status changing after Illness, Treatment and Recovery;
- missing vaccines and the health score;
- bad and future dates being rejected;
- adding, finding and removing animals in the list, including refusing duplicate tags;
- the healthiest animal and species statistics;
- weight updates.

## 8. Future work

- Save the herd to a CSV or JSON file so it remains after the program closes.
- Remind users when booster vaccinations are due.
- Track births and parent animals to build family trees for breeding.
- Add a Krio-language interface and an SMS version for areas without computers.

## 9. Licence

MIT – see [LICENSE](LICENSE).
