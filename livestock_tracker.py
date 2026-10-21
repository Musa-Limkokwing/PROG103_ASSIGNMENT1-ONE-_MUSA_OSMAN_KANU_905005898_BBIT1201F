"""
+-------------------------------------------------------------+
|  LIVESTOCK HEALTH & TRACKING SYSTEM                         |
|  PROG211 Object-Oriented Programming 1 - Individual Work    |
|  Real-World Solutions under DPG Standards                   |
|  Domain: Agriculture                                        |
+-------------------------------------------------------------+

How to run
    python livestock_tracker.py           interactive menu
    python livestock_tracker.py --demo    automatic demonstration
    python livestock_tracker.py --test    built-in unit tests

Design in one sentence
    A LIST called `herd` holds every animal object; each animal is a
    Cattle, Goat or Sheep object (all inherit from Animal) and keeps its
    own LIST of HealthEvent objects (vaccinations, illnesses, treatments).

Parts of this file
    PART A  Fixed reference data (tuples)
    PART B  Classes: Animal -> Cattle, Goat, Sheep  and  HealthEvent
    PART C  Herd functions (the list data structure)
    PART D  Sample herd
    PART E  Screens for the menu
    PART F  Menu, demonstration and start-up
    PART G  Unit tests

Privacy (DPG)
    Animals are identified by ear-tag numbers and farms by farm codes
    such as FARM-01. No farmer names, phone numbers, addresses, GPS
    locations or national ID numbers are stored anywhere.

Note
    Vaccine lists, healthy weight ranges and feed estimates are
    simplified examples for a programming assignment. They are not
    veterinary advice.
"""

import sys
import unittest
from datetime import date


# ==============================================================
# PART A - FIXED REFERENCE DATA (TUPLES)
# These values must not change while the program runs, so they
# are stored in tuples, which cannot be modified.
# ==============================================================

EVENT_TYPES = ("Vaccination", "Illness", "Treatment", "Recovery", "Check-up")

# (event type, the status the animal moves to after that event)
STATUS_CHANGES = (
    ("Illness",   "Sick"),
    ("Treatment", "Under treatment"),
    ("Recovery",  "Healthy"),
)

SEXES = ("Male", "Female")
FIRST_BIRTH_YEAR = 2000


def new_status_after(event_type):
    """Look up the STATUS_CHANGES tuple. Returns None if the status stays the same."""
    for kind, status in STATUS_CHANGES:      # tuple unpacking
        if kind == event_type:
            return status
    return None


# ==============================================================
# PART B - CLASSES
# ==============================================================

