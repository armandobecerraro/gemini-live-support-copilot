# Running SupportSight Live on iPhone (for demo video)

This guide explains how to run the Flutter app on a physical iPhone or the iOS Simulator so you can show it in your demo video.

## Prerequisites

- Mac with Xcode and Flutter installed (`flutter doctor` shows ✓ for iOS)
- iPhone connected by USB, or iOS Simulator
- Backend running somewhere the device can reach (see options below)

## Option A: iPhone + backend en tu Mac (misma WiFi)

1. **Start the backend on your Mac** (Docker or individual services):

   ```bash
   # From repo root — start all services
   docker-compose -f docker-compose.local.yml up --build
   ```

   The orchestrator will be at `http://localhost:8080`. For a **physical iPhone**, the phone cannot use "localhost"; it must use your Mac's IP.

2. **Get your Mac's local IP** (same WiFi as the iPhone):

   ```bash
   ipconfig getifaddr en0
   # Example: 192.168.1.105
   ```

3. **Run the Flutter app on the iPhone** with that URL:

   ```bash
   cd flutter_app
   flutter run --dart-define=BACKEND_URL=http://192.168.1.105:8080
   ```

   If multiple devices are connected, choose the iPhone:

   ```bash
   flutter devices   # list devices
   flutter run -d 00008140-000678263E39801C --dart-define=BACKEND_URL=http://192.168.1.105:8080
   ```

4. The app will open on the iPhone and call the backend on your Mac. You can now **record the screen** (iPhone: Settings → Control Center → Screen Recording) for the demo video.

## Option B: iOS Simulator (no iPhone needed)

1. Start the backend on your Mac (e.g. `docker-compose -f docker-compose.local.yml up --build`).
2. From the simulator, "localhost" is your Mac, so no `BACKEND_URL` needed:

   ```bash
   cd flutter_app
   flutter run
   ```

   Pick the iOS Simulator when prompted. The app will use `http://localhost:8080` by default.

3. Record the simulator window with QuickTime (File → New Screen Recording) or another tool.

## Option C: Backend en producción (Cloud Run)

If the backend is already deployed (e.g. Cloud Run), use its URL so the iPhone doesn’t depend on your Mac:

```bash
cd flutter_app
flutter run --dart-define=BACKEND_URL=https://supportsight-backend-XXXXXX.run.app
```

Replace with your real backend URL (from `gcloud run services describe supportsight-backend --region=... --format='value(status.url)'` or your deploy output).

## Grabar el video

- **iPhone físico:** Activa “Grabación de pantalla” en Centro de control y graba mientras usas la app. Luego pasa el vídeo al Mac (AirDrop, Photos, etc.).
- **Simulador:** En el Mac, QuickTime → Archivo → Nueva grabación de pantalla → selecciona la ventana del simulador.
- **Opción sin voz:** Graba pantalla y luego añade narración o subtítulos con una herramienta de IA (ver README o documentación del challenge).

## Resumen rápido

| Escenario              | Comando |
|------------------------|--------|
| Simulador + backend Mac | `cd flutter_app && flutter run` |
| iPhone + backend Mac    | `flutter run --dart-define=BACKEND_URL=http://TU_IP_MAC:8080` |
| iPhone/Sim + producción | `flutter run --dart-define=BACKEND_URL=https://tu-backend.run.app` |
