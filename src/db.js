import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import path from "node:path";

const dataDir = path.resolve("data");
fs.mkdirSync(dataDir, { recursive: true });

export const db = new DatabaseSync(path.join(dataDir, "tierras-magicas.db"));

db.exec(`
  PRAGMA journal_mode = WAL;

  CREATE TABLE IF NOT EXISTS reservas (
    id TEXT PRIMARY KEY,
    cabana_id TEXT NOT NULL,
    checkin TEXT NOT NULL,          -- YYYY-MM-DD
    checkout TEXT NOT NULL,         -- YYYY-MM-DD (exclusivo)
    huespedes INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    total INTEGER NOT NULL,
    sena INTEGER NOT NULL,
    estado TEXT NOT NULL,           -- pendiente_pago | confirmada | cancelada
    origen TEXT NOT NULL,           -- web | manual
    mp_preference_id TEXT,
    mp_payment_id TEXT,
    notas TEXT,
    creada TEXT NOT NULL DEFAULT (datetime('now'))
  );

  -- Fechas ocupadas importadas de Airbnb/Booking o bloqueadas a mano
  CREATE TABLE IF NOT EXISTS bloqueos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cabana_id TEXT NOT NULL,
    desde TEXT NOT NULL,
    hasta TEXT NOT NULL,            -- exclusivo
    origen TEXT NOT NULL,           -- airbnb | booking | manual
    uid TEXT,
    resumen TEXT
  );

  CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cabana_id TEXT NOT NULL,
    fecha TEXT NOT NULL,
    tipo TEXT NOT NULL,             -- limpieza | check-in | otro
    descripcion TEXT,
    reserva_id TEXT,
    hecha INTEGER NOT NULL DEFAULT 0
  );

  CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cabana_id TEXT NOT NULL,
    origen TEXT NOT NULL,
    fecha TEXT NOT NULL DEFAULT (datetime('now')),
    ok INTEGER NOT NULL,
    mensaje TEXT
  );
`);

// Migraciones simples: columnas agregadas después de la primera versión
const columnas = db.prepare("PRAGMA table_info(reservas)").all().map((c) => c.name);
if (!columnas.includes("metodo_pago")) db.exec("ALTER TABLE reservas ADD COLUMN metodo_pago TEXT"); // mercadopago | transferencia
if (!columnas.includes("modalidad")) db.exec("ALTER TABLE reservas ADD COLUMN modalidad TEXT NOT NULL DEFAULT 'sena'"); // sena | total
