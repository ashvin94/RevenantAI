export interface HealthResponse {
  status: "ok" | "degraded";
  database: "available" | "unavailable";
  ml: "available" | "unavailable";
  ai_provider: "gemini" | "groq" | "unavailable";
  ai_configured: boolean;
  fault_injection_enabled: boolean;
  version: string;
}

export interface OrderResponse { id: string; sku: string; quantity: number; status: string; version: number; }
export interface FaultResponse { injected_reservation_id: string; order_id: string; order_version: number; }
export interface InspectionResponse { order_id: string; healthy: boolean; incident: { id: string; status: string } | null; rules: Array<{ id: string; passed: boolean; expected: number | string; actual: number | string }> }
export interface MLScoreResponse { order_id: string; available: boolean; suspicious: boolean | null; score: number | null; reason?: string; synthetic_metrics?: Record<string, unknown> | null }
export interface SimulationResponse { incident_id: string; safe: boolean; after_available_stock: number; active_reservations_after: number; expected_order_version: number; candidate: { id: "RELEASE_DUPLICATE"; reservation_id: string } }
export interface RecoveryResponse { status: "COMMITTED" | "REPLAYED"; verified: boolean; available_stock: number; active_reservations: number; released_reservation_id: string }
export interface AnalysisResponse { incident_id: string; provider: "gemini" | "groq"; proposal: { root_cause: string; confidence: number; candidate: { id: "RELEASE_DUPLICATE"; reservation_id: string }; evidence_ids: string[] } }
