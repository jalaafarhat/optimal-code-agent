import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="footer">
      <div class="container footer-inner">
        <p>&copy; {{ year }} FinAgent Platform. AI-powered financial analysis.</p>
        <p class="disclaimer">Not financial or legal advice. Outcomes depend on execution and market conditions.</p>
      </div>
    </footer>
  `,
  styles: [`
    .footer {
      border-top: 1px solid var(--border);
      padding: 2rem 0;
      margin-top: auto;
    }
    .footer-inner {
      text-align: center;
      color: var(--text-muted);
      font-size: 0.875rem;
    }
    .disclaimer {
      margin-top: 0.5rem;
      font-size: 0.75rem;
      opacity: 0.7;
    }
  `],
})
export class FooterComponent {
  year = new Date().getFullYear();
}
