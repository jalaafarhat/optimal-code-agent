import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AgentService, AgentInfo } from '../../core/services/agent.service';

@Component({
  selector: 'app-agents',
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="agents-page container">
      <div class="page-header">
        <h1>Our AI Agents</h1>
        <p>Three specialized analysts, orchestrated by an intelligent manager agent.</p>
      </div>

      <div class="manager-card">
        <div class="manager-icon">◈</div>
        <div>
          <h2>Manager Agent</h2>
          <p>
            The entry point for every conversation. It reads your question, determines whether you need
            stock, crypto, or business analysis, and delegates to exactly the right specialist —
            never sending stock questions to crypto or vice versa.
          </p>
        </div>
      </div>

      <div class="agents-grid">
        @for (agent of agents; track agent.id) {
          <div class="agent-card">
            <div class="agent-icon" [attr.data-type]="agent.id">{{ iconFor(agent.id) }}</div>
            <h3>{{ agent.name }}</h3>
            <p>{{ agent.description }}</p>
            <div class="examples">
              <span class="examples-label">Example queries:</span>
              @for (ex of agent.examples; track ex) {
                <span class="example-tag">{{ ex }}</span>
              }
            </div>
          </div>
        }
      </div>

      <div class="cta">
        <a routerLink="/chat" class="btn-primary">Try It Now</a>
      </div>
    </div>
  `,
  styles: [`
    .agents-page {
      padding: 3rem 1.5rem 5rem;
    }
    .page-header {
      text-align: center;
      margin-bottom: 3rem;
    }
    .page-header h1 {
      font-size: 2rem;
      margin-bottom: 0.5rem;
    }
    .page-header p {
      color: var(--text-secondary);
    }
    .manager-card {
      display: flex;
      gap: 1.5rem;
      align-items: flex-start;
      background: linear-gradient(135deg, var(--surface), var(--bg-elevated));
      border: 1px solid var(--accent);
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2.5rem;
    }
    .manager-icon {
      font-size: 2.5rem;
      color: var(--accent);
      flex-shrink: 0;
    }
    .manager-card h2 {
      margin-bottom: 0.5rem;
    }
    .manager-card p {
      color: var(--text-secondary);
      line-height: 1.6;
    }
    .agents-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3rem;
    }
    .agent-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 2rem;
    }
    .agent-icon {
      font-size: 2rem;
      margin-bottom: 1rem;
    }
    .agent-card h3 {
      margin-bottom: 0.5rem;
    }
    .agent-card p {
      color: var(--text-secondary);
      font-size: 0.9rem;
      line-height: 1.5;
      margin-bottom: 1.25rem;
    }
    .examples-label {
      display: block;
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 0.5rem;
    }
    .example-tag {
      display: inline-block;
      padding: 0.3rem 0.65rem;
      margin: 0.2rem 0.3rem 0.2rem 0;
      background: var(--bg-elevated);
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 0.8rem;
      color: var(--text-secondary);
    }
    .cta {
      text-align: center;
    }
  `],
})
export class AgentsComponent implements OnInit {
  agents: AgentInfo[] = [];

  constructor(private agentService: AgentService) {}

  ngOnInit(): void {
    this.agentService.getAgents().subscribe({
      next: (data) => { this.agents = data; },
      error: () => {
        this.agents = [
          { id: 'stock_agent', name: 'Stock Analyst', description: 'Equities and ETF analysis', icon: 'trending_up', examples: ['Analyze Apple'] },
          { id: 'crypto_agent', name: 'Crypto Analyst', description: 'Cryptocurrency analysis', icon: 'currency_bitcoin', examples: ['Bitcoin price'] },
          { id: 'business_agent', name: 'Business Strategist', description: 'Side business ROI', icon: 'business_center', examples: ['Passive income'] },
        ];
      },
    });
  }

  iconFor(id: string): string {
    const icons: Record<string, string> = {
      stock_agent: '📈',
      crypto_agent: '₿',
      business_agent: '💼',
    };
    return icons[id] ?? '🤖';
  }
}
