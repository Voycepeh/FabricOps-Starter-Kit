import React from 'react';
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  useCurrentFrame,
} from 'remotion';

const C = {
  bg: '#07111F',
  panel: '#0C1728',
  panel2: '#101D30',
  text: '#F6F8FC',
  muted: '#8EA0B9',
  blue: '#4EA1FF',
  purple: '#A56CFF',
  green: '#35D48A',
  orange: '#FF9F43',
  line: '#273A52',
};

const ease = Easing.bezier(0.16, 1, 0.3, 1);

const Card: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  title: string;
  subtitle?: string;
  accent: string;
  delay?: number;
  opacity?: number;
}> = ({x, y, w, h, title, subtitle, accent, delay = 0, opacity = 1}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 18], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        borderRadius: 24,
        background: `linear-gradient(180deg, ${C.panel2}, ${C.panel})`,
        border: `1px solid ${C.line}`,
        boxShadow: '0 18px 60px rgba(0,0,0,.22)',
        opacity: p * opacity,
        scale: 0.94 + 0.06 * p,
        translate: `0 ${18 * (1 - p)}px`,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: 5,
          background: accent,
        }}
      />
      <div style={{padding: '24px 26px'}}>
        <div
          style={{
            fontSize: 15,
            letterSpacing: 2.4,
            textTransform: 'uppercase',
            fontWeight: 700,
            color: accent,
          }}
        >
          FabricOps
        </div>
        <div style={{fontSize: 28, fontWeight: 700, marginTop: 8, color: C.text}}>
          {title}
        </div>
        {subtitle && (
          <div style={{fontSize: 18, lineHeight: 1.45, marginTop: 8, color: C.muted}}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};

const Pill: React.FC<{
  x: number;
  y: number;
  label: string;
  accent: string;
  delay: number;
}> = ({x, y, label, accent, delay}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 14], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        padding: '12px 18px',
        borderRadius: 999,
        border: `1px solid ${accent}55`,
        background: `${accent}16`,
        fontSize: 18,
        fontWeight: 650,
        color: C.text,
        opacity: p,
        translate: `0 ${10 * (1 - p)}px`,
      }}
    >
      {label}
    </div>
  );
};

const Line: React.FC<{
  x: number;
  y: number;
  w: number;
  delay: number;
  accent?: string;
}> = ({x, y, w, delay, accent = C.line}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 22], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w * p,
        height: 2,
        background: `linear-gradient(90deg, ${accent}, ${accent}55)`,
      }}
    />
  );
};

const Dot: React.FC<{x: number; y: number; accent: string; delay: number}> = ({
  x,
  y,
  accent,
  delay,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 10], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: 12,
        height: 12,
        borderRadius: 99,
        background: accent,
        boxShadow: `0 0 24px ${accent}`,
        opacity: p,
        scale: p,
      }}
    />
  );
};

const Header: React.FC<{
  eyebrow: string;
  title: string;
  subtitle: string;
  delay?: number;
}> = ({eyebrow, title, subtitle, delay = 0}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + 24], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: 110,
        top: 78,
        width: 1100,
        opacity: p,
        translate: `0 ${18 * (1 - p)}px`,
      }}
    >
      <div
        style={{
          fontSize: 17,
          letterSpacing: 3.5,
          textTransform: 'uppercase',
          fontWeight: 750,
          color: C.blue,
        }}
      >
        {eyebrow}
      </div>
      <div
        style={{
          fontSize: 64,
          lineHeight: 1.05,
          fontWeight: 780,
          letterSpacing: -2.5,
          color: C.text,
          marginTop: 14,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontSize: 25,
          lineHeight: 1.45,
          color: C.muted,
          marginTop: 18,
          maxWidth: 900,
        }}
      >
        {subtitle}
      </div>
    </div>
  );
};

