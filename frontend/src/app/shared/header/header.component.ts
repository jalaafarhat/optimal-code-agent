import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <header class="header">
      <div class="container header-inner">
        <a routerLink="/" class="logo">
          <span class="logo-icon">◈</span>
          <span class="logo-text">FinAgent</span>
        </a>
        <nav class="nav">
          <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Home</a>
          <a routerLink="/chat" routerLinkActive="active">Chat</a>
          <a routerLink="/agents" routerLinkActive="active">Agents</a>
        </nav>
        <a routerLink="/chat" class="btn-primary btn-sm">Start Analysis</a>
      </div>
    </header>
  `,
  styles: [`
    .header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(10, 14, 23, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
    }
    .header-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 64px;
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      text-decoration: none;
      color: var(--text-primary);
      font-weight: 700;
      font-size: 1.25rem;
    }
    .logo-icon {
      color: var(--accent);
      font-size: 1.5rem;
    }
    .nav {
      display: flex;
      gap: 2rem;
    }
    .nav a {
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 0.95rem;
      transition: color 0.2s;
    }
    .nav a:hover, .nav a.active {
      color: var(--accent);
    }
    @media (max-width: 640px) {
      .nav { display: none; }
    }
  `],
})
export class HeaderComponent {}
