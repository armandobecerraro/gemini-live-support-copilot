import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:http/http.dart' as http;
import 'package:supportsight_live/services/api_service.dart';
import 'package:supportsight_live/models/issue_request.dart';
import 'dart:convert';

class MockHttpClient extends Mock implements http.Client {}

void main() {
  group('ApiService', () {
    late ApiService apiService;
    late MockHttpClient mockHttpClient;

    setUp(() {
      mockHttpClient = MockHttpClient();
      apiService = ApiService(baseUrl: 'http://localhost:8080', client: mockHttpClient);
      registerFallbackValue(Uri.parse('http://localhost:8080'));
    });

    test('analyzeIssue returns AgentResponse on success', () async {
      final mockResponse = {
        'session_id': 's1',
        'correlation_id': 'c1',
        'what_i_understood': 'ok',
        'recommendations': [],
        'hypotheses': [],
        'confidence': 1.0,
        'needs_more_info': false,
        'suggested_actions': []
      };
      
      when(() => mockHttpClient.post(any(), headers: any(named: 'headers'), body: any(named: 'body')))
          .thenAnswer((_) async => http.Response(jsonEncode(mockResponse), 200));

      final result = await apiService.analyzeIssue(IssueRequest(description: 'test'));
      expect(result.sessionId, 's1');
      expect(result.confidence, 1.0);
    });

    test('analyzeIssue throws on error', () async {
      when(() => mockHttpClient.post(any(), headers: any(named: 'headers'), body: any(named: 'body')))
          .thenAnswer((_) async => http.Response('Error', 500));

      expect(() => apiService.analyzeIssue(IssueRequest(description: 'test')), throwsException);
    });

    test('confirmAction returns map on success', () async {
      final mockResponse = {'status': 'approved'};
      when(() => mockHttpClient.post(any(), headers: any(named: 'headers'), body: any(named: 'body')))
          .thenAnswer((_) async => http.Response(jsonEncode(mockResponse), 200));

      final result = await apiService.confirmAction('s1', 'a1', true);
      expect(result['status'], 'approved');
    });
  });
}
