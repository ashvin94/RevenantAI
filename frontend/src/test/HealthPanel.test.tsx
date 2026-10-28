import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../App";
import { HealthPanel } from "../components/HealthPanel";
import type { HealthResponse } from "../types/contracts";

const mockHealthyResponse: HealthResponse = {
  status: "ok",
  database: "available",
  ml: "available",
  ai_provider: "gemini",
  ai_configured: true,
  fault_injection_enabled: false,
  version: "0.1.0",
};

const mockDegradedResponse: HealthResponse = {
  status: "degraded",
  database: "available",
  ml: "unavailable",
  ai_provider: "gemini",
  ai_configured: false,
  fault_injection_enabled: true,
  version: "0.1.0",
};

describe("HealthPanel Component", () => {
  it("displays loading state before request resolves", () => {
    render(<HealthPanel health={null} loading={true} error={null} />);
    expect(screen.getByText(/Checking backend status\.\.\./i)).toBeInTheDocument();
  });

  it("displays all real fields for a successful ok response", () => {
    render(<HealthPanel health={mockHealthyResponse} loading={false} error={null} />);
    
    expect(screen.getByText("Backend Gateway Health")).toBeInTheDocument();
    expect(screen.getByText("ok")).toBeInTheDocument();
    expect(screen.getByText("0.1.0")).toBeInTheDocument();
    expect(screen.getByText("Database")).toBeInTheDocument();
    expect(screen.getByText("ML Anomaly Model")).toBeInTheDocument();
    expect(screen.getByText("AI Provider")).toBeInTheDocument();
    expect(screen.getByText("Fault Injection")).toBeInTheDocument();
    expect(screen.getByText("gemini")).toBeInTheDocument();
    expect(screen.getByText("Configured")).toBeInTheDocument();
    expect(screen.getByText("DISABLED")).toBeInTheDocument();
  });

  it("accurately labels degraded status, unavailable ML, and unconfigured AI", () => {
    render(<HealthPanel health={mockDegradedResponse} loading={false} error={null} />);
    
    expect(screen.getByText("degraded")).toBeInTheDocument();
    expect(screen.getByText("unavailable")).toBeInTheDocument();
    expect(screen.getByText("Unconfigured")).toBeInTheDocument();
    expect(screen.getByText("ENABLED")).toBeInTheDocument();
  });

  it("displays API connection error when error prop is present", () => {
    render(
      <HealthPanel
        health={null}
        loading={false}
        error="Unable to connect to the backend API service. Please verify the server is running."
      />
    );
    expect(screen.getByText("Connection Error")).toBeInTheDocument();
    expect(
      screen.getByText("Unable to connect to the backend API service. Please verify the server is running.")
    ).toBeInTheDocument();
  });
});

describe("App End-to-End Shell & Navigation", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("handles non-2xx responses by displaying an error and no success status", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    } as Response);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Connection Error")).toBeInTheDocument();
    });
    expect(screen.queryByText("Overall Status")).not.toBeInTheDocument();
  });

  it("handles network failure by displaying connection error", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new Error("Failed to fetch"));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Connection Error")).toBeInTheDocument();
    });
    expect(screen.getByText(/Unable to connect to the backend API service/i)).toBeInTheDocument();
  });

  it("navigates across all three screens seamlessly", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockHealthyResponse,
    } as Response);

    render(<App />);

    // Default screen is Mission Control
    await waitFor(() => {
      expect(screen.getByText("Backend Gateway Health")).toBeInTheDocument();
    });
    expect(screen.getByText("Telemetry & Order Processing (Phase 2 & Phase 3)")).toBeInTheDocument();

    // Navigate to AI Investigation
    const investigationBtn = screen.getByRole("button", { name: /AI Investigation/i });
    fireEvent.click(investigationBtn);
    expect(screen.getByText("AI Investigation Lab")).toBeInTheDocument();
    expect(screen.getByText(/Phase 4 Capability/i)).toBeInTheDocument();

    // Navigate to Simulation Lab
    const simulationBtn = screen.getByRole("button", { name: /Simulation Lab/i });
    fireEvent.click(simulationBtn);
    expect(screen.getByText("Digital Twin Simulation Lab")).toBeInTheDocument();
    expect(screen.getByText(/Phase 5 Capability/i)).toBeInTheDocument();

    // Navigate back to Mission Control
    const missionBtn = screen.getByRole("button", { name: /Mission Control/i });
    fireEvent.click(missionBtn);
    expect(screen.getByText("Telemetry & Order Processing (Phase 2 & Phase 3)")).toBeInTheDocument();
  });

  it("does not render any fabricated order, incident, plan, metric, or recovery values", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockHealthyResponse,
    } as Response);

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Backend Gateway Health")).toBeInTheDocument();
    });

    // Check that fabricated business entities are absent
    expect(screen.queryByText(/ORD-[0-9]+/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/INCIDENT-[0-9]+/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/RELEASE_EXCESS_RESERVATION/i)).not.toBeInTheDocument();
  });
});
