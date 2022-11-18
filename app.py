import holoviews as hv
import networkx as nx
import pandas as pd
import panel as pn
from bokeh.models import HoverTool

# Load the bokeh extension
hv.extension("bokeh")

# Load Panel extensions
pn.extension()

# Set the sizing mode
pn.config.sizing_mode = "stretch_both"

# Default Colors
BLACK_COLOR = "#2F4F4F"
INCOMING_COLOR = "#006C97"
OUTGOING_COLOR = "#D44E00"

# App title
APP_TITLE = "Commuting flows between Italian Regions"

# Data source
ISTAT_LINK = "https://tinyurl.com/3hp5dhk5"
NE_LINK = "https://tinyurl.com/3ayyfmsv"

# HTML description
DASH_DESCR = f"""
<div>
  <hr />
  <p>A Panel dashboard showing <b style="color:{INCOMING_COLOR};">incoming</b>
     and <b style="color:{OUTGOING_COLOR};">outgoing</b> commuting flows
     for work and study between Italian Regions.</p>
  <p>The width of the curves reflects the magnitude of the flows.</p>
  <p>
    <a href="{ISTAT_LINK}" target="_blank">Commuting data</a> from the
    15th Population and Housing Census (Istat, 2011).
  </p>
  <p>
    <a href="{NE_LINK}" target="_blank">Administrative data</a> from
    Natural Earth.
  </p>
  <hr />
</div>
"""

# Load the input data
nodes_df = pd.read_json("https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/data/commuting_2011_nodes.json",
                        orient="split")

edges_df = pd.read_json("https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/data/commuting_2011_edges.json",
                        orient="split")

stats_df = pd.read_json("https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/data/commuting_2011_stats.json",
                        orient="split")

regions_df = pd.read_json("https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/data/italian_regions.json",
                          orient="split")

# Italian regions
ita_regions = dict(zip(stats_df["den_reg"], stats_df["cod_reg"]))
ita_regions = {key: value for key, value in sorted(ita_regions.items())}

# Commuting purpose - Work, Study, Total (Work + Study)
purpose = ["Work", "Study", "Total"]

# Region selector
region_select = pn.widgets.Select(
    name="Region:",
    options=ita_regions,
    sizing_mode="stretch_width"
    )

# Commuting purpose selector
purpose_select = pn.widgets.ToggleGroup(
    name="",
    options=purpose,
    behavior="radio",
    sizing_mode="stretch_width"
    )


def get_indicator_value(region_code, purpose, column):
    """
    Returns the number of commuters for the selected region, purpose
    and flow type (incoming, outgoing, internal)
    """

    if purpose == "Total":
        query = (stats_df["cod_reg"] == region_code)
        region_stats = stats_df[query]
        value = region_stats[column].sum()
    else:
        query = (stats_df["cod_reg"] == region_code) \
            & (stats_df["purpose"] == purpose)
        region_stats = stats_df[query]
        value = region_stats.iloc[0][column]
    return value


@pn.depends(region_select, purpose_select)
def get_incoming_num_ind(region_code, purpose):
    """
    Returns a numeric indicator showing
    the number of incoming commuters to
    the selected Region.
    """

    # Get the value of incoming commuters
    num_val = get_indicator_value(region_code,
                                  purpose,
                                  "incoming")

    return pn.indicators.Number(
        name="Incoming",
        value=num_val,
        default_color=BLACK_COLOR,
        title_size="18pt",
        font_size="24pt",
        sizing_mode="stretch_width"
        )


@pn.depends(region_select, purpose_select)
def get_outgoing_num_ind(region_code, purpose):
    """
    Returns a numeric indicator showing
    the number of outgoing commuters from
    the selected Region.
    """

    # Get the value of outgoing commuters
    num_val = get_indicator_value(region_code,
                                  purpose,
                                  "outgoing")

    return pn.indicators.Number(
        name="Outgoing",
        value=num_val,
        default_color=BLACK_COLOR,
        title_size="18pt",
        font_size="24pt",
        sizing_mode="stretch_width"
        )


@pn.depends(region_select, purpose_select)
def get_internal_num_ind(region_code, purpose):
    """
    Returns a numeric indicator showing
    the number of internal commuters of
    the selected Region.
    """

    # Get the value of internal commuters
    num_val = get_indicator_value(region_code,
                                  purpose,
                                  "internal")

    return pn.indicators.Number(
        name="Internal",
        value=num_val,
        default_color=BLACK_COLOR,
        title_size="18pt",
        font_size="24pt",
        sizing_mode="stretch_width"
        )


def get_commuters_stats(region_code, purpose, tp_flow):
    """
    Returns commuting statistics for the selected region, purpose
    and flow type (incoming and outgoing)
    """

    query = (edges_df["cod_ident"] == region_code) \
        & (edges_df["purpose"] == purpose)
    reg_column = "den_reg_o" if tp_flow == "Incoming" else "den_reg_d"

    commuters_stats = edges_df[query]
    commuters_stats = commuters_stats[commuters_stats["tp_flow"] == tp_flow]
    commuters_stats = commuters_stats[[reg_column, "commuters", "ln_cl"]]
    commuters_stats = commuters_stats.sort_values(by="commuters",
                                                  ascending=False)
    return commuters_stats


