import 'package:http/http.dart' as http;

class CrmConnectionService {
  static Future<CrmUrlResult> validateUrl(String value) async {
    var text = value.trim();

    if (text.isEmpty) {
      return const CrmUrlResult(false, 'Please enter your CRM URL.');
    }

    if (!text.startsWith('http://') && !text.startsWith('https://')) {
      text = 'https://$text';
    }

    final uri = Uri.tryParse(text);

    if (uri == null || uri.host.isEmpty) {
      return const CrmUrlResult(false, 'Please enter a valid CRM URL.');
    }

    // We validate the URL and try to reach it. Some CRMs reject automated
    // requests, so a network rejection does not automatically mean the URL
    // is invalid.
    try {
      final response = await http.get(uri).timeout(
        const Duration(seconds: 8),
      );

      if (response.statusCode >= 200 && response.statusCode < 500) {
        return CrmUrlResult(
          true,
          'CRM URL is reachable.',
          normalizedUrl: uri.toString(),
        );
      }
    } catch (_) {}

    return CrmUrlResult(
      true,
      'CRM URL format is valid. Continue with login.',
      normalizedUrl: uri.toString(),
    );
  }
}

class CrmUrlResult {
  final bool success;
  final String message;
  final String? normalizedUrl;

  const CrmUrlResult(
    this.success,
    this.message, {
    this.normalizedUrl,
  });
}
