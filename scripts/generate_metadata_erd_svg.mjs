// Generate the metadata ERD from the canonical generated reference model.
// Keep the reviewed design in docs/assets/fabricops-metadata-layout.svg.
// Usage: node scripts/generate_metadata_erd_svg.mjs [--check]
import fs from "node:fs";
import path from "node:path";
const root = path.resolve(import.meta.dirname, "..");
function renderMetadataSvg(layout, models) {
  // Fan-out ports follow destination order: the farthest target takes the outer
  // corridor, keeping nearer routes nested instead of crossing their stems.
  const routes = [
    ["DATA_STEWARD","DATA_AGREEMENT","1-N","physical","M335 170H425",[335,170],[425,170],"One steward may participate in many agreements"],
    ["DATA_AGREEMENT","PIPELINE_REGISTRY","1-N","nested","M725 170H815",[725,170],[815,170],"One exact Agreement version governs many pipeline approvals, each retaining its ID, version and content hash"],
    ["PIPELINE_REGISTRY","DATA_CONTRACT","N-N","nested","M1115 170H1205",[1115,170],[1205,170],"Pipeline approvals may share multiple exact Contract versions; Registry ownership retains their IDs, versions and payload hashes"],
    ["PIPELINE_RUN","DATA_CONTRACT","N-N","nested","M725 464H755V388H1175V218H1205",[725,464],[1205,218],"Run operations reference exact table contract versions"],
    ["PIPELINE_REGISTRY","PIPELINE_RUN","1-N","nested","M900 253V328H575V423",[900,253],[575,423],"One Registry approval authorizes many Live runs through approval_id. Each approval also retains one Test run_id. Cardinality describes approvals, not the singleton authority row"],
    ["DATA_CATALOGUE","DATA_CONTRACT","1-N","physical","M1355 423V253",[1355,423],[1355,253],"Catalogue table to contract versions"],
    ["PIPELINE_RUN","GUARDRAIL_RESULTS","1-N","physical","M425 515H335",[425,515],[335,515],"Pipeline run to recorded guardrail outcomes"],
    ["PIPELINE_RUN","PROCESSING_STATE","1-N","physical","M725 504H815",[725,504],[815,504],"Pipeline run to typed processing state"],
    ["DATA_CATALOGUE","PROCESSING_STATE","1-N","physical","M1205 545H1115",[1205,545],[1115,545],"Catalogue table to source and target processing state"],
    ["DATA_CATALOGUE","DATA_PROFILED","1-N","physical","M1280 598V655H575V735",[1280,598],[575,735],"Catalogue table to column statistics"],
    ["DATA_CATALOGUE","DATA_PROFILED_FREQUENCY","1-N","logical","M1230 598V630H185V735",[1230,598],[185,735],"Catalogue column to frequency observations"],
    ["DATA_CATALOGUE","DATA_LINEAGE","1-N","physical","M1355 598V680H965V735",[1355,598],[965,735],"Catalogue table to source and target lineage"],
    ["DATA_CATALOGUE","DATA_ACCESS","1-N","physical","M1430 598V705H1355V735",[1430,598],[1355,735],"Catalogue table to observed permissions"],
    ["DATA_PROFILED","DATA_PROFILED_FREQUENCY","1-N","physical","M425 821H335",[425,821],[335,821],"Optional statistical profile reference on frequency rows"],
    ["DATA_CONTRACT","GUARDRAIL_RESULTS","1-N","physical","M1205 194H1145V363H185V423",[1205,194],[185,423],"Contract versions to their Guardrail results"]
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
    const transform=block.match(/transform="translate\(\s*0\s+(-?[\d.]+)\s*\)"/);
    boxes[name]=[Number(rect[1]),Number(rect[2])+(transform?Number(transform[1]):0),Number(rect[3]),Number(rect[4])];
    const pk=(model.primary_key||[]).map(value=>["PK",value]);
    const fk=(model.foreign_keys||[]).filter(row=>!pk.some(k=>k[1]===row.local_field)).map(row=>["FK",row.local_field]);
    // Show composite version references together without hiding either key.
    const groupedFk = fk.filter(([, value]) => !value.endsWith("_version") ||
      !fk.some(([, other]) => other === value.replace(/_version$/, "_id")))
      .map(([kind, value]) => [kind, value.endsWith("_id") && fk.some(([, other]) => other === value.replace(/_id$/, "_version"))
        ? value.replace(/_id$/, "_id/version") : value]);
    const nestedKeys = [...new Set(Object.values(models).flatMap(other => (other.foreign_keys || [])
      .filter(fk => fk.referenced_table === "METADATA_" + name && fk.referenced_field.includes("[]"))
      .map(fk => fk.referenced_field)))].map(value => ["UK", value]);
    const all=[...pk,...nestedKeys,...groupedFk], rows=all.length>5?[...all.slice(0,4),["",`+${all.length-4} more keys`]]:all;
    const x=Number(rect[1]), y=Number(rect[2]);
    let lines=rows.map(([kind,value],i)=>{
      const baseline=y+57+(name === "PIPELINE_REGISTRY" ? 20 : 24)*i;
      const label=kind?`<text x="${x+13}" y="${baseline}" fill="${kind==="PK"?"#008064":"#0574C5"}" font-weight="700" font-size="14" font-family="Arial, sans-serif">${kind}</text>\n`:"";
      const normalized=String(value);
      const visible=normalized.length>42?normalized.slice(0,39)+"…":normalized;
      return label+`<text x="${x+51}" y="${baseline}" fill="#243550" font-size="${normalized.length > 35 ? 11 : normalized.length > 31 ? 12 : 14}" font-family="Arial, sans-serif">${esc(visible)}</text>`;
    }).join("\n");
    block=block.replace(/^<text (?![^>\n]*fill="white")[^\n]*\n/gm,"");
    if (name === "PIPELINE_REGISTRY") lines += `\n<text x="${x+13}" y="${y+162}" fill="#1168B6" font-size="12" font-family="Arial, sans-serif">Written by Engineering and Governance</text>`;
    block=block.replace(/<title>Open metadata documentation:/,lines+(lines?"\n":"")+"<title>Open metadata documentation:");
    return block;
  });
  const named=Object.keys(models);
  if(named.length!==12||found.size!==named.length)throw Error("Canonical model / visual layout changed. Review placements for "+named.filter(n=>!found.has(n)).join(", "));
  for(const row of routes){if(!found.has(row[0])||!found.has(row[1]))throw Error("Unknown relationship table");if(row[0]===row[1])throw Error("Self-referential 1-N connector would be misleading: "+row[0]);}
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
    const [one,many]=card ? card.split("-") : ["", ""];
    return `<g class="metadata-er-relationship" data-from="${from}" data-to="${to}" data-cardinality="${card}" data-kind="${kind}">\n<title>${esc(label)} (${card ? esc(card) + "; " : ""}${kind === "nested" ? "exact nested reference; application-enforced" : kind === "logical" ? "logical identity reference" : "keyed reference; application-enforced"})</title>\n<path d="${d}" fill="none" stroke="${color}" stroke-width="${kind==="logical"?"1.9":"2.2"}" stroke-linecap="round" stroke-linejoin="round"/>\n${badge(start[0],start[1],one,color)}${badge(end[0],end[1],many,color)}\n</g>`;
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