class Animal:
    """Base class for every animal in the herd.

    Cattle, Goat and Sheep INHERIT from this class. Each subclass
    supplies its own species name, tag prefix, healthy weight range
    and required vaccines, and overrides daily_feed_kg().
    """

    # Class attributes (subclasses replace these)
    species = "Animal"
    tag_prefix = "AN"
    healthy_weight = (1, 1000)          # (minimum kg, maximum kg) - a tuple
    required_vaccines = ()              # tuple of vaccine names

    # Class attributes shared by ALL animals
    total_animals = 0                   # animals currently in the herd
    next_number = 1                     # for automatic tags (never reused)

    def __init__(self, tag_id, breed, sex, birth_year, weight_kg, farm_code):
        if not Animal.is_valid_sex(sex):
            raise ValueError("Sex must be Male or Female.")
        if not Animal.is_valid_birth_year(birth_year):
            raise ValueError(f"Birth year must be from {FIRST_BIRTH_YEAR} to {date.today().year}.")
        if weight_kg <= 0:
            raise ValueError("Weight must be more than 0 kg.")
        # Instance attributes - different for every animal
        self.tag_id = tag_id.upper()
        self.breed = breed.strip() or "Unknown"
        self.sex = sex.capitalize()
        self.birth_year = birth_year
        self.weight_kg = float(weight_kg)
        self.farm_code = farm_code.upper()
        self.status = "Healthy"
        self.health_events = []          # LIST of HealthEvent objects
        Animal.total_animals += 1

    # ---------------- instance methods ----------------
    def age_years(self):
        return date.today().year - self.birth_year

    def daily_feed_kg(self):
        """Rough daily dry-feed estimate. Each species overrides this."""
        return round(self.weight_kg * 0.03, 1)

    def update_weight(self, new_weight):
        """Record a new weighing and report the change."""
        if new_weight <= 0:
            raise ValueError("Weight must be more than 0 kg.")
        change = round(new_weight - self.weight_kg, 1)
        self.weight_kg = float(new_weight)
        sign = "+" if change >= 0 else ""
        print(f"  Weight of {self.tag_id} updated to {self.weight_kg:.1f} kg ({sign}{change} kg)")

    def add_event(self, event):
        """Store a health event and let it change the animal's status."""
        self.health_events.append(event)
        status = new_status_after(event.event_type)
        if status is not None:
            self.status = status

    def vaccines_received(self):
        """Return a tuple of the vaccine names this animal has had."""
        names = ()
        for event in self.health_events:
            if event.event_type == "Vaccination" and event.details not in names:
                names = names + (event.details,)
        return names

    def missing_vaccines(self):
        """Return a tuple of required vaccines this animal has NOT had yet."""
        received = self.vaccines_received()
        missing = ()
        for vaccine in self.required_vaccines:
            if vaccine not in received:
                missing = missing + (vaccine,)
        return missing

    def weight_ok(self):
        low, high = self.healthy_weight
        return low <= self.weight_kg <= high

    def health_score(self):
        """A simple 0-100 score: 100 means healthy, vaccinated and a good weight."""
        score = 100
        if self.status == "Sick":
            score -= 40
        elif self.status == "Under treatment":
            score -= 20
        score -= 10 * len(self.missing_vaccines())
        if not self.weight_ok():
            score -= 15
        return max(score, 0)

    def display_row(self):
        print(f"  {self.tag_id:<8}{self.species:<8}{self.breed:<22}{self.sex:<8}"
              f"{self.age_years():>3} yr{self.weight_kg:>7.1f} kg  {self.status:<16}"
              f"{self.health_score():>4}")

    def display_health_card(self):
        low, high = self.healthy_weight
        line = "+" + "-" * 64 + "+"
        print(line)
        print(f"|{'ANIMAL HEALTH CARD':^64}|")
        print(line)
        print(f"  Tag / species : {self.tag_id}  {self.species} ({self.breed})")
        print(f"  Sex / age     : {self.sex}, {self.age_years()} year(s) (born {self.birth_year})")
        print(f"  Farm          : {self.farm_code}")
        print(f"  Weight        : {self.weight_kg} kg (healthy range {low}-{high} kg)"
              f"{'' if self.weight_ok() else '  <-- CHECK'}")
        print(f"  Daily feed    : about {self.daily_feed_kg()} kg (estimate)")
        print(f"  Status        : {self.status}")
        print(f"  Health score  : {self.health_score()} / 100")
        missing = ", ".join(self.missing_vaccines()) or "none - fully vaccinated"
        print(f"  Missing jabs  : {missing}")
        print("  Health history:")
        if not self.health_events:
            print("    (no events recorded)")
        for event in self.health_events:
            print(f"    {event}")
        print(line)

    def __str__(self):
        return f"{self.tag_id} ({self.species}, {self.breed})"

    # ---------------- class methods ----------------
    @classmethod
    def create(cls, breed, sex, birth_year, weight_kg, farm_code):
        """Create an animal of THIS class with an automatic tag, e.g. CT-001."""
        tag = f"{cls.tag_prefix}-{Animal.next_number:03d}"
        animal = cls(tag, breed, sex, birth_year, weight_kg, farm_code)
        Animal.next_number += 1
        return animal

    @classmethod
    def from_text(cls, text):
        """Create the right kind of animal from text such as
        'Goat, West African Dwarf, Female, 2024, 24, FARM-02'."""
        species, breed, sex, year, weight, farm = (part.strip() for part in text.split(","))
        animal_class = species_class(species)
        return animal_class.create(breed, sex, int(year), float(weight), farm)

    @classmethod
    def herd_statistics(cls, herd):
        """Statistics for every animal in the herd that belongs to THIS class.
        Returns a TUPLE: (count, average weight, heaviest animal, fully vaccinated)."""
        count = 0
        total_weight = 0
        heaviest = None
        vaccinated = 0
        for animal in herd:
            if not isinstance(animal, cls):
                continue
            count += 1
            total_weight += animal.weight_kg
            if heaviest is None or animal.weight_kg > heaviest.weight_kg:
                heaviest = animal
            if not animal.missing_vaccines():
                vaccinated += 1
        average = round(total_weight / count, 1) if count else 0.0
        return count, average, heaviest, vaccinated

    @classmethod
    def get_total_animals(cls):
        return Animal.total_animals

    @classmethod
    def record_removal(cls):
        Animal.total_animals -= 1

    # ---------------- static methods ----------------
    @staticmethod
    def is_valid_sex(sex):
        return sex.capitalize() in SEXES

    @staticmethod
    def is_valid_birth_year(year):
        return FIRST_BIRTH_YEAR <= year <= date.today().year

    @staticmethod
    def find_healthiest(herd):
        """Return the animal with the highest health score (heavier wins a tie)."""
        best = None
        for animal in herd:
            if (best is None or animal.health_score() > best.health_score() or
                    (animal.health_score() == best.health_score()
                     and animal.weight_kg > best.weight_kg)):
                best = animal
        return best