@pn.depends(region_select, purpose_select)
def get_ingoing_bar_plot(region_code, purpose):
    """
    Returns a bar plot showing the number of incoming commuters
    by Region of origin for the selected parameters.
    """

    def hook(plot, element):
        """
        Custom hook for disabling xaxis tick lines/labels
        """
        plot.state.xaxis.major_tick_line_color = None
        plot.state.xaxis.minor_tick_line_color = None
        plot.state.xaxis.major_label_text_font_size = "0pt"

    # Define a custom Hover tool
    ingoing_hover = HoverTool(
        tooltips=[
            ("Region", "@den_reg_o"),
            ("Commuters", "@commuters")
            ]
        )

    commuters_stats = get_commuters_stats(region_code, purpose, "Incoming")
    bar_color = commuters_stats["ln_cl"].iloc[0]
    bar_plt = hv.Bars(commuters_stats, "den_reg_o", "commuters")

    # Additional plot options
    bar_plt.opts(
        title=f"Incoming commuters by Region of origin",
        xlabel="",
        ylabel="Commuters",
        color=bar_color,
        alpha=0.7,
        line_color="rgba(0, 0, 0, 0)",
        show_legend=False,
        hooks=[hook],
        tools=[ingoing_hover]
        )

    return pn.pane.HoloViews(bar_plt, linked_axes=False)


@pn.depends(region_select, purpose_select)
def get_outgoing_bar_plot(region_code, purpose):
    """
    Returns a bar plot showing the number of outgoing commuters
    by Region of destination for the selected parameters.
    """

    def hook(plot, element):
        """
        Custom hook for disabling xaxis tick lines/labels
        """
        plot.state.xaxis.major_tick_line_color = None
        plot.state.xaxis.minor_tick_line_color = None
        plot.state.xaxis.major_label_text_font_size = "0pt"

    # Define a custom Hover tool
    outgoing_hover = HoverTool(
        tooltips=[
            ("Region", "@den_reg_d"),
            ("Commuters", "@commuters")
            ]
        )

    commuters_stats = get_commuters_stats(region_code, purpose, "Outgoing")

    bar_color = commuters_stats["ln_cl"].iloc[0]
    bar_plt = hv.Bars(commuters_stats, "den_reg_d", "commuters")

    # Additional plot options
    bar_plt.opts(
        title=f"Outgoing commuters by Region of destination",
        xlabel="",
        ylabel="Commuters",
        color=bar_color,
        alpha=0.7,
        invert_yaxis=True,
        show_legend=False,
        line_color="rgba(0, 0, 0, 0)",
        hooks=[hook],
        tools=[outgoing_hover]
        )

    return pn.Pane(bar_plt, linked_axes=False)


@pn.depends(region_select, purpose_select)
def get_region_flow_map(region_code, purpose):
    """
    Returns a Graph showing incoming and outgoing
    commuting flows for the selected parameters.
    """

    def hook(plot, element):
        """
        Custom hook for disabling x/y tick lines/labels
        """
        plot.state.xaxis.major_tick_line_color = None
        plot.state.xaxis.minor_tick_line_color = None
        plot.state.xaxis.major_label_text_font_size = "0pt"
        plot.state.yaxis.major_tick_line_color = None
        plot.state.yaxis.minor_tick_line_color = None
        plot.state.yaxis.major_label_text_font_size = "0pt"

    query_edges = (edges_df["cod_ident"] == region_code) \
        & (edges_df["purpose"] == purpose)
    query_nodes = (nodes_df["cod_ident"] == region_code) \
        & (nodes_df["purpose"] == purpose)
    query_regions = (regions_df["cod_reg"] == region_code)

    # Get the Region border
    region_border = regions_df[query_regions]

    # Graph's Edges
    edges = edges_df[query_edges]
    edges = edges.sort_values(by="commuters")

    # Use custom Bézier Curves to represent the Edges
    edges_curves = edges["path"].to_list()

    # Graph's Nodes
    nodes = hv.Nodes(nodes_df[query_nodes])

    # Draw the Region border
    region_border_path = hv.Path(region_border.to_dict('records'))
    region_border_path.opts(color=BLACK_COLOR,
                            line_width=1.5)

    # Define a custom Hover tool
    graph_hover = HoverTool(
        tooltips=[
            ("Origin", "@den_reg_o"),
            ("Destination", "@den_reg_d"),
            ("Commuters", "@commuters")
            ]
        )

    # Build a Graph from Edges, Nodes and Bézier curves
    commuters_graph = hv.Graph(
        (
            edges.drop("path", axis=1),
            nodes,
            edges_curves
         )
        )

    # Additional plot options
    commuters_graph.opts(
        title=f"Incoming and outgoing commuting flows",
        xlabel="",
        ylabel="",
        node_color="white",
        node_line_color=BLACK_COLOR,
        node_size="pt_size",
        node_marker="marker",
        edge_alpha=0.7,
        edge_color="ln_cl",
        edge_line_width="ln_w",
        inspection_policy="edges",
        tools=[graph_hover],
        hooks=[hook]
        )

    # Compose the flow map
    flow_map = \
        hv.element.tiles.CartoLight() * region_border_path * commuters_graph

    return flow_map


# Description pane
descr_pane = pn.pane.HTML(
    DASH_DESCR,
    style={'text-align': 'left'},
    sizing_mode="stretch_width"
    )

# Compose the left pane
left_pane = pn.Column(
    region_select,
    purpose_select,
    get_incoming_num_ind,
    get_outgoing_num_ind,
    get_internal_num_ind,
    descr_pane,
    width=200
    )

# Compose the layout
layout = pn.Row(
    left_pane,
    get_region_flow_map,
    pn.Column(
        get_ingoing_bar_plot,
        get_outgoing_bar_plot
        )
    )

# Turn into a deployable application
pn.template.FastListTemplate(
    site="Panel",
    title=APP_TITLE,
    theme="default",
    theme_toggle=False,
    header_background=BLACK_COLOR,
    main=[layout]
).servable()
