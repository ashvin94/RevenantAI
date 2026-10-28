import type { AnalysisResponse, FaultResponse, HealthResponse, InspectionResponse, MLScoreResponse, OrderResponse, RecoveryResponse, SimulationResponse } from "../types/contracts";

const getApiBaseUrl = (): string => {
  return import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
};

export async function fetchHealth(): Promise<HealthResponse> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl.replace(/\/+$/, "")}/api/health`;

  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });
  } catch {
    throw new Error("Unable to connect to the backend API service. Please verify the server is running.");
  }

  if (!response.ok) {
    throw new Error(`API health check failed with status ${response.status} (${response.statusText || "Error"})`);
  }

  try {
    const data = (await response.json()) as HealthResponse;
    return data;
  } catch {
    throw new Error("Invalid response format received from the health check endpoint.");
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl().replace(/\/+$/, "")}${path}`, { ...init, headers: { "Content-Type": "application/json", Accept: "application/json", ...init?.headers } });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || `API request failed (${response.status})`); }
  return response.json() as Promise<T>;
}

export const createOrder = (logical_event_id: string) => request<OrderResponse>("/api/orders", { method: "POST", body: JSON.stringify({ sku: "LAPTOP-001", quantity: 1, logical_event_id }) });
export const injectDuplicate = (orderId: string) => request<FaultResponse>(`/api/orders/${orderId}/inject-duplicate`, { method: "POST" });
export const scoreOrder = (orderId: string) => request<MLScoreResponse>(`/api/orders/${orderId}/ml-score`);
export const inspectOrder = (orderId: string) => request<InspectionResponse>(`/api/orders/${orderId}/inspect`, { method: "POST" });
export const analyzeIncident = (incidentId: string) => request<AnalysisResponse>(`/api/incidents/${incidentId}/analyze`, { method: "POST" });
export const simulateRepair = (incidentId: string, reservationId: string) => request<SimulationResponse>(`/api/incidents/${incidentId}/simulate`, { method: "POST", body: JSON.stringify({ candidate: { id: "RELEASE_DUPLICATE", reservation_id: reservationId } }) });
export const recoverIncident = (incidentId: string, reservationId: string, expectedOrderVersion: number) => request<RecoveryResponse>(`/api/incidents/${incidentId}/recover`, { method: "POST", body: JSON.stringify({ candidate: { id: "RELEASE_DUPLICATE", reservation_id: reservationId }, expected_order_version: expectedOrderVersion, idempotency_key: `ui-${incidentId}`, approved: true }) });