class Cattle(Animal):
    species = "Cattle"
    tag_prefix = "CT"
    healthy_weight = (150, 600)
    required_vaccines = ("Anthrax", "Blackleg", "FMD")

    def daily_feed_kg(self):                       # overrides Animal.daily_feed_kg
        return round(self.weight_kg * 0.025, 1)


class Goat(Animal):
    species = "Goat"
    tag_prefix = "GT"
    healthy_weight = (18, 70)
    required_vaccines = ("PPR", "Anthrax")

    def daily_feed_kg(self):
        return round(self.weight_kg * 0.035, 1)


class Sheep(Animal):
    species = "Sheep"
    tag_prefix = "SH"
    healthy_weight = (20, 80)
    required_vaccines = ("PPR", "Anthrax")

    def daily_feed_kg(self):
        return round(self.weight_kg * 0.03, 1)


# The species the system supports - a tuple of CLASSES
SPECIES_CLASSES = (Cattle, Goat, Sheep)


def species_class(name):
    """Return the class for a species name such as 'goat' (any case)."""
    for animal_class in SPECIES_CLASSES:
        if animal_class.species.lower() == name.strip().lower():
            return animal_class
    names = ", ".join(c.species for c in SPECIES_CLASSES)
    raise ValueError(f"Species must be one of: {names}.")


