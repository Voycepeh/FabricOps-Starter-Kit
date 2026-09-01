"""Generate the public-function call-flow dashboard from normalized graph JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import public_function_call_flows_dashboard_legacy as _legacy


for _name in dir(_legacy):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_legacy, _name)


_HYDRATE_NORMALIZED_GRAPH_JS = r"""
function hydrateNormalizedFlows(data){
  if(!data||!Array.isArray(data.relationships))return data;
  const byQn=new Map((data.defined_functions||[]).map(row=>[row.qualified_name,row]));
  const publicQns=new Set((data.public_functions||[]).map(row=>row.qualified_name));
  const children=new Map();
  (data.relationships||[]).forEach(rel=>{
    const caller=rel.caller_qualified_name, callee=rel.callee_qualified_name;
    if(!caller||!callee)return;
    if(!children.has(caller))children.set(caller,[]);
    children.get(caller).push(rel);
  });
  children.forEach(rows=>rows.sort((a,b)=>String(a.callee_qualified_name).localeCompare(String(b.callee_qualified_name))));

  function flowType(fn,qn,rootQn){
    if(qn===rootQn)return fn.function_type==='widget_function'?'widget_function':'public_function';
    if(publicQns.has(qn)&&fn.function_type!=='widget_function')return 'public_dependency';
    return fn.function_type||'shared_function';
  }

  function expand(rootQn){
    const rows=[];
    function visit(qn,depth,parent,stack,relationship){
      const fn=byQn.get(qn)||{qualified_name:qn,function_name:String(qn).split('.').pop(),source_path:'',source_start_line:0,source_end_line:0,function_type:'shared_function'};
      const recursive=stack.has(qn);
      rows.push({...fn,
        depth,
        function_type:flowType(fn,qn,rootQn),
        parent_qualified_name:parent,
        edge_type:parent?'direct':'root',
        architecture_violations:relationship?.architecture_violations||[],
        violation_types:relationship?.violation_types||[],
        violation_details:relationship?.violation_details||[],
        call_count_from_parent:parent?(relationship?.call_count||1):0,
        recursive
      });
      if(recursive)return;
      const next=new Set(stack);next.add(qn);
      (children.get(qn)||[]).forEach(rel=>visit(rel.callee_qualified_name,depth+1,qn,next,rel));
    }
    visit(rootQn,0,null,new Set(),null);
    return rows;
  }

  (data.public_functions||[]).forEach(publicFunction=>{
    if(!Array.isArray(publicFunction.flow))publicFunction.flow=expand(publicFunction.qualified_name);
  });
  return data;
}
"""


def render_dashboard(
    payload: dict[str, Any] | None = None,
    *,
    embed_json: bool = False,
    data_url: str = DASHBOARD_DATA_URL,
    metadata_url: str = ARTIFACT_METADATA_URL,
) -> str:
    """Render the existing dashboard and hydrate expanded flows from relationships at load time."""
    html = _legacy.render_dashboard(
        payload=payload,
        embed_json=embed_json,
        data_url=data_url,
        metadata_url=metadata_url,
    )
    html = html.replace(
        ".then(renderDashboard).catch(showDataLoadError);",
        ".then(bundle=>{hydrateNormalizedFlows(bundle.data);return bundle}).then(renderDashboard).catch(showDataLoadError);",
    )
    return html.replace("</script></main></body></html>", _HYDRATE_NORMALIZED_GRAPH_JS + "\n</script></main></body></html>")


def write_dashboard(dashboard_path: Path = DASHBOARD_PATH) -> None:
    """Write only the public function call-flow dashboard HTML output."""
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(render_dashboard(), encoding="utf-8")
    if dashboard_path == DASHBOARD_PATH:
        update_generated_artifact_metadata(
            artifact_key="public_function_call_flows_dashboard",
            label="Public function call-flow dashboard",
            generator="scripts/generate_public_function_call_flows_dashboard.py",
            output_path="docs/assets/public-function-call-flows-dashboard.html",
        )


def main() -> None:
    """Generate only the public function call-flow dashboard artifact."""
    write_dashboard()


if __name__ == "__main__":
    main()
