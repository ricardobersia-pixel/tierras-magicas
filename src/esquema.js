// Tablas y migraciones de la base. Las usa el servidor (node:sqlite) y la app de prueba del teléfono (sql.js).
export function crearEsquema(db) {
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
  if (!columnas.includes("adicionales")) db.exec("ALTER TABLE reservas ADD COLUMN adicionales INTEGER NOT NULL DEFAULT 0"); // personas en el dormi
  if (!columnas.includes("canal")) db.exec("ALTER TABLE reservas ADD COLUMN canal TEXT"); // web | whatsapp | instagram | telefono | ... (de dónde vino)

  // Finanzas: cobros, gastos y reservas de Airbnb/Booking (con su monto, cargado a mano)
  db.exec(`
    CREATE TABLE IF NOT EXISTS pagos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fecha TEXT NOT NULL,            -- YYYY-MM-DD en que entró el dinero
      reserva_id TEXT,                -- reserva directa (NULL si es otro ingreso)
      ota_id INTEGER,                 -- reserva de Airbnb/Booking
      concepto TEXT NOT NULL,         -- sena | saldo | total | extra | ota | otro
      medio TEXT NOT NULL,            -- efectivo | transferencia | mercadopago | plataforma
      monto INTEGER NOT NULL,
      nota TEXT,
      usuario_id INTEGER,
      creado TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS gastos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fecha TEXT NOT NULL,            -- YYYY-MM-DD (en los fijos mensuales: desde qué mes)
      categoria TEXT NOT NULL,
      concepto TEXT NOT NULL,
      monto INTEGER NOT NULL,
      tipo TEXT NOT NULL,             -- fijo | variable
      mensual INTEGER NOT NULL DEFAULT 0, -- 1: se repite todos los meses desde fecha
      hasta TEXT,                     -- YYYY-MM: último mes de un gasto mensual dado de baja
      nota TEXT,
      usuario_id INTEGER,
      creado TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- Registro permanente de las reservas importadas por iCal (los bloqueos se reemplazan en cada sincronización)
    CREATE TABLE IF NOT EXISTS reservas_ota (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cabana_id TEXT NOT NULL,
      origen TEXT NOT NULL,           -- airbnb | booking
      uid TEXT NOT NULL,
      desde TEXT NOT NULL,
      hasta TEXT NOT NULL,
      resumen TEXT,
      monto_neto INTEGER,             -- lo que deposita la plataforma (NULL: sin cargar)
      comision INTEGER,
      cancelada INTEGER NOT NULL DEFAULT 0,
      UNIQUE (origen, uid)
    );

    -- Turnos de jacuzzi, sauna, kayaks y tablas de stand up (recursos en config.json o editados en el panel)
    CREATE TABLE IF NOT EXISTS turnos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      fecha TEXT NOT NULL,            -- YYYY-MM-DD
      hora TEXT NOT NULL,             -- HH:MM de inicio
      recurso TEXT NOT NULL,          -- id del recurso
      cantidad INTEGER NOT NULL DEFAULT 1,
      cabana_id TEXT,
      reserva_id TEXT,
      nombre TEXT,
      nota TEXT,
      usuario_id INTEGER,
      creado TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- Tarifas y temporadas editadas desde el panel (reemplazan las de config.json)
    CREATE TABLE IF NOT EXISTS ajustes (
      clave TEXT PRIMARY KEY,
      valor TEXT NOT NULL,
      actualizado TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);
}
