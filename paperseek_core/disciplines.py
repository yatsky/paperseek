from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class DisciplineField:
    id: str
    label: str
    domain: str
    wos_categories: tuple[str, ...]

    @property
    def openalex_field_id(self) -> int:
        return int(self.id)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["openalex_field_id"] = self.openalex_field_id
        data["openalex_filter"] = f"primary_topic.field.id:{self.id}"
        data["wos_categories"] = list(self.wos_categories)
        return data


OPENALEX_FIELDS: tuple[DisciplineField, ...] = (
    DisciplineField("11", "Agricultural and Biological Sciences", "Life Sciences", ("Agricultural Economics & Policy", "Agricultural Engineering", "Agriculture, Dairy & Animal Science", "Agriculture, Multidisciplinary", "Agronomy", "Biodiversity Conservation", "Biology", "Ecology", "Entomology", "Fisheries", "Food Science & Technology", "Forestry", "Horticulture", "Marine & Freshwater Biology", "Plant Sciences", "Soil Science", "Zoology")),
    DisciplineField("12", "Arts and Humanities", "Social Sciences", ("Architecture", "Art", "Asian Studies", "Classics", "Cultural Studies", "Dance", "Film, Radio, Television", "Folklore", "History", "History & Philosophy of Science", "Humanities, Multidisciplinary", "Language & Linguistics", "Literary Reviews", "Literary Theory & Criticism", "Literature", "Music", "Poetry", "Religion", "Theater")),
    DisciplineField("13", "Biochemistry, Genetics and Molecular Biology", "Life Sciences", ("Biochemical Research Methods", "Biochemistry & Molecular Biology", "Biotechnology & Applied Microbiology", "Cell Biology", "Developmental Biology", "Genetics & Heredity", "Mathematical & Computational Biology", "Physiology", "Reproductive Biology")),
    DisciplineField("14", "Business, Management and Accounting", "Social Sciences", ("Business", "Business, Finance", "Hospitality, Leisure, Sport & Tourism", "Industrial Relations & Labor", "Management", "Operations Research & Management Science")),
    DisciplineField("15", "Chemical Engineering", "Physical Sciences", ("Chemistry, Applied", "Engineering, Chemical", "Energy & Fuels", "Polymer Science", "Thermodynamics")),
    DisciplineField("16", "Chemistry", "Physical Sciences", ("Chemistry, Analytical", "Chemistry, Applied", "Chemistry, Inorganic & Nuclear", "Chemistry, Medicinal", "Chemistry, Multidisciplinary", "Chemistry, Organic", "Chemistry, Physical", "Crystallography", "Electrochemistry", "Spectroscopy")),
    DisciplineField("17", "Computer Science", "Physical Sciences", ("Computer Science, Artificial Intelligence", "Computer Science, Cybernetics", "Computer Science, Hardware & Architecture", "Computer Science, Information Systems", "Computer Science, Interdisciplinary Applications", "Computer Science, Software Engineering", "Computer Science, Theory & Methods", "Information Science & Library Science", "Robotics", "Telecommunications")),
    DisciplineField("18", "Decision Sciences", "Social Sciences", ("Management", "Operations Research & Management Science", "Social Sciences, Mathematical Methods", "Statistics & Probability")),
    DisciplineField("19", "Earth and Planetary Sciences", "Physical Sciences", ("Astronomy & Astrophysics", "Geochemistry & Geophysics", "Geography, Physical", "Geology", "Geosciences, Multidisciplinary", "Meteorology & Atmospheric Sciences", "Mineralogy", "Oceanography", "Paleontology", "Remote Sensing")),
    DisciplineField("20", "Economics, Econometrics and Finance", "Social Sciences", ("Agricultural Economics & Policy", "Business, Finance", "Development Studies", "Economics", "Industrial Relations & Labor", "Regional & Urban Planning")),
    DisciplineField("21", "Energy", "Physical Sciences", ("Energy & Fuels", "Engineering, Petroleum", "Environmental Sciences", "Green & Sustainable Science & Technology", "Nuclear Science & Technology")),
    DisciplineField("22", "Engineering", "Physical Sciences", ("Automation & Control Systems", "Construction & Building Technology", "Engineering, Aerospace", "Engineering, Biomedical", "Engineering, Civil", "Engineering, Electrical & Electronic", "Engineering, Environmental", "Engineering, Geological", "Engineering, Industrial", "Engineering, Manufacturing", "Engineering, Marine", "Engineering, Mechanical", "Engineering, Multidisciplinary", "Engineering, Ocean", "Engineering, Petroleum", "Instruments & Instrumentation", "Mechanics", "Robotics", "Transportation Science & Technology")),
    DisciplineField("23", "Environmental Science", "Physical Sciences", ("Biodiversity Conservation", "Ecology", "Environmental Sciences", "Environmental Studies", "Green & Sustainable Science & Technology", "Limnology", "Remote Sensing", "Water Resources")),
    DisciplineField("24", "Immunology and Microbiology", "Life Sciences", ("Biotechnology & Applied Microbiology", "Immunology", "Infectious Diseases", "Microbiology", "Mycology", "Parasitology", "Virology")),
    DisciplineField("25", "Materials Science", "Physical Sciences", ("Materials Science, Biomaterials", "Materials Science, Ceramics", "Materials Science, Characterization & Testing", "Materials Science, Coatings & Films", "Materials Science, Composites", "Materials Science, Multidisciplinary", "Materials Science, Paper & Wood", "Materials Science, Textiles", "Metallurgy & Metallurgical Engineering", "Nanoscience & Nanotechnology", "Polymer Science")),
    DisciplineField("26", "Mathematics", "Physical Sciences", ("Logic", "Mathematical & Computational Biology", "Mathematics", "Mathematics, Applied", "Mathematics, Interdisciplinary Applications", "Statistics & Probability")),
    DisciplineField("27", "Medicine", "Health Sciences", ("Allergy", "Anatomy & Morphology", "Andrology", "Anesthesiology", "Cardiac & Cardiovascular Systems", "Clinical Neurology", "Critical Care Medicine", "Dermatology", "Emergency Medicine", "Endocrinology & Metabolism", "Gastroenterology & Hepatology", "Geriatrics & Gerontology", "Hematology", "Infectious Diseases", "Medicine, General & Internal", "Medicine, Research & Experimental", "Oncology", "Ophthalmology", "Orthopedics", "Pathology", "Pediatrics", "Psychiatry", "Public, Environmental & Occupational Health", "Radiology, Nuclear Medicine & Medical Imaging", "Respiratory System", "Surgery", "Urology & Nephrology")),
    DisciplineField("28", "Neuroscience", "Life Sciences", ("Behavioral Sciences", "Clinical Neurology", "Neuroimaging", "Neurosciences", "Psychology, Biological")),
    DisciplineField("29", "Nursing", "Health Sciences", ("Health Care Sciences & Services", "Nursing", "Primary Health Care", "Public, Environmental & Occupational Health")),
    DisciplineField("30", "Pharmacology, Toxicology and Pharmaceutics", "Life Sciences", ("Chemistry, Medicinal", "Pharmacology & Pharmacy", "Toxicology")),
    DisciplineField("31", "Physics and Astronomy", "Physical Sciences", ("Acoustics", "Astronomy & Astrophysics", "Optics", "Physics, Applied", "Physics, Atomic, Molecular & Chemical", "Physics, Condensed Matter", "Physics, Fluids & Plasmas", "Physics, Mathematical", "Physics, Multidisciplinary", "Physics, Nuclear", "Physics, Particles & Fields", "Quantum Science & Technology")),
    DisciplineField("32", "Psychology", "Social Sciences", ("Behavioral Sciences", "Psychiatry", "Psychology", "Psychology, Applied", "Psychology, Biological", "Psychology, Clinical", "Psychology, Developmental", "Psychology, Educational", "Psychology, Experimental", "Psychology, Mathematical", "Psychology, Multidisciplinary", "Psychology, Psychoanalysis", "Psychology, Social")),
    DisciplineField("33", "Social Sciences", "Social Sciences", ("Anthropology", "Area Studies", "Communication", "Criminology & Penology", "Demography", "Education & Educational Research", "Ethics", "Ethnic Studies", "Family Studies", "Geography", "International Relations", "Law", "Linguistics", "Political Science", "Public Administration", "Regional & Urban Planning", "Social Issues", "Social Sciences, Interdisciplinary", "Social Work", "Sociology", "Urban Studies", "Women's Studies")),
    DisciplineField("34", "Veterinary", "Health Sciences", ("Veterinary Sciences", "Zoology")),
    DisciplineField("35", "Dentistry", "Health Sciences", ("Dentistry, Oral Surgery & Medicine",)),
    DisciplineField("36", "Health Professions", "Health Sciences", ("Health Care Sciences & Services", "Health Policy & Services", "Medical Informatics", "Public, Environmental & Occupational Health", "Rehabilitation", "Sport Sciences")),
)


