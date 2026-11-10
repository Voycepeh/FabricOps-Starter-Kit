#!/usr/bin/env python3
# ruff: noqa: D103, E731
"""Generate the committed FabricOps Dashboard PBIP sources."""
from __future__ import annotations
import json
import shutil
import uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; PROJECT=ROOT/'FabricOpsDashboard'
MODEL=PROJECT/'FabricOpsDashboard.SemanticModel'; REPORT=PROJECT/'FabricOpsDashboard.Report'
RS='https://developer.microsoft.com/json-schemas/fabric/item/report/definition'
NS=uuid.UUID('8e42a289-b2d5-4e75-8c4a-130514f2e663')
def gid(s): return str(uuid.uuid5(NS,s))
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text((json.dumps(v,indent=2)+'\n') if isinstance(v,dict) else v,encoding='utf-8')
def expr(t,c,m=False): return {('Measure' if m else 'Column'):{'Expression':{'SourceRef':{'Entity':t}},'Property':c}}
def vis(n,typ,x,y,w,h,roles=None,title=None,sync=None):
 v={'visualType':typ}
 if roles:
  query_state={}
  for role,fields in roles.items():
   query_role='Data' if typ=='cardVisual' and role=='Values' else role
   query_state[query_role]={'projections':[{'field':expr(*field),'queryRef':f'{field[0]}.{field[1]}','nativeQueryRef':field[1]} for field in fields]}
  v['query']={'queryState':query_state}
 if title:v['visualContainerObjects']={'title':[{'properties':{'show':{'expr':{'Literal':{'Value':'true'}}},'text':{'expr':{'Literal':{'Value':json.dumps(title)}}}}}], 'general':[{'properties':{'altText':{'expr':{'Literal':{'Value':json.dumps(title+' visual')}}}}}]}
 if sync:v['syncGroup']={'groupName':sync,'fieldChanges':True,'filterChanges':True}
 return {'$schema':f'{RS}/visualContainer/2.9.0/schema.json','name':n,'position':{'x':x,'y':y,'z':0,'height':h,'width':w,'tabOrder':y+x},'visual':v}
