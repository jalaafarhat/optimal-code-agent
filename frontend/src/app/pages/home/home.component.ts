import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  template: `
    <section class="hero">
      <div class="container">
        <div class="hero-badge">Multi-Agent AI Platform</div>
        <h1>Intelligent Financial Analysis<br/><span class="gradient-text">Powered by Specialized Agents</span></h1>
        <p class="hero-sub">
          Ask about stocks, crypto, or business opportunities. Our manager agent routes your question
          to the right specialist for accurate, data-driven insights.
        </p>
        <div class="hero-actions">
          <a routerLink="/chat" class="btn-primary">Start Chatting</a>
          <a routerLink="/agents" class="btn-secondary">Meet the Agents</a>
        </div>
      </div>
      <div class="hero-glow"></div>
    </section>

    <section class="features container">
      <div class="feature-card">
        <div class="feature-icon stock">📈</div>
        <h3>Stock Analyst</h3>
        <p>Live prices, fundamentals, analyst consensus, and technical indicators for equities and ETFs.</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon crypto">₿</div>
        <h3>Crypto Analyst</h3>
        <p>Real-time crypto prices, historical performance, and multi-coin comparisons.</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon business">💼</div>
        <h3>Business Strategist</h3>
        <p>Side business ideas, ROI estimates, and passive income opportunity analysis.</p>
      </div>
    </section>

    <section class="how-it-works container">
      <h2>How It Works</h2>
      <div class="steps">
        <div class="step">
          <span class="step-num">1</span>
          <h4>Ask a Question</h4>
          <p>Type your financial question in natural language.</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
          <span class="step-num">2</span>
          <h4>Smart Routing</h4>
          <p>The manager agent identifies intent and delegates to the right specialist.</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
          <span class="step-num">3</span>
          <h4>Data-Driven Answer</h4>
          <p>Specialists fetch live market data and deliver structured analysis.</p>
        </div>
      </div>
    </section>
  `,
  styles: [`
    .hero {
      position: relative;
      padding: 6rem 0 4rem;
      text-align: center;
      overflow: hidden;
    }
    .hero-badge {
      display: inline-block;
      padding: 0.35rem 1rem;
      border-radius: 999px;
      background: var(--accent-dim);
      color: var(--accent);
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
    }
    h1 {
      font-size: clamp(2rem, 5vw, 3.25rem);
      font-weight: 800;
      line-height: 1.15;
      margin-bottom: 1.25rem;
    }
    .gradient-text {
      background: linear-gradient(135deg, var(--accent), #60a5fa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .hero-sub {
      max-width: 600px;
      margin: 0 auto 2rem;
      color: var(--text-secondary);
      font-size: 1.1rem;
      line-height: 1.6;
    }
    .hero-actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
      flex-wrap: wrap;
    }
    .hero-glow {
      position: absolute;
      top: -50%;
      left: 50%;
      transform: translateX(-50%);
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, transparent 70%);
      pointer-events: none;
    }
    .features {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.5rem;
      padding: 4rem 1.5rem;
    }
    .feature-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 2rem;
      transition: border-color 0.2s, transform 0.2s;
    }
    .feature-card:hover {
      border-color: var(--accent);
      transform: translateY(-2px);
    }
    .feature-icon {
      font-size: 2rem;
      margin-bottom: 1rem;
    }
    .feature-card h3 {
      margin-bottom: 0.5rem;
      font-size: 1.15rem;
    }
    .feature-card p {
      color: var(--text-secondary);
      font-size: 0.9rem;
      line-height: 1.5;
    }
    .how-it-works {
      padding: 4rem 1.5rem 6rem;
      text-align: center;
    }
    .how-it-works h2 {
      font-size: 1.75rem;
      margin-bottom: 2.5rem;
    }
    .steps {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      gap: 1rem;
      flex-wrap: wrap;
    }
    .step {
      flex: 1;
      min-width: 200px;
      max-width: 260px;
    }
    .step-num {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--accent);
      color: white;
      font-weight: 700;
      margin-bottom: 0.75rem;
    }
    .step h4 {
      margin-bottom: 0.35rem;
    }
    .step p {
      color: var(--text-secondary);
      font-size: 0.875rem;
    }
    .step-arrow {
      color: var(--text-muted);
      font-size: 1.5rem;
      padding-top: 0.5rem;
    }
    @media (max-width: 768px) {
      .step-arrow { display: none; }
    }
  `],
})
export class HomeComponent {}
