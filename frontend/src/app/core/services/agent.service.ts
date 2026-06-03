import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, tap, throwError } from 'rxjs';

export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  examples: string[];
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  agent: string | null;
}

export interface SessionResponse {
  session_id: string;
  user_id: string;
}

export interface HealthResponse {
  status: string;
  app?: string;
  model?: string;
  api_key_configured?: boolean;
}

@Injectable({ providedIn: 'root' })
export class AgentService {
  private baseUrl = '/api';
  private readonly fallbackUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  private request<T>(method: 'get' | 'post', path: string, body?: unknown): Observable<T> {
    const primary = `${this.baseUrl}${path}`;
    const fallback = `${this.fallbackUrl}${path}`;

    const call = (url: string) =>
      method === 'get'
        ? this.http.get<T>(url)
        : this.http.post<T>(url, body);

    return call(primary).pipe(
      catchError(() =>
        call(fallback).pipe(
          tap(() => {
            this.baseUrl = this.fallbackUrl;
          }),
        ),
      ),
    );
  }

  getAgents(): Observable<AgentInfo[]> {
    return this.request<AgentInfo[]>('get', '/agents');
  }

  createSession(): Observable<SessionResponse> {
    return this.request<SessionResponse>('post', '/sessions', {});
  }

  chat(request: ChatRequest): Observable<ChatResponse> {
    return this.request<ChatResponse>('post', '/chat', request);
  }

  healthCheck(): Observable<HealthResponse> {
    return this.request<HealthResponse>('get', '/health').pipe(
      catchError(() => throwError(() => new Error('Backend offline'))),
    );
  }
}