_BY_ID = {field.id: field for field in OPENALEX_FIELDS}


def _alias_key(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"^https?://openalex\.org/fields/", "", text)
    text = text.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "", text)


_ALIASES: dict[str, str] = {}
for _field in OPENALEX_FIELDS:
    for _value in (_field.id, _field.label, f"fields/{_field.id}", f"https://openalex.org/fields/{_field.id}"):
        _ALIASES[_alias_key(_value)] = _field.id


def _iter_values(values: object) -> Iterable[object]:
    if values is None:
        return ()
    if isinstance(values, str):
        if _alias_key(values) in _ALIASES:
            return (values,)
        return [part.strip() for part in re.split(r"[|;\n,]+", values) if part.strip()]
    if isinstance(values, Iterable):
        return values
    return (values,)


def normalize_discipline_ids(values: object) -> tuple[str, ...]:
    ids: list[str] = []
    for value in _iter_values(values):
        key = _alias_key(value)
        discipline_id = _ALIASES.get(key)
        if not discipline_id:
            continue
        if discipline_id not in ids:
            ids.append(discipline_id)
    return tuple(ids)


def list_discipline_fields() -> list[dict[str, object]]:
    return [field.to_dict() for field in OPENALEX_FIELDS]


def get_discipline_fields(values: object) -> tuple[DisciplineField, ...]:
    return tuple(_BY_ID[field_id] for field_id in normalize_discipline_ids(values))


