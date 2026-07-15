// Single source of truth for backend calls. Components should never
// call fetch() directly — they call functions exported from here.

const API_BASE_URL = "http://localhost:8000";

// TODO (Phase 5): uploadFile(), submitManualSchema(), generateSql()

export { API_BASE_URL };
