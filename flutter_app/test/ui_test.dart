import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:supportsight_live/widgets/response_panel.dart';
import 'package:supportsight_live/widgets/input_panel.dart';
import 'package:supportsight_live/screens/home_screen.dart';
import 'package:supportsight_live/models/agent_response.dart';
import 'package:supportsight_live/models/issue_request.dart';
import 'package:supportsight_live/services/api_service.dart';

class MockApiService extends Mock implements ApiService {}

void main() {
  late MockApiService mockApi;

  setUp(() {
    mockApi = MockApiService();
    registerFallbackValue(IssueRequest(description: 'test'));
  });

  group('HomeScreen', () {
    testWidgets('successfully analyzes an issue', (tester) async {
      final response = AgentResponse(
        sessionId: 's1',
        correlationId: 'c1',
        whatIUnderstood: 'ok',
        recommendations: [],
        hypotheses: [],
        confidence: 1.0,
        needsMoreInfo: false,
        suggestedActions: [],
      );

      when(() => mockApi.analyzeIssue(any())).thenAnswer((_) async => response);

      await tester.pumpWidget(MaterialApp(home: HomeScreen(api: mockApi)));
      
      await tester.enterText(find.byType(TextField).first, 'My issue description');
      await tester.tap(find.text('Analyze Incident'));
      await tester.pump(const Duration(milliseconds: 50)); // Start loading
      
      await tester.pumpAndSettle(); // Wait for API and animations
      expect(find.text('ok'), findsOneWidget);
    });

    testWidgets('renders narrow layout', (tester) async {
      tester.view.physicalSize = const Size(400, 800);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);
      
      await tester.pumpWidget(MaterialApp(home: HomeScreen(api: mockApi)));
      expect(find.byType(SingleChildScrollView), findsWidgets);
    });

    testWidgets('handles error during analysis', (tester) async {
      when(() => mockApi.analyzeIssue(any())).thenThrow(Exception('API Failure'));

      await tester.pumpWidget(MaterialApp(home: HomeScreen(api: mockApi)));
      
      await tester.enterText(find.byType(TextField).first, 'Trigger error');
      await tester.tap(find.text('Analyze Incident'));
      await tester.pumpAndSettle();
      
      expect(find.text('Exception: API Failure'), findsOneWidget);
    });

    testWidgets('does not analyze if description is empty', (tester) async {
      await tester.pumpWidget(MaterialApp(home: HomeScreen(api: mockApi)));
      await tester.tap(find.text('Analyze Incident'));
      await tester.pump();
      verifyNever(() => mockApi.analyzeIssue(any()));
    });
  });

  group('ResponsePanel', () {
    testWidgets('renders loading state', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: ResponsePanel(loading: true, api: mockApi),
        ),
      ));
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('renders initial empty state', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: ResponsePanel(loading: false, api: mockApi, response: null),
        ),
      ));
      expect(find.text('SupportSight will analyze your incident'), findsOneWidget);
    });

    testWidgets('renders full response with hypotheses and actions', (tester) async {
      final response = AgentResponse(
        sessionId: 's1',
        correlationId: 'c1',
        whatIUnderstood: 'Understood text',
        whatISee: 'Vision text',
        nextAction: 'Action text',
        recommendations: ['Rec 1'],
        hypotheses: [Hypothesis(description: 'Hyp 1', confidence: 0.8, evidence: [])],
        confidence: 0.8,
        needsMoreInfo: false,
        suggestedActions: [SuggestedAction(id: 'a1', title: 'Title 1', description: 'Desc 1', requiresConfirmation: true, isDestructive: true)],
      );

      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: ResponsePanel(loading: false, api: mockApi, response: response),
        ),
      ));

      expect(find.text('Understood text'), findsOneWidget);
      expect(find.text('Vision text'), findsOneWidget);
      expect(find.text('Action text'), findsOneWidget);
      expect(find.text('Hyp 1'), findsOneWidget);
      expect(find.text('Title 1'), findsOneWidget);
    });
  });

  group('InputPanel', () {
    testWidgets('renders initial state', (tester) async {
      final desc = TextEditingController();
      final logs = TextEditingController();
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: InputPanel(descController: desc, logsController: logs, loading: false, onAnalyze: () {}),
        ),
      ));
      expect(find.text('Incident Description'), findsOneWidget);
      expect(find.text('Paste Logs (optional)'), findsOneWidget);
    });

    testWidgets('shows error message', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: InputPanel(descController: TextEditingController(), logsController: TextEditingController(), loading: false, onAnalyze: () {}, error: 'Failed'),
        ),
      ));
      expect(find.text('Failed'), findsOneWidget);
    });
  });
}
