import {Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {OPENING_ARTIFACTS} from '../components/FabricIcons';
import {theme} from '../theme';
import {VIDEO_CONFIG} from '../videoConfig';
import {notebookFrame, VIDEO_TUNING} from '../videoTuning';

const NOTEBOOK = {
  width: 410,
  height: 220,
  borderRadius: 28,
  padding: 34,
  glyphSize: 48,
  titleSize: 31,
  subtitleSize: 21,
} as const;

const IMPORT_GROUPS = [
  ['pipeline_read,', 'pipeline_write,'],
  ['widget_data_contract,', 'widget_select_data_contract,'],
  ['check_schema,', 'check_dq,'],
] as const;

const EnvironmentIcon = OPENING_ARTIFACTS[3].icon;

const NotebookGlyph = ({color}: {color: string}) => (
  <div style={{position: 'relative', width: NOTEBOOK.glyphSize, height: NOTEBOOK.glyphSize, flex: '0 0 auto'}}>
    <div style={{position: 'absolute', inset: 0, border: `2px solid ${color}`, borderRadius: 8, background: `${color}12`}} />
    <div style={{position: 'absolute', left: -5, top: 9, width: 10, height: 4, borderRadius: 4, background: color, boxShadow: `0 11px 0 ${color}, 0 22px 0 ${color}`}} />
    <div style={{position: 'absolute', left: 13, right: 8, top: 14, height: 3, borderRadius: 3, background: color, boxShadow: `0 9px 0 ${color}99, 0 18px 0 ${color}66`}} />
  </div>
);

const NotebookCard = ({title, subtitle, color, progress, position}: {
  title: string;
  subtitle: string;
  color: string;
  progress: number;
  position: {left: number; top: number};
}) => (
  <div style={{position: 'absolute', ...position, width: NOTEBOOK.width, height: NOTEBOOK.height, boxSizing: 'border-box', borderRadius: NOTEBOOK.borderRadius, padding: NOTEBOOK.padding, display: 'flex', alignItems: 'center', background: `linear-gradient(145deg, ${color}24, #0b1525 74%)`, border: `2px solid ${color}cc`, boxShadow: `0 24px 58px #0008, 0 0 30px ${color}16, inset 0px 1px 0 #ffffff12`, opacity: progress, transform: `translateY(${(1 - progress) * 20}px) scale(${0.94 + progress * 0.06})`}}>
    <div style={{position: 'absolute', top: -2, left: 34, width: 80, height: 9, borderRadius: '0 0 8px 8px', background: color}} />
    <div style={{display: 'flex', alignItems: 'center', gap: 26, width: '100%'}}>
      <NotebookGlyph color={color} />
      <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 12, minWidth: 0}}>
        <div style={{fontSize: NOTEBOOK.titleSize, lineHeight: 1.15, fontWeight: 820, color: theme.text, whiteSpace: 'nowrap'}}>{title}</div>
        <div style={{fontSize: NOTEBOOK.subtitleSize, lineHeight: 1.25, fontWeight: 680, color}}>{subtitle}</div>
      </div>
    </div>
  </div>
);

const ContractDocument = ({progress}: {progress: number}) => {
  const guardrails = ['Schema', 'Freshness', 'Data Quality', 'Sensitivity', 'Source Drift'];
  const {contract} = VIDEO_TUNING.notebook.layout;
  return (
    <div style={{position: 'absolute', ...contract, boxSizing: 'border-box', padding: '34px 38px 24px', background: 'linear-gradient(150deg, #303a49, #1b2432 78%)', border: '2px solid #7f8b9b', borderRadius: '16px 16px 20px 20px', boxShadow: '0 28px 65px #0009, inset 0 1px 0 #ffffff1a', opacity: progress, transform: `translateY(${(1 - progress) * 18}px) scale(${0.95 + progress * 0.05})`, overflow: 'hidden'}}>
      <div style={{position: 'absolute', top: -2, right: -2, width: 66, height: 66, background: '#111a27', clipPath: 'polygon(100% 0, 0 0, 100% 100%)'}} />
      <div style={{position: 'absolute', top: 0, right: 0, width: 66, height: 66, background: '#697586', clipPath: 'polygon(0 0, 0 100%, 100% 100%)', opacity: 0.72}} />
      <div style={{width: 42, height: 48, boxSizing: 'border-box', border: '2px solid #aab3bf', borderRadius: 6, position: 'relative', marginBottom: 16}}>
        <div style={{position: 'absolute', left: 10, right: 8, top: 13, height: 3, borderRadius: 2, background: '#aab3bf', boxShadow: '0 9px 0 #8f9aa9, 0 18px 0 #768292'}} />
      </div>
      <div style={{fontSize: 30, lineHeight: 1.15, fontWeight: 820, color: '#f5f7fa', whiteSpace: 'nowrap'}}>Data Contract</div>
      <div style={{marginTop: 18, marginBottom: 9, fontSize: 19, lineHeight: 1.25, fontWeight: 740, color: '#aeb7c3', letterSpacing: 1, textTransform: 'uppercase'}}>Guardrails</div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 7}}>
        {guardrails.map((guardrail) => (
          <div key={guardrail} style={{minHeight: 29, display: 'flex', alignItems: 'center', gap: 13, fontSize: 21, lineHeight: 1.3, fontWeight: 560, color: '#dce1e8'}}>
            <span style={{width: 7, height: 7, flex: '0 0 auto', borderRadius: 7, background: '#9ca7b5'}} />
            {guardrail}
          </div>
        ))}
      </div>
    </div>
  );
};

