<?php
// MaxedHealth Premium: register-interest handler.
// Stores each sign-up as one CSV line OUTSIDE the public web folder and emails a notice.
// Upload to the same folder as index.html. See README.md in this folder.
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

$NOTIFY_TO = 'pspence@pspence.co.uk';
// Private folder one level above the public web root (public_html). Created if missing.
$DATA_DIR  = dirname($_SERVER['DOCUMENT_ROOT']) . '/maxedhealth_interest';
$CSV       = $DATA_DIR . '/interest.csv';

function fail($code, $msg) { http_response_code($code); echo json_encode(['ok' => false, 'error' => $msg]); exit; }

if ($_SERVER['REQUEST_METHOD'] !== 'POST') fail(405, 'Please use the form.');
if (!empty($_POST['website'])) { echo json_encode(['ok' => true]); exit; } // honeypot: pretend success

$email = trim((string)($_POST['email'] ?? ''));
$name  = trim((string)($_POST['name'] ?? ''));
$plat  = (string)($_POST['platform'] ?? 'other');
if (!filter_var($email, FILTER_VALIDATE_EMAIL) || strlen($email) > 120) fail(400, 'Please enter a valid email address.');
if (empty($_POST['consent'])) fail(400, 'Please tick the box so I know I can email you.');
if (!in_array($plat, ['android', 'iphone', 'other'], true)) $plat = 'other';
$name = mb_substr(preg_replace('/[\r\n,"]+/u', ' ', $name), 0, 60);

if (!is_dir($DATA_DIR) && !@mkdir($DATA_DIR, 0700, true)) fail(500, 'Could not save. Please try again later.');

// Light rate limit: one sign-up per IP per 30 seconds.
$ipHash = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . 'mh-salt');
$stamp  = $DATA_DIR . '/rl_' . substr($ipHash, 0, 16);
if (file_exists($stamp) && time() - filemtime($stamp) < 30) fail(429, 'Please wait a moment and try again.');
@touch($stamp);

// Guard against spreadsheet formula injection.
function safe($v) { return preg_match('/^[=+\-@]/', $v) ? "'" . $v : $v; }

$row = [gmdate('c'), safe($email), safe($name), $plat, 'consent=yes'];
$fh = @fopen($CSV, 'a');
if (!$fh) fail(500, 'Could not save. Please try again later.');
flock($fh, LOCK_EX);
if (filesize($CSV) === 0) fputcsv($fh, ['when_utc', 'email', 'first_name', 'phone', 'consent']);
fputcsv($fh, $row);
flock($fh, LOCK_UN);
fclose($fh);
@chmod($CSV, 0600);

@mail($NOTIFY_TO, 'MaxedHealth Premium: new interest', "New sign-up\nEmail: $email\nName: $name\nPhone: $plat\n", "From: no-reply@pspence.co.uk\r\nContent-Type: text/plain; charset=utf-8");

echo json_encode(['ok' => true]);
