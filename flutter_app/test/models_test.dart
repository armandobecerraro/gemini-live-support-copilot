import 'package:flutter_test/flutter_test.dart';
import 'package:supportsight_live/models/agent_response.dart';
import 'package:supportsight_live/models/issue_request.dart';

void main() {
  group('Models', () {
    test('Hypothesis.fromJson handles nulls', () {
      final h = Hypothesis.fromJson({});
      expect(h.description, '');
      expect(h.confidence, 0.0);
      expect(h.evidence, isEmpty);
    });

    test('SuggestedAction.fromJson handles nulls', () {
      final a = SuggestedAction.fromJson({});
      expect(a.id, '');
      expect(a.requiresConfirmation, true);
      expect(a.isDestructive, false);
    });

    test('AgentResponse.fromJson handles complex nested data', () {
      final json = {
        'session_id': 's1',
        'hypotheses': [{'description': 'h1', 'confidence': 0.8}],
        'suggested_actions': [{'id': 'a1', 'is_destructive': true}]
      };
      final r = AgentResponse.fromJson(json);
      expect(r.sessionId, 's1');
      expect(r.hypotheses.first.description, 'h1');
      expect(r.suggestedActions.first.id, 'a1');
      expect(r.suggestedActions.first.isDestructive, true);
    });

    test('IssueRequest.toJson creates correct map', () {
      final req = IssueRequest(description: 'desc', logs: 'logs', imageBase64: 'img', sessionId: 's1');
      final json = req.toJson();
      expect(json['description'], 'desc');
      expect(json['logs'], 'logs');
      expect(json['image_base64'], 'img');
      expect(json['session_id'], 's1');
    });
  });
}
