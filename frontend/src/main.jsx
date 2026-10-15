import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './style.css';

class AppErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error) { return { error }; }
  componentDidCatch(error) { console.error('Portal render error:', error); }
  render() {
    if (this.state.error) return <main className="shell"><h1>Nie udało się uruchomić panelu</h1><p>Odśwież stronę lub skontaktuj się z administratorem.</p></main>;
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(<AppErrorBoundary><React.StrictMode><App /></React.StrictMode></AppErrorBoundary>);
