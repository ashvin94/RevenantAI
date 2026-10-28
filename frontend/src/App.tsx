import { useState, useEffect, useCallback } from "react";
import { AppLayout } from "./components/AppLayout";
import type { ScreenId } from "./components/Navigation";
import { MissionControl } from "./pages/MissionControl";
import { Investigation } from "./pages/Investigation";
import { SimulationLab } from "./pages/SimulationLab";
import { fetchHealth } from "./lib/api";
import type { HealthResponse } from "./types/contracts";

export function App() {
  const [currentScreen, setCurrentScreen] = useState<ScreenId>("mission-control");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred while fetching health status.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHealth();
  }, [loadHealth]);

  return (
    <AppLayout currentScreen={currentScreen} onSelectScreen={setCurrentScreen}>
      {currentScreen === "mission-control" && (
        <MissionControl
          health={health}
          loading={loading}
          error={error}
          onRefresh={loadHealth}
        />
      )}
      {currentScreen === "investigation" && <Investigation />}
      {currentScreen === "simulation-lab" && <SimulationLab />}
    </AppLayout>
  );
}

export default App;
