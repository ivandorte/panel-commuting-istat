import holoviews as hv
import numpy as np
from bokeh.models import HoverTool
from modules.constants import (
    BLACK_COLOR,
    INCOMING_COLOR,
    ITA_REGIONS,
    OUTGOING_COLOR,
)
from shapely.geometry import LineString

# Min/Max node size
MIN_PT_SIZE = 7
MAX_PT_SIZE = 10

# Min/Max curve width
MIN_LW = 1
MAX_LW = 10


def filter_edges(edges, region_code, comm_purpose):
    """
    This function filters the rows of the edges for
    the selected Region and commuting purpose.
    """

    if comm_purpose == "Totale":
        query = f"(reg_o == {region_code} & interno == 0) |"
        query += f" (reg_d == {region_code} & interno == 0)"
    else:
        query = (
            f"(reg_o == {region_code} & motivo == '{comm_purpose}' & interno == 0) |"
        )
        query += (
            f" (reg_d == {region_code} & motivo == '{comm_purpose}' & interno == 0)"
        )
    return edges.query(query)


def get_nodes(nodes, edges, region_code, comm_purpose):
    """
    Get the graph's nodes for the selected Region and commuting purpose
    """

    # Filter the edges by Region and commuting purpose
    filt_edges = filter_edges(edges, region_code, comm_purpose)

    # Find the unique values of region codes
    region_codes = np.unique(filt_edges[["reg_o", "reg_d"]].values)

    # Filter the nodes
    nodes = nodes[nodes["cod_reg"].isin(region_codes)]

    # Reoder the columns for hv.Graph
    nodes = nodes[["x", "y", "cod_reg"]]

    # Assign the node size
    nodes["size"] = np.where(nodes["cod_reg"] == region_code, MAX_PT_SIZE, MIN_PT_SIZE)

    # Assigns a marker to the nodes
    nodes["marker"] = np.where(nodes["cod_reg"] == region_code, "square", "circle")

    return nodes


def get_bezier_curve(x_o, y_o, x_d, y_d, steps=25):
    """
    Draw a Bézier curve defined by a start point, endpoint and a control points
    Source: https://stackoverflow.com/questions/69804595/trying-to-make-a-bezier-curve-on-pygame-library
    """

    # Generate the O/D linestring
    od_line = LineString([(x_o, y_o), (x_d, y_d)])

    # Calculate the offset distance of the control point
    offset_distance = od_line.length / 2

    # Create a line parallel to the original at the offset distance
    offset_pline = od_line.parallel_offset(offset_distance, "left")

    # Get the XY coodinates of the control point
    ctrl_x = offset_pline.centroid.x
    ctrl_y = offset_pline.centroid.y

    # Calculate the XY coordinates of the Bézier curve
    t = np.array([i * 1 / steps for i in range(0, steps + 1)])
    x_coords = x_o * (1 - t) ** 2 + 2 * (1 - t) * t * ctrl_x + x_d * t**2
    y_coords = y_o * (1 - t) ** 2 + 2 * (1 - t) * t * ctrl_y + y_d * t**2

    return (x_coords, y_coords)


def get_edge_width(flow, min_flow, max_flow):
    """
    This function calculates the width of the curves
    according to the magnitude of the flow.
    """

    return MIN_LW + np.power(flow - min_flow, 0.57) * (MAX_LW - MIN_LW) / np.power(
        max_flow - min_flow, 0.57
    )


def get_edges(nodes, edges, region_code, comm_purpose):
    """
    Get the graph's edges for the selected Region and commuting purpose
    """

    # Filter the edges by Region and commuting purpose
    filt_edges = filter_edges(edges, region_code, comm_purpose)

    # Aggregate the flows by Region of origin and destination
    if comm_purpose == "Totale":
        filt_edges = (
            filt_edges.groupby(["reg_o", "reg_d"])
            .agg(
                motivo=("motivo", "first"),
                interno=("interno", "first"),
                flussi=("flussi", "sum"),
            )
            .reset_index()
        )

    # Assign Region names
    filt_edges["den_reg_o"] = filt_edges["reg_o"].map(ITA_REGIONS)
    filt_edges["den_reg_d"] = filt_edges["reg_d"].map(ITA_REGIONS)

    # Add xy coordinates of origin
    filt_edges = filt_edges.merge(
        nodes.add_suffix("_o"), left_on="reg_o", right_on="cod_reg_o"
    )

    # Add xy coordinates of destination
    filt_edges = filt_edges.merge(
        nodes.add_suffix("_d"), left_on="reg_d", right_on="cod_reg_d"
    )

    # Get the Bézier curve
    filt_edges["curve"] = filt_edges.apply(
        lambda row: get_bezier_curve(row["x_o"], row["y_o"], row["x_d"], row["y_d"]),
        axis=1,
    )

    # Get the minimum/maximum flow
    min_flow = filt_edges["flussi"].min()
    max_flow = filt_edges["flussi"].max()

    # Calculate the curve width
    filt_edges["width"] = filt_edges.apply(
        lambda row: get_edge_width(
            row["flussi"],
            min_flow,
            max_flow,
        ),
        axis=1,
    )

    # Assigns the color to the incoming/outgoing edges
    filt_edges["color"] = np.where(
        filt_edges["reg_d"] == region_code, INCOMING_COLOR, OUTGOING_COLOR
    )

    filt_edges = filt_edges.sort_values(by="flussi")

    return filt_edges


def get_flow_map(nodes, edges, region_code, comm_purpose):
    """
    Returns a Graph showing incoming and outgoing commuting flows
    for the selected Region and commuting purpose.
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

    # Define a custom Hover tool
    flow_map_hover = HoverTool(
        tooltips=[
            ("Origin", "@den_reg_o"),
            ("Destination", "@den_reg_d"),
            ("Commuters", "@flussi"),
        ]
    )

    # Get the Nodes of the selected Region and commuting purpose
    region_graph_nodes = get_nodes(nodes, edges, region_code, comm_purpose)

    # Get the Edges of the selected Region and commuting purpose
    region_graph_edges = get_edges(nodes, edges, region_code, comm_purpose)

    # Get the list of Bézier curves
    curves = region_graph_edges["curve"].to_list()

    # Build a Graph from Edges, Nodes and Bézier curves
    region_flow_graph = hv.Graph(
        (region_graph_edges.drop("curve", axis=1), region_graph_nodes, curves)
    )

    # Additional plot options
    region_flow_graph.opts(
        title="Incoming and outgoing commuting flows",
        xlabel="",
        ylabel="",
        node_color="white",
        node_hover_fill_color="magenta",
        node_line_color=BLACK_COLOR,
        node_size="size",
        node_marker="marker",
        edge_color="color",
        edge_hover_line_color="magenta",
        edge_line_width="width",
        inspection_policy="edges",
        tools=[flow_map_hover],
        hooks=[hook],
        frame_height=500,
    )

    # Compose the flow map
    positron_ret = hv.Tiles(
        "https://a.basemaps.cartocdn.com/light_all/{Z}/{X}/{Y}@2x.png",
        name="Positron (retina)",
    )
    flow_map = positron_ret * region_flow_graph

    return flow_map
