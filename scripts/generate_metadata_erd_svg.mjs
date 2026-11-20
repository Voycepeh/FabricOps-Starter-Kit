// Generate the metadata ERD from the canonical generated reference model.
// Keep the reviewed design in docs/assets/fabricops-metadata-layout.svg.
// Usage: node scripts/generate_metadata_erd_svg.mjs [--check]
import fs from "node:fs";
import path from "node:path";
const root = path.resolve(import.meta.dirname, "..");
function renderMetadataSvg(layout, models) {
  // Show direct keys plus the Catalogue links for nested Run participation
  // and optional asset Guardrail outcomes. Draft authoring and promotion details stay scoped.
  const directKey = (name, field) => !field.local_field.includes("[]") && !field.referenced_field.includes("[]") &&
    !(name === "PIPELINE_RUN" && field.local_field === "promotion_id" && field.referenced_table === "METADATA_PIPELINE_REGISTRY");
  const routes = [
    ["DATA_STEWARD","DATA_AGREEMENT","1-N","physical","M1205 170H1115",[1205,170],[1115,170],"One steward may participate in many agreements"],
    ["DATA_AGREEMENT","DATA_CONTRACT_ACTIVATION","1-N","physical","M815 170H725",[815,170],[725,170],"One exact Agreement version may govern many physical frozen Contract selections"],
    ["PIPELINE_ACTIVATION","PIPELINE_REGISTRY","1-N","physical","M1745 253V423",[1745,253],[1745,423],"Exact independently approved package authorizes Engineering deployment; approval does not deploy"],
    ["DATA_CONTRACT_ACTIVATION","DATA_CONTRACT","N-1","physical","M425 170H335",[425,170],[335,170],"Each physical workspace/Table ID activation references one exact frozen Contract version independently of Pipeline Promotion"],
    ["PIPELINE_RUN","GUARDRAIL_RESULTS","1-N","physical","M725 515H815",[725,515],[815,515],"Pipeline run to recorded guardrail outcomes"],
    ["DATA_CATALOGUE","DATA_PROFILED","1-N","physical","M185 598V735",[185,598],[185,735],"Catalogue asset to column statistics"],
    ["DATA_CATALOGUE","DATA_PROFILED_FREQUENCY","1-N","physical","M235 598V680H575V735",[235,598],[575,735],"Catalogue asset to frequency observations"],
    ["DATA_CATALOGUE","DATA_ACCESS","1-N","physical","M305 598V630H965V735",[305,598],[965,735],"Catalogue table to observed permissions"],
    ["DATA_PROFILED","DATA_PROFILED_FREQUENCY","1-N","physical","M335 821H425",[335,821],[425,821],"Optional statistical profile reference on frequency rows"],
    ["DATA_CONTRACT","GUARDRAIL_RESULTS","1-N","physical","M185 253V310H1355V510H1115",[185,253],[1115,510],"Contract versions to their Guardrail results"],
    ["DATA_CATALOGUE","PIPELINE_RUN","N-N","nested","M335 515H425",[335,515],[425,515],"Run asset participation via operations: asset_workspace_id + table_id + asset_type; participation does not prove transformation dependencies"],
    ["DATA_CATALOGUE","GUARDRAIL_RESULTS","0..1-N","optional","M260 423V360H965V423",[260,423],[965,423],"Optional Catalogue asset for Guardrail outcomes through asset_workspace_id + table_id + asset_type; pipeline-wide checks may have no asset"]
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
    const fk=(model.foreign_keys||[]).filter(row=>directKey(name,row)).filter(row=>!pk.some(k=>k[1]===row.local_field)).map(row=>["FK",row.local_field]);
    // Show composite version references together without hiding either key.
    const groupedFk = fk.filter(([, value]) => !value.endsWith("_version") ||
      !fk.some(([, other]) => other === value.replace(/_version$/, "_id")))
      .map(([kind, value]) => [kind, value.endsWith("_id") && fk.some(([, other]) => other === value.replace(/_id$/, "_version"))
        ? value.replace(/_id$/, "_id/version") : value]);
    const nestedKeys = [...new Set(Object.values(models).flatMap(other => (other.foreign_keys || [])
      .filter(fk => fk.referenced_table === "METADATA_" + name && fk.referenced_field.includes("[]"))
      .map(fk => fk.referenced_field)))].map(value => ["UK", value]);
    const catalogueReference = model.catalogue_reference_fields || [];
    const cataloguePrimary = name === "DATA_CATALOGUE";
    const authoringReference = model.catalogue_authoring_fields || [];
    const optionalReference = model.catalogue_optional_fields || [];
    const groupedPrimary = cataloguePrimary || authoringReference.length > 0;
    const primaryRows = groupedPrimary ? pk.map(([, field]) => ["", field])
      : catalogueReference.length && pk.length > 1 ? [["PK", model.primary_key.join(" + ")]]
      : pk;
    const keys = [...primaryRows, ...nestedKeys, ...groupedFk];
    const identityFields = model.asset_identity_fields.filter(field =>
      !model.primary_key.includes(field) && !catalogueReference.includes(field) && !authoringReference.includes(field) && !optionalReference.includes(field) && !fk.some(([, value]) => value === field));
    const fields = [
      ...catalogueReference,
      ...authoringReference,
      ...optionalReference,
      ...identityFields,
    ].map(value => ["", value]);
    if (cataloguePrimary) fields.push(["", "asset_workspace_name"], ["", "columns_json (current schema)"]);
    const all = [...keys, ...fields];
    const rows = all.length > 6 ? [...all.slice(0, 5), ["", `+${all.length - 5} more fields`]] : all;
    const rowSpacing = name === "PIPELINE_REGISTRY" || rows.length === 6 ? 20 : 24;
    const x=Number(rect[1]), y=Number(rect[2]);
    let lines=rows.map(([kind,value],i)=>{
      const baseline=y+57+rowSpacing*i;
      const label=kind?`<text x="${x+13}" y="${baseline}" fill="${kind==="PK"?"#7C3AED":"#2563EB"}" font-weight="700" font-size="14" font-family="Segoe UI, Arial, sans-serif">${kind}</text>\n`:"";
      const normalized=String(value);
      const visible=normalized.length>42?normalized.slice(0,39)+"…":normalized;
      return label+`<text x="${x+51}" y="${baseline}" fill="#19243A" font-size="${normalized.length > 35 ? 11 : normalized.length > 30 ? 12 : 14}" font-family="Segoe UI, Arial, sans-serif">${esc(visible)}</text>`;
    }).join("\n");
    const groups = [
      ["PK", groupedPrimary ? model.primary_key : [], 0, "Composite primary key"],
      ["FK", catalogueReference, keys.length, "Composite foreign key to DATA_CATALOGUE, checked by FabricOps"],
      ["REF", authoringReference, keys.length, "Catalogue authoring reference checked at draft creation"],
      ["REF", optionalReference, keys.length, "Optional physical Catalogue asset reference; pipeline-wide results may have none"],
    ];
    for (const [kind, groupFields, firstRow, title] of groups) {
      if (!groupFields.length) continue;
      const color = kind === "FK" ? "#2563EB" : "#7C3AED";
      const firstBaseline = y + 57 + firstRow * rowSpacing;
      const lastBaseline = firstBaseline + (groupFields.length - 1) * rowSpacing;
      const mid = (firstBaseline + lastBaseline) / 2;
      lines += `\n<g data-key-role="${kind}" data-key-fields="${esc(groupFields.join(","))}"><title>${title}</title><path d="M${x+45} ${firstBaseline-10}H${x+39}V${lastBaseline+4}H${x+45}" fill="none" stroke="${color}"/><text x="${x+13}" y="${mid}" fill="${color}" font-weight="700" font-size="${kind === "REF" ? 12 : 14}" font-family="Segoe UI, Arial, sans-serif">${kind}</text></g>`;
    }
    block=block.replace(/^<text (?![^>\n]*fill="white")[^\n]*\n/gm,"");
    if (name === "PIPELINE_REGISTRY") lines += `\n<text x="${x+13}" y="${y+162}" fill="#2563EB" font-size="12" font-family="Segoe UI, Arial, sans-serif">Engineering deployment evidence</text>`;
    block=block.replace(/<title>Open metadata documentation:/,lines+(lines?"\n":"")+"<title>Open metadata documentation:");
    return block;
  });
  const named=Object.keys(models);
  if(named.length!==12||found.size!==named.length)throw Error("Canonical model / visual layout changed. Review placements for "+named.filter(n=>!found.has(n)).join(", "));
  for(const row of routes){if(!found.has(row[0])||!found.has(row[1]))throw Error("Unknown relationship table");if(row[0]===row[1])throw Error("Self-referential 1-N connector would be misleading: "+row[0]);}
  // Every direct scalar key reference in this overview needs one connector.
  // Optional promotion provenance and nested references remain in the full schema.
  const edgeSet=new Set(routes.map(r=>[r[0],r[1]].sort().join("|")));
  for(const [name,model] of Object.entries(models)){
    for(const fk of (model.foreign_keys||[]).filter(field=>directKey(name,field))){
      const target=fk.referenced_table.replace(/^METADATA_/,"");
      // Same-table record references appear in the box's FK fields, not as cross-table connectors.
      if(target===name){
        if(!(model.primary_key||[]).includes(fk.referenced_field))throw Error("Invalid same-table record reference: "+name);
        continue;
      }
      if(!edgeSet.has([name,target].sort().join("|")))throw Error("Missing FK connector: "+name+" -> "+target);
    }
  }
  for (const [name, model] of Object.entries(models)) {
    if (!(model.catalogue_reference_fields || []).length) continue;
    if (JSON.stringify(model.catalogue_reference_fields) !== JSON.stringify(models.DATA_CATALOGUE.primary_key))
      throw Error("Catalogue parent reference differs from its unique asset key: " + name);
    if (!edgeSet.has([name, "DATA_CATALOGUE"].sort().join("|")))
      throw Error("Missing Catalogue parent connector: " + name);
  }
  // Keep both requested links grounded in the canonical asset reference fields.
  for (const [name, fields] of [
    ["GUARDRAIL_RESULTS", ["asset_workspace_id", "table_id", "asset_type"]],
    ["PIPELINE_RUN", ["operations[].asset_workspace_id", "operations[].table_id", "operations[].asset_type"]],
  ]) {
    if (JSON.stringify(models[name].asset_identity_fields) !== JSON.stringify(fields))
      throw Error("Catalogue asset reference changed; review connector: " + name);
    if (!edgeSet.has([name, "DATA_CATALOGUE"].sort().join("|")))
      throw Error("Missing Catalogue asset connector: " + name);
  }
  const badge=(x,y,label,color)=>{
    if(!label)return "";
    const str=esc(label);
    const halfWidth = label.length > 1 ? 19 : 13;
    return `<rect x="${x-halfWidth}" y="${y-11}" width="${halfWidth*2}" height="22" rx="6" fill="#FFFFFF" stroke="${color}" stroke-width="1.4"/><text x="${x}" y="${y+4.5}" text-anchor="middle" font-size="13" font-weight="700" font-family="Segoe UI, Arial, sans-serif" fill="${color}">${str}</text>`;
  };
  const direction=(a,b)=>{
    const dx=b[0]-a[0],dy=b[1]-a[1];
    const length=Math.hypot(dx,dy)||1;
    return [dx/length,dy/length];
  };
  const rendered=routes.map(r=>{
    const [from,to,card,kind,d,p0,p1,label]=r;
    const referenceFields = from === "DATA_CATALOGUE" ? models[to].catalogue_reference_fields : [];
    const referenceLabel = referenceFields?.length ? " through " + referenceFields.join(" + ") + " on new records" : "";
    const color=kind==="logical"?"#7C3AED":"#2563EB";
    // Explicit orientation follows the first and last path segments.
    const first=d.match(/^M(-?[\d.]+) (-?[\d.]+)([HV])(-?[\d.]+)/);
    const last=d.match(/([HV])(-?[\d.]+)$/);
    let start=[p0[0],p0[1]],end=[p1[0],p1[1]];
    if(first){const immediate=first[3]==="H"?[Number(first[4]),p0[1]]:[p0[0],Number(first[4])];let v=direction(p0,immediate);start=[p0[0]+v[0]*25,p0[1]+v[1]*25];}
    if(last){const horiz=last[1]==="H", target=boxes[to];
      const side=horiz?(end[0]<=target[0]?-1:1):(end[1]<=target[1]?-1:1);
      // Clamped badge offset stays outside the table, close to its connector.
      end=horiz?[end[0]+side*25,end[1]]:[end[0],end[1]+side*25];
    }
    const [one,many]=card ? card.split("-") : ["", ""];
    const relationshipLabel = from === "DATA_CATALOGUE" && to === "PIPELINE_RUN"
      ? '<text x="380" y="482" text-anchor="middle" font-size="12" font-family="Segoe UI, Arial, sans-serif" fill="#52627A">via</text><text x="380" y="497" text-anchor="middle" font-size="12" font-family="Segoe UI, Arial, sans-serif" fill="#52627A">operations</text>'
      : from === "DATA_CATALOGUE" && to === "DATA_CONTRACT"
      ? '<text x="203" y="337" font-size="13" font-family="Segoe UI, Arial, sans-serif" fill="#52627A">Draft authoring</text>'
      : "";
    return `<g class="metadata-er-relationship" data-from="${from}" data-to="${to}" data-cardinality="${card}" data-kind="${kind}">\n<title>${esc(label + referenceLabel)} (${card ? esc(card) + "; " : ""}${kind === "nested" ? "nested asset participation; join by identity" : kind === "logical" ? "logical identity reference" : kind === "optional" ? "optional physical asset reference" : "keyed reference; application-enforced"})</title>\n<path d="${d}" fill="none" stroke="${color}" stroke-width="${kind==="logical"?"1.9":"2.2"}" stroke-linecap="round" stroke-linejoin="round" ${["logical", "nested", "optional"].includes(kind)?'stroke-dasharray="5 4"':""}/>\n${badge(start[0],start[1],one,color)}${badge(end[0],end[1],many,color)}${relationshipLabel}\n</g>`;
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
