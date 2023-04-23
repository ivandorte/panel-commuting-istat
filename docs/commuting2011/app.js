importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.1/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/0.14.4/dist/wheels/bokeh-2.4.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/0.14.4/dist/wheels/panel-0.14.4-py3-none-any.whl', 'pyodide-http==0.1.0', 'holoviews>=1.15.4', 'numpy', 'pandas', 'shapely', 'networkx']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }

  // Load custom Python modules
  const custom_modules = ['https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/modules_pyodide/constants.py', 'https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/modules_pyodide/graphs.py', 'https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/modules_pyodide/indicators.py']
  for (const module of custom_modules) {
    let module_name;
    module_name = module.split('/').slice(-1)[0]
    await pyodide.runPythonAsync(`
        from pyodide.http import pyfetch
        module_pyodide = await pyfetch('${module}')
        with open('${module_name}', 'wb') as f:
            f.write(await module_pyodide.bytes())
      `);
  }

  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

import holoviews as hv
import pandas as pd
import panel as pn
from constants import (
    BLACK_COLOR,
    COMMUTING_PURPOSE,
    DASH_DESCR,
    DASH_TITLE,
    EDGES_DTYPES,
    ITA_REGIONS,
    ITA_REGIONS_DTYPES,
    NODES_DTYPES,
    NUMIND_CSS,
)
from graphs import get_flow_map
from indicators import (
    get_incoming_numind,
    get_internal_numind,
    get_outgoing_numind,
)

# Load the bokeh extension
hv.extension("bokeh")

# Set the sizing mode
pn.extension(sizing_mode="stretch_width")

# Load the CSS of the numerical indicator
pn.config.raw_css.append(NUMIND_CSS)

# Load the edges as a Dataframe
edges_df = pd.read_json(
    "https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/data/edges.json",
    orient="split",
    dtype=EDGES_DTYPES,
)

# Load the nodes as a Dataframe
nodes_df = pd.read_json(
    "https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/data/nodes.json",
    orient="split",
    dtype=NODES_DTYPES,
)

# Load the italian regions as a Dataframe
region_admin_bounds_df = pd.read_json(
    "https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/data/italian_regions.json",
    orient="split",
    dtype=ITA_REGIONS_DTYPES,
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
    region_admin_bounds=region_admin_bounds_df,
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
    logo="https://raw.githubusercontent.com/ivandorte/panel-commuting-istat/main/icons/home_work.svg",
    title=DASH_TITLE,
    theme="default",
    theme_toggle=False,
    header_background=BLACK_COLOR,
    main=[layout],
    main_max_width="1000px",
).servable()


await write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.runPythonAsync(`
    import json

    state.curdoc.apply_json_patch(json.loads('${msg.patch}'), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads("""${msg.location}""")
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()