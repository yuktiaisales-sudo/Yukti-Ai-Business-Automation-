import 'package:http/http.dart' as http;

class CrmConnectionService {
  static Future<CatalogResult> validateCrmUrl(String value) async {
    var text = value.trim();
    if (text.isEmpty) return const CatalogResult(false, 'Please enter your CRM URL.');

    if (!text.startsWith('http://') && !text.startsWith('https://')) {
      text = 'https://$text';
    }

    final uri = Uri.tryParse(text);
    if (uri == null || uri.host.isEmpty) {
      return const CatalogResult(false, 'Please enter a valid CRM URL.');
    }

    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 8));
      if (response.statusCode >= 200 && response.statusCode < 500) {
        return CatalogResult(true, 'CRM URL is reachable.', normalizedUrl: uri.toString());
      }
    } catch (_) {}

    // A valid URL may reject automated requests; continue to CRM login.
    return CatalogResult(
      true,
      'CRM URL format is valid. Continue with your CRM login.',
      normalizedUrl: uri.toString(),
    );
  }
}

class CatalogResult {
  final bool success;
  final String message;
  final String? normalizedUrl;

  const CatalogResult(this.success, this.message, {this.normalizedUrl});
}
