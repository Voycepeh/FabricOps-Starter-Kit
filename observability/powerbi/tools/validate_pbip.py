#!/usr/bin/env python3
"""Offline structural and repository-contract checks for the PBIP."""
from __future__ import annotations
import importlib.util, json, re, sys
from pathlib import Path

HERE=Path(__file__).resolve(); ROOT=HERE.parents[3]; PRODUCT=HERE.parents[1]; PBIP=PRODUCT/'FabricOpsObservability'
MODEL=PBIP/'FabricOpsObservability.SemanticModel/definition'; REPORT=PBIP/'FabricOpsObservability.Report/definition'
errors=[]
def check(ok,msg):
 if not ok: errors.append(msg)

for p in PBIP.rglob('*.json'):
 try: json.loads(p.read_text())
 except Exception as exc: errors.append(f'invalid JSON {p.relative_to(ROOT)}: {exc}')
for p in [PBIP/'FabricOpsObservability.pbip',PBIP/'FabricOpsObservability.Report/definition.pbir',MODEL/'database.tmdl',MODEL/'model.tmdl',MODEL/'relationships.tmdl']:
 check(p.exists(),f'missing {p.relative_to(ROOT)}')
project=json.loads((PBIP/'FabricOpsObservability.pbip').read_text()); pbir=json.loads((PBIP/'FabricOpsObservability.Report/definition.pbir').read_text())
check({next(iter(a)) for a in project['artifacts']}=={'report','semanticModel'},'PBIP artifact references are incomplete')
check(pbir.get('datasetReference',{}).get('byPath',{}).get('path')=='../FabricOpsObservability.SemanticModel','PBIR semantic-model path mismatch')

pages=json.loads((REPORT/'pages/pages.json').read_text()); check(pages['pageOrder']==['overview','engineering_pipelines','governance_tables','data_owner','pipeline_detail','table_detail'],'page order mismatch')
for pid in pages['pageOrder']:
 page=json.loads((REPORT/f'pages/{pid}/page.json').read_text()); visuals=[]
 for p in (REPORT/f'pages/{pid}/visuals').glob('*/visual.json'):
  v=json.loads(p.read_text());
  if v.get('visual',{}).get('query'): visuals.append(v['name'])
 expected={(a,b,'DataFilter') for a in visuals for b in visuals if a!=b}; actual={(x['source'],x['target'],x['type']) for x in page.get('visualInteractions',[])}
 check(expected==actual,f'{pid}: interactions are not explicit all-pair DataFilter')
 check((page.get('visibility')=='HiddenInViewMode')==(pid in {'pipeline_detail','table_detail'}),f'{pid}: visibility mismatch')
 if pid in {'pipeline_detail','table_detail'}:
  check(page.get('type')=='Drillthrough' and page.get('pageBinding',{}).get('type')=='Drillthrough',f'{pid}: native drillthrough missing')

all_tmdl='\n'.join(p.read_text() for p in MODEL.rglob('*.tmdl'))
check(not re.search(r'\bSELECT\s+\*',all_tmdl,re.I),'SELECT * found')
check('HistoryWindowDays = 180' in (MODEL/'expressions.tmdl').read_text(),'history-window parameter missing')
check(all_tmdl.count('DATEADD(day,-')>=5,'history filter missing from run/diagnostic queries')
for forbidden in ['result_payload_json','warnings_json','supporting_documents_json','approved_usage_json','custom_fields_json']:
 check(forbidden not in all_tmdl,f'unneeded payload loaded: {forbidden}')
for path in ['$.operation_key','$.read_mode','$.write_mode','$.stages','$.code','$.table.processing.load_strategy','$.guardrails','$.enrichment.table','$.dry_run.run_id','$.dry_run.status','$.dry_run.boundary_completed','$.dry_run.operations']:
 check(path in all_tmdl,f'selective JSON path absent: {path}')

