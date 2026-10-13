<?php
// MaxedHealth Premium: licence service. Upload next to register.php (pspence.co.uk/maxedhealth/licence.php).
// Config lives OUTSIDE the public folder: <parent of public_html>/maxedhealth_licence/config.php returning
//   ['signing_secret' => '<same value as the Worker secret LICENCE_SECRET>', 'admin_secret' => '<long random>']
// State (keys, devices, trials) is one JSON file in the same private folder. See README.md.
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') { http_response_code(204); exit; }

const TOKEN_DAYS = 30;        // a token is re-issued automatically by the app while the key is valid
const TRIAL_DAYS = 14;
const MAX_DEVICES = 2;        // devices one paid key may be bound to
$DIR = getenv('MH_LICENCE_DIR') ?: dirname($_SERVER['DOCUMENT_ROOT'] ?? '.') . '/maxedhealth_licence';
$STATE = $DIR . '/state.json';

function out($code, $arr) { http_response_code($code); echo json_encode($arr); exit; }
function b64u($s) { return rtrim(strtr(base64_encode($s), '+/', '-_'), '='); }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') out(405, ['ok' => false, 'error' => 'POST only']);
if (!is_dir($DIR) && !@mkdir($DIR, 0700, true)) out(500, ['ok' => false, 'error' => 'Server not configured']);
$cfg = @include $DIR . '/config.php';
if (!is_array($cfg) || empty($cfg['signing_secret']) || empty($cfg['admin_secret'])) out(500, ['ok' => false, 'error' => 'Server not configured']);

$in = json_decode(file_get_contents('php://input'), true);
if (!is_array($in)) $in = $_POST;
$action = (string)($in['action'] ?? '');
$device = (string)($in['device'] ?? '');
$validDevice = (bool)preg_match('/^[A-Za-z0-9_-]{16,64}$/', $device);

function token($cfg, $id, $tier, $days) {
    $p = b64u(json_encode(['id' => $id, 'tier' => $tier, 'exp' => time() + $days * 86400]));
    return $p . '.' . b64u(hash_hmac('sha256', $p, $cfg['signing_secret'], true));
}
function verify($cfg, $tok) {
    $parts = explode('.', (string)$tok);
    if (count($parts) !== 2) return null;
    if (!hash_equals(b64u(hash_hmac('sha256', $parts[0], $cfg['signing_secret'], true)), $parts[1])) return null;
    $p = json_decode(base64_decode(strtr($parts[0], '-_', '+/')), true);
    return (is_array($p) && ($p['exp'] ?? 0) > time()) ? $p : null;
}

// Load state under an exclusive lock, run $fn(&$state), save.
function with_state($file, $fn) {
    $fh = fopen($file, 'c+'); if (!$fh) out(500, ['ok' => false, 'error' => 'Could not open state']);
    flock($fh, LOCK_EX);
    $raw = stream_get_contents($fh); $st = $raw ? json_decode($raw, true) : null;
    if (!is_array($st)) $st = ['keys' => [], 'trials' => [], 'throttle' => []];
    $res = $fn($st);
    ftruncate($fh, 0); rewind($fh); fwrite($fh, json_encode($st, JSON_PRETTY_PRINT)); fflush($fh);
    flock($fh, LOCK_UN); fclose($fh); @chmod($file, 0600);
    return $res;
}
function newkey() { $c = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; $s = ''; for ($i = 0; $i < 16; $i++) $s .= $c[random_int(0, 31)]; return implode('-', str_split($s, 4)); }

// ── Admin: issue a key (founder, premium, or a gift) ────────────────────────
if ($action === 'issue') {
    if (!hash_equals($cfg['admin_secret'], (string)($in['admin'] ?? ''))) out(403, ['ok' => false, 'error' => 'Not allowed']);
    $tier = in_array($in['tier'] ?? '', ['founder', 'premium'], true) ? $in['tier'] : 'premium';
    $note = mb_substr(preg_replace('/[\r\n]+/u', ' ', (string)($in['note'] ?? '')), 0, 80);
    $max = max(1, min(10, (int)($in['max_devices'] ?? ($tier === 'founder' ? 5 : MAX_DEVICES))));
    $key = with_state($STATE, function (&$st) use ($tier, $note, $max) {
        $k = newkey(); $st['keys'][hash('sha256', $k)] = ['tier' => $tier, 'note' => $note, 'max' => $max, 'devices' => [], 'created' => gmdate('c'), 'revoked' => false];
        return $k;
    });
    out(200, ['ok' => true, 'key' => $key, 'tier' => $tier, 'max_devices' => $max]);
}
if ($action === 'revoke') {
    if (!hash_equals($cfg['admin_secret'], (string)($in['admin'] ?? ''))) out(403, ['ok' => false, 'error' => 'Not allowed']);
    $h = hash('sha256', strtoupper(trim((string)($in['key'] ?? ''))));
    $found = with_state($STATE, function (&$st) use ($h) { if (!isset($st['keys'][$h])) return false; $st['keys'][$h]['revoked'] = true; return true; });
    out($found ? 200 : 404, ['ok' => $found]);
}

