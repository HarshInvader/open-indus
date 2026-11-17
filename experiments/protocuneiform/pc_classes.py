"""Function classes of proto-cuneiform signs (base names, CDLI/Englund sign list).

Assigned from the standard readings of the archaic signs (Englund 1998, "Texts from the Late Uruk
Period", OBO 160/1; Green & Nissen 1987; CDLI sign names, which follow later Sumerian values).
Written BEFORE any shape match or Indus distribution was computed, from PC scholarship only.
Signs whose administrative function I am not confident of are left UNKNOWN (not guessed).
"""

CLASSES = {
    # commodities: grain and cereal products / rations
    "GRAIN_FOOD": ["SZE", "GAR", "NINDA2", "GU7"],
    # liquids and dairy products
    "LIQUID_DAIRY": ["KASZ", "GA", "NI", "KISIM", "GARA2"],
    # vessels and containers (incl. measuring vessels)
    "VESSEL": ["DUG", "UTUL", "BUR", "SILA3", "SZAGAN", "SZEN", "GA2", "SZAKIR"],
    # textiles and fibre
    "TEXTILE": ["TUG2", "SIG2", "GADA"],
    # livestock, fish, fowl
    "LIVESTOCK": ["UDU", "U8", "UDUNITA", "MASZ", "MASZ2", "UD5", "GU4", "AB2", "AMAR", "SILA4",
                  "SILANITA", "KU6", "SUHUR", "MUSZEN", "KIR11", "DARA4", "GUKKAL", "ESZGAR", "SZUBUR"],
    # other goods: metals, aromatics, wood, reed, plants, salt, fruit
    "OTHER_GOODS": ["URUDU", "KU3", "SZIM", "NAGA", "GISZ", "GI", "MUN", "U2", "HASZHUR", "NUNUZ",
                    "GISZIMMAR", "SAR", "IM"],
    # offices, titles, professions, persons and worker categories
    "OFFICE_PERSON": ["EN", "SANGA", "NAMESZDA", "NIMGIR", "SUKKAL", "NAR", "NAGAR", "ESZDA", "BAHAR2",
                      "SAL", "ERIM", "ERIN", "GURUSZ", "GURUSZDA", "UKKIN", "LU2", "NIN", "SAG", "SZITA",
                      "UMUN2", "ABGAL", "KINGAL", "GAL", "PA", "AMA", "SZESZ", "SZIDIM", "LAGAR"],
    # places, institutions, deities, fields, waterways
    "PLACE_INST": ["AN", "E2", "UNUG", "KI", "URI3", "URI", "KUR", "MUSZ3", "BARA2", "TUR3", "AB", "ZABALAM",
                   "SZURUPPAK", "ADAB", "URU", "EZEN", "IDIGNA", "KISAL", "GAN2", "DILMUN", "KALAM",
                   "KASKAL", "NIM", "E", "KAR2"],
}
COMMODITY = {"GRAIN_FOOD", "LIQUID_DAIRY", "VESSEL", "TEXTILE", "LIVESTOCK", "OTHER_GOODS"}

BASE2CLASS = {b: c for c, bs in CLASSES.items() for b in bs}


def base(name):
    import re
    return re.sub(r"(~.*|@.*)$", "", name)


def pc_class(name):
    return BASE2CLASS.get(base(name), "UNKNOWN")
