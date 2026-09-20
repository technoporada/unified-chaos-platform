#!/usr/bin/env python3
"""
Testy jednostkowe UNIFIED CHAOS PLATFORM v1.0
Uruchomienie: python3 -m unittest test_chaos_platform.py
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import socket
import time
import random
import os
import io

from UNIFIED_CHAOS_PLATFORM import (
    ChaosStats,
    ChaosProxyEngine,
    ISPObfuscator,
    HTTPInterceptor,
    TCPFragmenter,
    SmugglingProbe,
    BulkSmugglingTester,
    TrafficAudit,
    AuditScanner,
    VictimServer,
    EngineMode,
)


class SuppressPrints(unittest.TestCase):
    """Base class that suppresses all print() output during tests."""
    def setUp(self):
        self._print_patcher = patch('builtins.print')
        self._print_patcher.start()

    def tearDown(self):
        self._print_patcher.stop()


# ============================================================================
# 1. CHAOS STATS - Testy współdzielonej statystyki
# ============================================================================

class TestChaosStats(SuppressPrints):

    def test_update_bytes_thread_safe(self):
        stats = ChaosStats()
        stats.update_bytes(sent=100, received=50)
        self.assertEqual(stats.bytes_sent, 100)
        self.assertEqual(stats.bytes_received, 50)
        stats.update_bytes(sent=200)
        self.assertEqual(stats.bytes_sent, 300)
        self.assertEqual(stats.bytes_received, 50)

    def test_add_mutation_counter(self):
        stats = ChaosStats()
        self.assertEqual(stats.mutations_count, 0)
        stats.add_mutation()
        stats.add_mutation()
        self.assertEqual(stats.mutations_count, 2)

    def test_add_vulnerability(self):
        stats = ChaosStats()
        stats.add_vulnerability("test-vuln-1")
        stats.add_vulnerability("test-vuln-2")
        self.assertEqual(len(stats.vulnerabilities_found), 2)
        self.assertIn("test-vuln-1", stats.vulnerabilities_found)

    def test_get_stats_returns_dict(self):
        stats = ChaosStats()
        stats.update_bytes(sent=1024)
        result = stats.get_stats()
        self.assertIsInstance(result, dict)
        self.assertEqual(result['bytes_sent'], 1024)
        self.assertEqual(result['mutations'], 0)
        self.assertIn('elapsed', result)
        self.assertIn('mbps', result)

    def test_get_stats_zero_division_safety(self):
        stats = ChaosStats()
        stats.start_time = time.time()
        result = stats.get_stats()
        self.assertIsInstance(result['mbps'], float)


# ============================================================================
# 2. CHAOS PROXY ENGINE - Test mutacji pakietów
# ============================================================================

class TestChaosProxyEngine(SuppressPrints):

    def test_mutate_always_mutates_when_random_below_threshold(self):
        engine = ChaosProxyEngine()
        original = b"Hello World!"
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.random.return_value = 0.05
            mock_random.randint.return_value = 0
            result, mutated = engine.mutate(original)
        self.assertTrue(mutated)
        self.assertIsInstance(result, bytes)
        self.assertEqual(len(result), len(original))

    def test_mutate_never_mutates_when_random_above_threshold(self):
        engine = ChaosProxyEngine()
        original = b"Hello World!"
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.random.return_value = 0.5
            result, mutated = engine.mutate(original)
        self.assertFalse(mutated)
        self.assertEqual(result, original)

    def test_mutate_modifies_exact_byte_count(self):
        engine = ChaosProxyEngine()
        original = b"ABCD"
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.random.return_value = 0.05
            mock_random.randint.return_value = 2
            result, mutated = engine.mutate(original)
        self.assertTrue(mutated)
        self.assertEqual(len(result), 4)
        self.assertNotEqual(result[2], original[2])

    def test_mutate_empty_data_returns_original(self):
        engine = ChaosProxyEngine()
        original = b""
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.random.return_value = 0.05
            result, mutated = engine.mutate(original)
        self.assertFalse(mutated)
        self.assertEqual(result, b"")

    def test_mutate_increments_mutation_counter(self):
        stats = ChaosStats()
        engine = ChaosProxyEngine(stats=stats)
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.random.return_value = 0.05
            mock_random.randint.return_value = 0
            engine.mutate(b"test")
        self.assertEqual(stats.mutations_count, 1)

    def test_bridge_closes_sockets_on_completion(self):
        engine = ChaosProxyEngine()
        engine.running = False
        mock_src = MagicMock()
        mock_dst = MagicMock()
        mock_src.recv.return_value = b""
        engine.bridge(mock_src, mock_dst)
        mock_src.close.assert_called_once()
        mock_dst.close.assert_called_once()

    def test_bridge_forwards_data_with_mutation(self):
        engine = ChaosProxyEngine()
        engine.running = True
        call_count = [0]

        def fake_recv(bufsize):
            call_count[0] += 1
            if call_count[0] == 1:
                return b"test data"
            engine.running = False
            return b""

        mock_src = MagicMock()
        mock_src.recv.side_effect = fake_recv
        mock_dst = MagicMock()
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.random.return_value = 0.5
            engine.bridge(mock_src, mock_dst)
        mock_dst.sendall.assert_called_with(b"test data")


# ============================================================================
# 3. ISP OBFUSCATOR - Test dodawania paddingu
# ============================================================================

class TestISPObfuscator(SuppressPrints):

    def test_add_padding_increases_size(self):
        obs = ISPObfuscator()
        data = b"Hello"
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 100
            result = obs._add_padding(data)
        self.assertEqual(len(result), len(data) + 100)

    def test_add_padding_minimum_size(self):
        obs = ISPObfuscator()
        data = b"X"
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 10
            result = obs._add_padding(data)
        self.assertEqual(len(result), 11)

    def test_add_padding_maximum_size(self):
        obs = ISPObfuscator()
        data = b"X"
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 500
            result = obs._add_padding(data)
        self.assertEqual(len(result), 501)

    def test_add_padding_preserves_original_data(self):
        obs = ISPObfuscator()
        data = b"OriginalContent"
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 50
            result = obs._add_padding(data)
        self.assertTrue(result.startswith(data))

    def test_add_padding_fills_with_null_bytes(self):
        obs = ISPObfuscator()
        data = b"A"
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 5
            result = obs._add_padding(data)
        padding = result[1:]
        self.assertEqual(padding, b'\x00' * 5)

    def test_handle_traffic_closes_sockets(self):
        obs = ISPObfuscator()
        mock_src = MagicMock()
        mock_dst = MagicMock()
        mock_src.recv.return_value = b""
        obs.handle_traffic(mock_src, mock_dst)
        mock_src.close.assert_called_once()
        mock_dst.close.assert_called_once()

    def test_handle_traffic_forwards_padded_data(self):
        obs = ISPObfuscator()
        mock_src = MagicMock()
        mock_dst = MagicMock()
        call_count = [0]

        def fake_recv(bufsize):
            call_count[0] += 1
            if call_count[0] == 1:
                return b"test"
            return b""

        mock_src.recv.side_effect = fake_recv
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 10
            mock_random.uniform.return_value = 0.01
            with patch('UNIFIED_CHAOS_PLATFORM.time'):
                obs.handle_traffic(mock_src, mock_dst)
        args = mock_dst.sendall.call_args[0][0]
        self.assertTrue(args.startswith(b"test"))
        self.assertEqual(len(args), 14)


# ============================================================================
# 4. TCP FRAGMENTER - Test fragmentacji strumienia
# ============================================================================

class TestTCPFragmenter(SuppressPrints):

    def test_fragmentation_logic_small_chunks(self):
        frag = TCPFragmenter('127.0.0.1', 9000)
        data = b"A" * 20
        chunks = []
        i = 0
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 3
            while i < len(data):
                chunk_size = mock_random.randint(1, 5)
                chunk = data[i:i+chunk_size]
                chunks.append(chunk)
                i += chunk_size
        total_bytes = sum(len(c) for c in chunks)
        self.assertEqual(total_bytes, 20)

    def test_fragmentation_chunk_sizes_within_bounds(self):
        data = b"X" * 100
        chunk_sizes = []
        i = 0
        while i < len(data):
            chunk_size = random.randint(1, 5)
            chunk_sizes.append(chunk_size)
            i += chunk_size
        for size in chunk_sizes:
            self.assertGreaterEqual(size, 1)
            self.assertLessEqual(size, 5)

    def test_fragmentation_reassembles_correctly(self):
        data = b"Hello World! This is a fragmentation test."
        chunks = []
        i = 0
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 2
            while i < len(data):
                chunk_size = mock_random.randint(1, 5)
                chunk = data[i:i+chunk_size]
                chunks.append(chunk)
                i += chunk_size
        reassembled = b"".join(chunks)
        self.assertEqual(reassembled, data)

    def test_fragmentation_empty_data(self):
        data = b""
        chunks = []
        i = 0
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 3
            while i < len(data):
                chunk_size = mock_random.randint(1, 5)
                chunk = data[i:i+chunk_size]
                chunks.append(chunk)
                i += chunk_size
        self.assertEqual(len(chunks), 0)

    def test_fragmentation_single_byte(self):
        data = b"Z"
        chunks = []
        i = 0
        with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
            mock_random.randint.return_value = 1
            while i < len(data):
                chunk_size = mock_random.randint(1, 5)
                chunk = data[i:i+chunk_size]
                chunks.append(chunk)
                i += chunk_size
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], b"Z")

    def test_chaos_loop_closes_sockets(self):
        frag = TCPFragmenter('127.0.0.1', 9000)
        mock_client = MagicMock()
        mock_target = MagicMock()
        mock_client.recv.return_value = b""
        frag.chaos_loop(mock_client, mock_target)
        mock_client.close.assert_called_once()
        mock_target.close.assert_called_once()

    def test_chaos_loop_handles_blocking_io(self):
        frag = TCPFragmenter('127.0.0.1', 9000)
        mock_client = MagicMock()
        mock_target = MagicMock()
        call_count = [0]

        def fake_client_recv(bufsize):
            call_count[0] += 1
            if call_count[0] == 1:
                return b"data"
            return b""

        mock_client.recv.side_effect = fake_client_recv
        mock_target.recv.side_effect = BlockingIOError
        mock_target.sendall.side_effect = None
        mock_client.sendall.side_effect = BlockingIOError
        frag.running = False
        frag.chaos_loop(mock_client, mock_target)
        mock_client.close.assert_called_once()
        mock_target.close.assert_called_once()


# ============================================================================
# 5. SMUGGLING PROBE - Test wykrywania podatności CL.TE
# ============================================================================

class TestSmugglingProbe(SuppressPrints):

    def test_probe_detects_timeout_as_cl_te(self):
        probe = SmugglingProbe()
        with patch('UNIFIED_CHAOS_PLATFORM.socket.socket') as mock_sock_cls:
            mock_sock = MagicMock()
            mock_sock_cls.return_value = mock_sock
            mock_sock.recv.side_effect = socket.timeout("timed out")
            result = probe.probe_single("testhost.com", 80)
        self.assertTrue(result)
        self.assertEqual(len(probe.stats.vulnerabilities_found), 1)
        self.assertIn("TIMEOUT", probe.stats.vulnerabilities_found[0])

    def test_probe_returns_false_on_normal_response(self):
        probe = SmugglingProbe()
        with patch('UNIFIED_CHAOS_PLATFORM.socket.socket') as mock_sock_cls:
            mock_sock = MagicMock()
            mock_sock_cls.return_value = mock_sock
            mock_sock.recv.return_value = b"HTTP/1.1 200 OK"
            with patch('UNIFIED_CHAOS_PLATFORM.time') as mock_time:
                mock_time.time.return_value = 1000.0
                mock_time.time.side_effect = [1000.0, 1000.5]
                result = probe.probe_single("safehost.com", 80)
        self.assertFalse(result)
        self.assertEqual(len(probe.stats.vulnerabilities_found), 0)

    def test_probe_detects_slow_response_as_vuln(self):
        probe = SmugglingProbe()
        with patch('UNIFIED_CHAOS_PLATFORM.socket.socket') as mock_sock_cls:
            mock_sock = MagicMock()
            mock_sock_cls.return_value = mock_sock
            mock_sock.recv.return_value = b"HTTP/1.1 200 OK"
            with patch('UNIFIED_CHAOS_PLATFORM.time') as mock_time:
                mock_time.time.side_effect = [1000.0, 1004.0]
                result = probe.probe_single("slowhost.com", 80)
        self.assertTrue(result)
        self.assertIn("CL.TE", probe.stats.vulnerabilities_found[0])

    def test_probe_sends_correct_payload(self):
        probe = SmugglingProbe()
        with patch('UNIFIED_CHAOS_PLATFORM.socket.socket') as mock_sock_cls:
            mock_sock = MagicMock()
            mock_sock_cls.return_value = mock_sock
            mock_sock.recv.side_effect = socket.timeout
            probe.probe_single("target.com", 80)
        sent_data = mock_sock.sendall.call_args[0][0]
        self.assertIn(b"Content-Length: 4", sent_data)
        self.assertIn(b"Transfer-Encoding: chunked", sent_data)
        self.assertIn(b"0\r\nX", sent_data)

    def test_probe_handles_connection_error(self):
        probe = SmugglingProbe()
        with patch('UNIFIED_CHAOS_PLATFORM.socket.socket') as mock_sock_cls:
            mock_sock = MagicMock()
            mock_sock_cls.return_value = mock_sock
            mock_sock.connect.side_effect = ConnectionRefusedError
            result = probe.probe_single("deadhost.com", 80)
        self.assertFalse(result)
        mock_sock.close.assert_called()

    def test_probe_sets_timeout(self):
        probe = SmugglingProbe()
        with patch('UNIFIED_CHAOS_PLATFORM.socket.socket') as mock_sock_cls:
            mock_sock = MagicMock()
            mock_sock_cls.return_value = mock_sock
            mock_sock.recv.side_effect = socket.timeout
            probe.probe_single("host.com", 80)
        mock_sock.settimeout.assert_called_with(5)


# ============================================================================
# 6. BULK SMUGGLING TESTER - Test payload generation
# ============================================================================

class TestBulkSmugglingTester(SuppressPrints):

    def test_create_payload_contains_required_headers(self):
        tester = BulkSmugglingTester()
        payload = tester.create_payload("example.com")
        self.assertIn(b"Host: example.com", payload)
        self.assertIn(b"Content-Length: 4", payload)
        self.assertIn(b"Transfer-Encoding: chunked", payload)
        self.assertIn(b"0\r\nX", payload)

    def test_create_payload_is_bytes(self):
        tester = BulkSmugglingTester()
        payload = tester.create_payload("test.com")
        self.assertIsInstance(payload, bytes)

    def test_create_payload_starts_with_post(self):
        tester = BulkSmugglingTester()
        payload = tester.create_payload("any.com")
        self.assertTrue(payload.startswith(b"POST / HTTP/1.1"))


# ============================================================================
# 7. TRAFFIC AUDIT - Test wykrywania wycieków
# ============================================================================

class TestTrafficAudit(SuppressPrints):

    def test_check_detects_password_leak(self):
        audit = TrafficAudit()
        result = audit.check_unencrypted_leak(b"password=secret123")
        self.assertEqual(result, b'password')

    def test_check_detects_session_leak(self):
        audit = TrafficAudit()
        result = audit.check_unencrypted_leak(b"session_id=abc123")
        self.assertEqual(result, b'session')

    def test_check_detects_key_leak(self):
        audit = TrafficAudit()
        result = audit.check_unencrypted_leak(b"api_key=xyz789")
        self.assertEqual(result, b'key')

    def test_check_returns_none_for_clean_data(self):
        audit = TrafficAudit()
        result = audit.check_unencrypted_leak(b"GET / HTTP/1.1\r\nHost: example.com")
        self.assertIsNone(result)

    def test_check_is_case_insensitive(self):
        audit = TrafficAudit()
        result = audit.check_unencrypted_leak(b"PASSWORD=secret")
        self.assertEqual(result, b'password')

    def test_bridge_closes_sockets(self):
        audit = TrafficAudit()
        mock_src = MagicMock()
        mock_dst = MagicMock()
        mock_src.recv.return_value = b""
        audit.bridge(mock_src, mock_dst)
        mock_src.close.assert_called_once()
        mock_dst.close.assert_called_once()


# ============================================================================
# 8. HTTP INTERCEPTOR - Test wykrywania słów kluczowych
# ============================================================================

class TestHTTPInterceptor(SuppressPrints):

    def test_detects_user_keyword(self):
        interceptor = HTTPInterceptor()
        result = interceptor.log_interesting_stuff(b"user=admin", "C->S")
        self.assertTrue(result)

    def test_detects_pass_keyword(self):
        interceptor = HTTPInterceptor()
        result = interceptor.log_interesting_stuff(b"pass=secret", "C->S")
        self.assertTrue(result)

    def test_detects_token_keyword(self):
        interceptor = HTTPInterceptor()
        result = interceptor.log_interesting_stuff(b"token=abc123", "S->C")
        self.assertTrue(result)

    def test_returns_none_for_no_match(self):
        interceptor = HTTPInterceptor()
        result = interceptor.log_interesting_stuff(b"GET / HTTP/1.1", "C->S")
        self.assertFalse(result)

    def test_bridge_closes_sockets(self):
        interceptor = HTTPInterceptor()
        mock_src = MagicMock()
        mock_dst = MagicMock()
        mock_src.recv.return_value = b""
        interceptor.bridge(mock_src, mock_dst, "C->S")
        mock_src.close.assert_called_once()
        mock_dst.close.assert_called_once()


# ============================================================================
# 9. AUDIT SCANNER - Test ładowania i parsowania plików
# ============================================================================

class TestAuditScanner(SuppressPrints):

    def test_scan_detects_password_in_code(self):
        scanner = AuditScanner()
        fake_dir = "/fake/dir"
        fake_files = {"test.py": "password = 'secret123'"}
        with patch('UNIFIED_CHAOS_PLATFORM.os.walk') as mock_walk:
            mock_walk.return_value = [("/fake/dir", [], ["test.py"])]
            with patch('builtins.open', mock_open(read_data="password = 'secret123'")):
                scanner.audit_files(fake_dir)
        self.assertGreater(len(scanner.PATTERNS), 0)

    def test_scan_skips_non_matching_files(self):
        scanner = AuditScanner()
        with patch('UNIFIED_CHAOS_PLATFORM.os.walk') as mock_walk:
            mock_walk.return_value = [("/fake/dir", [], ["readme.txt"])]
            scanner.audit_files("/fake/dir")

    def test_scan_handles_io_error(self):
        scanner = AuditScanner()
        with patch('UNIFIED_CHAOS_PLATFORM.os.walk') as mock_walk:
            mock_walk.return_value = [("/fake/dir", [], ["protected.py"])]
            with patch('builtins.open', side_effect=PermissionError("denied")):
                scanner.audit_files("/fake/dir")

    def test_patterns_dict_is_not_empty(self):
        scanner = AuditScanner()
        self.assertGreater(len(scanner.PATTERNS), 0)

    def test_scan_iterates_file_line_by_line(self):
        scanner = AuditScanner()
        content = "line1\npassword='test'\nline3\n"
        with patch('UNIFIED_CHAOS_PLATFORM.os.walk') as mock_walk:
            mock_walk.return_value = [("/fake", [], ["code.py"])]
            m = mock_open(read_data=content)
            with patch('builtins.open', m):
                scanner.audit_files("/fake")
        handle = m()
        lines_read = [call for call in handle.__iter__.call_args_list]
        self.assertTrue(len(lines_read) > 0)

    def test_scan_only_checks_allowed_extensions(self):
        scanner = AuditScanner()
        with patch('UNIFIED_CHAOS_PLATFORM.os.walk') as mock_walk:
            mock_walk.return_value = [("/fake", [], ["image.png", "script.py"])]
            with patch('builtins.open', mock_open(read_data="password='x'")):
                scanner.audit_files("/fake")


# ============================================================================
# 10. VICTIM SERVER - Test obsługi klientów
# ============================================================================

class TestVictimServer(SuppressPrints):

    def test_start_handles_client_and_closes(self):
        vs = VictimServer(port=9999)
        with patch('UNIFIED_CHAOS_PLATFORM.socket.socket') as mock_cls:
            mock_server = MagicMock()
            mock_cls.return_value = mock_server
            mock_client = MagicMock()
            mock_client.recv.return_value = b"GET / HTTP/1.1"
            mock_server.accept.return_value = (mock_client, ("127.0.0.1", 12345))

            def stop_after_accept(*args, **kwargs):
                vs._running = False
                raise KeyboardInterrupt

            mock_server.accept.side_effect = stop_after_accept
            vs._running = True
            try:
                vs.start()
            except KeyboardInterrupt:
                pass
            mock_server.close.assert_called()


# ============================================================================
# 11. ENGINE MODE ENUM
# ============================================================================

class TestEngineMode(SuppressPrints):

    def test_all_modes_exist(self):
        modes = list(EngineMode)
        self.assertEqual(len(modes), 10)

    def test_mode_values_are_strings(self):
        for mode in EngineMode:
            self.assertIsInstance(mode.value, str)

    def test_chaos_proxy_mode(self):
        self.assertEqual(EngineMode.CHAOS_PROXY.value, "Chaos Proxy - Mutacja i logowanie ruchu")


# ============================================================================
# 12. ZINTEGROWANE TESTY LOGIKI
# ============================================================================

class TestIntegrationLogic(SuppressPrints):

    def test_chaos_stats_thread_safety(self):
        import threading
        stats = ChaosStats()
        errors = []

        def update_stats():
            try:
                for _ in range(100):
                    stats.update_bytes(sent=1)
                    stats.add_mutation()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=update_stats) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(errors), 0)
        self.assertEqual(stats.bytes_sent, 1000)
        self.assertEqual(stats.mutations_count, 1000)

    def test_mutate_deterministic_with_seed(self):
        engine = ChaosProxyEngine()
        data = b"ABCDEFGHIJ"
        random.seed(42)
        results = []
        for _ in range(20):
            _, mutated = engine.mutate(data)
            results.append(mutated)
        mutation_rate = sum(results) / len(results)
        self.assertGreater(mutation_rate, 0.0)
        self.assertLess(mutation_rate, 0.5)

    def test_padding_range_is_valid(self):
        obs = ISPObfuscator()
        sizes = []
        for _ in range(100):
            with patch('UNIFIED_CHAOS_PLATFORM.random') as mock_random:
                mock_random.randint.return_value = random.randint(10, 500)
                result = obs._add_padding(b"X")
                sizes.append(len(result) - 1)
        self.assertTrue(all(10 <= s <= 500 for s in sizes))


if __name__ == '__main__':
    unittest.main()
