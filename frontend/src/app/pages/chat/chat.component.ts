import { Component, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { AgentService, ChatResponse } from '../../core/services/agent.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  agent?: string | null;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule, DatePipe],
  template: `
    <div class="chat-page">
      <div class="chat-header container">
        <h1>Financial Analysis Chat</h1>
        <p>Ask about stocks, crypto, or business opportunities</p>
        @if (connectionStatus === 'offline') {
          <div class="status-banner error">
            Backend offline — run in a terminal:
            <code>cd multi-agent</code> then <code>uvicorn server:app --reload --port 8000</code>
            <button type="button" class="retry-btn" (click)="checkConnection()">Retry</button>
          </div>
        }
      </div>

      <div class="chat-layout container">
        <aside class="suggestions">
          <h3>Try asking</h3>
          @for (s of suggestions; track s) {
            <button class="suggestion-btn" (click)="sendSuggestion(s)" [disabled]="loading">
              {{ s }}
            </button>
          }
        </aside>

        <div class="chat-panel">
          <div class="messages" #messagesContainer>
            @if (messages.length === 0) {
              <div class="empty-state">
                <div class="empty-icon">◈</div>
                <p>Start a conversation. The manager agent will route your question to the right specialist.</p>
              </div>
            }
            @for (msg of messages; track msg.timestamp) {
              <div class="message" [class.user]="msg.role === 'user'" [class.assistant]="msg.role === 'assistant'">
                @if (msg.role === 'assistant' && msg.agent) {
                  <span class="agent-badge">{{ formatAgent(msg.agent) }}</span>
                }
                <div class="message-content">{{ msg.content }}</div>
                <span class="message-time">{{ msg.timestamp | date:'shortTime' }}</span>
              </div>
            }
            @if (loading) {
              <div class="message assistant loading-msg">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
                <span>Analyzing...</span>
              </div>
            }
          </div>

          <form class="input-bar" (ngSubmit)="sendMessage()">
            <input
              type="text"
              [(ngModel)]="inputText"
              name="message"
              placeholder="e.g. Analyze Apple stock, Bitcoin price, side business with $5000..."
              [disabled]="loading"
              autocomplete="off"
            />
            <button type="submit" class="btn-primary" [disabled]="loading || !inputText.trim()">
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-page {
      min-height: calc(100vh - 64px);
      display: flex;
      flex-direction: column;
    }
    .chat-header {
      padding: 2rem 1.5rem 1rem;
      text-align: center;
    }
    .chat-header h1 {
      font-size: 1.75rem;
      margin-bottom: 0.25rem;
    }
    .chat-header p {
      color: var(--text-secondary);
    }
    .status-banner {
      margin-top: 1rem;
      padding: 0.75rem 1rem;
      border-radius: 8px;
      font-size: 0.875rem;
    }
    .status-banner.error {
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #fca5a5;
    }
    .status-banner code {
      background: rgba(0,0,0,0.3);
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      font-size: 0.8rem;
    }
    .retry-btn {
      margin-left: 0.75rem;
      padding: 0.25rem 0.75rem;
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
    }
    .chat-layout {
      display: grid;
      grid-template-columns: 260px 1fr;
      gap: 1.5rem;
      flex: 1;
      padding-bottom: 2rem;
      min-height: 0;
    }
    @media (max-width: 768px) {
      .chat-layout { grid-template-columns: 1fr; }
      .suggestions { display: none; }
    }
    .suggestions h3 {
      font-size: 0.85rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.75rem;
    }
    .suggestion-btn {
      display: block;
      width: 100%;
      text-align: left;
      padding: 0.65rem 0.85rem;
      margin-bottom: 0.5rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text-secondary);
      font-size: 0.85rem;
      cursor: pointer;
      transition: border-color 0.2s, color 0.2s;
    }
    .suggestion-btn:hover:not(:disabled) {
      border-color: var(--accent);
      color: var(--text-primary);
    }
    .chat-panel {
      display: flex;
      flex-direction: column;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      min-height: 500px;
      max-height: calc(100vh - 220px);
    }
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .empty-state {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: var(--text-muted);
      text-align: center;
      padding: 2rem;
    }
    .empty-icon {
      font-size: 3rem;
      color: var(--accent);
      margin-bottom: 1rem;
      opacity: 0.5;
    }
    .message {
      max-width: 85%;
      padding: 0.85rem 1.1rem;
      border-radius: 12px;
      position: relative;
    }
    .message.user {
      align-self: flex-end;
      background: var(--accent);
      color: white;
      border-bottom-right-radius: 4px;
    }
    .message.assistant {
      align-self: flex-start;
      background: var(--bg-elevated);
      border: 1px solid var(--border);
      border-bottom-left-radius: 4px;
    }
    .agent-badge {
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--accent);
      margin-bottom: 0.35rem;
    }
    .message-content {
      white-space: pre-wrap;
      line-height: 1.55;
      font-size: 0.925rem;
    }
    .message-time {
      display: block;
      font-size: 0.7rem;
      opacity: 0.6;
      margin-top: 0.35rem;
    }
    .loading-msg {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      color: var(--text-muted);
      font-size: 0.875rem;
    }
    .typing-indicator {
      display: flex;
      gap: 4px;
    }
    .typing-indicator span {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--accent);
      animation: bounce 1.4s infinite ease-in-out both;
    }
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }
    .input-bar {
      display: flex;
      gap: 0.75rem;
      padding: 1rem;
      border-top: 1px solid var(--border);
      background: var(--bg);
    }
    .input-bar input {
      flex: 1;
      padding: 0.75rem 1rem;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
      color: var(--text-primary);
      font-size: 0.95rem;
      outline: none;
    }
    .input-bar input:focus {
      border-color: var(--accent);
    }
    .input-bar input::placeholder {
      color: var(--text-muted);
    }
  `],
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;

  messages: ChatMessage[] = [];
  inputText = '';
  loading = false;
  sessionId: string | null = null;
  connectionStatus: 'online' | 'offline' = 'online';
  private shouldScroll = false;
  private healthInterval: ReturnType<typeof setInterval> | null = null;

  suggestions = [
    'What is Apple stock price right now?',
    'Analyze Tesla fundamentals',
    'Bitcoin price and 1-year performance',
    'Compare BTC and ETH',
    'Side business ideas with $5000 budget',
    'Best passive income opportunities',
  ];

  constructor(private agentService: AgentService) {}

  ngOnInit(): void {
    this.checkConnection();
    this.healthInterval = setInterval(() => this.checkConnection(), 5000);

    this.agentService.createSession().subscribe({
      next: (res) => { this.sessionId = res.session_id; },
      error: () => {},
    });
  }

  ngOnDestroy(): void {
    if (this.healthInterval) {
      clearInterval(this.healthInterval);
    }
  }

  checkConnection(): void {
    this.agentService.healthCheck().subscribe({
      next: () => { this.connectionStatus = 'online'; },
      error: () => { this.connectionStatus = 'offline'; },
    });
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  sendSuggestion(text: string): void {
    this.inputText = text;
    this.sendMessage();
  }

  sendMessage(): void {
    const text = this.inputText.trim();
    if (!text || this.loading) return;

    this.messages.push({
      role: 'user',
      content: text,
      timestamp: new Date(),
    });
    this.inputText = '';
    this.loading = true;
    this.shouldScroll = true;

    this.agentService.chat({
      message: text,
      session_id: this.sessionId ?? undefined,
    }).subscribe({
      next: (res: ChatResponse) => {
        this.sessionId = res.session_id;
        this.messages.push({
          role: 'assistant',
          content: res.response,
          agent: res.agent,
          timestamp: new Date(),
        });
        this.loading = false;
        this.connectionStatus = 'online';
        this.shouldScroll = true;
      },
      error: (err) => {
        const detail = err?.error?.detail;
        const message = typeof detail === 'string'
          ? detail
          : 'Failed to reach the analysis server. Start the backend: cd multi-agent && uvicorn server:app --reload --port 8000';
        this.messages.push({
          role: 'assistant',
          content: message,
          timestamp: new Date(),
        });
        this.loading = false;
        this.connectionStatus = 'offline';
        this.shouldScroll = true;
      },
    });
  }

  formatAgent(agent: string): string {
    const map: Record<string, string> = {
      manager: 'Manager',
      stock_agent: 'Stock Analyst',
      crypto_agent: 'Crypto Analyst',
      business_agent: 'Business Strategist',
    };
    return map[agent] ?? agent;
  }

  private scrollToBottom(): void {
    const el = this.messagesContainer?.nativeElement;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }
}
