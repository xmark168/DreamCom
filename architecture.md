# DeamCompan Architecture Diagram

## Overview (Mid-level)

```mermaid
flowchart TB
  %% Governance
  user[User / Founder] --> bod[BOD Governance]
  bod --> ceo[CEO Orchestrator]

  %% Teams
  ceo --> t_product[Product Team Lead]
  ceo --> t_engineering[Engineering Team Lead]
  ceo --> t_research[Research Team Lead]
  ceo --> t_ops[Operations Team Lead]
  ceo --> t_sales[Sales & Marketing Team Lead]

  %% Sub-agents
  t_product --> p_sub[Sub-agents]
  t_engineering --> e_sub[Sub-agents]
  t_research --> r_sub[Sub-agents]
  t_ops --> o_sub[Sub-agents]
  t_sales --> s_sub[Sub-agents]

  %% Workspace & artifacts
  subgraph Workspace
    meeting[Meeting Engine]
    artifacts[Artifact Store]
    registry[Decision Registry]
    initiatives[Initiative Rooms]
  end

  ceo --> meeting
  t_product --> meeting
  t_engineering --> meeting
  t_research --> meeting
  t_ops --> meeting
  t_sales --> meeting

  p_sub --> artifacts
  e_sub --> artifacts
  r_sub --> artifacts
  o_sub --> artifacts
  s_sub --> artifacts
  meeting --> registry
  meeting --> initiatives
  artifacts --> initiatives

  %% Signals & metrics
  subgraph Observability
    metrics[Metrics & KPIs]
    signals[Signals / Risks]
  end

  artifacts --> metrics
  registry --> metrics
  initiatives --> signals
  metrics --> ceo
  signals --> ceo
  ceo --> bod
```

## Data & Decision Flow
- Governance sets strategy → CEO orchestrates → Team Leads execute with sub‑agents.
- Meetings generate decisions and action items stored as artifacts.
- Artifacts feed metrics and signals back up to the CEO and BOD.