const CodePackage = ({frame, fps}: {frame: number; fps: number}) => {
  const {timingSeconds, layout} = VIDEO_TUNING.notebook;
  const packageEnter = notebookFrame(timingSeconds.packageEnter, fps);
  const packageExit = notebookFrame(timingSeconds.packageExit, fps);
  const importFrames = timingSeconds.packageImports.map((seconds) => notebookFrame(seconds, fps));
  const enter = spring({frame: frame - packageEnter, fps, config: {damping: 18, stiffness: 82}});
  const exit = interpolate(frame, [packageExit - 18, packageExit], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});

  return <div style={{position: 'absolute', ...layout.package, boxSizing: 'border-box', borderRadius: 26, overflow: 'hidden', background: 'linear-gradient(145deg, #101c2e, #08111f 78%)', border: `2px solid ${theme.production}88`, boxShadow: `0 30px 85px #000a, 0 0 48px ${theme.production}20`, opacity: enter * exit, transform: `translateY(${(1 - enter) * 24}px) scale(${0.94 + enter * 0.06 - (1 - exit) * 0.05})`}}>
    <div style={{height: 70, display: 'flex', alignItems: 'center', padding: '0 28px', gap: 12, borderBottom: '1px solid #ffffff18', background: '#ffffff08'}}>
      {['#ff6b6b', '#ffd166', '#38d991'].map((color) => <span key={color} style={{width: 15, height: 15, borderRadius: 20, background: color}} />)}
      <div style={{marginLeft: 18, fontFamily: 'monospace', fontSize: 23, color: '#aebed2'}}>fabricops_package.py</div>
      <div style={{marginLeft: 'auto', padding: '8px 16px', borderRadius: 99, background: `${theme.production}20`, border: `1px solid ${theme.production}88`, color: theme.production, fontSize: 20, fontWeight: 760}}>.py package</div>
    </div>
    <div style={{padding: '40px 58px', fontFamily: 'monospace', fontSize: 29, lineHeight: 1.5, color: '#dce7f5'}}>
      <div style={{opacity: enter, color: '#8ed8ff'}}><span style={{color: '#c792ea'}}>from</span> fabricops_kit <span style={{color: '#c792ea'}}>import</span> (</div>
      {IMPORT_GROUPS.map((group, index) => {
        const progress = spring({frame: frame - importFrames[index], fps, config: {damping: 17, stiffness: 105}});
        return <div key={group[0]} style={{marginLeft: 46, opacity: progress, transform: `translateX(${(1 - progress) * 24}px)`}}>
          {group.map((functionName) => <div key={functionName} style={{color: '#f3f7fc'}}>{functionName}</div>)}
        </div>;
      })}
      <div style={{color: '#8ed8ff'}}>)</div>
    </div>
  </div>;
};