// ── Activate / refresh a paid or founder key on this device ─────────────────
if ($action === 'activate') {
    if (!$validDevice) out(400, ['ok' => false, 'error' => 'Missing device id']);
    $k = strtoupper(trim((string)($in['key'] ?? ''))); $h = hash('sha256', $k);
    $ip = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . 'mh-lic');
    $res = with_state($STATE, function (&$st) use ($h, $device, $ip, $cfg) {
        $now = time();
        $st['throttle'][$ip] = array_values(array_filter($st['throttle'][$ip] ?? [], fn($t) => $t > $now - 600)); // wrong guesses in 10 min
        if (count($st['throttle'][$ip]) >= 8) return [429, ['ok' => false, 'error' => 'Too many tries. Please wait a few minutes.']];
        $e = $st['keys'][$h] ?? null;
        if (!$e || $e['revoked']) { $st['throttle'][$ip][] = $now; return [403, ['ok' => false, 'error' => 'That key was not recognised.']]; }
        if (!in_array($device, $e['devices'], true)) {
            if (count($e['devices']) >= $e['max']) return [409, ['ok' => false, 'error' => 'This key is already in use on ' . $e['max'] . ' devices. Contact support to move it.']];
            $st['keys'][$h]['devices'][] = $device;
        }
        $id = substr($h, 0, 12);
        return [200, ['ok' => true, 'token' => token($cfg, $id, $e['tier'], TOKEN_DAYS), 'tier' => $e['tier'], 'days' => TOKEN_DAYS]];
    });
    out($res[0], $res[1]);
}

// ── Start the free 14-day trial (one per device, light per-IP throttle) ─────
if ($action === 'trial') {
    if (!$validDevice) out(400, ['ok' => false, 'error' => 'Missing device id']);
    $ip = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . 'mh-lic');
    $res = with_state($STATE, function (&$st) use ($device, $ip, $cfg) {
        $now = time(); $dh = hash('sha256', $device);
        if (isset($st['trials'][$dh])) {
            $left = $st['trials'][$dh] + TRIAL_DAYS * 86400 - $now;
            if ($left <= 0) return [403, ['ok' => false, 'error' => 'The trial on this device has ended.']];
            return [200, ['ok' => true, 'token' => token($cfg, 't' . substr($dh, 0, 11), 'trial', max(1, (int)ceil($left / 86400))), 'tier' => 'trial', 'days' => (int)ceil($left / 86400)]];
        }
        $st['throttle']['t' . $ip] = array_values(array_filter($st['throttle']['t' . $ip] ?? [], fn($t) => $t > $now - 86400));
        if (count($st['throttle']['t' . $ip]) >= 3) return [429, ['ok' => false, 'error' => 'Too many trials from this connection today.']];
        $st['throttle']['t' . $ip][] = $now; $st['trials'][$dh] = $now;
        return [200, ['ok' => true, 'token' => token($cfg, 't' . substr($dh, 0, 11), 'trial', TRIAL_DAYS), 'tier' => 'trial', 'days' => TRIAL_DAYS]];
    });
    out($res[0], $res[1]);
}

// ── Download the Premium files (only with a valid, unexpired token) ─────────
if ($action === 'download') {
    $p = verify($cfg, $in['token'] ?? '');
    if (!$p) out(403, ['ok' => false, 'error' => 'Licence not valid']);
    $zip = $DIR . '/premium_payload.zip';
    if (!is_file($zip)) out(404, ['ok' => false, 'error' => 'Premium files are not published yet']);
    header('Content-Type: application/zip'); header('Content-Length: ' . filesize($zip)); header('Content-Disposition: attachment; filename="maxedhealth-premium.zip"');
    readfile($zip); exit;
}
out(400, ['ok' => false, 'error' => 'Unknown action']);
