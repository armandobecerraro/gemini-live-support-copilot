import 'package:flutter/material.dart';
import 'config.dart';
import 'screens/home_screen.dart';
import 'services/api_service.dart';

void main() => runApp(const SupportSightApp());

class SupportSightApp extends StatelessWidget {
  const SupportSightApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'SupportSight Live',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorScheme: const ColorScheme.dark(primary: Color(0xFF01696F), secondary: Color(0xFF4F98A3)),
      useMaterial3: true,
    ),
    home: HomeScreen(api: ApiService(baseUrl: kBackendBaseUrl)),
  );
}
