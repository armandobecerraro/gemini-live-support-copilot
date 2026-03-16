'use client';

import { useState, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { AgentResponse, SessionStatus } from '@/types';
import { analyzeIssue, confirmAction } from '@/services/api';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { useScreenCapture } from '@/hooks/useScreenCapture';
import { 
  Mic, 
  MicOff, 
  Monitor, 
  FileText, 
  Play, 
  RotateCcw, 
  Brain, 
  Zap, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  Loader2,
  Trash2,
  BookOpen,
  HelpCircle,
  Code2
} from 'lucide-react';

export default function Home() {
  const [description, setDescription] = useState('');
  const [logs, setLogs] = useState('');
  const [sessionId] = useState(uuidv4());
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showDocs, setShowDocs] = useState(false);
  const { isRecording, transcript, startRecording, stopRecording, clearTranscript } = useAudioRecorder();
  const { capturedImage, captureScreen, clearCapture } = useScreenCapture();

  const handleAnalyze = useCallback(async () => {
    const text = description || transcript;
    if (!text.trim()) return;
    setStatus('loading');
    setError(null);
    try {
      const result = await analyzeIssue({
        description: text,
        logs: logs || undefined,
        image_base64: capturedImage || undefined,
        session_id: sessionId,
      });
      setResponse(result);
      setStatus('active');
    } catch (e: any) {
      setError(e?.response?.data?.error || 'Failed to connect to agent');
      setStatus('error');
    }
  }, [description, transcript, logs, capturedImage, sessionId]);

  const handleConfirm = async (actionId: string, approved: boolean) => {
    if (!response) return;
    try {
      await confirmAction(response.session_id, actionId, approved);
      setResponse(prev => prev ? {
        ...prev,
        suggested_actions: prev.suggested_actions.map(a =>
          a.id === actionId ? { ...a, title: approved ? `✓ ${a.title}` : `✗ ${a.title}` } : a
        )
      } : prev);
    } catch (e) {
      console.error('Failed to confirm action', e);
    }
  };

  const handleReset = () => {
    setDescription('');
    setLogs('');
    clearTranscript();
    clearCapture();
    setResponse(null);
    setStatus('idle');
    setError(null);
  };

  const loadExample = (type: 'db' | 'auth' | 'deploy' | 'memory' | 'timeout' | 'disk' | 'ratelimit' | 'ssl' | 'voice1' | 'voice2' | 'screenshot1' | 'screenshot2') => {
    // Replace previous content so each example is tried one at a time
    setDescription('');
    setLogs('');
    clearTranscript();
    clearCapture();
    setResponse(null);
    setError(null);
    setStatus('idle');
    if (type === 'db') {
      setDescription('Our payment API has been returning 503 errors for the last 10 minutes. Users cannot complete checkouts.');
      setLogs('2026-03-12 10:45:01 ERROR Connection refused to database host db-primary:5432\n2026-03-12 10:45:02 ERROR Failed to acquire connection from pool (timeout=30s)\n2026-03-12 10:45:03 FATAL Max connection pool size (100) reached\n2026-03-12 10:45:04 ERROR HTTP 503 returned to client on /api/payments\n2026-03-12 10:45:05 WARN Retrying connection (attempt 3/3)\n2026-03-12 10:45:06 FATAL Database connection exhausted — all retries failed');
    } else if (type === 'auth') {
      setDescription('Authentication service is returning 401 for all users. Login and API calls started failing after the last deploy.');
      setLogs('2026-03-16 10:00:00 ERROR [auth-service] JWT secret key mismatch\n2026-03-16 10:00:05 WARN [auth-service] Token validation failed: signature invalid\n2026-03-16 10:00:10 ERROR [auth-service] 401 Unauthorized returned to client');
    } else if (type === 'deploy') {
      setDescription('New deployment is stuck. Pods are not starting after the latest release.');
      setLogs('2026-03-12 14:00:01 INFO Deployment supportsight-backend rolling update started\n2026-03-12 14:00:15 WARNING Pod supportsight-backend-xyz ImagePullBackOff\n2026-03-12 14:00:45 ERROR Failed to pull image gcr.io/project/backend:v2.1.0 - 403 Forbidden\n2026-03-12 14:01:15 ERROR Readiness probe failed: container not ready\n2026-03-12 14:02:00 WARNING Rollout stalled — 0/3 pods ready');
    } else if (type === 'memory') {
      setDescription('Backend service keeps restarting every 20 minutes. Kubernetes shows OOMKilled status.');
      setLogs('2026-03-12 09:00:00 INFO Service started OK\n2026-03-12 09:15:32 WARN Heap usage at 78% (3.1GB/4GB)\n2026-03-12 09:18:44 WARN Heap usage at 92% (3.7GB/4GB)\n2026-03-12 09:20:01 ERROR OutOfMemoryError: Java heap space\n2026-03-12 09:20:01 FATAL JVM terminated: OOM\n2026-03-12 09:20:15 INFO Service restarting (attempt 1)');
    } else if (type === 'timeout') {
      setDescription('API gateway is returning 504 Gateway Timeout. Downstream services are slow or not responding.');
      setLogs('2026-03-14 11:00:00 WARN Upstream timeout after 30s (service: orders-api)\n2026-03-14 11:00:01 ERROR 504 Gateway Timeout returned to client\n2026-03-14 11:00:05 WARN Upstream timeout after 30s (service: inventory)\n2026-03-14 11:00:06 ERROR Read timed out reading from backend\n2026-03-14 11:00:10 FATAL Timeout cascade: 3/5 upstreams failed');
    } else if (type === 'disk') {
      setDescription('Batch jobs are failing. Logs show "No space left on device" and write errors.');
      setLogs('2026-03-13 08:00:00 ERROR Failed to write checkpoint: No space left on device\n2026-03-13 08:00:01 FATAL ENOSPC: disk full on /data\n2026-03-13 08:00:05 ERROR Cannot create temp file for export\n2026-03-13 08:00:10 WARN Disk usage 99% on volume /data');
    } else if (type === 'ratelimit') {
      setDescription('Third-party API integration started returning 429. Our service is being rate-limited.');
      setLogs('2026-03-15 09:30:00 WARN Rate limit exceeded for API key (retry-after: 60s)\n2026-03-15 09:30:01 ERROR 429 Too Many Requests from external-api.com\n2026-03-15 09:30:05 ERROR EXCEPTION in sync job: RateLimitExceeded\n2026-03-15 09:30:10 WARN Backing off 120s before next request');
    } else if (type === 'ssl') {
      setDescription('Service cannot connect to the legacy API. SSL handshake failures in the logs.');
      setLogs('2026-03-14 14:00:00 ERROR SSL handshake failed: certificate has expired\n2026-03-14 14:00:01 FATAL EXCEPTION: javax.net.ssl.SSLPeerUnverifiedException\n2026-03-14 14:00:05 ERROR Failed to connect to legacy-api.internal (TLS 1.2)\n2026-03-14 14:00:10 WARN Certificate valid until 2025-12-01 — expired');
    } else if (type === 'voice1') {
      setDescription('Our payment API is returning 503 errors and users cannot complete checkouts.');
      setLogs('');
    } else if (type === 'voice2') {
      setDescription('Backend service keeps restarting every 20 minutes; Kubernetes shows OOMKilled and we see OutOfMemoryError in the logs.');
      setLogs('');
    } else if (type === 'screenshot1') {
      setDescription('I am seeing this error on the production dashboard — see attached screenshot. The UI shows a 503 Service Unavailable message.');
      setLogs('');
    } else if (type === 'screenshot2') {
      setDescription('New deployment is stuck. Pods are in ImagePullBackOff — see attached screenshot of kubectl get pods output.');
      setLogs('');
    }
    setShowDocs(false);
  };

  return (
    <main className="min-h-screen bg-[#050505] text-gray-100 selection:bg-cyan-500/30">
      {/* Documentation Overlay */}
      {showDocs && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/80 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-[#0a0a0a] border border-white/10 rounded-3xl w-full max-w-2xl max-h-[80vh] overflow-y-auto p-8 shadow-2xl relative text-left">
            <button 
              onClick={() => setShowDocs(false)}
              className="absolute top-6 right-6 p-2 hover:bg-white/5 rounded-full transition-colors"
            >
              <XCircle className="w-6 h-6 text-white/40 hover:text-white" />
            </button>
            
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 bg-cyan-500/20 rounded-xl flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-cyan-400" />
              </div>
              <h2 className="text-2xl font-bold">Quick Start Guide</h2>
            </div>

            <div className="space-y-8">
              <section className="space-y-3">
                <h3 className="text-sm font-bold uppercase tracking-widest text-white/40 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-emerald-400" /> How does it work?
                </h3>
                <p className="text-sm text-gray-400 leading-relaxed">
                  SupportSight Live is a multimodal autonomous agent designed for SRE and DevOps engineers. It analyzes incidents using three simultaneous data streams:
                </p>
                <ul className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <li className="bg-white/5 border border-white/5 rounded-2xl p-4 text-center">
                    <Mic className="w-5 h-5 mx-auto mb-2 text-cyan-400" />
                    <span className="text-[10px] font-bold uppercase tracking-tighter">Real-Time Voice</span>
                  </li>
                  <li className="bg-white/5 border border-white/5 rounded-2xl p-4 text-center">
                    <Monitor className="w-5 h-5 mx-auto mb-2 text-emerald-400" />
                    <span className="text-[10px] font-bold uppercase tracking-tighter">Screen Vision</span>
                  </li>
                  <li className="bg-white/5 border border-white/5 rounded-2xl p-4 text-center">
                    <FileText className="w-5 h-5 mx-auto mb-2 text-purple-400" />
                    <span className="text-[10px] font-bold uppercase tracking-tighter">Log Analysis</span>
                  </li>
                </ul>
              </section>

              <section className="space-y-3 p-4 bg-white/5 border border-white/10 rounded-2xl">
                <h3 className="text-sm font-bold uppercase tracking-widest text-cyan-400 flex items-center gap-2">
                  <FileText className="w-4 h-4" /> Logs attached — how the log parser works
                </h3>
                <p className="text-xs text-gray-400 leading-relaxed">
                  When you attach logs and tap <strong>Analyze Incident</strong>, the backend analyzes them and extracts every line containing <strong>ERROR</strong>, <strong>FATAL</strong>, or <strong>EXCEPTION</strong>, then infers a <strong>probable cause</strong> from keywords. That summary is used by the agent to produce hypotheses and recommendations.
                </p>
                <ul className="text-[10px] text-gray-500 space-y-1 mt-2">
                  <li>• <strong className="text-cyan-400">Connection refused</strong> in logs → parser returns <em>Service connectivity failure</em> → expect DB/connectivity hypotheses.</li>
                  <li>• <strong className="text-amber-400">OutOfMemoryError / OOM</strong> → <em>Memory exhaustion</em> → expect backend/memory-leak hypotheses.</li>
                  <li>• <strong className="text-purple-400">timeout</strong> → <em>Timeout cascade</em> → expect timeout/retry recommendations.</li>
                  <li>• Other errors → <em>Application error in N log lines</em> → agent uses the error list for hypotheses (e.g. auth, deployment).</li>
                </ul>
              </section>

              <section className="space-y-3">
                <h3 className="text-sm font-bold uppercase tracking-widest text-white/40 flex items-center gap-2">
                  <Play className="w-4 h-4 text-cyan-400" /> Ready-to-run examples (description + logs)
                </h3>
                <p className="text-[10px] text-white/30">Each button replaces the current form and fills <strong>Incident Context</strong> and <strong>Logs</strong> with realistic content. Tap &quot;Analyze Incident&quot; to see hypotheses and recommendations.</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button 
                    onClick={() => loadExample('db')}
                    className="flex flex-col gap-2 p-4 bg-cyan-500/5 border border-cyan-500/20 rounded-2xl hover:bg-cyan-500/10 transition-all text-left group"
                  >
                    <span className="text-xs font-bold text-cyan-400 group-hover:underline">1. Database / 503</span>
                    <span className="text-[10px] text-gray-500">Connection refused and pool errors → connectivity failure. Expect DB/connection-pool hypotheses.</span>
                  </button>
                  <button 
                    onClick={() => loadExample('memory')}
                    className="flex flex-col gap-2 p-4 bg-amber-500/5 border border-amber-500/20 rounded-2xl hover:bg-amber-500/10 transition-all text-left group"
                  >
                    <span className="text-xs font-bold text-amber-400 group-hover:underline">2. Backend / OOM</span>
                    <span className="text-[10px] text-gray-500">OutOfMemoryError and OOM → memory exhaustion. Expect heap/GC recommendations.</span>
                  </button>
                  <button 
                    onClick={() => loadExample('deploy')}
                    className="flex flex-col gap-2 p-4 bg-purple-500/5 border border-purple-500/20 rounded-2xl hover:bg-purple-500/10 transition-all text-left group"
                  >
                    <span className="text-xs font-bold text-purple-400 group-hover:underline">3. Deployment</span>
                    <span className="text-[10px] text-gray-500">ImagePullBackOff and 403 Forbidden → deployment/registry auth hypotheses.</span>
                  </button>
                  <button 
                    onClick={() => loadExample('auth')}
                    className="flex flex-col gap-2 p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-2xl hover:bg-emerald-500/10 transition-all text-left group"
                  >
                    <span className="text-xs font-bold text-emerald-400 group-hover:underline">4. Auth / 401</span>
                    <span className="text-[10px] text-gray-500">JWT and 401 errors → auth/signing hypotheses and recommendations.</span>
                  </button>
                  <button 
                    onClick={() => loadExample('timeout')}
                    className="flex flex-col gap-2 p-4 bg-rose-500/5 border border-rose-500/20 rounded-2xl hover:bg-rose-500/10 transition-all text-left group"
                  >
                    <span className="text-xs font-bold text-rose-400 group-hover:underline">5. Timeout / 504</span>
                    <span className="text-[10px] text-gray-500">Upstream timeouts and 504 → timeout cascade. Expect timeout/retry recommendations.</span>
                  </button>
                  <button 
                    onClick={() => loadExample('disk')}
                    className="flex flex-col gap-2 p-4 bg-slate-500/5 border border-slate-400/20 rounded-2xl hover:bg-slate-500/10 transition-all text-left group"
                  >
                    <span className="text-xs font-bold text-slate-300 group-hover:underline">6. Disk full</span>
                    <span className="text-[10px] text-gray-500">No space left / ENOSPC → disk exhaustion. Expect storage/cleanup recommendations.</span>
                  </button>
                  <button 
                    onClick={() => loadExample('ratelimit')}
                    className="flex flex-col gap-2 p-4 bg-orange-500/5 border border-orange-500/20 rounded-2xl hover:bg-orange-500/10 transition-all text-left group"
                  >
                    <span className="text-xs font-bold text-orange-400 group-hover:underline">7. Rate limit / 429</span>
                    <span className="text-[10px] text-gray-500">429 Too Many Requests and rate limit → backoff/retry and quota hypotheses.</span>
                  </button>
                  <button 
                    onClick={() => loadExample('ssl')}
                    className="flex flex-col gap-2 p-4 bg-teal-500/5 border border-teal-500/20 rounded-2xl hover:bg-teal-500/10 transition-all text-left group"
                  >
                    <span className="text-xs font-bold text-teal-400 group-hover:underline">8. SSL / certificate</span>
                    <span className="text-[10px] text-gray-500">Certificate expired and SSL handshake failed → TLS/certificate renewal recommendations.</span>
                  </button>
                </div>
              </section>

              <section className="space-y-3 p-6 bg-gradient-to-br from-cyan-500/10 to-transparent border border-cyan-500/20 rounded-2xl">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-sm font-bold uppercase tracking-widest text-white">Gemini Reasoning</h3>
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">
                  The agent uses the project&apos;s official runbooks to provide accurate, safe solutions and suggested actions.
                </p>
              </section>
            </div>
          </div>
        </div>
      )}

      {/* Navbar / Header */}
      <nav className="border-b border-white/5 bg-black/40 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-emerald-500 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Brain className="w-5 h-5 text-black" strokeWidth={2.5} />
            </div>
            <h1 className="text-xl font-bold tracking-tight">SupportSight <span className="bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent">Live</span></h1>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setShowDocs(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full transition-all text-[10px] font-bold uppercase tracking-widest text-cyan-400"
            >
              <HelpCircle className="w-3.5 h-3.5" /> Guide
            </button>
            <span className="text-[10px] font-medium uppercase tracking-widest text-white/40 border border-white/10 px-2 py-0.5 rounded-full bg-white/5">Production v1.0</span>
            <button 
              onClick={handleReset}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors text-white/60 hover:text-white"
              title="Reset Workspace"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* LEFT: Command Center (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            <section className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm shadow-2xl">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-1.5 h-4 bg-cyan-500 rounded-full"></div>
                <h2 className="text-sm font-bold uppercase tracking-wider text-white/80">Command Center</h2>
              </div>

              <div className="space-y-6">
                {/* Voice Input Section */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-medium text-white/40 flex items-center gap-1.5 uppercase tracking-tighter">
                      <Mic className="w-3 h-3" /> Voice Analysis
                    </label>
                    <button
                      onClick={isRecording ? stopRecording : startRecording}
                      className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all border ${
                        isRecording
                          ? 'bg-red-500/10 border-red-500/50 text-red-400 animate-pulse'
                          : 'bg-white/5 border-white/10 text-white hover:bg-white/10'
                      }`}
                    >
                      {isRecording ? <><MicOff className="w-3 h-3" /> Stop Recording</> : <><Mic className="w-3 h-3" /> Start Analysis</>}
                    </button>
                  </div>
                  {transcript && (
                    <div className="bg-white/5 border border-white/5 rounded-xl p-4 text-sm leading-relaxed text-cyan-50/80 italic relative group">
                      "{transcript}"
                      <button onClick={clearTranscript} className="absolute -top-2 -right-2 w-6 h-6 bg-black border border-white/10 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:text-red-400">
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>

                {/* Text Description */}
                <div className="space-y-2">
                  <label className="text-xs font-medium text-white/40 flex items-center gap-1.5 uppercase tracking-tighter">
                    <FileText className="w-3 h-3" /> Incident Context
                  </label>
                  <textarea
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    placeholder="Briefly describe the anomaly..."
                    className="w-full bg-black/40 text-white rounded-xl p-4 text-sm border border-white/5 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 outline-none transition-all h-28 placeholder:text-white/10"
                  />
                </div>

                {/* Evidence Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-white/40 flex items-center gap-1.5 uppercase tracking-tighter">
                      <Monitor className="w-3 h-3" /> Visuals
                    </label>
                    <button
                      onClick={captureScreen}
                      className="w-full h-12 flex items-center justify-center gap-2 rounded-xl bg-white/5 border border-dashed border-white/20 hover:border-cyan-500/50 hover:bg-cyan-500/5 transition-all text-xs font-medium text-white/60 hover:text-white"
                    >
                      <Monitor className="w-4 h-4" /> Capture Screen
                    </button>
                  </div>
                  <div className="space-y-2 text-right">
                    <label className="text-xs font-medium text-white/40 flex items-center gap-1.5 uppercase tracking-tighter justify-end">
                      Logs <FileText className="w-3 h-3" />
                    </label>
                    <button 
                      onClick={() => setLogs(logs ? '' : '...')}
                      className="w-full h-12 flex items-center justify-center gap-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-xs font-medium text-white/60"
                    >
                      {logs ? 'Logs Attached' : 'Attach Snippets'}
                    </button>
                  </div>
                </div>

                {capturedImage && (
                  <div className="relative rounded-xl overflow-hidden border border-white/10 group">
                    <img src={`data:image/png;base64,${capturedImage}`} alt="Evidence" className="w-full grayscale group-hover:grayscale-0 transition-all duration-500" />
                    <button onClick={clearCapture} className="absolute top-2 right-2 w-8 h-8 bg-black/80 backdrop-blur border border-white/10 rounded-lg flex items-center justify-center text-white/60 hover:text-red-400 transition-colors">
                      <XCircle className="w-4 h-4" />
                    </button>
                  </div>
                )}

                {logs && (
                  <textarea
                    value={logs}
                    onChange={e => setLogs(e.target.value)}
                    className="w-full bg-black/60 text-[10px] font-mono text-emerald-400/80 rounded-xl p-4 border border-emerald-500/10 h-32 focus:border-emerald-500/30 outline-none"
                  />
                )}

                {/* Main Action */}
                <button
                  onClick={handleAnalyze}
                  disabled={status === 'loading'}
                  className="w-full group relative flex items-center justify-center gap-3 py-4 rounded-2xl bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 disabled:opacity-50 disabled:grayscale transition-all shadow-xl shadow-cyan-500/10 overflow-hidden"
                >
                  <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                  {status === 'loading' ? (
                    <><Loader2 className="w-5 h-5 animate-spin" /> <span className="font-bold tracking-tight">ENGINEERING ANALYSIS...</span></>
                  ) : (
                    <><Zap className="w-5 h-5 fill-current" /> <span className="font-bold tracking-tight uppercase">Analyze Incident</span></>
                  )}
                </button>

                {error && (
                  <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-xs leading-relaxed">
                    <AlertTriangle className="w-4 h-4 shrink-0" />
                    <span>{error}</span>
                  </div>
                )}
              </div>
            </section>
          </div>

          {/* RIGHT: Analysis Output (7 cols) */}
          <div className="lg:col-span-7">
            {!response && status !== 'loading' && (
              <div className="h-full min-h-[500px] flex flex-col items-center justify-center text-center space-y-6 bg-white/[0.02] border border-dashed border-white/10 rounded-3xl p-12">
                <div className="relative">
                  <div className="absolute -inset-4 bg-cyan-500/20 blur-3xl rounded-full"></div>
                  <Brain className="w-16 h-16 text-white/20 relative z-10" strokeWidth={1} />
                </div>
                <div className="max-w-xs">
                  <h3 className="text-lg font-semibold text-white/60 mb-2">Systems Standby</h3>
                  <p className="text-sm text-white/30 leading-relaxed">Ready to process multimodal data streams. Provide context to begin incident triage.</p>
                </div>
              </div>
            )}

            {status === 'loading' && (
              <div className="h-full min-h-[500px] flex flex-col items-center justify-center space-y-8 bg-white/[0.02] border border-white/5 rounded-3xl p-12 overflow-hidden relative">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent animate-shimmer"></div>
                <div className="flex gap-1 items-center">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-2 h-8 bg-cyan-500/40 rounded-full animate-pulse" style={{ animationDelay: `${i * 0.2}s` }}></div>
                  ))}
                </div>
                <div className="text-center">
                  <p className="text-sm font-mono text-cyan-400 mb-2">GEMINI LIVE REASONING</p>
                  <p className="text-white/40 text-xs uppercase tracking-[0.2em]">Processing high-dimensional evidence...</p>
                </div>
              </div>
            )}

            {response && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                {/* Root Cause Banner (Competitive Addition) */}
                {response.root_cause_summary && (
                  <div className="bg-gradient-to-r from-red-500/10 to-transparent border-l-4 border-red-500 rounded-r-2xl p-6 shadow-lg shadow-red-500/5">
                    <h3 className="text-[10px] font-bold text-red-400 uppercase tracking-[0.2em] mb-2 flex items-center gap-2">
                      <Zap className="w-3 h-3 fill-current" /> Primary Root Cause Identified
                    </h3>
                    <p className="text-lg font-semibold text-white leading-tight">
                      {response.root_cause_summary}
                    </p>
                  </div>
                )}

                {/* Executive Summary */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {response.root_cause_summary && (
                    <section className="md:col-span-2 bg-gradient-to-r from-cyan-900/40 to-emerald-900/40 border border-cyan-500/30 rounded-2xl p-6 shadow-lg shadow-cyan-500/5">
                      <h3 className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                        <Zap className="w-3 h-3" /> Potential Root Cause Identified
                      </h3>
                      <p className="text-lg font-medium leading-tight text-white">{response.root_cause_summary}</p>
                    </section>
                  )}
                  <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-4 flex items-center gap-2">
                      <CheckCircle2 className="w-3 h-3 text-cyan-500" /> Executive Summary
                    </h3>
                    <p className="text-sm leading-relaxed text-gray-200">{response.what_i_understood}</p>
                  </section>

                  <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-4 flex items-center gap-2">
                      <Monitor className="w-3 h-3 text-emerald-500" /> Visual Context
                    </h3>
                    <p className="text-sm leading-relaxed text-gray-200">{response.what_i_see || "No visual evidence processed."}</p>
                  </section>
                </div>

                {/* Hypotheses */}
                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-6">Probability Matrix</h3>
                  <div className="grid gap-4">
                    {response.hypotheses.map((h, i) => (
                      <div key={i} className="bg-black/40 border border-white/5 rounded-xl p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-white/80">{h.description}</span>
                          <span className="text-xs font-mono text-cyan-400">{(h.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 transition-all duration-1000" 
                            style={{ width: `${h.confidence * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Suggested Actions */}
                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-6">Remediation Protocol</h3>
                  <div className="space-y-4">
                    {response.suggested_actions.map((action) => (
                      <div key={action.id} className={`group border rounded-2xl p-5 transition-all ${
                        action.is_destructive 
                          ? 'bg-red-500/[0.02] border-red-500/20 hover:border-red-500/40' 
                          : 'bg-white/[0.02] border-white/10 hover:border-cyan-500/30'
                      }`}>
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <h4 className="text-sm font-bold text-white">{action.title}</h4>
                              {action.is_destructive && (
                                <span className="text-[8px] font-bold bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded border border-red-500/20 uppercase tracking-tighter">Destructive</span>
                              )}
                            </div>
                            <p className="text-xs text-white/40 leading-relaxed max-w-md">{action.description}</p>
                          </div>
                          <div className="flex gap-2">
                            <button 
                              onClick={() => handleConfirm(action.id, false)}
                              className="px-4 py-2 rounded-xl text-[10px] font-bold uppercase tracking-wider text-white/40 hover:text-white hover:bg-white/5 transition-all"
                            >
                              Ignore
                            </button>
                            <button 
                              onClick={() => handleConfirm(action.id, true)}
                              className={`px-6 py-2 rounded-xl text-[10px] font-bold uppercase tracking-wider transition-all shadow-lg ${
                                action.is_destructive
                                  ? 'bg-red-600 text-white hover:bg-red-500 shadow-red-500/10'
                                  : 'bg-white text-black hover:bg-cyan-50 shadow-white/5'
                              }`}
                            >
                              Execute Protocol
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {response.needs_more_info && (
                  <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-2xl p-6 flex gap-4">
                    <AlertTriangle className="w-5 h-5 text-yellow-500 shrink-0" />
                    <div className="space-y-1">
                      <h4 className="text-sm font-bold text-yellow-500/80 uppercase tracking-tight">Signal Interference</h4>
                      <p className="text-xs text-yellow-500/60 leading-relaxed">Evidence streams are currently insufficient. Supplemental logs or visual evidence recommended for higher confidence analysis.</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
