// Generate the metadata ERD from the canonical generated reference model.
// Keep the reviewed design in docs/assets/fabricops-metadata-layout.svg.
// Usage: node scripts/generate_metadata_erd_svg.mjs [--check]
import fs from "node:fs";
import path from "node:path";
const root = path.resolve(import.meta.dirname, "..");
function renderMetadataSvg(layout, models) {
  const routes = [
    ["DATA_STEWARD","DATA_AGREEMENT","1:N","physical","M335 170H425",[335,170],[425,170],"One steward may participate in many agreements"],
    ["DATA_AGREEMENT","ACTIVATION_STATE","","logical","M725 170H815",[725,170],[815,170],"Agreement to Activated Pipeline releases stored in Activation State"],
    ["ACTIVATION_STATE","DATA_CONTRACT","","logical","M1115 170H1205",[1115,170],[1205,170],"Activated releases reference frozen Data Contract versions"],
    ["PIPELINE_REGISTRY","ACTIVATION_STATE","","logical","M725 725H765V215H815",[725,725],[815,215],"Registered pipeline to approved releases stored inside Activation State"],
    ["ACTIVATION_STATE","PIPELINE_RUN","","logical","M900 253V356H575V423",[900,253],[575,423],"Approved Activated Pipeline releases authorize Live runs"],
    ["DATA_CATALOGUE","DATA_CONTRACT","1:N","physical","M1355 423V253",[1355,423],[1355,253],"Catalogue table to contract versions"],
    ["PIPELINE_RUN","GUARDRAIL_RESULTS","1:N","physical","M425 515H335",[425,515],[335,515],"Pipeline run to recorded guardrail outcomes"],
    ["PIPELINE_RUN","PROCESSING_STATE","1:N","physical","M725 504H815",[725,504],[815,504],"Pipeline run to typed processing state"],
    ["DATA_CATALOGUE","PROCESSING_STATE","1:N","physical","M1205 545H1115",[1205,545],[1115,545],"Catalogue table to source and target processing state"],
    ["PIPELINE_REGISTRY","PIPELINE_RUN","1:N","physical","M575 675V598",[575,675],[575,598],"Registered pipeline to its execution history"],
    ["DATA_CATALOGUE","DATA_PROFILED","1:N","physical","M1250 598V902H575V995",[1250,598],[575,995],"Catalogue table to column statistics"],
    ["DATA_CATALOGUE","DATA_PROFILED_FREQUENCY","","logical","M1290 598V877H185V995",[1290,598],[185,995],"Catalogue column to frequency observations"],
    ["DATA_CATALOGUE","DATA_LINEAGE","1:N","physical","M1355 598V927H965V995",[1355,598],[965,995],"Catalogue table to source and target lineage"],
    ["DATA_CATALOGUE","DATA_ACCESS","1:N","physical","M1430 598V963H1355V995",[1430,598],[1355,995],"Catalogue table to observed permissions"],
    ["DATA_PROFILED","DATA_PROFILED_FREQUENCY","1:N","physical","M425 1081H335",[425,1081],[335,1081],"Optional statistical profile reference on frequency rows"],
    ["DATA_CONTRACT","GUARDRAIL_RESULTS","1:N","physical","M1205 218H1165V388H185V423",[1205,218],[185,423],"Contract versions to their Guardrail results"]
  ];
  const esc = value => String(value).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const source = layout.indexOf("<a ");
  if(source < 0) throw Error("Missing template table anchors");
  const prefix = layout.slice(0,source).replace(/^<path [^\n]+\n/gm,"");
  let body = layout.slice(source);
  const found = new Set(), boxes = {};
  body = body.replace(/<a\b[^>]*>[\s\S]*?<\/a>/g, block => {
    const match = block.match(/<title>Open metadata documentation: ([A-Z_]+)<\/title>/);
    if(!match) throw Error("Unrecognized diagram table anchor");
    const name=match[1], model=models[name];
    if(!model) throw Error("Diagram contains table missing from canonical models: "+name);
    if(found.has(name)) throw Error("Duplicate table "+name);
    found.add(name);
    const rect=block.match(/<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/);
    if(!rect) throw Error("Missing table geometry for "+name);
    const transform=block.match(/transform="translate\(\s*0\s+([\d.]+)\s*\)"/);
    boxes[name]=[Number(rect[1]),Number(rect[2])+(transform?Number(transform[1]):0),Number(rect[3]),Number(rect[4])];
    const pk=(model.primary_key||[]).map(value=>["PK",value]);
    const fk=(model.foreign_keys||[]).filter(row=>!pk.some(k=>k[1]===row.local_field)).map(row=>["FK",row.local_field]);
    const all=[...pk,...fk], rows=all.length>5?[...all.slice(0,4),["",`+${all.length-4} more keys`]]:all;
    const x=Number(rect[1]), y=Number(rect[2]);
    let lines=rows.map(([kind,value],i)=>{
      const baseline=y+57+24*i;
      const label=kind?`<text x="${x+13}" y="${baseline}" fill="${kind==="PK"?"#008064":"#0574C5"}" font-weight="700" font-size="14" font-family="Arial, sans-serif">${kind}</text>\n`:"";
      const normalized=String(value);
      const visible=normalized.length>33?normalized.slice(0,30)+"…":normalized;
      return label+`<text x="${x+51}" y="${baseline}" fill="#243550" font-size="14" font-family="Arial, sans-serif">${esc(visible)}</text>`;
    }).join("\n");
    block=block.replace(/^<text (?![^>\n]*fill="white")[^\n]*\n/gm,"");
    block=block.replace(/<title>Open metadata documentation:/,lines+(lines?"\n":"")+"<title>Open metadata documentation:");
    return block;
  });
  const named=Object.keys(models);
  if(named.length!==13||found.size!==named.length)throw Error("Canonical model / visual layout changed. Review placements for "+named.filter(n=>!found.has(n)).join(", "));
  for(const row of routes){if(!found.has(row[0])||!found.has(row[1]))throw Error("Unknown relationship table");if(row[0]===row[1])throw Error("Self-referential 1:N connector would be misleading: "+row[0]);}
  // Every canonical cross-table physical FK requires a visible connector; logical links
  // are also deliberate and carry explanatory SVG <title> tooltips.
  const edgeSet=new Set(routes.map(r=>[r[0],r[1]].sort().join("|")));
  for(const [name,model] of Object.entries(models)){
    for(const fk of model.foreign_keys||[]){
      const target=fk.referenced_table.replace(/^METADATA_/,"");
      // Same-table record references appear in the box's FK fields, not as cross-table connectors.
      if(target===name){
        if(!(model.primary_key||[]).includes(fk.referenced_field))throw Error("Invalid same-table record reference: "+name);
        continue;
      }
      if(!edgeSet.has([name,target].sort().join("|")))throw Error("Missing FK connector: "+name+" -> "+target);
    }
  }
  const badge=(x,y,label,color)=>{
    if(!label)return "";
    const str=esc(label);
    return `<rect x="${x-11}" y="${y-11}" width="22" height="22" rx="6" fill="#FFFFFF" stroke="${color}" stroke-width="1.4"/><text x="${x}" y="${y+4.5}" text-anchor="middle" font-size="13" font-weight="700" font-family="Arial, sans-serif" fill="${color}">${str}</text>`;
  };
  const direction=(a,b)=>{
    const dx=b[0]-a[0],dy=b[1]-a[1];
    const length=Math.hypot(dx,dy)||1;
    return [dx/length,dy/length];
  };
  const rendered=routes.map(r=>{
    const [from,to,card,kind,d,p0,p1,label]=r;
    const color=kind==="logical"?"#7144AE":"#1168B6";
    // Explicit orientation follows the first and last path segments.
    const first=d.match(/^M(-?[\d.]+) (-?[\d.]+)([HV])(-?[\d.]+)/);
    const last=d.match(/([HV])(-?[\d.]+)$/);
    let start=[p0[0],p0[1]],end=[p1[0],p1[1]];
    if(first){const immediate=first[3]==="H"?[Number(first[4]),p0[1]]:[p0[0],Number(first[4])];let v=direction(p0,immediate);start=[p0[0]+v[0]*25,p0[1]+v[1]*25];}
    if(last){const horiz=last[1]==="H";let side=(horiz?end[0]-p0[0]:end[1]-p0[1])>=0?-1:1;
      // Clamped badge offset stays outside the table, close to its connector.
      end=horiz?[end[0]+side*25,end[1]]:[end[0],end[1]+side*25];
    }
    const [one,many]=card ? card.split(":") : ["", ""];
    return `<g class="metadata-er-relationship" data-from="${from}" data-to="${to}" data-cardinality="${card}" data-kind="${kind}">\n<title>${esc(label)} (${card ? esc(card) + "; " : ""}${kind === "logical" ? "conceptual reference; no declared physical FK or table-row cardinality" : "physical keyed relationship"})</title>\n<path d="${d}" fill="none" stroke="${color}" stroke-width="${kind==="logical"?"1.9":"2.2"}" stroke-linecap="round" stroke-linejoin="round"${kind==="logical"?' stroke-dasharray="7 7"':""}/>\n${badge(start[0],start[1],one,color)}${badge(end[0],end[1],many,color)}\n</g>`;
  }).join("\n");
  return prefix+`<g id="metadata-er-relationships" aria-label="Metadata table relationships">\n${rendered}\n</g>\n`+body;
}
const overview = fs.readFileSync(path.join(root, "docs/reference/metadata.md"), "utf8");
const openTag = '<script type="application/json" class="metadata-explorer-model">';
const start = overview.indexOf(openTag);
const end = start < 0 ? -1 : overview.indexOf("</script>", start);
const match = start < 0 || end < 0 ? null : [null, overview.slice(start + openTag.length, end).trim()];
if (!match) throw new Error("Missing canonical metadata model in generated overview. Regenerate metadata references first.");
const models = JSON.parse(match[1]);
// Git on Windows may check out SVG and Markdown as CRLF. Normalise both
// inputs and comparisons so line endings never look like a metadata change;
// the emitted artifact is consistently LF on every operating system.
const normaliseNewlines = value => value.replace(/\r\n?/g, "\n");
const layout = normaliseNewlines(
  fs.readFileSync(path.join(root, "docs/assets/fabricops-metadata-layout.svg"), "utf8")
);
const target = path.join(root, "docs/assets/fabricops-metadata-approved.svg");
const output = normaliseNewlines(renderMetadataSvg(layout, models));
if (process.argv.includes("--check")) {
  const committed = fs.existsSync(target)
    ? normaliseNewlines(fs.readFileSync(target, "utf8"))
    : null;
  if (committed !== output) {
    console.error("Generated metadata diagram drift. Run node scripts/generate_metadata_erd_svg.mjs, then commit the SVG.");
    process.exitCode = 1;
  }
} else {
  fs.writeFileSync(target, output);
  console.log("Generated " + path.relative(root, target));
}