# Compare every intentionally selected physical field with the authoritative registry.
spec=importlib.util.spec_from_file_location('metadata_schemas',ROOT/'src/fabricops_kit/config/metadata_schemas.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
schemas=mod.metadata_table_schema_registry(logical=True)
selected={
'METADATA_PIPELINE_REGISTRY':{'execution_workspace_id','pipeline_id','pipeline_version','promotion_id','status','governed_notebook_id','promoted_at'},
'METADATA_PIPELINE_ACTIVATION':{'approval_id','submission_id','execution_workspace_id','pipeline_id','revision','status','decision_kind','package_json','expected_active_version','restores_promotion_id','expires_at','decided_at','review_note'},
'METADATA_PIPELINE_RUN':{'run_id','pipeline_id','execution_mode','workspace_id','started_at','completed_at','status','boundary_completed','pipeline_version','promotion_id','governed_notebook_id','operations','failures'},
'METADATA_GUARDRAIL_RESULTS':{'run_id','table_id','table_name','workspace_id','contract_id','contract_version','status','can_continue','severity','guardrail_type','rule_type','action','reason','_committed_at'},
'METADATA_DATA_CATALOGUE':{'metadata_level','table_id','column_id','workspace_id','store_type','layer','schema_name','table_name','column_name','data_type','load_strategy','last_profiled_at','is_active'},
'METADATA_DATA_PROFILED':{'profile_snapshot_id','table_id','column_id','workspace_id','row_count','null_percent','distinct_percent','min_value','max_value','_committed_at'},
'METADATA_DATA_ACCESS':{'user_principal','table_id','workspace_id','access_level','access_value','access_state','access_snapshot_id','user_type','role_name','permission_source','_committed_at'},
'METADATA_DATA_CONTRACT':{'contract_id','contract_version','evidence_workspace_id','contract_payload_json'},
'METADATA_DATA_CONTRACT_ACTIVATION':{'workspace_id','table_id','contract_id','contract_version','activation_id','revision','status','activated_at','agreement_id','agreement_version'},
'METADATA_DATA_AGREEMENT':{'agreement_id','agreement_version','agreement_name','domain','provider_steward_id','recipient_steward_id','start_date','expiry_date','business_purpose'},
'METADATA_DATA_STEWARD':{'steward_id','steward_name','contact','is_active'}}
for table,cols in selected.items():
 actual={f.name for f in schemas[table].fields}; check(cols<=actual,f'{table}: invented fields {sorted(cols-actual)}')

# Ensure every report semantic reference resolves to a committed table column or measure.
columns={}; measures=set(); used_columns=set()
for p in (MODEL/'tables').glob('*.tmdl'):
 text=p.read_text(); match=re.search(r"^table '?([^'\n]+)'?",text)
 if not match: continue
 table=match.group(1); columns[table]=set(re.findall(r"^\s*column '([^']+)'",text,re.M)); measures|={(table,m) for m in re.findall(r"^\s*measure '?([^'=\n]+)'?\s*=",text,re.M)}
for p in REPORT.glob('pages/*/visuals/*/visual.json'):
 raw=json.loads(p.read_text())
 for role in raw.get('visual',{}).get('query',{}).get('queryState',{}).values():
  for item in role.get('projections',[]):
   fld=item['field']; kind='Measure' if 'Measure' in fld else 'Column'; body=fld[kind]; table=body['Expression']['SourceRef']['Entity']; prop=body['Property']
   check((table,prop) in measures if kind=='Measure' else prop in columns.get(table,set()),f'{p.relative_to(ROOT)}: missing {kind} {table}.{prop}')
   if kind=='Column': used_columns.add((table,prop))
for ft,fc,tt,tc in re.findall(r"fromColumn: '([^']+)'\['([^']+)'\]\s+toColumn: '([^']+)'\['([^']+)'\]",(MODEL/'relationships.tmdl').read_text()):
 check(fc in columns.get(ft,set()) and tc in columns.get(tt,set()),f'relationship endpoint missing: {ft}.{fc} -> {tt}.{tc}')
 used_columns.update({(ft,fc),(tt,tc)})
for table,table_columns in columns.items():
 for column in table_columns:
  if f"'{table}'[{column}]" in all_tmdl: used_columns.add((table,column))
unused={(table,column) for table,table_columns in columns.items() for column in table_columns if (table,column) not in used_columns}
check(not unused,f'loaded model columns without a traceable reporting purpose: {sorted(unused)}')
required={'Registered Pipelines','Pipeline Identities','Pipelines Run','Submitted Dry Run Submissions','Approved Activation Decisions','Registered Physical Tables','Run Count','Successful Runs','Failed Runs','Incomplete Runs','Pipeline Success Rate','Run Duration Minutes','Historical Median Duration Minutes','Duration Deviation Percent','Active Contracts','Contract Coverage','Recorded Guardrail Failures','Recorded Blocking Guardrail Outcomes','Last Successful Execution','Latest Recorded Run Status','Tables With Agreement','Recorded Access Observations','Tables With Recorded Access'}
check(required<={name for table,name in measures if table=='Measures'},f'missing required measures: {sorted(required-{name for table,name in measures if table=="Measures"})}')
relationships=(MODEL/'relationships.tmdl').read_text()
for edge in [("Pipeline Activation","Pipeline Key","Pipeline","Pipeline Key"),("Pipeline Run","Pipeline Key","Pipeline","Pipeline Key"),("Pipeline Registry","Pipeline Key","Pipeline","Pipeline Key")]:
 check(f"fromColumn: '{edge[0]}'['{edge[1]}']\n\ttoColumn: '{edge[2]}'['{edge[3]}']" in relationships,f'missing pipeline identity relationship: {edge}')
check("fromColumn: 'Guardrail Result'['Table Key']\n\ttoColumn: 'Catalogue Table'['Table Key']" in relationships,'missing table-to-guardrail relationship')

# Representative test-only outcomes remain mutually exclusive and descriptive.
def outcome(status,boundary):
 if status=='failed': return 'Failed'
 if status in {'succeeded','ungoverned_completed','dry_run_completed'} and boundary: return 'Successful'
 return 'Incomplete'
check([outcome('failed',False),outcome('succeeded',True),outcome('running',False)]==['Failed','Successful','Incomplete'],'mock run outcome classification failed')
check('steward' in [p.parent.name for p in REPORT.glob('pages/data_owner/visuals/*/visual.json')],'Data Owner steward slicer missing')

if errors:
 print('\n'.join('ERROR: '+e for e in errors)); sys.exit(1)
print(f'PASS: {len(list(PBIP.rglob("*")))} PBIP paths checked; repository mappings, projections, interactions, drillthrough, measures and mock outcomes validated.')
