/// Backend URL for the SupportSight Live orchestrator.
/// Set at build time: flutter run --dart-define=BACKEND_URL=https://...
/// - Simulator / same machine: http://localhost:8080 (default)
/// - Physical device (same WiFi): http://YOUR_MAC_IP:8080
/// - Production: your Cloud Run backend URL (e.g. https://supportsight-backend-xxx.run.app)
const String kBackendBaseUrl = String.fromEnvironment(
  'BACKEND_URL',
  defaultValue: 'http://localhost:8080',
);
