# Dashboard title
DASH_TITLE = "Commuting flows between Italian Regions"

# Default colors for the dashboard
BLACK_COLOR = "rgba(47, 79, 79, 1)"
INCOMING_COLOR = "rgba(0, 108, 151, 0.75)"
OUTGOING_COLOR = "rgba(199, 81, 51, 0.75)"
INTERNAL_COLOR = "rgba(47, 79, 79, 0.55)"

# Dataframes dtypes
ITA_REGIONS_DTYPES = {
    "cod_reg": "uint8",
    "den_reg": "object",
    "x": "object",
    "y": "object",
}

NODES_DTYPES = {
    "cod_reg": "uint8",
    "x": "float64",
    "y": "float64",
}

EDGES_DTYPES = {
    "motivo": "object",
    "interno": "bool",
    "flussi": "uint32",
    "reg_o": "uint8",
    "reg_d": "uint8",
    "x_o": "float64",
    "y_o": "float64",
    "x_d": "float64",
    "y_d": "float64",
}

# Dictionary that maps region code to its name
ITA_REGIONS = {
    1: "Piemonte",
    2: "Valle d'Aosta/Vallée d'Aoste",
    3: "Lombardia",
    4: "Trentino-Alto Adige/Südtirol",
    5: "Veneto",
    6: "Friuli-Venezia Giulia",
    7: "Liguria",
    8: "Emilia-Romagna",
    9: "Toscana",
    10: "Umbria",
    11: "Marche",
    12: "Lazio",
    13: "Abruzzo",
    14: "Molise",
    15: "Campania",
    16: "Puglia",
    17: "Basilicata",
    18: "Calabria",
    19: "Sicilia",
    20: "Sardegna",
}

# Dictionary of options (Label/option) for commuting purpose
COMMUTING_PURPOSE = {
    "Work": "Lavoro",
    "Study": "Studio",
    "Total": "Totale",
}

# Dashboard description
DASH_DESCR = f"""
<div>
  <hr />
  <p>A Panel dashboard showing <b style="color:{INCOMING_COLOR};">incoming</b>
    and <b style="color:{OUTGOING_COLOR};">outgoing</b> commuting flows
    for work and study between Italian Regions.</p>
  <p>The width of the curves reflects the magnitude of the flows.</p>
  <p>
    <a href="https://www.istat.it/it/archivio/139381" target="_blank">Commuting data</a> from the
    15th Population and Housing Census (Istat, 2011).
  </p>
  <hr />
</div>
"""