const SetupFlow = ({frame, fps}: {frame: number; fps: number}) => {
  const {timingSeconds, layout} = VIDEO_TUNING.notebook;
  const workspaceAt = notebookFrame(timingSeconds.setupWorkspace, fps);
  const environmentAt = notebookFrame(timingSeconds.setupEnvironment, fps);
  const configLinkAt = notebookFrame(timingSeconds.setupConfigLink, fps);
  const setupExit = notebookFrame(timingSeconds.setupExit, fps);
  const workspace = spring({frame: frame - workspaceAt, fps, config: {damping: 20, stiffness: 86}});
  const environment = spring({frame: frame - environmentAt, fps, config: {damping: 18, stiffness: 92}});
  const packageToEnvironment = interpolate(frame, [environmentAt, environmentAt + 24], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const environmentToConfig = interpolate(frame, [configLinkAt, configLinkAt + 26], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const fadeOut = interpolate(frame, [setupExit - 18, setupExit], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const groupOpacity = workspace * fadeOut;
  const whl = layout.whl;
  const fabricEnvironment = layout.fabricEnvironment;
  const config = layout.setupEnvironment;
  const whlCenterY = whl.top + whl.height / 2;
  const environmentCenterX = fabricEnvironment.left + fabricEnvironment.width / 2;
  const environmentCenterY = fabricEnvironment.top + fabricEnvironment.height / 2;
  const configCenterX = config.left + NOTEBOOK.width / 2;

  return (
    <div style={{position: 'absolute', inset: 0, opacity: groupOpacity}}>
      <div style={{position: 'absolute', ...layout.workspace, boxSizing: 'border-box', borderRadius: 34, background: 'linear-gradient(180deg, #10203a80 0%, #09142670 100%)', border: '2px solid #71839a55', boxShadow: 'inset 0 1px 0 #ffffff12, 0 28px 80px #0005'}}>
        <div style={{position: 'absolute', left: 34, top: 24, fontSize: 22, fontWeight: 720, letterSpacing: 1.2, color: '#91a0b4', textTransform: 'uppercase'}}>Fabric workspace</div>
      </div>

      <div style={{position: 'absolute', ...whl, boxSizing: 'border-box', borderRadius: 24, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, padding: '14px 18px 16px', background: 'linear-gradient(150deg, #4f2875, #2a1744 78%)', border: '2px solid #a978e0aa', boxShadow: '0 24px 56px #0008, 0 0 34px #8f4ad733'}}>
        <div style={{position: 'relative', width: 92, height: 108, flex: '0 0 auto', borderRadius: '14px 14px 18px 18px', border: '5px solid #c89cf0', background: '#ffffff08'}}>
          <div style={{position: 'absolute', top: -5, right: -5, width: 34, height: 34, background: '#7c55a6', clipPath: 'polygon(0 0, 100% 100%, 0 100%)'}} />
          <div style={{position: 'absolute', top: 12, left: 0, right: 0, textAlign: 'center', fontSize: 28, fontWeight: 850, color: '#fff'}}>WHL</div>
          <div style={{position: 'absolute', bottom: 16, left: 0, right: 0, textAlign: 'center', fontFamily: 'monospace', fontSize: 17, fontWeight: 720, color: '#e4cff9'}}>&lt;/&gt;</div>
        </div>
        <div style={{textAlign: 'center', fontSize: 20, lineHeight: 1.05, fontWeight: 760, color: '#eadcf7'}}>
          <div>FabricOps</div>
          <div>package</div>
        </div>
      </div>

      <div style={{position: 'absolute', ...fabricEnvironment, boxSizing: 'border-box', borderRadius: 24, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, padding: '16px 18px', background: 'linear-gradient(150deg, #142844, #0c182a 78%)', border: '2px solid #4e91d899', boxShadow: '0 24px 56px #0008, 0 0 34px #3097dd22', opacity: environment, transform: `scale(${0.9 + environment * 0.1})`}}>
        <div style={{width: 72, height: 72, display: 'grid', placeItems: 'center', transform: 'scale(1.45)'}}>
          <EnvironmentIcon aria-hidden="true" width={48} height={48} />
        </div>
        <div style={{textAlign: 'center', fontSize: 20, lineHeight: 1.08, fontWeight: 760, color: '#eef6ff'}}>
          <div>Fabric</div>
          <div>Environment</div>
        </div>
      </div>

      <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <defs>
          <marker id="setup-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
            <path d="M0 0 L9 4.5 L0 9 Z" fill="#8fa0b6" />
          </marker>
        </defs>
        <path d={`M${whl.left + whl.width} ${whlCenterY} C${whl.left + whl.width + 38} ${whlCenterY}, ${fabricEnvironment.left - 38} ${environmentCenterY}, ${fabricEnvironment.left} ${environmentCenterY}`} fill="none" stroke="#8fa0b6" strokeWidth="4" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - packageToEnvironment} opacity={packageToEnvironment} markerEnd="url(#setup-arrow)" />
        <path d={`M${environmentCenterX} ${fabricEnvironment.top + fabricEnvironment.height} C${environmentCenterX} ${fabricEnvironment.top + fabricEnvironment.height + 48}, ${configCenterX} ${config.top - 48}, ${configCenterX} ${config.top}`} fill="none" stroke="#8fa0b6" strokeWidth="4" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - environmentToConfig} opacity={environmentToConfig} markerEnd="url(#setup-arrow)" />
      </svg>
    </div>
  );
};

export const NotebookJourney = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {scenes, timing} = VIDEO_CONFIG;
  const {timingSeconds, layout} = VIDEO_TUNING.notebook;
  const enter = (delay: number) => spring({frame: frame - delay, fps, config: {damping: 21, stiffness: 88}});
  const environmentAt = notebookFrame(timingSeconds.environment, fps);
  const setupExitAt = notebookFrame(timingSeconds.setupExit, fps);
  const foundationAt = notebookFrame(timingSeconds.foundation, fps);
  const lowerNotebooksAt = notebookFrame(timingSeconds.lowerNotebooks, fps);
  const contractAt = notebookFrame(timingSeconds.contract, fps);
  const relationshipAt = notebookFrame(timingSeconds.relationship, fps);
  const environment = enter(environmentAt);
  const environmentTop = interpolate(frame, [setupExitAt, setupExitAt + 18], [layout.setupEnvironment.top, layout.environment.top], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const environmentPosition = {left: layout.environment.left, top: environmentTop};
  const foundationFlow = interpolate(frame, [foundationAt, foundationAt + 44], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const lowerNotebooks = enter(lowerNotebooksAt);
  const contract = enter(contractAt);
  const relationshipFlow = interpolate(frame, [relationshipAt, relationshipAt + 44], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const connectorSettle = spring({frame: frame - relationshipAt - 20, fps, config: {damping: 17, stiffness: 92}});
  const exit = interpolate(frame, [scenes.notebooks - timing.sceneExit, scenes.notebooks], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const connectorY = layout.connectorY;
  const environmentBottomY = layout.environment.top + NOTEBOOK.height;
  const environmentLeftX = layout.environment.left + 100;
  const environmentRightX = layout.environment.left + NOTEBOOK.width - 100;

  return <div style={{position: 'absolute', inset: 0, opacity: exit}}>
    <CodePackage frame={frame} fps={fps} />
    <SetupFlow frame={frame} fps={fps} />

    <svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
      <defs>
        <marker id="notebook-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill={theme.neutral} /></marker>
      </defs>
      <g fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path d={`M${environmentLeftX} ${environmentBottomY} C${environmentLeftX} ${environmentBottomY + 44}, 425 ${environmentBottomY + 44}, 425 638`} stroke={theme.neutral} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - foundationFlow} opacity={foundationFlow * 0.72} markerEnd="url(#notebook-arrow)" />
        <path d={`M${environmentRightX} ${environmentBottomY} C${environmentRightX} ${environmentBottomY + 44}, 1495 ${environmentBottomY + 44}, 1495 638`} stroke={theme.neutral} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - foundationFlow} opacity={foundationFlow * 0.72} markerEnd="url(#notebook-arrow)" />
        <path d={`M630 ${connectorY} H760`} stroke={theme.governance} strokeWidth="14" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - relationshipFlow} opacity={relationshipFlow} />
        <path d={`M1160 ${connectorY} H1290`} stroke={theme.engineering} strokeWidth="14" pathLength="1" strokeDasharray="1" strokeDashoffset={1 - relationshipFlow} opacity={relationshipFlow} />
      </g>
      <g opacity={relationshipFlow}>
        <rect x={752 - connectorSettle * 10} y={connectorY - 27} width="34" height="54" rx="8" fill={theme.governance} />
        <rect x={1134 + connectorSettle * 10} y={connectorY - 27} width="34" height="54" rx="8" fill={theme.engineering} />
        <rect x="778" y={connectorY - 20} width="14" height="14" rx="4" fill="#dce7f5" />
        <rect x="778" y={connectorY + 6} width="14" height="14" rx="4" fill="#dce7f5" />
        <rect x="1128" y={connectorY - 20} width="14" height="14" rx="4" fill="#dce7f5" />
        <rect x="1128" y={connectorY + 6} width="14" height="14" rx="4" fill="#dce7f5" />
        <circle cx="785" cy={connectorY} r={23 + connectorSettle * 5} fill="none" stroke={theme.governance} strokeWidth="4" />
        <circle cx="1135" cy={connectorY} r={23 + connectorSettle * 5} fill="none" stroke={theme.engineering} strokeWidth="4" />
      </g>
    </svg>

    <NotebookCard title="00_env_config" subtitle="Config-driven" color={theme.neutral} progress={environment} position={environmentPosition} />
    <NotebookCard title="01_governance" subtitle="Governance" color={theme.governance} progress={lowerNotebooks} position={layout.governance} />
    <ContractDocument progress={contract} />
    <NotebookCard title="02_pipeline" subtitle="ETL Pipeline" color={theme.engineering} progress={lowerNotebooks} position={layout.pipeline} />
  </div>;
};