const SceneFragmented: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 165], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: 'Inter, Arial, sans-serif'}}>
      <Header
        eyebrow="Before FabricOps"
        title="One platform. Too many ways of working."
        subtitle="Pipelines, notebooks, governance and configuration drift apart as teams scale."
      />
      <Card
        x={190 + drift * 12}
        y={430}
        w={350}
        h={170}
        title="Pipeline A"
        subtitle="Own conventions"
        accent={C.blue}
        delay={20}
      />
      <Card
        x={760 - drift * 8}
        y={380}
        w={355}
        h={170}
        title="Governance"
        subtitle="Separate metadata flow"
        accent={C.purple}
        delay={34}
      />
      <Card
        x={1280 + drift * 10}
        y={485}
        w={350}
        h={170}
        title="Notebook"
        subtitle="Different patterns"
        accent={C.orange}
        delay={48}
      />
      <Card
        x={520 - drift * 10}
        y={705}
        w={360}
        h={150}
        title="Environment config"
        subtitle="Local assumptions"
        accent="#BAC7D9"
        delay={62}
      />
      <Card
        x={1110 + drift * 8}
        y={745}
        w={360}
        h={150}
        title="Pipeline B"
        subtitle="Another implementation"
        accent={C.blue}
        delay={76}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: 220,
          background: 'linear-gradient(180deg, transparent, rgba(78,161,255,.045))',
        }}
      />
    </AbsoluteFill>
  );
};

const SceneOperatingLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, 45], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });

  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: 'Inter, Arial, sans-serif'}}>
      <div
        style={{
          position: 'absolute',
          left: 120,
          top: 120,
          right: 120,
          bottom: 120,
          borderRadius: 38,
          border: `1px solid ${C.line}`,
          background: 'radial-gradient(circle at 50% 30%, rgba(78,161,255,.10), transparent 45%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 160,
          top: 155,
          fontSize: 18,
          letterSpacing: 3,
          textTransform: 'uppercase',
          fontWeight: 750,
          color: C.blue,
          opacity: p,
        }}
      >
        The operating practice
      </div>
      <div
        style={{
          position: 'absolute',
          left: 160,
          top: 215,
          fontSize: 84,
          fontWeight: 820,
          letterSpacing: -4,
          color: C.text,
          opacity: p,
          translate: `0 ${18 * (1 - p)}px`,
        }}
      >
        FabricOps
      </div>
      <div
        style={{
          position: 'absolute',
          left: 160,
          top: 325,
          fontSize: 31,
          color: C.muted,
          opacity: p,
          maxWidth: 1030,
          lineHeight: 1.4,
        }}
      >
        Configuration-driven engineering and governance brought into one repeatable operating flow.
      </div>
      <Pill x={160} y={465} label="Configuration-driven" accent="#C4D1E2" delay={35} />
      <Pill x={410} y={465} label="PySpark-first" accent={C.blue} delay={45} />
      <Pill x={600} y={465} label="Governance-as-Code" accent={C.purple} delay={55} />
      <Card
        x={165}
        y={620}
        w={360}
        h={170}
        title="00 Env Config"
        subtitle="Shared operating context"
        accent="#DCE5F2"
        delay={65}
      />
      <Line x={525} y={705} w={210} delay={78} accent="#DCE5F2" />
      <Card
        x={735}
        y={620}
        w={400}
        h={170}
        title="Governance"
        subtitle="Contracts + guardrails"
        accent={C.purple}
        delay={88}
      />
      <Line x={1135} y={705} w={210} delay={100} accent={C.purple} />
      <Card
        x={1345}
        y={620}
        w={410}
        h={170}
        title="Engineering"
        subtitle="Pipeline + validation"
        accent={C.blue}
        delay={110}
      />
    </AbsoluteFill>
  );
};

const SceneCollaboration: React.FC = () => {
  const frame = useCurrentFrame();
  const contractPulse = 1 + 0.018 * Math.sin(frame / 10);

  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: 'Inter, Arial, sans-serif'}}>
      <Header
        eyebrow="One connected workflow"
        title="Governance and Engineering move together."
        subtitle="The contract becomes the shared object that connects intent, implementation and validation."
        delay={0}
      />
      <Card
        x={155}
        y={440}
        w={540}
        h={370}
        title="Governance workspace"
        subtitle="Author contracts, enrichment and guardrails"
        accent={C.purple}
        delay={25}
      />
      <Card
        x={1225}
        y={440}
        w={540}
        h={370}
        title="Engineering workspace"
        subtitle="Build pipelines against governed expectations"
        accent={C.blue}
        delay={35}
      />
      <Line x={700} y={625} w={520} delay={48} accent={C.purple} />
      <div
        style={{
          position: 'absolute',
          left: 835,
          top: 515,
          width: 250,
          height: 220,
          borderRadius: 30,
          background: `linear-gradient(180deg, ${C.panel2}, ${C.panel})`,
          border: `1px solid ${C.purple}66`,
          boxShadow: '0 0 55px rgba(165,108,255,.18)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          scale: contractPulse,
        }}
      >
        <div
          style={{
            fontSize: 14,
            letterSpacing: 2.5,
            textTransform: 'uppercase',
            fontWeight: 800,
            color: C.purple,
          }}
        >
          Shared object
        </div>
        <div style={{fontSize: 32, fontWeight: 760, color: C.text, marginTop: 12}}>
          Data Contract
        </div>
        <div style={{fontSize: 18, color: C.muted, marginTop: 10}}>table_id · version</div>
      </div>
      <Dot x={712 + ((frame % 80) / 80) * 475} y={619} accent={C.green} delay={55} />
      <div style={{position: 'absolute', left: 710, top: 748, fontSize: 18, color: C.muted}}>
        Validate → refine → test → activate
      </div>
    </AbsoluteFill>
  );
};

