import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import path from "node:path";
import { crearEsquema } from "./esquema.js";

// En producción apuntar DATA_DIR a un volumen persistente (si no, los datos se pierden en cada despliegue)
const dataDir = path.resolve(process.env.DATA_DIR || process.env.RAILWAY_VOLUME_MOUNT_PATH || "data");
fs.mkdirSync(dataDir, { recursive: true });

export const db = new DatabaseSync(path.join(dataDir, "tierras-magicas.db"));

crearEsquema(db);