def discipline_labels(values: object) -> tuple[str, ...]:
    return tuple(field.label for field in get_discipline_fields(values))


def discipline_summary(values: object) -> str:
    return ", ".join(discipline_labels(values))


def openalex_field_ids(values: object) -> tuple[str, ...]:
    return normalize_discipline_ids(values)


def openalex_field_filter(values: object) -> str:
    ids = openalex_field_ids(values)
    if not ids:
        return ""
    return "primary_topic.field.id:" + "|".join(ids)


def wos_categories(values: object) -> tuple[str, ...]:
    categories: list[str] = []
    for discipline in get_discipline_fields(values):
        for category in discipline.wos_categories:
            if category not in categories:
                categories.append(category)
    return tuple(categories)


def wos_category_clause(values: object, max_categories: int = 24) -> str:
    categories = wos_categories(values)[:max(1, int(max_categories or 24))]
    if not categories:
        return ""
    return "WC=(" + " OR ".join(categories) + ")"


def apply_wos_discipline_filter(query: str, values: object) -> str:
    query = (query or "").strip()
    clause = wos_category_clause(values)
    if not clause:
        return query
    if re.search(r"\bWC\s*=", query, flags=re.IGNORECASE):
        return query
    return f"{query} AND {clause}" if query else clause


def discipline_prompt_context(values: object, source: str) -> str:
    fields = get_discipline_fields(values)
    if not fields:
        return ""
    labels = ", ".join(field.label for field in fields)
    source = (source or "").strip().lower()
    if source == "openalex":
        return (
            f"\nDiscipline limit: {labels}.\n"
            f"The source request will apply OpenAlex filter={openalex_field_filter(values)}. "
            "Keep the search terms consistent with the selected disciplines, but do not output API parameters."
        )
    if source == "wos":
        return (
            f"\nDiscipline limit: {labels}.\n"
            f"Map this to Web of Science Categories using {wos_category_clause(values)}. "
            "Keep this WC= limiter in the final query."
        )
    return (
        f"\nDiscipline limit: {labels}.\n"
        "This source has no native shared taxonomy filter here, so include these disciplines as bibliographic search context."
    )


def discipline_source_note(values: object, source: str) -> str:
    fields = get_discipline_fields(values)
    if not fields:
        return ""
    labels = ", ".join(field.label for field in fields)
    source = (source or "").strip().lower()
    if source == "openalex":
        return f"discipline={labels}; filter={openalex_field_filter(values)}"
    if source == "wos":
        return f"discipline={labels}; {wos_category_clause(values)}"
    if source == "crossref":
        return f"discipline={labels}; query context only"
    return f"discipline={labels}"
