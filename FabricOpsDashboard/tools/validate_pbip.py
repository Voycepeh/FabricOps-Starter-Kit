#!/usr/bin/env python3
# ruff: noqa: D103
"""Offline structural and repository-contract checks for the PBIP."""
from __future__ import annotations
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE=Path(__file__).resolve(); ROOT=HERE.parents[2]; PRODUCT=HERE.parents[1]; PBIP=PRODUCT/'FabricOpsDashboard'
MODEL=PBIP/'FabricOpsDashboard.SemanticModel/definition'; REPORT=PBIP/'FabricOpsDashboard.Report/definition'
errors=[]
def check(ok,msg):
 if not ok: errors.append(msg)

for p in PBIP.rglob('*.json'):
 try: json.loads(p.read_text())
 except Exception as exc: errors.append(f'invalid JSON {p.relative_to(ROOT)}: {exc}')
for p in [PBIP/'FabricOpsDashboard.pbip',PBIP/'FabricOpsDashboard.Report/definition.pbir',REPORT/'version.json',MODEL.parent/'definition.pbism',MODEL/'database.tmdl',MODEL/'model.tmdl',MODEL/'relationships.tmdl']:
 check(p.exists(),f'missing {p.relative_to(ROOT)}')
project=json.loads((PBIP/'FabricOpsDashboard.pbip').read_text()); pbir=json.loads((PBIP/'FabricOpsDashboard.Report/definition.pbir').read_text()); pbism=json.loads((MODEL.parent/'definition.pbism').read_text()); version=json.loads((REPORT/'version.json').read_text())
check(project.get('$schema')=='https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','PBIP schema reference mismatch')
check(project.get('artifacts')==[{'report':{'path':'FabricOpsDashboard.Report'}}],'PBIP must reference only its report folder')
check(pbir.get('$schema')=='https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','PBIR schema reference mismatch')
check(pbir.get('datasetReference',{}).get('byPath',{}).get('path')=='../FabricOpsDashboard.SemanticModel','PBIR semantic-model path mismatch')
check(pbism.get('$schema')=='https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','PBISM schema reference mismatch')
check(version=={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'},'PBIR version metadata mismatch')

pages=json.loads((REPORT/'pages/pages.json').read_text()); check(pages['pageOrder']==['overview','engineering_pipelines','governance_tables','data_owner','pipeline_detail','table_detail'],'page order mismatch')
relationships=(MODEL/'relationships.tmdl').read_text()
relationship_columns=re.findall(r"(?m)^\t(?:from|to)Column: (.+)$",relationships)
check(bool(relationship_columns) and all(re.fullmatch(r"'(?:[^']|'')+'\.'(?:[^']|'')+'",column) for column in relationship_columns),'TMDL relationship columns must use dotted quoted references')
cross_filter_values=re.findall(r"(?m)^\tcrossFilteringBehavior: (.+)$",relationships)
check(set(cross_filter_values)<={'oneDirection','bothDirections','automatic'},'TMDL relationship cross-filter behavior is invalid')
for pid in pages['pageOrder']:
 page=json.loads((REPORT/f'pages/{pid}/page.json').read_text()); visuals=[]
 for p in (REPORT/f'pages/{pid}/visuals').glob('*/visual.json'):
  v=json.loads(p.read_text())
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
for path in ['$.operation_key','$.read_mode','$.write_mode','$.rows_read','$.rows_written','$.metrics.rows_read','$.metrics.columns','$.metrics.input_rows','$.metrics.input_columns','$.metrics.rows_committed','$.metrics.rows_inserted','$.metrics.rows_updated','$.metrics.rows_unchanged','$.metrics.versions_inserted','$.metrics.versions_expired','$.metrics.total_target_rows','$.metrics.measurement_source','$.stages','$.code','$.table.processing.load_strategy','$.guardrails','$.enrichment.table','$.dry_run.run_id','$.dry_run.status','$.dry_run.boundary_completed','$.dry_run.operations']:
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
 owner=mod.metadata_table_owner(table)
 schema_expression='GovernanceSchemaSql' if owner=='governance' else 'EngineeringSchemaSql'
 check(f'[" & {schema_expression} & "].[{table}]' in all_tmdl,f'{table}: query does not use its canonical {owner} schema')

# Validate every selected Pipeline Run JSON metric against the current typed
# logical contract, not only against a copied list of expected path strings.
def logical_type(table,*path):
 current=schemas[table]
 for name in path:
  if hasattr(current,'elementType'): current=current.elementType
  fields={field.name:field.dataType for field in current.fields}
  if name not in fields: return None
  current=fields[name]
 if hasattr(current,'elementType'): current=current.elementType
 return type(current).__name__

operation_paths={
 ('rows_read',):'LongType',('rows_written',):'LongType',
 ('metrics','rows_read'):'LongType',('metrics','columns'):'LongType',
 ('metrics','input_rows'):'LongType',('metrics','input_columns'):'LongType',
 ('metrics','rows_committed'):'LongType',('metrics','rows_inserted'):'LongType',
 ('metrics','rows_updated'):'LongType',('metrics','rows_unchanged'):'LongType',
 ('metrics','versions_inserted'):'LongType',('metrics','versions_expired'):'LongType',
 ('metrics','total_target_rows'):'LongType',('metrics','measurement_source'):'StringType',
}
for path,expected in operation_paths.items():
 actual=logical_type('METADATA_PIPELINE_RUN','operations',*path)
 check(actual==expected,f'METADATA_PIPELINE_RUN.operations.{".".join(path)}: expected {expected}, found {actual}')

# Ensure every report semantic reference resolves to a committed table column or measure.
columns={}; measures=set(); used_columns=set()
for p in (MODEL/'tables').glob('*.tmdl'):
 text=p.read_text()
 match=re.search(r"^table '?([^'\n]+)'?",text)
 if not match: continue
 table=match.group(1); columns[table]=set(re.findall(r"^\s*column '([^']+)'",text,re.M)); measures|={(table,m) for m in re.findall(r"^\s*measure '?([^'=\n]+)'?\s*=",text,re.M)}
for p in REPORT.glob('pages/*/visuals/*/visual.json'):
 raw=json.loads(p.read_text())
 for role in raw.get('visual',{}).get('query',{}).get('queryState',{}).values():
  for item in role.get('projections',[]):
   fld=item['field']; kind='Measure' if 'Measure' in fld else 'Column'; body=fld[kind]; table=body['Expression']['SourceRef']['Entity']; prop=body['Property']
   check((table,prop) in measures if kind=='Measure' else prop in columns.get(table,set()),f'{p.relative_to(ROOT)}: missing {kind} {table}.{prop}')
   if kind=='Column': used_columns.add((table,prop))
for ft,fc,tt,tc in re.findall(r"fromColumn: '([^']+)'\.'([^']+)'\s+toColumn: '([^']+)'\.'([^']+)'",(MODEL/'relationships.tmdl').read_text()):
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
 check(f"fromColumn: '{edge[0]}'.'{edge[1]}'\n\ttoColumn: '{edge[2]}'.'{edge[3]}'" in relationships,f'missing pipeline identity relationship: {edge}')
check("fromColumn: 'Guardrail Result'.'Table Key'\n\ttoColumn: 'Catalogue Table'.'Table Key'" in relationships,'missing table-to-guardrail relationship')

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