class HealthEvent:
    """One vaccination, illness, treatment, recovery or check-up."""

    total_events = 0
    next_number = 1

    def __init__(self, animal, event_type, event_date, details, officer_code):
        event_type = HealthEvent.normalise_type(event_type)
        if isinstance(event_date, str):
            event_date = HealthEvent.parse_date(event_date)
        if not details.strip():
            raise ValueError("Please describe the event (for a vaccination, the vaccine name).")
        self.event_id = f"E{HealthEvent.next_number:03d}"
        HealthEvent.next_number += 1
        HealthEvent.total_events += 1
        self.animal = animal                     # the Animal OBJECT
        self.event_type = event_type
        self.event_date = event_date
        self.details = details.strip()
        self.officer_code = officer_code.upper() or "VO-??"
        animal.add_event(self)                   # objects interacting

    def __str__(self):
        return (f"{self.event_id}  {self.event_date.isoformat()}  {self.event_type:<12}"
                f"{self.details:<26}by {self.officer_code}")

    # ---------------- class methods ----------------
    @classmethod
    def from_text(cls, text, herd):
        """Create an event from text such as 'CT-001, Vaccination, 2026-03-10, Anthrax, VO-01'."""
        tag, kind, when, details, officer = (part.strip() for part in text.split(","))
        return cls(find_animal(herd, tag), kind, when, details, officer)

    @classmethod
    def get_total_events(cls):
        return cls.total_events

    @classmethod
    def record_removal(cls, count):
        cls.total_events -= count

    # ---------------- static methods ----------------
    @staticmethod
    def normalise_type(text):
        """Accept any capitalisation, e.g. 'illness' -> 'Illness'."""
        for kind in EVENT_TYPES:
            if kind.lower() == text.strip().lower():
                return kind
        raise ValueError("Event type must be one of: " + ", ".join(EVENT_TYPES) + ".")

    @staticmethod
    def parse_date(text):
        """Turn 'YYYY-MM-DD' into a date. Future dates are refused."""
        try:
            when = date.fromisoformat(text.strip())
        except ValueError:
            raise ValueError("Dates must be written as YYYY-MM-DD, e.g. 2026-03-10.")
        if when > date.today():
            raise ValueError("The date cannot be in the future.")
        return when


# ==============================================================
# PART C - HERD FUNCTIONS (THE LIST DATA STRUCTURE)
# The ONE data structure used to store objects is the LIST:
#     herd = [<Cattle CT-001>, <Goat GT-002>, ...]
#     animal.health_events = [<HealthEvent E001>, ...]
# ==============================================================

def add_animal(herd, animal):
    """Add an animal to the herd list (duplicate tags are refused)."""
    for existing in herd:
        if existing.tag_id == animal.tag_id:
            raise ValueError(f"Tag {animal.tag_id} is already in the herd.")
    herd.append(animal)
    return animal


def find_animal(herd, tag_id):
    """Loop through the list to find an animal by its tag (any case)."""
    wanted = tag_id.strip().upper()
    for animal in herd:
        if animal.tag_id == wanted:
            return animal
    raise ValueError(f"No animal with tag {wanted} in the herd.")


def remove_animal(herd, tag_id):
    """Remove an animal (sold, slaughtered or died) and its health history."""
    animal = find_animal(herd, tag_id)
    herd.remove(animal)
    HealthEvent.record_removal(len(animal.health_events))
    Animal.record_removal()
    return animal


def display_herd(herd):
    """Display every animal in the herd list."""
    print(f"\n  HERD REGISTER - {len(herd)} animal(s)")
    print("  " + "-" * 86)
    print(f"  {'Tag':<8}{'Species':<8}{'Breed':<22}{'Sex':<8}{'Age':>6}{'Weight':>10}  "
          f"{'Status':<16}{'Score':>5}")
    print("  " + "-" * 86)
    for animal in herd:
        animal.display_row()


def search_herd(herd, text):
    """Print animals whose tag, species, breed or farm contains the text."""
    text = text.lower()
    found = 0
    for animal in herd:
        if (text in animal.tag_id.lower() or text in animal.species.lower()
                or text in animal.breed.lower() or text in animal.farm_code.lower()):
            print(f"  {animal.tag_id:<8}{animal.species:<8}{animal.breed:<22}"
                  f"{animal.farm_code:<9}{animal.status}")
            found += 1
    return found


# ==============================================================
# PART D - SAMPLE HERD (fictional animals and farm codes)
# ==============================================================

