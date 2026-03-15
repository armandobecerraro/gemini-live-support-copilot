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
  Trash2
} from 'lucide-react';

export default function Home() {
  const [description, setDescription] = useState('');
  const [logs, setLogs] = useState('');
  const [sessionId] = useState(uuidv4());
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
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

  return (
    <main className="min-h-screen bg-[#050505] text-gray-100 selection:bg-cyan-500/30">
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
