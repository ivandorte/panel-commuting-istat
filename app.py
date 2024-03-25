import os
import pathlib

import holoviews as hv
import pandas as pd
import panel as pn
from modules.constants import (
    BLACK_COLOR,
    COMMUTING_PURPOSE,
    DASH_DESCR,
    DASH_TITLE,
    EDGES_DTYPES,
    ITA_REGIONS,
    NODES_DTYPES,
)
from modules.graphs import get_flow_map
from modules.indicators import (
    get_incoming_numind,
    get_internal_numind,
    get_outgoing_numind,
)

# Load the bokeh extension
hv.extension("bokeh")

# Disable webgl: https://github.com/holoviz/panel/issues/4855
hv.renderer("bokeh").webgl = False  # Disable Webgl

# Set the sizing mode
pn.extension(sizing_mode="stretch_width")

ROOT = pathlib.Path(__file__).parent

# Load the edges as a Dataframe
edges_df = pd.read_json(
    os.path.join(ROOT, "data/edges.json"),
    orient="split",
    dtype=EDGES_DTYPES,
)

# Load the nodes as a Dataframe
nodes_df = pd.read_json(
    os.path.join(ROOT, "data/nodes.json"),
    orient="split",
    dtype=NODES_DTYPES,
)

# Region selector
region_options = dict(map(reversed, ITA_REGIONS.items()))
region_options = dict(sorted(region_options.items()))

region_select = pn.widgets.Select(
    name="Region:",
    options=region_options,
    sizing_mode="stretch_width",
)

# Toggle buttons to select the commuting purpose
purpose_select = pn.widgets.ToggleGroup(
    name="",
    options=COMMUTING_PURPOSE,
    behavior="radio",
    sizing_mode="stretch_width",
)

# Description pane
descr_pane = pn.pane.HTML(DASH_DESCR, style={"text-align": "left"})

# Numeric indicator for incoming flows
incoming_numind_bind = pn.bind(
    get_incoming_numind,
    edges=edges_df,
    region_code=region_select,
    comm_purpose=purpose_select,
)

# Numeric indicator for outgoing flows
outgoing_numind_bind = pn.bind(
    get_outgoing_numind,
    edges=edges_df,
    region_code=region_select,
    comm_purpose=purpose_select,
)

# Numeric indicator for internal flows
internal_numind_bind = pn.bind(
    get_internal_numind,
    edges=edges_df,
    region_code=region_select,
    comm_purpose=purpose_select,
)

# Flow map
flowmap_bind = pn.bind(
    get_flow_map,
    nodes=nodes_df,
    edges=edges_df,
    region_code=region_select,
    comm_purpose=purpose_select,
)

# Compose the layout
layout = pn.Row(
    pn.Column(
        region_select,
        purpose_select,
        pn.Row(incoming_numind_bind, outgoing_numind_bind),
        internal_numind_bind,
        descr_pane,
        width=350,
    ),
    flowmap_bind,
)

# Turn into a deployable application
pn.template.FastListTemplate(
    site="",
    logo=os.path.join(ROOT, "icons/home_work.svg"),
    title=DASH_TITLE,
    theme="default",
    theme_toggle=False,
    header_background=BLACK_COLOR,
    main=[layout],
    main_max_width="1000px",
).servable()