M=lambda n:[('Dashboard Metrics',n,True)]
C=lambda t,*cs:[(t,c,False) for c in cs]
PAGES={
'overview':('Platform Activity Overview',False,[
 vis('workspace','slicer',25,30,280,60,{'Values':C('Pipeline Run','Workspace Name')},'Workspace','workspace'),vis('mode','slicer',320,30,190,60,{'Values':C('Pipeline Run','Execution Mode')},'Execution mode'),vis('run_status','slicer',525,30,190,60,{'Values':C('Pipeline Run','Status')},'Run status'),vis('date','slicer',730,30,290,60,{'Values':C('Pipeline Run','Started At')},'Reporting period','date'),vis('refresh','cardVisual',1035,30,205,60,{'Values':M('Dataset Refreshed At')},'Dataset refreshed (UTC)'),
 vis('pipelines_run','cardVisual',25,115,225,105,{'Values':M('Pipelines Run')},'Pipelines with executions'),vis('runs','cardVisual',260,115,225,105,{'Values':M('Run Count')},'Recorded executions'),vis('successful','cardVisual',495,115,225,105,{'Values':M('Successful Runs')},'Successful'),vis('failed','cardVisual',730,115,225,105,{'Values':M('Failed Runs')},'Failed'),vis('incomplete','cardVisual',965,115,225,105,{'Values':M('Incomplete Runs')},'Incomplete'),
 vis('trend','lineChart',25,245,590,220,{'Category':C('Pipeline Run','Run Date'),'Y':M('Run Count')+M('Successful Runs')+M('Failed Runs')},'Execution volume and outcomes'),vis('workspace_activity','clusteredBarChart',635,245,555,220,{'Category':C('Pipeline Run','Workspace Name'),'Y':M('Run Count')},'Executions by workspace'),
 vis('pipeline_activity','tableEx',25,485,590,200,{'Values':C('Pipeline Run','Notebook Name','Execution Identity')+M('Run Count')+M('Pipeline Success Rate')+M('Last Recorded Execution')+M('Latest Recorded Run Status')},'Pipeline activity by recorded notebook name'),vis('recent_runs','tableEx',635,485,555,200,{'Values':C('Pipeline Run','Workspace Name','Notebook Name','Execution Identity','Execution Mode','Status','Started At','Completed At','Failure Count')},'Recent executions')]),
'engineering_pipelines':('Engineering — Pipelines',False,[
 vis('workspace_e','slicer',25,55,250,55,{'Values':C('Pipeline','Workspace ID')},'Workspace','workspace'),vis('pipeline_e','slicer',290,55,280,55,{'Values':C('Pipeline','Pipeline ID')},'Pipeline'),vis('mode_e','slicer',585,55,250,55,{'Values':C('Pipeline Run','Execution Mode')},'Recorded execution mode'),vis('date_e','slicer',850,55,280,55,{'Values':C('Pipeline Run','Started At')},'Run period','date'),
 vis('pipelines_e','cardVisual',25,135,220,105,{'Values':M('Pipelines Run')},'Unique pipelines that ran'),vis('runs_e','cardVisual',260,135,220,105,{'Values':M('Run Count')},'Recorded runs'),vis('success_e','cardVisual',495,135,220,105,{'Values':M('Successful Runs')},'Successful runs'),vis('failed_e','cardVisual',730,135,220,105,{'Values':M('Failed Runs')},'Failed runs'),vis('incomplete_e','cardVisual',965,135,225,105,{'Values':M('Incomplete Runs')},'Incomplete runs'),
 vis('performance_e','lineChart',25,270,520,225,{'Category':C('Pipeline Run','Started At'),'Y':M('Run Duration Minutes')+M('Historical Median Duration Minutes')},'Recorded duration and historical median'),vis('pipeline_list','tableEx',570,270,620,225,{'Values':C('Pipeline','Pipeline Key','Pipeline ID','Workspace ID')+C('Pipeline Registry','Pipeline Version','Status','Promotion ID','Promoted At','Fabric Notebook URL')+M('Run Count')+M('Latest Recorded Run Status')+M('Last Recorded Execution')},'Pipeline identities and recorded activity — drill through for details'),
 vis('activation_e','tableEx',25,520,555,165,{'Values':C('Pipeline Activation','Pipeline ID','Revision','Status','Decision Kind','Decided At','Submitted Dry Run ID','Submitted Dry Run Status','Submitted Dry Run Operation Count')},'Activation decisions and submitted Dry Run evidence'),vis('guardrail_e','tableEx',605,520,585,165,{'Values':C('Guardrail Result','Run ID','Table Name','Guardrail Type','Status','Can Continue','Action','Reason')},'Recorded Guardrail outcomes')]),
'governance_tables':('Governance — Tables',False,[
 vis('workspace_g','slicer',25,55,285,55,{'Values':C('Catalogue Table','Workspace ID')},'Workspace','workspace'),vis('catalogue_g','slicer',325,55,260,55,{'Values':C('Catalogue Table','Is Active')},'Catalogue state'),vis('activation_g','slicer',600,55,280,55,{'Values':C('Contract Activation','Status')},'Recorded activation status'),
 vis('tables_g','cardVisual',25,135,220,105,{'Values':M('Registered Physical Tables')},'Registered physical tables'),vis('contracts_g','cardVisual',260,135,220,105,{'Values':M('Active Contracts')},'Active Contract selections'),vis('agreements_g','cardVisual',495,135,220,105,{'Values':M('Tables With Agreement')},'Tables with an Agreement'),vis('profiled_g','cardVisual',730,135,220,105,{'Values':M('Profiled Tables')},'Tables with a profile'),vis('access_g','cardVisual',965,135,225,105,{'Values':M('Tables With Recorded Access')},'Tables with access observations'),
 vis('all_tables','tableEx',25,270,1165,265,{'Values':C('Catalogue Table','Table Key','Table ID','Workspace ID','Store Type','Layer','Schema Name','Table Name','Is Active')+M('Selected Contract')+M('Selected Agreement')+M('Latest Profiled At')+M('Recorded Access Observations')},'All registered physical tables — drill through to Table Detail'),
 vis('layers_g','clusteredBarChart',25,560,565,125,{'Category':C('Catalogue Table','Layer'),'Y':M('Registered Physical Tables')},'Tables by recorded layer'),vis('contracts_by_status','clusteredBarChart',615,560,575,125,{'Category':C('Contract Activation','Status'),'Y':M('Contract Selections')},'Contract selections by recorded status')]),
'data_owner':('Data Owner — Tables',False,[
 vis('steward','slicer',25,55,370,55,{'Values':C('Data Steward','Steward Display')},'Data Steward (all by default)'),vis('role','slicer',410,55,250,55,{'Values':C('Agreement Steward','Participation Role')},'Agreement participation role'),vis('domain','slicer',675,55,270,55,{'Values':C('Data Agreement','Domain')},'Domain'),
 vis('tables_o','cardVisual',25,135,220,105,{'Values':M('Registered Physical Tables')},'Associated physical tables'),vis('agreements_o','cardVisual',260,135,220,105,{'Values':M('Agreements')},'Agreements'),vis('contracts_o','cardVisual',495,135,220,105,{'Values':M('Active Contracts')},'Active Contract selections'),vis('profiled_o','cardVisual',730,135,220,105,{'Values':M('Profiled Tables')},'Tables with a profile'),vis('access_o','cardVisual',965,135,225,105,{'Values':M('Tables With Recorded Access')},'Tables with access observations'),
 vis('agreements_list','tableEx',25,270,500,230,{'Values':C('Data Agreement','Agreement ID','Agreement Name','Agreement Version','Domain','Business Purpose','Start Date','Expiry Date')+C('Agreement Steward','Participation Role')+C('Data Steward','Steward Name','Contact')},'Agreement participation'),vis('owner_tables','tableEx',550,270,640,230,{'Values':C('Catalogue Table','Table Key','Table Name','Schema Name')+M('Selected Contract')+M('Selected Agreement')+M('Latest Profiled At')+M('Recorded Access Observations')},'Associated tables — drill through to Table Detail'),
 vis('profile_o','clusteredBarChart',25,525,1165,160,{'Category':C('Catalogue Column','Column Name'),'Y':M('Average Null Percent')+M('Average Distinct Percent')},'Latest selected column profile')]),
'pipeline_detail':('Pipeline Detail',True,[
 vis('pipeline_d','slicer',25,55,330,55,{'Values':C('Pipeline','Pipeline Key')},'Pipeline'),vis('run_d','slicer',370,55,410,55,{'Values':C('Pipeline Run','Run ID')},'Selected recorded run'),
 vis('pstatus','cardVisual',25,135,220,105,{'Values':M('Latest Recorded Run Status')},'Recorded status'),vis('pduration','cardVisual',260,135,220,105,{'Values':M('Run Duration Minutes')},'Recorded duration'),vis('plast','cardVisual',495,135,280,105,{'Values':M('Last Successful Execution')},'Last successful execution'),vis('fabric_link','tableEx',800,135,390,105,{'Values':C('Pipeline Run','Pipeline ID','Pipeline Version','Promotion ID','Execution Mode','Fabric Notebook URL')},'Selected execution and governed notebook'),
 vis('history','lineChart',25,270,350,210,{'Category':C('Pipeline Run','Started At'),'Y':M('Run Duration Minutes')},'Recorded run history'),vis('activation_history','tableEx',400,270,370,210,{'Values':C('Pipeline Activation','Approval ID','Revision','Status','Decision Kind','Expected Active Version','Restores Promotion ID','Expires At','Decided At','Review Note','Submitted Dry Run ID','Submitted Dry Run Status','Submitted Dry Run Boundary Completed','Submitted Dry Run Operation Count')},'Activation decision history and submitted Dry Run evidence'),vis('operations','tableEx',795,270,395,210,{'Values':C('Run Operation','Operation Key','Table ID','Pipeline Role','Read Mode','Write Mode','Rows Read','Columns','Input Rows','Input Columns','Rows Committed','Rows Inserted','Rows Updated','Rows Unchanged','Versions Inserted','Versions Expired','Total Target Rows','Measurement Source','Contract ID','Contract Version','Status','Started At','Completed At','Destination Kind','Destination Table Name','Fabric Item URL')},'Selected run operations, tables and recorded execution metrics'),
 vis('stages','tableEx',25,505,555,180,{'Values':C('Run Stage','Operation Key','Stage','Status','Evaluation Status')},'Recorded sequential stages — absent stages were not recorded'),vis('failures','tableEx',605,505,585,180,{'Values':C('Run Failure','Failure Code','Exception Type')},'Recorded safe failure diagnostics')]),
'table_detail':('Table Detail',True,[
 vis('table_d','slicer',25,55,480,55,{'Values':C('Catalogue Table','Table Key')},'Physical workspace/Table'),
 vis('tcontract','cardVisual',25,135,275,105,{'Values':M('Selected Contract')},'Current recorded Contract'),vis('tagreement','cardVisual',315,135,275,105,{'Values':M('Selected Agreement')},'Current recorded Agreement'),vis('tprofiled','cardVisual',605,135,275,105,{'Values':M('Latest Profiled At')},'Latest profile timestamp'),vis('taccess','cardVisual',895,135,295,105,{'Values':M('Recorded Access Observations')},'Current access observations'),
 vis('identity','tableEx',25,270,430,190,{'Values':C('Catalogue Table','Table ID','Workspace ID','Store Type','Layer','Schema Name','Table Name','Load Strategy','Is Active')},'Catalogue identity'),vis('governance','tableEx',470,270,720,190,{'Values':C('Contract Activation','Activation ID','Revision','Status','Activated At')+C('Data Agreement','Agreement ID','Agreement Name','Agreement Version')+C('Data Contract','Contract Version','Evidence Workspace ID','Processing Strategy','Guardrail Count','Table Description')},'Recorded activation, Agreement and Contract'),
 vis('columns','tableEx',25,485,385,200,{'Values':C('Catalogue Column','Column ID','Column Name','Data Type')+C('Profiled Column','Profile Snapshot ID','Row Count','Null Percent','Distinct Percent','Minimum Value','Maximum Value','Profiled At')},'Latest selected column profile'),vis('access','tableEx',425,485,250,200,{'Values':C('Data Access','Access Snapshot ID','User Principal','User Type','Access Level','Access Value','Access State','Role Name','Permission Source','Observed At')},'Latest recorded access observations'),vis('guardrails','tableEx',690,485,275,200,{'Values':C('Guardrail Result','Run ID','Table Name','Contract ID','Contract Version','Severity','Guardrail Type','Rule Type','Status','Can Continue','Action','Reason','Committed At')},'Related recorded Guardrail outcomes'),vis('activity','tableEx',980,485,210,200,{'Values':C('Pipeline Run','Pipeline ID','Run ID','Started At')+C('Run Operation','Pipeline Role','Read Mode','Write Mode','Rows Read','Input Rows','Rows Committed','Measurement Source','Status')},'Related recorded pipeline activity and execution metrics')])}