def load_sample_herd():
    herd = []
    for text in (
        "Cattle, N'Dama, Female, 2021, 310, FARM-01",
        "Cattle, N'Dama, Male, 2022, 140, FARM-01",
        "Goat, West African Dwarf, Female, 2024, 24, FARM-02",
        "Goat, West African Dwarf, Male, 2023, 31, FARM-02",
        "Sheep, Djallonke, Female, 2023, 34, FARM-01",
    ):
        add_animal(herd, Animal.from_text(text))
    for text in (
        "CT-001, Vaccination, 2026-02-10, Anthrax, VO-01",
        "CT-001, Vaccination, 2026-02-10, Blackleg, VO-01",
        "CT-001, Vaccination, 2026-03-15, FMD, VO-01",
        "CT-001, Check-up, 2026-08-01, Good body condition, VO-02",
        "CT-002, Vaccination, 2026-02-10, Anthrax, VO-01",
        "CT-002, Illness, 2026-09-20, Diarrhoea and weight loss, VO-02",
        "CT-002, Treatment, 2026-09-21, Dewormer given, VO-02",
        "GT-003, Vaccination, 2026-04-02, PPR, VO-03",
        "GT-004, Vaccination, 2026-04-02, PPR, VO-03",
        "GT-004, Vaccination, 2026-04-02, Anthrax, VO-03",
        "SH-005, Vaccination, 2026-04-02, PPR, VO-03",
        "SH-005, Illness, 2026-10-01, Coughing, VO-03",
    ):
        HealthEvent.from_text(text, herd)
    return herd


# ==============================================================
# PART E - SCREENS FOR THE MENU
# ==============================================================

def ask(prompt):
    return input(prompt).strip()


def ask_until_valid(prompt, convert, problem):
    """Ask again and again until convert(answer) works."""
    while True:
        try:
            return convert(ask(prompt))
        except ValueError:
            print(f"  ! {problem}")


def positive_number(text):
    value = float(text)
    if value <= 0:
        raise ValueError
    return value


def valid_year(text):
    year = int(text)
    if not Animal.is_valid_birth_year(year):
        raise ValueError
    return year


def valid_sex(text):
    if not Animal.is_valid_sex(text):
        raise ValueError
    return text.capitalize()


def screen_register(herd):
    names = "/".join(c.species for c in SPECIES_CLASSES)
    animal_class = ask_until_valid(f"  Species ({names}): ", species_class,
                                   f"please type {names}.")
    breed = ask("  Breed (or press Enter if unknown): ")
    sex = ask_until_valid("  Sex (Male/Female): ", valid_sex, "please type Male or Female.")
    year = ask_until_valid("  Birth year (e.g. 2024): ", valid_year,
                           f"please type a year from {FIRST_BIRTH_YEAR} to {date.today().year}.")
    weight = ask_until_valid("  Weight in kg (e.g. 25.5): ", positive_number,
                             "please type a number above 0.")
    farm = ask("  Farm code (e.g. FARM-01): ") or "FARM-01"
    animal = add_animal(herd, animal_class.create(breed, sex, year, weight, farm))
    print(f"  OK - registered with ear tag {animal.tag_id}.")


def screen_health_event(herd):
    animal = find_animal(herd, ask("  Ear tag (e.g. GT-003): "))
    print("  Event types: " + ", ".join(EVENT_TYPES))
    kind = ask_until_valid("  Event type: ", HealthEvent.normalise_type,
                           "please type one of the event types shown.")
    if kind == "Vaccination":
        print(f"  Required for {animal.species}: " + ", ".join(animal.required_vaccines))
    when = ask_until_valid("  Date (YYYY-MM-DD): ", HealthEvent.parse_date,
                           "please type a past date like 2026-09-30.")
    details = ask("  Details (vaccine name, illness or medicine): ")
    officer = ask("  Vet officer code (e.g. VO-01): ")
    event = HealthEvent(animal, kind, when, details, officer)
    print(f"  OK - saved {event.event_id}. {animal.tag_id} is now: {animal.status}.")


def screen_weight(herd):
    animal = find_animal(herd, ask("  Ear tag: "))
    print(f"  Current weight: {animal.weight_kg} kg")
    animal.update_weight(ask_until_valid("  New weight in kg: ", positive_number,
                                         "please type a number above 0."))


