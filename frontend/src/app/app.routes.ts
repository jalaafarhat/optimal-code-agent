import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { ChatComponent } from './pages/chat/chat.component';
import { AgentsComponent } from './pages/agents/agents.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'chat', component: ChatComponent },
  { path: 'agents', component: AgentsComponent },
  { path: '**', redirectTo: '' },
];