def report():
 d=REPORT/'definition'; put(REPORT/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../FabricOpsDashboard.SemanticModel'}}}); put(REPORT/'.platform',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json','metadata':{'type':'Report','displayName':'FabricOps Dashboard','description':'FabricOps operational and governance dashboard.'},'config':{'version':'2.0','logicalId':gid('report')}})
 put(d/'version.json',{'$schema':f'{RS}/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
 put(d/'report.json',{'$schema':f'{RS}/report/3.0.0/schema.json','themeCollection':{'customTheme':{'name':'FabricOpsDashboard.json','reportVersionAtImport':{'visual':'2.9.0','page':'2.0.0','report':'3.0.0'},'type':'RegisteredResources'}}}); put(d/'pages/pages.json',{'$schema':f'{RS}/pagesMetadata/1.0.0/schema.json','pageOrder':list(PAGES),'activePageName':'overview'})
 for pid,(name,hidden,vs) in PAGES.items():
  q=[v for v in vs if v['visual'].get('query')]; pg={'$schema':f'{RS}/page/2.0.0/schema.json','name':pid,'displayName':name,'displayOption':'FitToPage','height':720,'width':1280,'visualInteractions':[{'source':a['name'],'target':b['name'],'type':'DataFilter'} for a in q for b in q if a is not b]}
  if hidden:
   pg['visibility']='HiddenInViewMode'; pg['type']='Drillthrough'
   if pid=='pipeline_detail': fields=[('Pipeline','Pipeline Key')]
   else: fields=[('Catalogue Table','Table Key')]
   pg['pageBinding']={'name':pid+'_drillthrough','type':'Drillthrough','referenceScope':'Default','acceptsFilterContext':'Default','parameters':[{'name':c,'fieldExpr':expr(t,c)} for t,c in fields]}
  put(d/f'pages/{pid}/page.json',pg)
  for v in vs:put(d/f"pages/{pid}/visuals/{v['name']}/visual.json",v)
 theme={'name':'FabricOps Dashboard','dataColors':['#0F766E','#14B8A6','#475569','#F59E0B','#DC2626'],'background':'#F8FAFC','foreground':'#172033','tableAccent':'#0F766E','visualStyles':{'*':{'*':{'background':[{'color':{'solid':{'color':'#FFFFFF'}},'transparency':0}],'border':[{'show':True,'color':{'solid':{'color':'#E2E8F0'}},'radius':4}],'title':[{'fontColor':{'solid':{'color':'#172033'}},'fontSize':11,'fontFamily':'Segoe UI Semibold'}]}}}}
 put(d/'StaticResources/RegisteredResources/FabricOpsDashboard.json',theme)

TABLES={
'Pipeline':([('Pipeline Key','string'),('Workspace ID','string'),('Pipeline ID','string')],"SELECT DISTINCT CONCAT(p.workspace_id,'|',p.pipeline_id) pipeline_key,p.workspace_id,p.pipeline_id FROM (SELECT execution_workspace_id workspace_id,pipeline_id FROM {E}.[METADATA_PIPELINE_REGISTRY] WHERE ({WF}='' OR execution_workspace_id={WF}) UNION SELECT workspace_id,pipeline_id FROM {E}.[METADATA_PIPELINE_RUN] WHERE started_at>=DATEADD(day,-{HD},SYSUTCDATETIME()) AND ({WF}='' OR workspace_id={WF}) UNION SELECT execution_workspace_id workspace_id,pipeline_id FROM {G}.[METADATA_PIPELINE_ACTIVATION] WHERE ({WF}='' OR execution_workspace_id={WF})) p"),
'Pipeline Registry':([('Pipeline Key','string'),('Pipeline Version','int64'),('Promotion ID','string'),('Status','string'),('Promoted At','dateTime'),('Fabric Notebook URL','string')],"SELECT pipeline_key,pipeline_version,promotion_id,status,promoted_at,CASE WHEN governed_notebook_id IS NULL OR governed_notebook_id='' THEN NULL ELSE CONCAT('https://app.fabric.microsoft.com/groups/',execution_workspace_id,'/notebooks/',governed_notebook_id) END fabric_notebook_url FROM (SELECT CONCAT(execution_workspace_id,'|',pipeline_id) pipeline_key,pipeline_version,promotion_id,status,governed_notebook_id,promoted_at,execution_workspace_id,ROW_NUMBER() OVER(PARTITION BY execution_workspace_id,pipeline_id ORDER BY pipeline_version DESC,promoted_at DESC) rn FROM {E}.[METADATA_PIPELINE_REGISTRY] WHERE ({WF}='' OR execution_workspace_id={WF})) p WHERE rn=1"),
'Pipeline Activation':([('Pipeline Key','string'),('Pipeline ID','string'),('Approval ID','string'),('Submission ID','string'),('Revision','int64'),('Status','string'),('Decision Kind','string'),('Expected Active Version','int64'),('Restores Promotion ID','string'),('Expires At','dateTime'),('Decided At','dateTime'),('Review Note','string'),('Submitted Dry Run ID','string'),('Submitted Dry Run Status','string'),('Submitted Dry Run Boundary Completed','boolean'),('Submitted Dry Run Operation Count','int64')],"SELECT CONCAT(a.execution_workspace_id,'|',a.pipeline_id) pipeline_key,a.pipeline_id,a.approval_id,a.submission_id,a.revision,a.status,a.decision_kind,a.expected_active_version,a.restores_promotion_id,a.expires_at,a.decided_at,a.review_note,JSON_VALUE(a.package_json,'$.dry_run.run_id') submitted_dry_run_id,JSON_VALUE(a.package_json,'$.dry_run.status') submitted_dry_run_status,CASE JSON_VALUE(a.package_json,'$.dry_run.boundary_completed') WHEN 'true' THEN CAST(1 AS bit) WHEN 'false' THEN CAST(0 AS bit) END submitted_dry_run_boundary_completed,(SELECT COUNT(1) FROM OPENJSON(a.package_json,'$.dry_run.operations')) submitted_dry_run_operation_count FROM {G}.[METADATA_PIPELINE_ACTIVATION] a WHERE ({WF}='' OR a.execution_workspace_id={WF})"),
'Pipeline Run':([('Run ID','string'),('Pipeline Key','string'),('Pipeline ID','string'),('Workspace ID','string'),('Workspace Name','string'),('Notebook Name','string'),('Execution Identity','string'),('Started At','dateTime'),('Completed At','dateTime'),('Run Date','dateTime'),('Status','string'),('Boundary Completed','boolean'),('Pipeline Version','int64'),('Promotion ID','string'),('Execution Mode','string'),('Failure Count','int64'),('Fabric Notebook URL','string')],"SELECT r.run_id,CONCAT(r.workspace_id,'|',r.pipeline_id) pipeline_key,r.pipeline_id,r.workspace_id,r._workspace_name workspace_name,r._notebook_name notebook_name,r.execution_identity,r.started_at,r.completed_at,CAST(r.started_at AS date) run_date,r.status,r.boundary_completed,r.pipeline_version,r.promotion_id,r.execution_mode,(SELECT COUNT(1) FROM OPENJSON(r.failures)) failure_count,CASE WHEN r.governed_notebook_id IS NULL OR r.governed_notebook_id='' THEN NULL ELSE CONCAT('https://app.fabric.microsoft.com/groups/',r.workspace_id,'/notebooks/',r.governed_notebook_id) END fabric_notebook_url FROM {E}.[METADATA_PIPELINE_RUN] r WHERE r.started_at>=DATEADD(day,-{HD},SYSUTCDATETIME()) AND ({WF}='' OR r.workspace_id={WF})"),
'Dashboard Refresh':([('Refreshed At','dateTime')],"SELECT SYSUTCDATETIME() refreshed_at"),
'Run Operation':([('Operation Key','string'),('Run ID','string'),('Table Key','string'),('Table ID','string'),('Pipeline Role','string'),('Read Mode','string'),('Write Mode','string'),('Rows Read','int64'),('Columns','int64'),('Input Rows','int64'),('Input Columns','int64'),('Rows Committed','int64'),('Rows Inserted','int64'),('Rows Updated','int64'),('Rows Unchanged','int64'),('Versions Inserted','int64'),('Versions Expired','int64'),('Total Target Rows','int64'),('Measurement Source','string'),('Contract ID','string'),('Contract Version','int64'),('Status','string'),('Started At','dateTime'),('Completed At','dateTime'),('Destination Kind','string'),('Destination Table Name','string'),('Fabric Item URL','string')],"SELECT o.operation_key,r.run_id,CONCAT(COALESCE(o.destination_workspace_id,r.workspace_id),'|',o.table_id) table_key,o.table_id,o.pipeline_role,o.read_mode,o.write_mode,COALESCE(o.metric_rows_read,o.rows_read) rows_read,o.columns,o.input_rows,o.input_columns,COALESCE(o.rows_committed,o.rows_written) rows_committed,o.rows_inserted,o.rows_updated,o.rows_unchanged,o.versions_inserted,o.versions_expired,o.total_target_rows,o.measurement_source,o.contract_id,o.contract_version,o.status,o.started_at,o.completed_at,o.destination_kind,o.destination_table_name,CASE WHEN o.destination_workspace_id IS NULL OR o.destination_item_id IS NULL OR LOWER(o.destination_kind) NOT IN ('lakehouse','warehouse') THEN NULL ELSE CONCAT('https://app.fabric.microsoft.com/groups/',o.destination_workspace_id,'/',LOWER(o.destination_kind),'s/',o.destination_item_id) END fabric_item_url FROM {E}.[METADATA_PIPELINE_RUN] r CROSS APPLY OPENJSON(r.operations) WITH (operation_key nvarchar(400) '$.operation_key',table_id nvarchar(400) '$.table_id',pipeline_role nvarchar(50) '$.pipeline_role',read_mode nvarchar(100) '$.read_mode',write_mode nvarchar(100) '$.write_mode',rows_read bigint '$.rows_read',rows_written bigint '$.rows_written',metric_rows_read bigint '$.metrics.rows_read',columns bigint '$.metrics.columns',input_rows bigint '$.metrics.input_rows',input_columns bigint '$.metrics.input_columns',rows_committed bigint '$.metrics.rows_committed',rows_inserted bigint '$.metrics.rows_inserted',rows_updated bigint '$.metrics.rows_updated',rows_unchanged bigint '$.metrics.rows_unchanged',versions_inserted bigint '$.metrics.versions_inserted',versions_expired bigint '$.metrics.versions_expired',total_target_rows bigint '$.metrics.total_target_rows',measurement_source nvarchar(100) '$.metrics.measurement_source',contract_id nvarchar(400) '$.contract_id',contract_version bigint '$.contract_version',status nvarchar(80) '$.status',started_at datetime2 '$.started_at',completed_at datetime2 '$.completed_at',destination_workspace_id nvarchar(400) '$.destination.workspace_id',destination_item_id nvarchar(400) '$.destination.item_id',destination_kind nvarchar(80) '$.destination.kind',destination_table_name nvarchar(400) '$.destination.table_name') o WHERE r.started_at>=DATEADD(day,-{HD},SYSUTCDATETIME()) AND ({WF}='' OR r.workspace_id={WF})"),
'Run Stage':([('Run ID','string'),('Operation Key','string'),('Stage','string'),('Status','string'),('Evaluation Status','string')],"SELECT r.run_id,o.operation_key,s.stage,s.status,s.evaluation_status FROM {E}.[METADATA_PIPELINE_RUN] r CROSS APPLY OPENJSON(r.operations) WITH (operation_key nvarchar(400) '$.operation_key',stages nvarchar(max) '$.stages' AS JSON) o CROSS APPLY OPENJSON(o.stages) WITH (stage nvarchar(200) '$.stage',status nvarchar(80) '$.status',evaluation_status nvarchar(80) '$.evaluation_status') s WHERE r.started_at>=DATEADD(day,-{HD},SYSUTCDATETIME()) AND ({WF}='' OR r.workspace_id={WF})"),
'Run Failure':([('Run ID','string'),('Failure Code','string'),('Exception Type','string')],"SELECT r.run_id,f.code failure_code,f.exception_type FROM {E}.[METADATA_PIPELINE_RUN] r CROSS APPLY OPENJSON(r.failures) WITH (code nvarchar(400) '$.code',exception_type nvarchar(400) '$.exception_type') f WHERE r.started_at>=DATEADD(day,-{HD},SYSUTCDATETIME()) AND ({WF}='' OR r.workspace_id={WF})"),
'Guardrail Result':([('Run ID','string'),('Table Key','string'),('Table Name','string'),('Contract ID','string'),('Contract Version','int64'),('Status','string'),('Can Continue','boolean'),('Severity','string'),('Guardrail Type','string'),('Rule Type','string'),('Action','string'),('Reason','string'),('Committed At','dateTime')],"SELECT run_id,CONCAT(workspace_id,'|',table_id) table_key,table_name,contract_id,contract_version,status,can_continue,severity,guardrail_type,rule_type,action,reason,_committed_at committed_at FROM {E}.[METADATA_GUARDRAIL_RESULTS] WHERE _committed_at>=DATEADD(day,-{HD},SYSUTCDATETIME()) AND ({WF}='' OR workspace_id={WF})"),
'Catalogue Table':([('Table Key','string'),('Table ID','string'),('Workspace ID','string'),('Store Type','string'),('Layer','string'),('Schema Name','string'),('Table Name','string'),('Load Strategy','string'),('Last Profiled At','dateTime'),('Is Active','boolean')],"SELECT CONCAT(workspace_id,'|',table_id) table_key,table_id,workspace_id,store_type,layer,schema_name,table_name,load_strategy,last_profiled_at,is_active FROM {E}.[METADATA_DATA_CATALOGUE] WHERE (metadata_level='table' OR column_id IS NULL OR column_id='') AND ({WF}='' OR workspace_id={WF})"),
'Catalogue Column':([('Column Key','string'),('Table Key','string'),('Column ID','string'),('Column Name','string'),('Data Type','string')],"SELECT CONCAT(workspace_id,'|',table_id,'|',column_id) column_key,CONCAT(workspace_id,'|',table_id) table_key,column_id,column_name,data_type FROM {E}.[METADATA_DATA_CATALOGUE] WHERE column_id IS NOT NULL AND column_id<>'' AND is_active=1 AND ({WF}='' OR workspace_id={WF})"),
'Data Access':([('Table Key','string'),('Access Snapshot ID','string'),('User Principal','string'),('User Type','string'),('Access Level','string'),('Access Value','string'),('Access State','string'),('Role Name','string'),('Permission Source','string'),('Observed At','dateTime')],"SELECT CONCAT(a.workspace_id,'|',a.table_id) table_key,a.access_snapshot_id,a.user_principal,a.user_type,a.access_level,a.access_value,a.access_state,a.role_name,a.permission_source,s.observed_at FROM {E}.[METADATA_DATA_ACCESS] a INNER JOIN (SELECT workspace_id,table_id,access_snapshot_id,MAX(_committed_at) observed_at,ROW_NUMBER() OVER(PARTITION BY workspace_id,table_id ORDER BY MAX(_committed_at) DESC,access_snapshot_id DESC) rn FROM {E}.[METADATA_DATA_ACCESS] WHERE ({WF}='' OR workspace_id={WF}) GROUP BY workspace_id,table_id,access_snapshot_id) s ON s.workspace_id=a.workspace_id AND s.table_id=a.table_id AND s.access_snapshot_id=a.access_snapshot_id AND s.rn=1"),
'Profiled Column':([('Column Key','string'),('Profile Snapshot ID','string'),('Row Count','int64'),('Null Percent','double'),('Distinct Percent','double'),('Minimum Value','string'),('Maximum Value','string'),('Profiled At','dateTime')],"SELECT column_key,profile_snapshot_id,row_count,null_percent,distinct_percent,min_value AS minimum_value,max_value AS maximum_value,profiled_at FROM (SELECT CONCAT(workspace_id,'|',table_id,'|',column_id) column_key,profile_snapshot_id,row_count,null_percent,distinct_percent,min_value,max_value,_committed_at profiled_at,ROW_NUMBER() OVER(PARTITION BY workspace_id,table_id,column_id ORDER BY _committed_at DESC,profile_snapshot_id DESC) rn FROM {E}.[METADATA_DATA_PROFILED] WHERE ({WF}='' OR workspace_id={WF})) p WHERE rn=1"),
'Data Contract':([('Contract Key','string'),('Contract ID','string'),('Contract Version','int64'),('Evidence Workspace ID','string'),('Processing Strategy','string'),('Guardrail Count','int64'),('Table Description','string')],"SELECT CONCAT(c.contract_id,'|',c.contract_version) contract_key,c.contract_id,c.contract_version,c.evidence_workspace_id,c.contract_payload_json FROM {G}.[METADATA_DATA_CONTRACT] c"),
'Contract Activation':([('Table Key','string'),('Contract Key','string'),('Agreement Key','string'),('Activation ID','string'),('Revision','int64'),('Status','string'),('Activated At','dateTime')],"SELECT table_key,contract_key,agreement_key,activation_id,revision,status,activated_at FROM (SELECT CONCAT(workspace_id,'|',table_id) table_key,CONCAT(contract_id,'|',contract_version) contract_key,CASE WHEN agreement_id IS NULL THEN NULL ELSE CONCAT(agreement_id,'|',agreement_version) END agreement_key,activation_id,revision,status,activated_at,ROW_NUMBER() OVER(PARTITION BY workspace_id,table_id ORDER BY revision DESC,activated_at DESC) rn FROM {G}.[METADATA_DATA_CONTRACT_ACTIVATION] WHERE ({WF}='' OR workspace_id={WF})) a WHERE rn=1"),
'Data Agreement':([('Agreement Key','string'),('Agreement ID','string'),('Agreement Version','string'),('Agreement Name','string'),('Domain','string'),('Start Date','dateTime'),('Expiry Date','dateTime'),('Business Purpose','string')],"SELECT CONCAT(agreement_id,'|',agreement_version) agreement_key,agreement_id,agreement_version,agreement_name,domain,start_date,expiry_date,business_purpose FROM {G}.[METADATA_DATA_AGREEMENT]"),
'Agreement Steward':([('Agreement Key','string'),('Steward ID','string'),('Participation Role','string')],"SELECT CONCAT(agreement_id,'|',agreement_version) agreement_key,provider_steward_id steward_id,'Provider' participation_role FROM {G}.[METADATA_DATA_AGREEMENT] UNION ALL SELECT CONCAT(agreement_id,'|',agreement_version),recipient_steward_id,'Recipient' FROM {G}.[METADATA_DATA_AGREEMENT]"),
'Data Steward':([('Steward ID','string'),('Steward Name','string'),('Contact','string'),('Steward Display','string')],"SELECT steward_id,steward_name,contact,CONCAT(COALESCE(steward_name,steward_id),CASE WHEN contact IS NULL OR contact='' THEN '' ELSE CONCAT(' | ',contact) END) steward_display FROM {G}.[METADATA_DATA_STEWARD] WHERE is_active=1 OR is_active IS NULL")}

def msql(sql):
 sql=sql.replace('{E}','[" & EngineeringSchemaSql & "]').replace('{G}','[" & GovernanceSchemaSql & "]')
 sql=sql.replace('{HD}','" & Number.ToText(HistoryWindowDays) & "').replace('{WF}',"'"+'" & Text.Replace(WorkspaceFilter, "\'", "\'\'") & "'+"'")
 return 'let\n    Source = Sql.Database(MetadataServer, MetadataDatabase),\n    Query = "'+sql+'",\n    Rows = Value.NativeQuery(Source, Query, null, [EnableFolding=true])\nin\n    Rows'
def mcontract(sql):
 m=msql(sql)
 old='    Rows = Value.NativeQuery(Source, Query, null, [EnableFolding=true])\nin\n    Rows'
 steps=[
  '    Rows = Value.NativeQuery(Source, Query, null, [EnableFolding=true]),',
  '    Payload = Table.AddColumn(Rows, "_payload", each try Json.Document([contract_payload_json]) otherwise null),',
  '    ReadField = (value as any, field as text) as any => if Value.Is(value, type record) then Record.FieldOrDefault(value, field, null) else null,',
  '    ProcessingStrategy = Table.AddColumn(Payload, "processing_strategy", each let value = ReadField(ReadField(ReadField([_payload], "table"), "processing"), "load_strategy") in if value = null then null else if Value.Is(value, type text) or Value.Is(value, type number) or Value.Is(value, type logical) then Text.From(value) else null, type nullable text),',
  '    GuardrailCount = Table.AddColumn(ProcessingStrategy, "guardrail_count", each let value = ReadField([_payload], "guardrails") in if Value.Is(value, type list) then List.Count(value) else if Value.Is(value, type record) then Record.FieldCount(value) else null, Int64.Type),',
  '    TableDescription = Table.AddColumn(GuardrailCount, "table_description", each let enrichmentSection = ReadField(ReadField([_payload], "enrichment"), "table"), items = if Value.Is(enrichmentSection, type list) then enrichmentSection else if Value.Is(enrichmentSection, type record) then {enrichmentSection} else {}, matches = List.Select(items, each ReadField(_, "enrichment_type") = "Description"), value = if List.IsEmpty(matches) then null else ReadField(matches{0}, "value") in if value = null then null else if Value.Is(value, type text) or Value.Is(value, type number) or Value.Is(value, type logical) then Text.From(value) else null, type nullable text),',
  '    WithoutPayload = Table.RemoveColumns(TableDescription, {"contract_payload_json", "_payload"}),',
  '    Typed = Table.TransformColumnTypes(WithoutPayload, {{"contract_version", Int64.Type}})'
 ]
 new='\n'.join(steps)+'\nin\n    Typed'
 if old not in m: raise ValueError('Expected NativeQuery terminal step in Data Contract M query')
 return m.replace(old,new,1)

def table(name,cols,sql):
 out=[f"table '{name}'",f"\tlineageTag: {gid('table:'+name)}",'']
 for c,t in cols:
  out += [f"\tcolumn '{c}'",f"\t\tdataType: {t}",f"\t\tlineageTag: {gid(name+':'+c)}",f"\t\tsourceColumn: {c.lower().replace(' ','_')}"]
  if t in {'int64','double'}:
   out.append('\t\tsummarizeBy: none'); out.append('\t\tformatString: #,0' if t=='int64' else '\t\tformatString: #,0.0')
  if t=='dateTime': out.append('\t\tformatString: yyyy-MM-dd' if c in {'Run Date','Start Date','Expiry Date'} else '\t\tformatString: yyyy-MM-dd HH:mm')
  if c.endswith('URL'): out.append('\t\tdataCategory: WebUrl')
  out.append('')
 source=mcontract(sql) if name=='Data Contract' else msql(sql)
 out += [f"\tpartition '{name}' = m",'\t\tmode: import','\t\tsource =','\t\t\t'+source.replace('\n','\n\t\t\t'),'']
 return '\n'.join(out)
MEASURES=r'''table 'Dashboard Metrics'
	lineageTag: 00000000-0000-0000-0000-000000000001
	measure 'Registered Pipelines' = DISTINCTCOUNT('Pipeline Registry'[Pipeline Key])
		formatString: #,0
	measure 'Pipeline Identities' = DISTINCTCOUNT('Pipeline'[Pipeline Key])
		formatString: #,0
	measure 'Pipelines Run' = DISTINCTCOUNT('Pipeline Run'[Pipeline Key])
		formatString: #,0
	measure 'Submitted Dry Run Submissions' = CALCULATE(DISTINCTCOUNT('Pipeline Activation'[Submission ID]), NOT ISBLANK('Pipeline Activation'[Submitted Dry Run ID]))
		formatString: #,0
	measure 'Approved Activation Decisions' = CALCULATE(COUNTROWS('Pipeline Activation'), 'Pipeline Activation'[Status] = "approved")
		formatString: #,0
	measure 'Registered Physical Tables' = DISTINCTCOUNT('Catalogue Table'[Table Key])
		formatString: #,0
	measure 'Monitored Tables' = CALCULATE(DISTINCTCOUNT('Catalogue Table'[Table Key]), 'Catalogue Table'[Is Active] <> FALSE())
		formatString: #,0
	measure 'Run Count' = COUNTROWS('Pipeline Run')
		formatString: #,0
	measure 'Dataset Refreshed At' = MAX('Dashboard Refresh'[Refreshed At])
		formatString: yyyy-MM-dd HH:mm
	measure 'Successful Runs' = CALCULATE([Run Count], 'Pipeline Run'[Status] IN {"succeeded", "ungoverned_completed", "dry_run_completed"}, 'Pipeline Run'[Boundary Completed] = TRUE())
		formatString: #,0
	measure 'Failed Runs' = CALCULATE([Run Count], 'Pipeline Run'[Status] = "failed")
		formatString: #,0
	measure 'Incomplete Runs' = COUNTROWS(FILTER('Pipeline Run', 'Pipeline Run'[Status] <> "failed" && (NOT ('Pipeline Run'[Status] IN {"succeeded", "ungoverned_completed", "dry_run_completed"}) || 'Pipeline Run'[Boundary Completed] <> TRUE())))
		formatString: #,0
	measure 'Pipeline Success Rate' = DIVIDE([Successful Runs], [Run Count])
		formatString: #,0.0%;-#,0.0%;#,0.0%
	measure 'Run Duration Minutes' = AVERAGEX(FILTER('Pipeline Run', NOT ISBLANK('Pipeline Run'[Completed At])), DIVIDE(DATEDIFF('Pipeline Run'[Started At], 'Pipeline Run'[Completed At], SECOND), 60.0))
		formatString: #,0.0
	measure 'Historical Median Duration Minutes' = MEDIANX(FILTER(ALLSELECTED('Pipeline Run'), NOT ISBLANK('Pipeline Run'[Completed At])), DIVIDE(DATEDIFF('Pipeline Run'[Started At], 'Pipeline Run'[Completed At], SECOND), 60.0))
		formatString: #,0.0
	measure 'Duration Deviation Percent' = DIVIDE([Run Duration Minutes]-[Historical Median Duration Minutes],[Historical Median Duration Minutes])
		formatString: +#,0.0%;-#,0.0%;#,0.0%
	measure 'Last Recorded Execution' = MAX('Pipeline Run'[Started At])
		formatString: yyyy-MM-dd HH:mm
	measure 'Last Successful Execution' = CALCULATE(MAX('Pipeline Run'[Completed At]), 'Pipeline Run'[Status] IN {"succeeded", "ungoverned_completed", "dry_run_completed"}, 'Pipeline Run'[Boundary Completed] = TRUE())
		formatString: yyyy-MM-dd HH:mm
	measure 'Latest Recorded Run Status' = VAR LatestRun=TOPN(1,'Pipeline Run','Pipeline Run'[Started At],DESC,'Pipeline Run'[Run ID],DESC) RETURN COALESCE(MAXX(LatestRun,'Pipeline Run'[Status]),"No run recorded")
		formatString: @
	measure 'Contract Selections' = COUNTROWS('Contract Activation')
		formatString: #,0
	measure 'Active Contracts' = CALCULATE([Contract Selections], 'Contract Activation'[Status] = "active")
		formatString: #,0
	measure 'Contract Coverage' = DIVIDE(CALCULATE(DISTINCTCOUNT('Contract Activation'[Table Key]), 'Contract Activation'[Status] = "active"), [Monitored Tables])
		formatString: #,0.0%;-#,0.0%;#,0.0%
	measure 'Tables With Agreement' = CALCULATE(DISTINCTCOUNT('Contract Activation'[Table Key]), NOT ISBLANK('Contract Activation'[Agreement Key]))
		formatString: #,0
	measure 'Recorded Guardrail Failures' = CALCULATE(COUNTROWS('Guardrail Result'), 'Guardrail Result'[Status] IN {"failed", "error"})
		formatString: #,0
	measure 'Recorded Blocking Guardrail Outcomes' = CALCULATE(COUNTROWS('Guardrail Result'), 'Guardrail Result'[Can Continue] = FALSE() || 'Guardrail Result'[Action] = "Block")
		formatString: #,0
	measure 'Agreements' = DISTINCTCOUNT('Data Agreement'[Agreement Key])
		formatString: #,0
	measure 'Latest Profiled At' = MAX('Catalogue Table'[Last Profiled At])
		formatString: yyyy-MM-dd HH:mm
	measure 'Profiled Tables' = COUNTROWS(FILTER(VALUES('Catalogue Table'[Table Key]), NOT ISBLANK([Latest Profiled At])))
		formatString: #,0
	measure 'Average Null Percent' = AVERAGE('Profiled Column'[Null Percent])
		formatString: #,0.0
	measure 'Average Distinct Percent' = AVERAGE('Profiled Column'[Distinct Percent])
		formatString: #,0.0
	measure 'Selected Contract' = VAR ContractId=SELECTEDVALUE('Data Contract'[Contract ID]) RETURN IF(ISBLANK(ContractId), "No active Contract recorded", ContractId & " v" & FORMAT(SELECTEDVALUE('Data Contract'[Contract Version]), "0"))
		formatString: @
	measure 'Selected Agreement' = VAR AgreementName=SELECTEDVALUE('Data Agreement'[Agreement Name]) RETURN IF(ISBLANK(AgreementName), "No Agreement recorded", AgreementName & " v" & SELECTEDVALUE('Data Agreement'[Agreement Version]))
		formatString: @
	measure 'Recorded Access Observations' = COUNTROWS('Data Access')
		formatString: #,0
	measure 'Tables With Recorded Access' = DISTINCTCOUNT('Data Access'[Table Key])
		formatString: #,0
	partition Measures = calculated
		mode: import
		source = ROW("Value",1)
'''
def model():
 d=MODEL/'definition';put(MODEL/'.platform',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json','metadata':{'type':'SemanticModel','displayName':'FabricOps Dashboard','description':'FabricOps dashboard semantic model.'},'config':{'version':'2.0','logicalId':gid('model')}});put(MODEL/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.0','settings':{'qnaEnabled':False}});put(d/'database.tmdl','database FabricOpsDashboard\n\tcompatibilityLevel: 1604\n');put(d/'model.tmdl','model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n')
 put(d/'expressions.tmdl','expression MetadataServer = "<your-sql-endpoint>.datawarehouse.fabric.microsoft.com" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\nexpression MetadataDatabase = "<metadata-lakehouse-or-warehouse>" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\nexpression WorkspaceFilter = "" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=false]\n\nexpression HistoryWindowDays = 180 meta [IsParameterQuery=true, Type="Number", IsParameterQueryRequired=true]\n\nexpression GovernanceSchema = "governance" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\nexpression EngineeringSchema = "engineering" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\nexpression GovernanceSchemaSql = if Text.Select(GovernanceSchema, {"A".."Z", "a".."z", "0".."9", "_"}) = GovernanceSchema then GovernanceSchema else error "GovernanceSchema must be a SQL identifier."\n\nexpression EngineeringSchemaSql = if Text.Select(EngineeringSchema, {"A".."Z", "a".."z", "0".."9", "_"}) = EngineeringSchema then EngineeringSchema else error "EngineeringSchema must be a SQL identifier."\n')
 for n,(c,q) in TABLES.items():put(d/f'tables/{n}.tmdl',table(n,c,q))
 put(d/'tables/Dashboard Metrics.tmdl',MEASURES)
 rels=[('Pipeline Registry','Pipeline Key','Pipeline','Pipeline Key',None),('Pipeline Activation','Pipeline Key','Pipeline','Pipeline Key',None),('Pipeline Run','Pipeline Key','Pipeline','Pipeline Key',None),('Run Operation','Run ID','Pipeline Run','Run ID','bothDirections'),('Run Stage','Run ID','Pipeline Run','Run ID',None),('Run Failure','Run ID','Pipeline Run','Run ID',None),('Guardrail Result','Run ID','Pipeline Run','Run ID',None),('Run Operation','Table Key','Catalogue Table','Table Key',None),('Guardrail Result','Table Key','Catalogue Table','Table Key',None),('Catalogue Column','Table Key','Catalogue Table','Table Key',None),('Profiled Column','Column Key','Catalogue Column','Column Key',None),('Data Access','Table Key','Catalogue Table','Table Key',None),('Contract Activation','Table Key','Catalogue Table','Table Key','bothDirections'),('Contract Activation','Contract Key','Data Contract','Contract Key','bothDirections'),('Contract Activation','Agreement Key','Data Agreement','Agreement Key','bothDirections'),('Agreement Steward','Agreement Key','Data Agreement','Agreement Key','bothDirections'),('Agreement Steward','Steward ID','Data Steward','Steward ID',None)]
 out=[]
 for i,(a,b,c,e,f) in enumerate(rels):
  out += [f"relationship {gid('rel:'+str(i))}",f"\tfromColumn: '{a}'.'{b}'",f"\ttoColumn: '{c}'.'{e}'"]+([f'\tcrossFilteringBehavior: {f}'] if f else [])+['']
 put(d/'relationships.tmdl','\n'.join(out))
def main():
 PROJECT.mkdir(parents=True,exist_ok=True)
 for child in PROJECT.iterdir():
  if child.name=='.pbi': continue
  if child.is_dir(): shutil.rmtree(child)
  else: child.unlink()
 put(PROJECT/'.gitignore','.pbi/\n*.pbix\n*.pbit\n')
 put(PROJECT/'FabricOpsDashboard.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'FabricOpsDashboard.Report'}}],'settings':{'enableAutoRecovery':True}});report();model()
if __name__=='__main__':main()