def screen_card(herd):
    animal = find_animal(herd, ask("  Ear tag: "))
    print()
    animal.display_health_card()


def screen_remove(herd):
    animal = find_animal(herd, ask("  Ear tag of the animal to remove: "))
    print(f"  {animal}  -  {len(animal.health_events)} health event(s) on record")
    if ask("  Type YES to remove it (e.g. sold or died): ").upper() != "YES":
        print("  Cancelled - nothing was removed.")
        return
    remove_animal(herd, animal.tag_id)
    print(f"  OK - {animal.tag_id} and its health history were removed. "
          f"{len(herd)} animal(s) remain.")


def screen_search(herd):
    text = ask("  Search for (tag, species, breed or farm): ")
    if not text:
        raise ValueError("Please type something to search for.")
    print()
    if search_herd(herd, text) == 0:
        print("  No animals matched.")


def screen_healthiest(herd):
    best = Animal.find_healthiest(herd)                     # static method
    print("\n  HEALTHIEST ANIMAL IN THE HERD")
    print("  " + "-" * 44)
    if best is None:
        print("  The herd is empty.")
        return
    print(f"  {best}  on {best.farm_code}")
    print(f"  Health score {best.health_score()}/100, {best.weight_kg} kg, status {best.status}")
    print(f"  Vaccines: {', '.join(best.vaccines_received()) or 'none'}")


def screen_species_report(herd):
    print("\n  SPECIES REPORT")
    print("  " + "-" * 62)
    print(f"  {'Species':<9}{'Count':>6}{'Avg kg':>9}{'Vaccinated':>12}   Heaviest")
    print("  " + "-" * 62)
    for animal_class in SPECIES_CLASSES:
        count, average, heaviest, vaccinated = animal_class.herd_statistics(herd)  # class method
        heavy = f"{heaviest.tag_id} ({heaviest.weight_kg} kg)" if heaviest else "-"
        print(f"  {animal_class.species:<9}{count:>6}{average:>9}{vaccinated:>7} of {count:<3}  {heavy}")


def screen_attention(herd):
    """Animals that need a vet visit: sick, under treatment, missing vaccines or bad weight."""
    print("\n  ANIMALS NEEDING ATTENTION")
    print("  " + "-" * 62)
    found = 0
    for animal in herd:
        reasons = ()
        if animal.status != "Healthy":
            reasons = reasons + (animal.status.lower(),)
        if animal.missing_vaccines():
            reasons = reasons + ("needs " + ", ".join(animal.missing_vaccines()),)
        if not animal.weight_ok():
            reasons = reasons + (f"weight {animal.weight_kg} kg out of range",)
        if reasons:
            found += 1
            print(f"  {animal.tag_id:<8}{animal.species:<8}" + "; ".join(reasons))
    print(f"  {found} animal(s) need attention." if found else "  Every animal is fine.")


def screen_summary(herd):
    healthy = 0
    for animal in herd:
        if animal.status == "Healthy":
            healthy += 1
    print("\n  HERD SUMMARY")
    print("  " + "-" * 44)
    print(f"  Animals in herd      : {Animal.get_total_animals()}")
    print(f"  Healthy right now    : {healthy}")
    print(f"  Health events stored : {HealthEvent.get_total_events()}")
    print("  Required vaccines (fixed tuples):")
    for animal_class in SPECIES_CLASSES:
        low, high = animal_class.healthy_weight
        print(f"    {animal_class.species:<7}{', '.join(animal_class.required_vaccines):<24}"
              f"healthy weight {low}-{high} kg")


# ==============================================================
# PART F - MENU, DEMONSTRATION AND START-UP
# ==============================================================