const SceneProduction: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  const consumerP = interpolate(frame, [100, 170], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: ease,
  });
  const consumers = [
    [140, 270],
    [140, 480],
    [140, 690],
    [1490, 250],
    [1490, 455],
    [1490, 660],
    [815, 845],
  ];

  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: 'Inter, Arial, sans-serif'}}>
      <Header
        eyebrow="Promotion"
        title="Production receives the validated pair."
        subtitle="The engineering pipeline runs with the activated contract. Consumers only connect to Production."
        delay={0}
      />
      <div
        style={{
          position: 'absolute',
          left: 610,
          top: 395,
          width: 700,
          height: 380,
          borderRadius: 40,
          background: 'linear-gradient(180deg, rgba(53,212,138,.14), rgba(12,23,40,.94))',
          border: `1px solid ${C.green}66`,
          boxShadow: '0 0 85px rgba(53,212,138,.12)',
          opacity: p,
          scale: 0.96 + 0.04 * p,
        }}
      >
        <div style={{padding: '34px 40px'}}>
          <div
            style={{
              fontSize: 16,
              letterSpacing: 2.8,
              textTransform: 'uppercase',
              fontWeight: 800,
              color: C.green,
            }}
          >
            Production workspace
          </div>
          <div style={{fontSize: 42, fontWeight: 780, color: C.text, marginTop: 13}}>
            Validated operating pair
          </div>
          <div style={{display: 'flex', gap: 18, marginTop: 46}}>
            <div
              style={{
                flex: 1,
                padding: 22,
                borderRadius: 22,
                background: C.panel2,
                border: `1px solid ${C.blue}55`,
              }}
            >
              <div style={{fontSize: 15, color: C.blue, fontWeight: 750}}>ENGINEERING</div>
              <div style={{fontSize: 27, color: C.text, fontWeight: 720, marginTop: 8}}>
                02 Pipeline
              </div>
            </div>
            <div
              style={{
                flex: 1,
                padding: 22,
                borderRadius: 22,
                background: C.panel2,
                border: `1px solid ${C.purple}55`,
              }}
            >
              <div style={{fontSize: 15, color: C.purple, fontWeight: 750}}>GOVERNANCE</div>
              <div style={{fontSize: 27, color: C.text, fontWeight: 720, marginTop: 8}}>
                Active Contract
              </div>
            </div>
          </div>
        </div>
      </div>
      {consumers.map(([x, y], i) => (
        <React.Fragment key={i}>
          <div
            style={{
              position: 'absolute',
              left: x,
              top: y,
              width: 290,
              height: 108,
              borderRadius: 22,
              background: C.panel,
              border: `1px solid ${C.orange}55`,
              opacity: consumerP,
              translate: `0 ${18 * (1 - consumerP)}px`,
            }}
          >
            <div style={{padding: '20px 24px'}}>
              <div style={{fontSize: 14, color: C.orange, fontWeight: 800, letterSpacing: 2}}>
                CONSUMER {i + 1}
              </div>
              <div style={{fontSize: 22, color: C.text, fontWeight: 700, marginTop: 7}}>
                Production only
              </div>
            </div>
          </div>
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};

export const FabricOpsHero: React.FC = () => {
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <Sequence from={0} durationInFrames={165}>
        <SceneFragmented />
      </Sequence>
      <Sequence from={165} durationInFrames={185}>
        <SceneOperatingLayer />
      </Sequence>
      <Sequence from={350} durationInFrames={190}>
        <SceneCollaboration />
      </Sequence>
      <Sequence from={540} durationInFrames={210}>
        <SceneProduction />
      </Sequence>
    </AbsoluteFill>
  );
};
