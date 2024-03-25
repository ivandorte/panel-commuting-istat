import panel as pn
from modules.constants import INCOMING_COLOR, INTERNAL_COLOR, OUTGOING_COLOR

DEFAULT_COLOR = "white"
TITLE_SIZE = "18pt"
FONT_SIZE = "20pt"


def get_incoming_numind(edges, region_code, comm_purpose):
    """
    Returns the total incoming commuters to the selected Region.
    """

    # Get the value of incoming commuters
    if comm_purpose == "Totale":
        query = f"reg_d == {region_code} & interno == 0"
    else:
        query = f"(reg_d == {region_code} & motivo == '{comm_purpose}' & interno == 0)"

    flows = edges.query(query)["flussi"].sum()

    return pn.indicators.Number(
        name="Incoming",
        value=flows,
        default_color=DEFAULT_COLOR,
        styles={"background": INCOMING_COLOR, "text-align": "center"},
        title_size=TITLE_SIZE,
        font_size=FONT_SIZE,
        sizing_mode="stretch_width",
    )


def get_outgoing_numind(edges, region_code, comm_purpose):
    """
    Returns the outgoing commuters from
    the selected Region.
    """

    # Get the value of outgoing commuters
    if comm_purpose == "Totale":
        query = f"reg_o == {region_code} & interno == 0"
    else:
        query = f"(reg_o == {region_code} & motivo == '{comm_purpose}' & interno == 0)"

    flows = edges.query(query)["flussi"].sum()

    return pn.indicators.Number(
        name="Outgoing",
        value=flows,
        default_color=DEFAULT_COLOR,
        styles={"background": OUTGOING_COLOR, "text-align": "center"},
        title_size=TITLE_SIZE,
        font_size=FONT_SIZE,
        sizing_mode="stretch_width",
        align="center",
    )


def get_internal_numind(edges, region_code, comm_purpose):
    """
    Returns the number of internal commuters of
    the selected Region.
    """

    # Get the value of internal commuters
    if comm_purpose == "Totale":
        query = f"reg_o == {region_code} & interno == 1"
    else:
        query = f"(reg_o == {region_code} & motivo == '{comm_purpose}' & interno == 1)"

    flows = edges.query(query)["flussi"].sum()

    return pn.indicators.Number(
        name="Internal mobility",
        value=flows,
        default_color=DEFAULT_COLOR,
        styles={"background": INTERNAL_COLOR, "text-align": "center"},
        title_size=TITLE_SIZE,
        font_size=FONT_SIZE,
        sizing_mode="stretch_width",
        align="center",
    )