MENU = (
    ("1", "Herd register (all animals)"),
    ("2", "Register a new animal"),
    ("3", "Record a health event"),
    ("4", "Update an animal's weight"),
    ("5", "Animal health card"),
    ("6", "Remove an animal (sold / died)"),
    ("7", "Search the herd"),
    ("8", "Healthiest animal"),
    ("9", "Species report"),
    ("10", "Animals needing attention"),
    ("11", "Herd summary"),
    ("0", "Exit"),
)


def run_menu():
    herd = load_sample_herd()
    print("+" + "-" * 58 + "+")
    print(f"|{'LIVESTOCK HEALTH & TRACKING SYSTEM':^58}|")
    print(f"|{'no farmer personal data is stored':^58}|")
    print("+" + "-" * 58 + "+")
    while True:
        print()
        for key, label in MENU:
            print(f"  [{key:>2}] {label}")
        choice = ask("  Select: ")
        try:
            if choice == "1":
                display_herd(herd)
            elif choice == "2":
                screen_register(herd)
            elif choice == "3":
                screen_health_event(herd)
            elif choice == "4":
                screen_weight(herd)
            elif choice == "5":
                screen_card(herd)
            elif choice == "6":
                screen_remove(herd)
            elif choice == "7":
                screen_search(herd)
            elif choice == "8":
                screen_healthiest(herd)
            elif choice == "9":
                screen_species_report(herd)
            elif choice == "10":
                screen_attention(herd)
            elif choice == "11":
                screen_summary(herd)
            elif choice == "0":
                print("  Goodbye - keep your animals healthy!")
                break
            else:
                print("  ! Please choose a number from the menu.")
        except ValueError as problem:
            print(f"  ! {problem}")


def banner(text):
    print(f"\n>>> {text}")


def run_demo():
    banner("TASK 1 - creating objects from three subclasses of Animal")
    herd = load_sample_herd()
    for animal in herd[:3]:
        print(f"  {animal}  is a {type(animal).__name__}, inherits from Animal: "
              f"{isinstance(animal, Animal)}")

    banner("TASK 2 - the herd LIST, displayed by display_herd()")
    display_herd(herd)

    banner("TASK 3 - instance method update_weight() and polymorphic daily_feed_kg()")
    herd[1].update_weight(158)
    for animal in herd[1:4]:
        print(f"  {animal.tag_id} ({animal.species}) eats about {animal.daily_feed_kg()} kg/day")

    banner("TASK 3 - class methods Animal.from_text() and Goat.create()")
    sheep = add_animal(herd, Animal.from_text("Sheep, Djallonke, Male, 2025, 22, FARM-03"))
    goat = add_animal(herd, Goat.create("Sahel", "Female", 2025, 19, "FARM-03"))
    print(f"  Created {sheep} and {goat}; animals in herd: {Animal.get_total_animals()}")

    banner("TASK 3 - static methods and validation")
    print(f"  Animal.is_valid_sex('female') -> {Animal.is_valid_sex('female')}")
    print(f"  Animal.is_valid_birth_year(1995) -> {Animal.is_valid_birth_year(1995)}")
    for bad in (lambda: HealthEvent(goat, "Party", "2026-05-01", "x", "VO-01"),
                lambda: HealthEvent(goat, "Illness", "2099-01-01", "Fever", "VO-01"),
                lambda: find_animal(herd, "CT-999")):
        try:
            bad()
        except ValueError as problem:
            print(f"  ! {problem}")

    banner("OBJECT INTERACTION - a HealthEvent changes its Animal's status")
    HealthEvent(herd[1], "Recovery", "2026-10-05", "Eating well again", "VO-02")
    herd[1].display_health_card()

    banner("EXTRA FEATURES - healthiest animal, species report, attention list")
    screen_healthiest(herd)
    screen_species_report(herd)
    screen_attention(herd)

    banner("EXTRA FEATURE - removing an animal from the list")
    removed = remove_animal(herd, "SH-005")
    print(f"  Removed {removed}. {len(herd)} animal(s) remain.")
    screen_summary(herd)


# ==============================================================
# PART G - UNIT TESTS  (python livestock_tracker.py --test)
# ==============================================================

class LivestockTests(unittest.TestCase):

    def setUp(self):
        self.herd = []
        self.cow = add_animal(self.herd, Cattle.create("N'Dama", "Female", 2021, 300, "F-1"))
        self.goat = add_animal(self.herd, Goat.create("WAD", "Male", 2024, 25, "F-1"))

    def test_inheritance_and_tags(self):
        self.assertIsInstance(self.cow, Animal)
        self.assertTrue(self.cow.tag_id.startswith("CT-"))
        self.assertTrue(self.goat.tag_id.startswith("GT-"))

    def test_polymorphic_feed(self):
        self.assertEqual(self.cow.daily_feed_kg(), 7.5)      # 300 x 2.5%
        self.assertEqual(self.goat.daily_feed_kg(), 0.9)     # 25 x 3.5%

    def test_from_text_picks_subclass(self):
        sheep = Animal.from_text("sheep, Djallonke, female, 2023, 30, F-2")
        self.assertIsInstance(sheep, Sheep)
        self.assertEqual(sheep.sex, "Female")

    def test_invalid_animals_rejected(self):
        with self.assertRaises(ValueError):
            Goat.create("WAD", "Unknown", 2024, 20, "F-1")
        with self.assertRaises(ValueError):
            Goat.create("WAD", "Male", 1990, 20, "F-1")
        with self.assertRaises(ValueError):
            Animal.from_text("Camel, X, Male, 2020, 300, F-1")

    def test_events_change_status(self):
        HealthEvent(self.goat, "illness", "2026-09-01", "Fever", "VO-01")
        self.assertEqual(self.goat.status, "Sick")
        HealthEvent(self.goat, "Treatment", "2026-09-02", "Antibiotic", "VO-01")
        self.assertEqual(self.goat.status, "Under treatment")
        HealthEvent(self.goat, "Recovery", "2026-09-09", "Well", "VO-01")
        self.assertEqual(self.goat.status, "Healthy")

    def test_missing_vaccines_and_score(self):
        self.assertEqual(self.goat.missing_vaccines(), ("PPR", "Anthrax"))
        self.assertEqual(self.goat.health_score(), 80)
        HealthEvent(self.goat, "Vaccination", "2026-04-01", "PPR", "VO-03")
        HealthEvent(self.goat, "Vaccination", "2026-04-01", "Anthrax", "VO-03")
        self.assertEqual(self.goat.health_score(), 100)

    def test_bad_dates_rejected(self):
        with self.assertRaises(ValueError):
            HealthEvent.parse_date("01/04/2026")
        with self.assertRaises(ValueError):
            HealthEvent.parse_date("2099-01-01")

    def test_list_add_find_remove(self):
        with self.assertRaises(ValueError):
            add_animal(self.herd, self.cow)                  # duplicate tag
        self.assertIs(find_animal(self.herd, self.goat.tag_id.lower()), self.goat)
        remove_animal(self.herd, self.goat.tag_id)
        self.assertEqual(len(self.herd), 1)
        with self.assertRaises(ValueError):
            find_animal(self.herd, self.goat.tag_id)

    def test_healthiest_and_statistics(self):
        HealthEvent(self.cow, "Illness", "2026-09-01", "Lame", "VO-01")
        self.assertIs(Animal.find_healthiest(self.herd), self.goat)
        count, average, heaviest, vaccinated = Cattle.herd_statistics(self.herd)
        self.assertEqual((count, average, heaviest, vaccinated), (1, 300.0, self.cow, 0))

    def test_weight_update(self):
        self.goat.update_weight(90)
        self.assertFalse(self.goat.weight_ok())
        with self.assertRaises(ValueError):
            self.goat.update_weight(0)


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0], "-v"])
    elif "--demo" in sys.argv:
        run_demo()
    else:
        run_menu()
